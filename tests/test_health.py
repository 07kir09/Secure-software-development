from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_includes_security_headers():
    r = client.get("/health")

    assert r.headers["Strict-Transport-Security"].startswith("max-age=")
    assert r.headers["Content-Security-Policy"].startswith("default-src")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Cache-Control"] == "no-store"
