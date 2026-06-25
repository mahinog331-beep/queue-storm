"""Text normalisation helpers — O(n) in message length."""

from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")
_BANGLA_CURRENCY_RE = re.compile(r"৳\s*(\d[\d,]*)")
_TAKA_RE = re.compile(r"(\d[\d,]*)\s*(?:taka|টাকা|bdt)", re.IGNORECASE)


def normalize(text: str) -> str:
    """
    Lower-case, unicode-normalise (NFC), collapse whitespace.
    Keeps Bangla script characters intact.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def normalize_amounts(text: str) -> str:
    """
    Rewrite Bangla currency symbols and 'taka' variants to a canonical form
    so keyword rules can match consistently.
    """
    text = _BANGLA_CURRENCY_RE.sub(r"\1 taka", text)
    return text


def preprocess(text: str) -> str:
    """Full pipeline: normalise then canonicalise currency."""
    return normalize_amounts(normalize(text))
