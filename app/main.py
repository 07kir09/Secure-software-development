import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import (
    ApiError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.db import get_session, init_db, reset_database
from app.models import Item as ItemModel
from app.schemas import ALLOWED_STATUSES, Item, ItemCreate, ItemUpdate

app = FastAPI(title="SecDev Course App", version="0.1.0")

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

API_TOKEN_HEADER_ALIAS = "X-API-Key"
API_TOKEN_ENV = "APP_API_TOKEN"

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


def _get_expected_api_token() -> str:
    token = os.getenv(API_TOKEN_ENV)
    if token is None:
        raise ApiError(
            code="auth_not_configured",
            detail="API token not configured",
            status=500,
        )
    return token


def require_api_token(
    x_api_key: str | None = Header(default=None, alias=API_TOKEN_HEADER_ALIAS),
) -> None:
    expected = _get_expected_api_token()
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise ApiError(
            code="not_authorized",
            detail="missing or invalid API token",
            status=401,
        )


@app.middleware("http")
async def enforce_security_headers(request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _reset_db() -> None:
    """Test helper: restore database to a clean state."""
    reset_database()


def _serialize_item(record: ItemModel) -> dict[str, object]:
    return {
        "id": record.id,
        "name": record.name,
        "description": record.description,
        "status": record.status,
    }


@app.get("/items", response_model=list[Item])
def list_items(
    status: str | None = None,
    session: Session = Depends(get_session),
):
    if status is not None and status not in ALLOWED_STATUSES:
        raise ApiError(
            code="validation_error",
            detail=f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}",
            status=422,
        )

    stmt = select(ItemModel).order_by(ItemModel.id)
    if status is not None:
        stmt = stmt.where(ItemModel.status == status)
    records = session.execute(stmt).scalars().all()
    return [_serialize_item(record) for record in records]


@app.post("/items", response_model=Item, status_code=201)
def create_item(
    payload: ItemCreate,
    session: Session = Depends(get_session),
    _auth: None = Depends(require_api_token),
):
    record = ItemModel(**payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_item(record)


@app.get("/items/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    session: Session = Depends(get_session),
):
    record = session.get(ItemModel, item_id)
    if record is not None:
        return _serialize_item(record)
    raise ApiError(code="not_found", detail="item not found", status=404)


@app.put("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    session: Session = Depends(get_session),
    _auth: None = Depends(require_api_token),
):
    record = session.get(ItemModel, item_id)
    if record is None:
        raise ApiError(code="not_found", detail="item not found", status=404)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise ApiError(
            code="validation_error",
            detail="at least one field must be provided",
            status=422,
        )

    if update_data.get("name") is None and "name" in update_data:
        raise ApiError(
            code="validation_error",
            detail="name cannot be null",
            status=422,
        )

    if update_data.get("status") is None and "status" in update_data:
        raise ApiError(
            code="validation_error",
            detail="status cannot be null",
            status=422,
        )

    for field, value in update_data.items():
        setattr(record, field, value)

    session.commit()
    session.refresh(record)
    return _serialize_item(record)


@app.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
    _auth: None = Depends(require_api_token),
):
    record = session.get(ItemModel, item_id)
    if record is None:
        raise ApiError(code="not_found", detail="item not found", status=404)
    session.delete(record)
    session.commit()
    return Response(status_code=204)
