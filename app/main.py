"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.utils.logger import get_logger

logger = get_logger()

_PREFIX = "/queue-storm"


class StripPrefixMiddleware(BaseHTTPMiddleware):
    """
    Strip the /queue-storm reverse-proxy prefix before routing.
    Also sets root_path so FastAPI generates correct OpenAPI / docs URLs.
    """

    async def dispatch(self, request: Request, call_next):
        path: str = request.scope.get("path", "")
        if path.startswith(_PREFIX):
            # Strip the prefix from the routed path
            request.scope["path"] = path[len(_PREFIX):] or "/"
            # Tell FastAPI its mount point — used for openapi.json URL in Swagger
            request.scope["root_path"] = _PREFIX
        return await call_next(request)


# Do NOT set root_path here — the middleware injects it per-request from the
# proxy scope so it is set exactly once and never doubled.
app = FastAPI(
    title="QueueStorm — Ticket Triage API",
    description=(
        "Production-ready ticket triage API that classifies customer complaints "
        "for a digital finance company."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(StripPrefixMiddleware)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    detail = [
        {
            "field": ".".join(str(loc) for loc in e["loc"] if loc != "body"),
            "message": e["msg"],
            "type": e["type"],
        }
        for e in errors
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
