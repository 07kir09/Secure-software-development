"""Pydantic схемы и константы для работы с сущностями бэклога."""

import re

from pydantic import BaseModel, Field, field_validator

ALLOWED_STATUSES = {"draft", "in_progress", "done"}

SAFE_TEXT_PATTERN = re.compile(r"[<>]|[\x00-\x08\x0B\x0C\x0E-\x1F]")


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: str = Field(default="draft")

    @field_validator("status")
    @classmethod
    def ensure_valid_status(cls, value: str) -> str:
        if value not in ALLOWED_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
            )
        return value

    @field_validator("name", "description")
    @classmethod
    def ensure_safe_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if SAFE_TEXT_PATTERN.search(value):
            raise ValueError(
                "text contains forbidden control or angle bracket characters"
            )
        return value


class ItemCreate(ItemBase):
    """Payload used to create new items in the backlog."""


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: str | None = None

    @field_validator("status")
    @classmethod
    def ensure_valid_optional_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in ALLOWED_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
            )
        return value

    @field_validator("name", "description")
    @classmethod
    def ensure_safe_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if SAFE_TEXT_PATTERN.search(value):
            raise ValueError(
                "text contains forbidden control or angle bracket characters"
            )
        return value


class Item(ItemBase):
    id: int
