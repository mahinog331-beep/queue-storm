"""
Layer 1: High-confidence regex rules — compiled once at import time.
Each rule yields a (CaseType, score) pair; highest score wins.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.ticket import CaseType


@dataclass(frozen=True)
class RegexRule:
    pattern: re.Pattern[str]
    case_type: CaseType
    score: float


_RULES: list[RegexRule] = [
    # ------------------------------------------------------------------
    # Phishing / social engineering — highest priority
    # ------------------------------------------------------------------
    RegexRule(
        pattern=re.compile(
            r"\b(?:otp|one[\s-]time[\s-]password|pin|password|cvv|card[\s-]number|card[\s-]detail)\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.phishing_or_social_engineering,
        score=1.0,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:ওটিপি|পিন|পাসওয়ার্ড|কার্ড নম্বর)",
        ),
        case_type=CaseType.phishing_or_social_engineering,
        score=1.0,
    ),
    RegexRule(
        pattern=re.compile(
            r"\b(?:phishing|scam|fraud|hack(?:ed)?|account\s+(?:compromise|hacked|breach))\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.phishing_or_social_engineering,
        score=1.0,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:প্রতারণা|জালিয়াতি|স্ক্যাম|হ্যাক)",
        ),
        case_type=CaseType.phishing_or_social_engineering,
        score=1.0,
    ),
    # ------------------------------------------------------------------
    # Wrong transfer — money sent to wrong recipient
    # ------------------------------------------------------------------
    RegexRule(
        pattern=re.compile(
            r"\b(?:sent?|transfer(?:red)?|send)\b.{0,30}\b(?:wrong|mistaken|accidental|incorrect)\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.wrong_transfer,
        score=0.95,
    ),
    RegexRule(
        pattern=re.compile(
            r"\b(?:wrong|mistaken|incorrect)\b.{0,30}\b(?:number|account|recipient|person|bkash|nagad|mobile)\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.wrong_transfer,
        score=0.95,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:ভুল নম্বরে|ভুল নাম্বারে|ভুল একাউন্টে).{0,30}(?:টাকা|পাঠিয়েছি|পাঠিয়ে)",
        ),
        case_type=CaseType.wrong_transfer,
        score=0.95,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:টাকা).{0,20}(?:ভুল নম্বরে|ভুল নাম্বারে|ভুল একাউন্টে)",
        ),
        case_type=CaseType.wrong_transfer,
        score=0.95,
    ),
    # ------------------------------------------------------------------
    # Payment failed — deducted but transaction incomplete
    # ------------------------------------------------------------------
    RegexRule(
        pattern=re.compile(
            r"\b(?:payment|transaction)\s+(?:fail(?:ed)?|unsuccessful|not\s+(?:complete|process))\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.payment_failed,
        score=0.95,
    ),
    RegexRule(
        pattern=re.compile(
            r"\b(?:money|balance|amount|taka)\b.{0,15}(?:deduct|cut|charg|taken)\w*\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.payment_failed,
        score=0.90,
    ),
    RegexRule(
        pattern=re.compile(
            r"\bbalance\s+was\s+(?:deduct|cut)\w*\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.payment_failed,
        score=0.92,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:পেমেন্ট ফেল|পেমেন্ট ব্যর্থ|টাকা কেটে|ট্রানজেকশন ফেল)",
        ),
        case_type=CaseType.payment_failed,
        score=0.95,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:কেটে নিয়েছে).{0,30}(?:পাননি|হয়নি)",
        ),
        case_type=CaseType.payment_failed,
        score=0.92,
    ),
    # ------------------------------------------------------------------
    # Refund request
    # ------------------------------------------------------------------
    RegexRule(
        pattern=re.compile(
            r"\b(?:refund|money\s+back|return\s+(?:my\s+)?money|reimburse|reverse\s+(?:the\s+)?(?:transaction|payment))\b",
            re.IGNORECASE,
        ),
        case_type=CaseType.refund_request,
        score=0.90,
    ),
    RegexRule(
        pattern=re.compile(
            r"(?:টাকা ফেরত|রিফান্ড|ফেরত চাই|টাকা ফিরিয়ে)",
        ),
        case_type=CaseType.refund_request,
        score=0.90,
    ),
]


def apply_rules(text: str) -> dict[CaseType, float]:
    """
    Return a mapping of CaseType → max rule score found.
    O(n * R) where R = number of rules (constant), so effectively O(n).
    """
    scores: dict[CaseType, float] = {}
    for rule in _RULES:
        if rule.pattern.search(text):
            existing = scores.get(rule.case_type, 0.0)
            if rule.score > existing:
                scores[rule.case_type] = rule.score
    return scores
