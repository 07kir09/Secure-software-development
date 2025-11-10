from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": "test-token"}
PROBLEM_BASE = "https://problems.secdev.local/"


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert body["type"] == f"{PROBLEM_BASE}not_found"
    assert UUID(body["correlation_id"])
    assert r.headers["X-Correlation-ID"] == body["correlation_id"]


def test_rfc7807_contract():
    r = client.post("/items", json={"name": ""}, headers=AUTH_HEADERS)
    assert r.status_code == 422
    body = r.json()
    assert body["type"] == f"{PROBLEM_BASE}validation_error"
    assert body["title"] == "Validation Error"
    assert UUID(body["correlation_id"])
    assert isinstance(body["errors"], list) and body["errors"]
    message = body["detail"].lower()
    assert "at least" in message and "character" in message


def test_validation_error_does_not_echo_user_input():
    payload = {"name": ""}
    response = client.post("/items", json=payload, headers=AUTH_HEADERS)
    errors = response.json()["errors"]
    assert all("input" not in error for error in errors)
