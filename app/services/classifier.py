"""
4-layer classification engine + confidence scoring.

Layer 1  — High-confidence regex rules          (weight 0.50)
Layer 2  — Keyword hash-set lookup              (weight 0.30)
Layer 3  — Semantic phrase matching             (weight 0.20)
Layer 4  — Fallback to CaseType.other

Confidence formula:
    confidence = rule_score*0.5 + keyword_score*0.3 + semantic_score*0.2
"""

from __future__ import annotations

from dataclasses import dataclass

from app.classifiers.keywords import (
    CRITICAL_KW,
    HIGH_KW,
    KEYWORD_SETS,
    MEDIUM_KW,
)
from app.classifiers.rules import apply_rules
from app.classifiers.semantic import apply_semantic
from app.models.ticket import (
    CASE_TYPE_TO_DEPARTMENT,
    CaseType,
    Department,
    Severity,
)
from app.services.extractor import extract_largest_amount
from app.utils.normalizer import preprocess

# Large-amount threshold (BDT) above which human review is warranted
LARGE_AMOUNT_THRESHOLD = 10_000


@dataclass
class ClassificationResult:
    case_type: CaseType
    severity: Severity
    department: Department
    confidence: float
    human_review_required: bool


def _keyword_score(text: str, case_type: CaseType) -> float:
    """
    Fraction of case-type keywords present in the text.
    Capped at 1.0 and normalised to give a meaningful 0-1 score.
    """
    kw_set = KEYWORD_SETS.get(case_type, frozenset())
    if not kw_set:
        return 0.0
    hits = sum(1 for kw in kw_set if kw in text)
    # Score scales quickly: 1 hit → ~0.5, 2 hits → ~0.75, 3+ hits → ~1.0
    return min(1.0, hits / 2)


def _determine_severity(text: str, case_type: CaseType) -> Severity:
    """Derive severity from case type and keyword presence."""
    if case_type == CaseType.phishing_or_social_engineering:
        return Severity.critical
    for kw in CRITICAL_KW:
        if kw in text:
            return Severity.critical
    if case_type in (CaseType.wrong_transfer, CaseType.payment_failed):
        return Severity.high
    for kw in HIGH_KW:
        if kw in text:
            return Severity.high
    for kw in MEDIUM_KW:
        if kw in text:
            return Severity.medium
    if case_type == CaseType.refund_request:
        return Severity.low
    return Severity.low


def classify(message: str) -> ClassificationResult:
    """
    Classify a customer message end-to-end.
    All string operations are O(n) in message length.
    """
    normalised = preprocess(message)

    # Layer 1 — regex rules
    rule_scores = apply_rules(normalised)

    # Layer 2 — keyword matching (per candidate case type)
    # Layer 3 — semantic phrases
    semantic_scores = apply_semantic(normalised)

    # Combine: for each candidate CaseType, compute weighted confidence
    candidate_types: set[CaseType] = (
        set(rule_scores.keys()) | set(semantic_scores.keys())
    )

    # Always score refund / payment_failed / wrong_transfer as candidates
    # so Layer 2 alone can still surface them.
    candidate_types.update(
        [
            CaseType.wrong_transfer,
            CaseType.payment_failed,
            CaseType.refund_request,
            CaseType.phishing_or_social_engineering,
        ]
    )

    best_case: CaseType = CaseType.other
    best_confidence: float = 0.0

    for ct in candidate_types:
        rs = rule_scores.get(ct, 0.0)
        ks = _keyword_score(normalised, ct)
        ss = semantic_scores.get(ct, 0.0)
        conf = rs * 0.5 + ks * 0.3 + ss * 0.2
        conf = min(1.0, max(0.0, conf))
        if conf > best_confidence:
            best_confidence = conf
            best_case = ct

    # Layer 4 fallback
    if best_confidence < 0.1:
        best_case = CaseType.other
        best_confidence = 0.0

    severity = _determine_severity(normalised, best_case)
    department: Department = CASE_TYPE_TO_DEPARTMENT[best_case]

    # Human review logic
    largest_amount = extract_largest_amount(message)
    human_review = (
        severity == Severity.critical
        or best_case == CaseType.phishing_or_social_engineering
        or best_confidence < 0.65
        or (largest_amount is not None and largest_amount >= LARGE_AMOUNT_THRESHOLD)
    )

    return ClassificationResult(
        case_type=best_case,
        severity=severity,
        department=department,
        confidence=round(best_confidence, 4),
        human_review_required=human_review,
    )
