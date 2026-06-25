"""
Layer 2: Hash-set keyword lookup — O(1) per token, O(n) overall.
All sets use lower-cased, NFC-normalised strings to match the normalizer output.
"""

from __future__ import annotations

from app.models.ticket import CaseType

# ---------------------------------------------------------------------------
# Wrong transfer keywords (English + Bangla)
# ---------------------------------------------------------------------------
WRONG_TRANSFER_KW: frozenset[str] = frozenset(
    {
        # English
        "wrong transfer",
        "wrong number",
        "wrong account",
        "wrong recipient",
        "wrong person",
        "wrong bkash",
        "wrong nagad",
        "sent to wrong",
        "sent wrong",
        "transferred to wrong",
        "mistaken transfer",
        "accidental transfer",
        "wrong mobile",
        "wrong destination",
        # Bangla
        "ভুল নম্বরে",
        "ভুল নাম্বারে",
        "ভুল একাউন্টে",
        "ভুল নম্বর",
        "ভুল নাম্বার",
        "ভুল লোককে",
        "ভুলে পাঠিয়েছি",
        "ভুল ট্রান্সফার",
        "অন্য নম্বরে",
        "অন্য একাউন্টে",
        "ভুল বিকাশে",
        "ভুল নগদে",
        "পাঠিয়ে ফেলেছি",
    }
)

# ---------------------------------------------------------------------------
# Payment failed keywords
# ---------------------------------------------------------------------------
PAYMENT_FAILED_KW: frozenset[str] = frozenset(
    {
        # English
        "payment failed",
        "payment unsuccessful",
        "transaction failed",
        "transaction unsuccessful",
        "payment not completed",
        "failed payment",
        "deducted but not received",
        "balance deducted",
        "money deducted",
        "amount deducted",
        "charged but failed",
        "not credited",
        "not received",
        "not processed",
        "double charge",
        "double deduction",
        "duplicate charge",
        # Bangla
        "পেমেন্ট ফেল",
        "পেমেন্ট ব্যর্থ",
        "টাকা কেটেছে",
        "টাকা কেটে নিয়েছে",
        "ব্যালেন্স কাটা",
        "পেমেন্ট সম্পন্ন হয়নি",
        "ট্রানজেকশন ফেল",
        "পাননি",
        "ক্রেডিট হয়নি",
        "ডাবল কাটা",
    }
)

# ---------------------------------------------------------------------------
# Refund request keywords
# ---------------------------------------------------------------------------
REFUND_REQUEST_KW: frozenset[str] = frozenset(
    {
        # English
        "refund",
        "money back",
        "return money",
        "get my money back",
        "want my money back",
        "reverse the transaction",
        "reverse transaction",
        "cashback",
        "reimbursement",
        "compensation",
        "reverse payment",
        "undo payment",
        # Bangla
        "টাকা ফেরত",
        "টাকা ফিরিয়ে",
        "রিফান্ড",
        "ফেরত চাই",
        "টাকা ফেরত চাই",
        "রিভার্স",
        "ক্যাশব্যাক",
        "ক্ষতিপূরণ",
    }
)

# ---------------------------------------------------------------------------
# Phishing / social engineering keywords
# ---------------------------------------------------------------------------
PHISHING_KW: frozenset[str] = frozenset(
    {
        # English
        "otp",
        "one time password",
        "pin",
        "password",
        "cvv",
        "card number",
        "card details",
        "account credentials",
        "asking for otp",
        "asked for otp",
        "someone asked",
        "someone called",
        "called asking",
        "suspicious call",
        "suspicious link",
        "suspicious message",
        "phishing",
        "scam",
        "fraud",
        "fake agent",
        "fake customer care",
        "impersonating",
        "hacked",
        "account compromised",
        "unauthorized access",
        "unknown login",
        "unrecognized transaction",
        "i did not do",
        "i did not make",
        "not authorized",
        "not me",
        # Bangla
        "ওটিপি",
        "পিন",
        "পাসওয়ার্ড",
        "কেউ ওটিপি চাইছে",
        "কেউ ফোন করেছে",
        "সন্দেহজনক",
        "প্রতারণা",
        "জালিয়াতি",
        "স্ক্যাম",
        "হ্যাক",
        "আনঅথরাইজড",
        "আমি করিনি",
    }
)

# ---------------------------------------------------------------------------
# Severity keyword sets (used to override severity score)
# ---------------------------------------------------------------------------
CRITICAL_KW: frozenset[str] = frozenset(
    {
        "otp",
        "pin",
        "password",
        "cvv",
        "card number",
        "phishing",
        "scam",
        "fraud",
        "hacked",
        "account compromised",
        "unauthorized",
        "ওটিপি",
        "পিন",
        "পাসওয়ার্ড",
        "প্রতারণা",
        "জালিয়াতি",
        "হ্যাক",
    }
)

HIGH_KW: frozenset[str] = frozenset(
    {
        "wrong transfer",
        "payment failed",
        "balance deducted",
        "financial loss",
        "money lost",
        "money deducted",
        "ভুল ট্রান্সফার",
        "টাকা কেটেছে",
        "আর্থিক ক্ষতি",
    }
)

MEDIUM_KW: frozenset[str] = frozenset(
    {
        "repeated",
        "again",
        "merchant",
        "dispute",
        "multiple times",
        "বারবার",
        "আবার",
        "মার্চেন্ট",
    }
)

# Master lookup: case_type → keyword set
KEYWORD_SETS: dict[CaseType, frozenset[str]] = {
    CaseType.phishing_or_social_engineering: PHISHING_KW,
    CaseType.wrong_transfer: WRONG_TRANSFER_KW,
    CaseType.payment_failed: PAYMENT_FAILED_KW,
    CaseType.refund_request: REFUND_REQUEST_KW,
}
