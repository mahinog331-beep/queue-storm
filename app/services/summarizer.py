"""
Summary generation engine.
Produces concise, professional agent summaries from classification results
and extracted entities. Never includes sensitive credential terms.
"""

from __future__ import annotations

from app.models.ticket import CaseType, ExtractedEntities

# Words that must never appear in a generated summary
_REDACTED_TERMS: frozenset[str] = frozenset(
    {"otp", "pin", "password", "cvv", "card number", "card details"}
)

_AMOUNT_PLACEHOLDER = "an amount"


def _format_amount(amounts: list[str]) -> str:
    if not amounts:
        return _AMOUNT_PLACEHOLDER
    # Use first detected amount; normalise "taka" → "BDT"
    raw = amounts[0]
    # Attempt to produce a clean "X BDT" string
    import re
    num_match = re.search(r"[\d,]+", raw)
    if num_match:
        number = num_match.group(0).replace(",", "")
        return f"{number} BDT"
    return raw


def _safe(text: str) -> str:
    """Ensure no sensitive terms leak into the summary."""
    lower = text.lower()
    for term in _REDACTED_TERMS:
        if term in lower:
            # Replace the term with a safe placeholder
            import re
            text = re.sub(re.escape(term), "[credential]", text, flags=re.IGNORECASE)
    return text


_SUMMARIES: dict[CaseType, str] = {
    CaseType.wrong_transfer: (
        "Customer reports transferring {amount} to an unintended recipient"
        " and seeks recovery assistance."
    ),
    CaseType.payment_failed: (
        "Customer reports that {amount} was deducted from their account"
        " but the transaction was not completed; requests resolution."
    ),
    CaseType.refund_request: (
        "Customer requests a refund of {amount} for a previous transaction."
    ),
    CaseType.phishing_or_social_engineering: (
        "Customer reports a suspicious request for account credentials"
        " and seeks verification of the incident."
    ),
    CaseType.other: (
        "Customer has submitted a general inquiry or complaint requiring agent review."
    ),
}


def generate_summary(
    case_type: CaseType,
    entities: ExtractedEntities,
) -> str:
    """
    Build a professional, one-sentence agent summary.
    Sensitive credential terms are never emitted.
    """
    template = _SUMMARIES[case_type]
    amount_str = _format_amount(entities.amounts)

    summary = template.format(amount=amount_str)
    return _safe(summary)
