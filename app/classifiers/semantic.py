"""
Layer 3: Semantic phrase matching.
Multi-word expressions that span token boundaries and carry strong signal.
Uses substring matching (O(n) per phrase via Python's optimised str.find).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.ticket import CaseType


@dataclass(frozen=True)
class SemanticPhrase:
    phrase: str
    case_type: CaseType
    score: float


_PHRASES: list[SemanticPhrase] = [
    # -- Phishing / social engineering --
    SemanticPhrase("someone asked for my", CaseType.phishing_or_social_engineering, 0.90),
    SemanticPhrase("someone is asking", CaseType.phishing_or_social_engineering, 0.90),
    SemanticPhrase("called and asked", CaseType.phishing_or_social_engineering, 0.90),
    SemanticPhrase("called asking for", CaseType.phishing_or_social_engineering, 0.90),
    SemanticPhrase("pretending to be", CaseType.phishing_or_social_engineering, 0.90),
    SemanticPhrase("fake customer care", CaseType.phishing_or_social_engineering, 0.92),
    SemanticPhrase("claiming to be", CaseType.phishing_or_social_engineering, 0.85),
    SemanticPhrase("i did not make this", CaseType.phishing_or_social_engineering, 0.80),
    SemanticPhrase("i did not do this", CaseType.phishing_or_social_engineering, 0.80),
    SemanticPhrase("without my knowledge", CaseType.phishing_or_social_engineering, 0.80),
    SemanticPhrase("not authorised", CaseType.phishing_or_social_engineering, 0.80),
    SemanticPhrase("not authorized", CaseType.phishing_or_social_engineering, 0.80),
    SemanticPhrase("কেউ ওটিপি চাইছে", CaseType.phishing_or_social_engineering, 0.95),
    SemanticPhrase("কেউ ফোন করে", CaseType.phishing_or_social_engineering, 0.85),
    SemanticPhrase("আমি করিনি", CaseType.phishing_or_social_engineering, 0.80),
    # -- Wrong transfer --
    SemanticPhrase("sent to the wrong", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("transferred to wrong", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("sent money to wrong", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("sent taka to wrong", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("help me get it back", CaseType.wrong_transfer, 0.75),
    SemanticPhrase("recover the money", CaseType.wrong_transfer, 0.75),
    SemanticPhrase("to a wrong number", CaseType.wrong_transfer, 0.88),
    SemanticPhrase("wrong number this", CaseType.wrong_transfer, 0.88),
    SemanticPhrase("balance was deducted", CaseType.payment_failed, 0.90),
    SemanticPhrase("was deducted but", CaseType.payment_failed, 0.90),
    SemanticPhrase("merchant did not receive", CaseType.payment_failed, 0.85),
    SemanticPhrase("ভুল নম্বরে টাকা", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("ভুল নাম্বারে টাকা", CaseType.wrong_transfer, 0.95),
    SemanticPhrase("ভুলে পাঠিয়েছি", CaseType.wrong_transfer, 0.90),
    SemanticPhrase("অন্য নম্বরে পাঠিয়েছি", CaseType.wrong_transfer, 0.90),
    # -- Payment failed --
    SemanticPhrase("money was deducted but", CaseType.payment_failed, 0.92),
    SemanticPhrase("amount was deducted but", CaseType.payment_failed, 0.92),
    SemanticPhrase("balance was cut but", CaseType.payment_failed, 0.90),
    SemanticPhrase("charged twice", CaseType.payment_failed, 0.88),
    SemanticPhrase("double charged", CaseType.payment_failed, 0.88),
    SemanticPhrase("পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে", CaseType.payment_failed, 0.95),
    SemanticPhrase("টাকা কেটেছে কিন্তু", CaseType.payment_failed, 0.90),
    # -- Refund request --
    SemanticPhrase("want my money back", CaseType.refund_request, 0.90),
    SemanticPhrase("i want a refund", CaseType.refund_request, 0.90),
    SemanticPhrase("please refund", CaseType.refund_request, 0.88),
    SemanticPhrase("আমার টাকা ফেরত চাই", CaseType.refund_request, 0.95),
    SemanticPhrase("টাকা ফেরত দিন", CaseType.refund_request, 0.92),
]


def apply_semantic(text: str) -> dict[CaseType, float]:
    """
    Substring scan over all phrases — O(n * P) where P = phrase count (constant).
    Returns highest score per CaseType found.
    """
    scores: dict[CaseType, float] = {}
    for phrase in _PHRASES:
        if phrase.phrase in text:
            existing = scores.get(phrase.case_type, 0.0)
            if phrase.score > existing:
                scores[phrase.case_type] = phrase.score
    return scores
