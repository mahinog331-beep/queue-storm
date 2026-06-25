"""
Sample test payloads — documents the expected behaviour for each
challenge-specified example. Run with: pytest tests/test_payloads.py -v
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_PAYLOADS = [
    # id, message, expected_case_type, expected_severity, expected_dept
    (
        "T-S01",
        "I sent 5000 taka to a wrong number this morning, please help me get it back",
        "wrong_transfer",
        "high",
        "dispute_resolution",
    ),
    (
        "T-S02",
        "ভুল নাম্বারে টাকা পাঠিয়েছি",
        "wrong_transfer",
        "high",
        "dispute_resolution",
    ),
    (
        "T-S03",
        "পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে নিয়েছে",
        "payment_failed",
        "high",
        "payments_ops",
    ),
    (
        "T-S04",
        "আমার টাকা ফেরত চাই",
        "refund_request",
        "low",
        "customer_support",
    ),
    (
        "T-S05",
        "কেউ OTP চাইছে",
        "phishing_or_social_engineering",
        "critical",
        "fraud_risk",
    ),
    (
        "T-S06",
        "Someone called me asking for my OTP",
        "phishing_or_social_engineering",
        "critical",
        "fraud_risk",
    ),
    (
        "T-S07",
        "My payment failed but money was deducted",
        "payment_failed",
        "high",
        "payments_ops",
    ),
    (
        "T-S08",
        "I want my money back, please refund me",
        "refund_request",
        "low",
        "customer_support",
    ),
]


@pytest.mark.parametrize("ticket_id,message,exp_case,exp_sev,exp_dept", SAMPLE_PAYLOADS)
def test_sample_payload(
    ticket_id: str,
    message: str,
    exp_case: str,
    exp_sev: str,
    exp_dept: str,
) -> None:
    resp = client.post(
        "/sort-ticket",
        json={
            "ticket_id": ticket_id,
            "channel": "app",
            "locale": "en",
            "message": message,
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["case_type"] == exp_case, f"[{ticket_id}] got {data['case_type']!r}, expected {exp_case!r}"
    assert data["severity"] == exp_sev, f"[{ticket_id}] got {data['severity']!r}, expected {exp_sev!r}"
    assert data["department"] == exp_dept, f"[{ticket_id}] got {data['department']!r}, expected {exp_dept!r}"
