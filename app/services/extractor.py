"""
Entity extraction: money amounts, phone numbers, transaction IDs.
All regexes compiled once at import time — O(n) runtime.
"""

from __future__ import annotations

import re

from app.models.ticket import ExtractedEntities


_AMOUNT_RE = re.compile(
    r"(?:"
    r"৳\s*\d[\d,]*"               # ৳5000 or ৳ 5,000
    r"|"
    r"\d[\d,]*\s*(?:taka|টাকা|bdt|BDT|tk|Tk)"  # 5000 taka / 5000 টাকা
    r")",
    re.IGNORECASE,
)

_PHONE_RE = re.compile(
    r"\b(?:\+?880|0)1[3-9]\d{8}\b"  # BD mobile: 017XXXXXXXX, +8801XXXXXXXXX
)

_TXN_RE = re.compile(
    r"\b(?:TXN|BKASH|NGD|TRX|REF)[A-Z0-9]{4,16}\b",
    re.IGNORECASE,
)

_NUMERIC_AMOUNT_RE = re.compile(
    r"\b(\d[\d,]*)\s*(?:taka|টাকা|bdt)\b",
    re.IGNORECASE,
)


def extract_entities(text: str) -> ExtractedEntities:
    """Extract structured entities from the original (un-lowercased) text."""
    amounts = [m.group(0).strip() for m in _AMOUNT_RE.finditer(text)]
    phone_numbers = [m.group(0).strip() for m in _PHONE_RE.finditer(text)]
    transaction_ids = [m.group(0).strip() for m in _TXN_RE.finditer(text)]
    return ExtractedEntities(
        amounts=amounts,
        phone_numbers=phone_numbers,
        transaction_ids=transaction_ids,
    )


def extract_largest_amount(text: str) -> int | None:
    """Return the largest numeric amount found in the message, or None."""
    values: list[int] = []
    for m in _NUMERIC_AMOUNT_RE.finditer(text):
        try:
            values.append(int(m.group(1).replace(",", "")))
        except ValueError:
            pass
    # Also catch ৳ amounts
    for m in re.finditer(r"৳\s*(\d[\d,]*)", text):
        try:
            values.append(int(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return max(values) if values else None
