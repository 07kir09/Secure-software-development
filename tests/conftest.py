# tests/conftest.py
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]  # корень репозитория
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def reset_in_memory_db():
    from app.main import _reset_db

    _reset_db()
    yield
    _reset_db()


@pytest.fixture(autouse=True)
def configure_api_token(monkeypatch):
    monkeypatch.setenv("APP_API_TOKEN", "test-token")
