"""API route definitions."""

from __future__ import annotations

import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.ticket import (
    HealthResponse,
    TicketRequest,
    TicketResponse,
)
from app.services.classifier import classify
from app.services.extractor import extract_entities
from app.services.summarizer import generate_summary
from app.utils.logger import get_logger, log_classification

logger = get_logger()
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/sort-ticket", response_model=TicketResponse, tags=["tickets"])
async def sort_ticket(request: Request, body: TicketRequest) -> TicketResponse:
    start = time.perf_counter()

    result = classify(body.message)
    entities = extract_entities(body.message)
    summary = generate_summary(result.case_type, entities)

    latency_ms = (time.perf_counter() - start) * 1000
    log_classification(
        logger,
        ticket_id=body.ticket_id,
        case_type=result.case_type.value,
        severity=result.severity.value,
        confidence=result.confidence,
        latency_ms=latency_ms,
    )

    return TicketResponse(
        ticket_id=body.ticket_id,
        case_type=result.case_type,
        severity=result.severity,
        department=result.department,
        agent_summary=summary,
        human_review_required=result.human_review_required,
        confidence=result.confidence,
    )
