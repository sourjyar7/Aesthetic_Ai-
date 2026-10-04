import pytest
from fastapi.testclient import TestClient

from aesthetic_api.main import app

client = TestClient(app)


def test_health_is_ok_without_database() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_id_is_generated() -> None:
    response = client.get("/api/health")
    assert response.headers["X-Request-ID"].startswith("req_")


def test_request_id_is_echoed() -> None:
    response = client.get("/api/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


@pytest.mark.integration
def test_ready_reports_postgres_and_pgvector() -> None:
    response = client.get("/api/health/ready")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ready"
    assert body["pgvector"].startswith("0.")
