from fastapi.testclient import TestClient
from app.core.config import Settings
from app.main import create_app

def make_client() -> TestClient:
    return TestClient(create_app(Settings(application_name="vedic-astrology", application_version="0.1.0", environment="development", allowed_origins_raw="http://localhost:5173,http://127.0.0.1:5173")))

def test_application_starts_and_docs_are_available() -> None:
    with make_client() as client: assert client.get("/docs").status_code == 200

def test_health_endpoint() -> None:
    response = make_client().get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "application": "vedic-astrology", "service": "backend"}

def test_version_endpoint() -> None:
    response = make_client().get("/api/version")
    assert response.status_code == 200
    assert response.json() == {"application": "vedic-astrology", "version": "0.1.0", "environment": "development"}

def test_unknown_api_route_returns_404() -> None:
    assert make_client().get("/api/unknown").status_code == 404

def test_cors_allows_authorized_development_origin() -> None:
    response = make_client().options("/api/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_cors_does_not_allow_unknown_origin() -> None:
    response = make_client().options("/api/health", headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in response.headers
