"""Unit tests for entity extraction."""

from __future__ import annotations

import pytest

from app.services.extractor import extract_entities, extract_largest_amount


class TestAmountExtraction:
    def test_taka_english(self):
        e = extract_entities("I sent 5000 taka to a wrong number")
        assert any("5000" in a for a in e.amounts)

    def test_bangladeshi_currency_symbol(self):
        e = extract_entities("Balance: ৳5000")
        assert any("5000" in a for a in e.amounts)

    def test_bangla_taka(self):
        e = extract_entities("আমি ৳3000 পাঠিয়েছি")
        assert len(e.amounts) >= 1

    def test_no_amount(self):
        e = extract_entities("my payment failed")
        assert e.amounts == []


class TestPhoneExtraction:
    def test_bd_mobile(self):
        e = extract_entities("sent to 01712345678")
        assert len(e.phone_numbers) >= 1

    def test_bd_mobile_with_country_code(self):
        e = extract_entities("number: +8801812345678")
        assert len(e.phone_numbers) >= 1

    def test_no_phone(self):
        e = extract_entities("payment failed")
        assert e.phone_numbers == []


class TestTransactionIdExtraction:
    def test_txn_id(self):
        e = extract_entities("transaction ID: TXN12345ABC")
        assert len(e.transaction_ids) >= 1

    def test_bkash_ref(self):
        e = extract_entities("bKash reference BKASH9876XYZ")
        assert len(e.transaction_ids) >= 1


class TestLargestAmount:
    def test_single_amount(self):
        assert extract_largest_amount("5000 taka") == 5000

    def test_multiple_amounts(self):
        assert extract_largest_amount("3000 taka or 15000 taka") == 15000

    def test_no_amount(self):
        assert extract_largest_amount("my payment failed") is None

    def test_bangla_symbol(self):
        assert extract_largest_amount("৳12000") == 12000
