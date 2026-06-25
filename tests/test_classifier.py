"""Unit tests for the classification engine."""

from __future__ import annotations

import pytest

from app.models.ticket import CaseType, Severity
from app.services.classifier import classify


# ---------------------------------------------------------------------------
# Challenge sample cases (English)
# ---------------------------------------------------------------------------

class TestWrongTransferEnglish:
    def test_basic_wrong_number(self):
        r = classify("I sent 5000 taka to a wrong number this morning, please help me get it back")
        assert r.case_type == CaseType.wrong_transfer

    def test_wrong_account(self):
        r = classify("I accidentally transferred money to the wrong account")
        assert r.case_type == CaseType.wrong_transfer

    def test_wrong_number_short(self):
        r = classify("sent to wrong number")
        assert r.case_type == CaseType.wrong_transfer

    def test_severity_is_high(self):
        r = classify("I sent 1000 taka to a wrong number")
        assert r.severity == Severity.high


class TestPaymentFailedEnglish:
    def test_basic_payment_failed(self):
        r = classify("My payment failed but money was deducted from my account")
        assert r.case_type == CaseType.payment_failed

    def test_transaction_failed(self):
        r = classify("Transaction failed but balance was cut")
        assert r.case_type == CaseType.payment_failed

    def test_balance_deducted(self):
        r = classify("My balance was deducted but the merchant did not receive it")
        assert r.case_type == CaseType.payment_failed

    def test_severity_is_high(self):
        r = classify("payment failed and balance deducted")
        assert r.severity == Severity.high


class TestRefundEnglish:
    def test_basic_refund(self):
        r = classify("I want my money back, please process a refund")
        assert r.case_type == CaseType.refund_request

    def test_money_back(self):
        r = classify("please give me my money back")
        assert r.case_type == CaseType.refund_request

    def test_reverse_transaction(self):
        r = classify("please reverse the transaction and refund me")
        assert r.case_type == CaseType.refund_request

    def test_severity_is_low(self):
        r = classify("I want a refund for my order")
        assert r.severity == Severity.low


class TestPhishingEnglish:
    def test_otp_request(self):
        r = classify("Someone called me asking for my OTP")
        assert r.case_type == CaseType.phishing_or_social_engineering

    def test_pin_request(self):
        r = classify("A person called and asked for my PIN number")
        assert r.case_type == CaseType.phishing_or_social_engineering

    def test_scam(self):
        r = classify("I think I was scammed by someone pretending to be customer support")
        assert r.case_type == CaseType.phishing_or_social_engineering

    def test_severity_is_critical(self):
        r = classify("Someone is asking for my OTP")
        assert r.severity == Severity.critical

    def test_human_review_required(self):
        r = classify("Someone called asking for my OTP")
        assert r.human_review_required is True


# ---------------------------------------------------------------------------
# Challenge sample cases (Bangla)
# ---------------------------------------------------------------------------

class TestWrongTransferBangla:
    def test_bangla_wrong_number(self):
        r = classify("ভুল নাম্বারে টাকা পাঠিয়েছি")
        assert r.case_type == CaseType.wrong_transfer

    def test_bangla_wrong_number_alt(self):
        r = classify("ভুল নম্বরে টাকা পাঠিয়েছি")
        assert r.case_type == CaseType.wrong_transfer


class TestPaymentFailedBangla:
    def test_bangla_payment_failed(self):
        r = classify("পেমেন্ট ফেল করেছে কিন্তু টাকা কেটে নিয়েছে")
        assert r.case_type == CaseType.payment_failed


class TestRefundBangla:
    def test_bangla_refund(self):
        r = classify("আমার টাকা ফেরত চাই")
        assert r.case_type == CaseType.refund_request


class TestPhishingBangla:
    def test_bangla_otp(self):
        r = classify("কেউ OTP চাইছে")
        assert r.case_type == CaseType.phishing_or_social_engineering

    def test_bangla_otp_full(self):
        r = classify("কেউ ওটিপি চাইছে")
        assert r.case_type == CaseType.phishing_or_social_engineering


# ---------------------------------------------------------------------------
# Human review rules
# ---------------------------------------------------------------------------

class TestHumanReview:
    def test_phishing_always_human_review(self):
        r = classify("Someone asked for my password")
        assert r.human_review_required is True

    def test_critical_severity_human_review(self):
        r = classify("Someone is asking for my OTP")
        assert r.human_review_required is True

    def test_large_amount_triggers_human_review(self):
        r = classify("I sent 15000 taka to a wrong number")
        assert r.human_review_required is True

    def test_small_amount_wrong_transfer_may_not(self):
        r = classify("I sent 500 taka to a wrong number")
        # May or may not require human review — just check it classifies correctly
        assert r.case_type == CaseType.wrong_transfer


# ---------------------------------------------------------------------------
# Department mapping
# ---------------------------------------------------------------------------

class TestDepartmentMapping:
    def test_wrong_transfer_department(self):
        from app.models.ticket import Department
        r = classify("I sent money to a wrong number")
        assert r.department == Department.dispute_resolution

    def test_payment_failed_department(self):
        from app.models.ticket import Department
        r = classify("My payment failed and balance deducted")
        assert r.department == Department.payments_ops

    def test_refund_department(self):
        from app.models.ticket import Department
        r = classify("I want a refund")
        assert r.department == Department.customer_support

    def test_phishing_department(self):
        from app.models.ticket import Department
        r = classify("Someone is asking for my OTP")
        assert r.department == Department.fraud_risk


# ---------------------------------------------------------------------------
# Confidence range
# ---------------------------------------------------------------------------

class TestConfidence:
    def test_confidence_in_range(self):
        messages = [
            "I sent 5000 taka to a wrong number",
            "payment failed but money deducted",
            "refund please",
            "someone asking for my otp",
            "hello",
        ]
        for msg in messages:
            r = classify(msg)
            assert 0.0 <= r.confidence <= 1.0, f"Out of range for: {msg!r}"

    def test_high_confidence_for_strong_signals(self):
        r = classify("I sent 5000 taka to a wrong number this morning")
        assert r.confidence >= 0.65
