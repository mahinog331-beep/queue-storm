from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Channel(str, Enum):
    app = "app"
    web = "web"
    sms = "sms"
    call = "call"
    chat = "chat"
    email = "email"


class Locale(str, Enum):
    en = "en"
    bn = "bn"
    mixed = "mixed"


class CaseType(str, Enum):
    wrong_transfer = "wrong_transfer"
    payment_failed = "payment_failed"
    refund_request = "refund_request"
    phishing_or_social_engineering = "phishing_or_social_engineering"
    other = "other"


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Department(str, Enum):
    dispute_resolution = "dispute_resolution"
    payments_ops = "payments_ops"
    customer_support = "customer_support"
    fraud_risk = "fraud_risk"


CASE_TYPE_TO_DEPARTMENT: dict[CaseType, Department] = {
    CaseType.wrong_transfer: Department.dispute_resolution,
    CaseType.payment_failed: Department.payments_ops,
    CaseType.refund_request: Department.customer_support,
    CaseType.phishing_or_social_engineering: Department.fraud_risk,
    CaseType.other: Department.customer_support,
}


class TicketRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1, max_length=64, description="Unique ticket identifier")
    channel: Channel = Field(..., description="Submission channel")
    locale: Locale = Field(..., description="Language locale")
    message: str = Field(..., min_length=1, max_length=4096, description="Customer complaint text")

    @field_validator("ticket_id")
    @classmethod
    def ticket_id_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ticket_id must not be blank")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be blank")
        return v.strip()


class ExtractedEntities(BaseModel):
    amounts: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    transaction_ids: list[str] = Field(default_factory=list)


class TicketResponse(BaseModel):
    ticket_id: str
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    human_review_required: bool
    confidence: float = Field(..., ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    status: Literal["healthy"] = "healthy"
    service: Literal["queue-storm"] = "queue-storm"
    version: Literal["1.0.0"] = "1.0.0"
