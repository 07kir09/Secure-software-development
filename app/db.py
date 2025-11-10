"""Database utilities and SQLAlchemy session management."""

from __future__ import annotations

import os
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL_ENV = "DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite:///./app.db"


Base = declarative_base()

_engine: Engine | None = None


def _build_engine() -> Engine:
    """Initialise SQLAlchemy engine based on runtime configuration."""
    database_url = os.getenv(DATABASE_URL_ENV, DEFAULT_DATABASE_URL)
    engine_kwargs: dict[str, Any] = {}
    connect_args: dict[str, Any] = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if database_url == "sqlite:///:memory:":
            engine_kwargs["poolclass"] = StaticPool

    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)


def get_engine() -> Engine:
    """Return the singleton engine instance."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


SessionLocal = sessionmaker(
    bind=get_engine(),
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(get_engine())


def reset_database() -> None:
    """Drop and recreate all tables. Intended for test usage."""
    Base.metadata.drop_all(get_engine())
    Base.metadata.create_all(get_engine())
