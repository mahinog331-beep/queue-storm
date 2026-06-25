"""Integration tests for the FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body(self):
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "queue-storm"
        assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# POST /sort-ticket — happy path
# ---------------------------------------------------------------------------

class TestSortTicketHappyPath:
    def _post(self, payload: dict) -> dict:
        resp = client.post("/sort-ticket", json=payload)
        assert resp.status_code == 200, resp.text
        return resp.json()

    def test_challenge_sample_wrong_transfer(self):
        data = self._post(
            {
                "ticket_id": "T-001",
                "channel": "app",
                "locale": "en",
                "message": "I sent 5000 taka to a wrong number this morning, please help me get it back",
            }
        )
        assert data["ticket_id"] == "T-001"
        assert data["case_type"] == "wrong_transfer"
        assert data["severity"] == "high"
        assert data["department"] == "dispute_resolution"
        assert "agent_summary" in data
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["human_review_required"], bool)

    def test_payment_failed_english(self):
        data = self._post(
            {
                "ticket_id": "T-002",
                "channel": "web",
                "locale": "en",
                "message": "My payment failed but the amount was deducted from my account",
            }
        )
        assert data["case_type"] == "payment_failed"
        assert data["department"] == "payments_ops"

    def test_refund_request_english(self):
        data = self._post(
            {
                "ticket_id": "T-003",
                "channel": "chat",
                "locale": "en",
                "message": "I want my money back please process a refund",
            }
        )
        assert data["case_type"] == "refund_request"
        assert data["department"] == "customer_support"

    def test_phishing_otp(self):
        data = self._post(
            {
                "ticket_id": "T-004",
                "channel": "app",
                "locale": "en",
                "message": "Someone called me asking for my OTP",
            }
        )
        assert data["case_type"] == "phishing_or_social_engineering"
        assert data["department"] == "fraud_risk"
        assert data["severity"] == "critical"
        assert data["human_review_required"] is True

    def test_bangla_wrong_transfer(self):
        data = self._post(
            {
                "ticket_id": "T-005",
                "channel": "app",
                "locale": "bn",
                "message": "ভুল নাম্বারে টাকা পাঠিয়েছি",
            }
        )
        assert data["case_type"] == "wrong_transfer"

    def test_bangla_payment_failed(self):
        data = self._post(
            {
                "ticket_id": "T-006",
                "channel": "app",
                "locale": "bn",
                "message": "পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে নিয়েছে",
            }
        )
        assert data["case_type"] == "payment_failed"

    def test_bangla_refund(self):
        data = self._post(
            {
                "ticket_id": "T-007",
                "channel": "app",
                "locale": "bn",
                "message": "আমার টাকা ফেরত চাই",
            }
        )
        assert data["case_type"] == "refund_request"

    def test_bangla_phishing(self):
        data = self._post(
            {
                "ticket_id": "T-008",
                "channel": "app",
                "locale": "bn",
                "message": "কেউ OTP চাইছে",
            }
        )
        assert data["case_type"] == "phishing_or_social_engineering"

    def test_summary_never_contains_otp(self):
        data = self._post(
            {
                "ticket_id": "T-009",
                "channel": "app",
                "locale": "en",
                "message": "Someone is asking for my OTP and PIN",
            }
        )
        summary_lower = data["agent_summary"].lower()
        for term in ["otp", "pin", "password", "cvv"]:
            assert term not in summary_lower, f"Summary contains '{term}': {data['agent_summary']}"

    def test_response_fields_present(self):
        data = self._post(
            {
                "ticket_id": "T-010",
                "channel": "sms",
                "locale": "mixed",
                "message": "My payment failed and I want a refund",
            }
        )
        required = [
            "ticket_id", "case_type", "severity", "department",
            "agent_summary", "human_review_required", "confidence",
        ]
        for field in required:
            assert field in data, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# POST /sort-ticket — validation errors
# ---------------------------------------------------------------------------

class TestSortTicketValidation:
    def test_missing_ticket_id(self):
        resp = client.post(
            "/sort-ticket",
            json={"channel": "app", "locale": "en", "message": "hello"},
        )
        assert resp.status_code == 422

    def test_missing_message(self):
        resp = client.post(
            "/sort-ticket",
            json={"ticket_id": "T-001", "channel": "app", "locale": "en"},
        )
        assert resp.status_code == 422

    def test_invalid_channel(self):
        resp = client.post(
            "/sort-ticket",
            json={
                "ticket_id": "T-001",
                "channel": "fax",
                "locale": "en",
                "message": "hello",
            },
        )
        assert resp.status_code == 422

    def test_invalid_locale(self):
        resp = client.post(
            "/sort-ticket",
            json={
                "ticket_id": "T-001",
                "channel": "app",
                "locale": "fr",
                "message": "hello",
            },
        )
        assert resp.status_code == 422

    def test_empty_message(self):
        resp = client.post(
            "/sort-ticket",
            json={
                "ticket_id": "T-001",
                "channel": "app",
                "locale": "en",
                "message": "   ",
            },
        )
        assert resp.status_code == 422

    def test_empty_ticket_id(self):
        resp = client.post(
            "/sort-ticket",
            json={
                "ticket_id": "   ",
                "channel": "app",
                "locale": "en",
                "message": "hello",
            },
        )
        assert resp.status_code == 422

    def test_missing_body(self):
        resp = client.post("/sort-ticket")
        assert resp.status_code == 422
