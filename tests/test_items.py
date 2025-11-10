from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": "test-token"}
PROBLEM_BASE = "https://problems.secdev.local/"


def test_create_item_success():
    payload = {"name": "Plan sprint", "description": "Outline goals"}
    response = client.post("/items", json=payload, headers=AUTH_HEADERS)

    assert response.status_code == 201
    body = response.json()

    assert body["id"] == 1
    assert body["name"] == payload["name"]
    assert body["description"] == payload["description"]
    assert body["status"] == "draft"


def test_list_items_with_status_filter():
    client.post("/items", json={"name": "Write docs"}, headers=AUTH_HEADERS)
    client.post(
        "/items",
        json={"name": "Implement API", "status": "in_progress"},
        headers=AUTH_HEADERS,
    )

    filtered = client.get("/items", params={"status": "in_progress"})
    assert filtered.status_code == 200
    body = filtered.json()

    assert len(body) == 1
    assert body[0]["name"] == "Implement API"
    assert body[0]["status"] == "in_progress"

    invalid = client.get("/items", params={"status": "unknown"})
    assert invalid.status_code == 422
    body = invalid.json()
    assert body["type"] == f"{PROBLEM_BASE}validation_error"
    assert body["status"] == 422
    assert UUID(body["correlation_id"])


def test_update_item_allows_partial_fields():
    item = client.post(
        "/items",
        json={"name": "Draft plan", "description": "v1"},
        headers=AUTH_HEADERS,
    ).json()
    response = client.put(
        f"/items/{item['id']}",
        json={"status": "done", "description": None},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "done"
    assert body["description"] is None

    empty_payload = client.put(f"/items/{item['id']}", json={}, headers=AUTH_HEADERS)
    assert empty_payload.status_code == 422
    problem = empty_payload.json()
    assert problem["type"] == f"{PROBLEM_BASE}validation_error"
    assert "at least one field" in problem["detail"]
    assert UUID(problem["correlation_id"])


def test_delete_item_removes_from_store():
    item = client.post(
        "/items", json={"name": "Remove me"}, headers=AUTH_HEADERS
    ).json()

    delete_response = client.delete(f"/items/{item['id']}", headers=AUTH_HEADERS)
    assert delete_response.status_code == 204
    assert delete_response.content in (b"", None)

    follow_up = client.get(f"/items/{item['id']}")
    assert follow_up.status_code == 404
    not_found = follow_up.json()
    assert not_found["type"] == f"{PROBLEM_BASE}not_found"
    assert not_found["status"] == 404


def test_mutating_without_api_key_returns_401():
    payload = {"name": "Unsafe mutation"}
    response = client.post("/items", json=payload)

    assert response.status_code == 401
    body = response.json()
    assert body["type"] == f"{PROBLEM_BASE}not_authorized"
    assert body["status"] == 401
    assert UUID(body["correlation_id"])
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]


def test_create_item_rejects_angle_brackets():
    payload = {"name": "<script>alert(1)</script>"}
    response = client.post("/items", json=payload, headers=AUTH_HEADERS)

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == f"{PROBLEM_BASE}validation_error"
    assert body["status"] == 422
    assert "forbidden control" in body["detail"]


def test_description_max_length_boundary():
    description = "a" * 300
    payload = {"name": "Edge case", "description": description}
    response = client.post("/items", json=payload, headers=AUTH_HEADERS)

    assert response.status_code == 201
    body = response.json()
    assert body["description"] == description
