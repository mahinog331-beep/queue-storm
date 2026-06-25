"""Structured JSON logging setup."""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log.update(record.extra)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)


def get_logger(name: str = "queue-storm") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_classification(
    logger: logging.Logger,
    ticket_id: str,
    case_type: str,
    severity: str,
    confidence: float,
    latency_ms: float,
) -> None:
    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="ticket classified",
        args=(),
        exc_info=None,
    )
    record.extra = {
        "ticket_id": ticket_id,
        "classification": case_type,
        "severity": severity,
        "confidence": round(confidence, 4),
        "latency_ms": round(latency_ms, 2),
    }
    logger.handle(record)
