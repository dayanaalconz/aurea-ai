"""Tests for the AUREA AI health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_healthy_status() -> None:
    """Verify that the health endpoint reports an operational API."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "aurea-api",
    }