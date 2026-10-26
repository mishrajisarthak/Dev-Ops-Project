from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.db import get_db
from app.main import app


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Folio Library API"
    assert data["status"] == "UP"


def test_health_liveness_probe(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP", "version": "2.0.0"}


def test_readiness_probe_healthy(client: TestClient):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_readiness_probe_database_failure():
    def mock_broken_db():
        mock = MagicMock()
        mock.execute.side_effect = Exception("Connection refused")
        yield mock

    app.dependency_overrides[get_db] = mock_broken_db
    try:
        with TestClient(app) as test_client:
            response = test_client.get("/ready")
            assert response.status_code == 503
            assert "Database connectivity check failed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_prometheus_metrics_endpoint(client: TestClient):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text or "http_request_duration_seconds" in response.text
