"""Единая обработка исключений и ошибок API."""

from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

PROBLEM_BASE_URI = "https://problems.secdev.local/"


class ApiError(Exception):
    def __init__(
        self, code: str, detail: str, status: int = 400, title: str | None = None
    ):
        self.code = code
        self.detail = detail
        self.status = status
        self.title = title or code.replace("_", " ").title()


def _scrub_sensitive_data(payload: Any) -> Any:
    """Remove raw user input from validation errors before returning to clients."""
    if isinstance(payload, dict):
        return {
            key: _scrub_sensitive_data(value)
            for key, value in payload.items()
            if key != "input"
        }
    if isinstance(payload, list):
        return [_scrub_sensitive_data(item) for item in payload]
    return payload


def problem(
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    extras: Dict[str, Any] | None = None,
) -> JSONResponse:
    """Emit RFC 7807 response with correlation id header/body."""
    correlation_id = str(uuid4())
    payload: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": correlation_id,
    }
    if extras:
        payload.update(extras)

    response = JSONResponse(
        payload,
        status_code=status,
        media_type="application/problem+json",
    )
    response.headers.setdefault("X-Correlation-ID", correlation_id)
    return response


async def api_error_handler(request: Request, exc: ApiError):
    response = problem(
        status=exc.status,
        title=exc.title,
        detail=exc.detail,
        type_=f"{PROBLEM_BASE_URI}{exc.code}",
    )
    request.state.correlation_id = response.headers["X-Correlation-ID"]
    return response


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    code = "http_error"
    title = exc.headers.get("X-Error-Title") if exc.headers else None
    response = problem(
        status=exc.status_code,
        title=title or code.replace("_", " ").title(),
        detail=detail,
        type_=f"{PROBLEM_BASE_URI}{code}",
    )
    request.state.correlation_id = response.headers["X-Correlation-ID"]
    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = errors[0]["msg"] if errors else "Invalid payload"
    encoded_errors = _scrub_sensitive_data(jsonable_encoder(errors)) if errors else None
    response = problem(
        status=422,
        title="Validation Error",
        detail=message,
        type_=f"{PROBLEM_BASE_URI}validation_error",
        extras={"errors": encoded_errors} if encoded_errors else None,
    )
    request.state.correlation_id = response.headers["X-Correlation-ID"]
    return response
