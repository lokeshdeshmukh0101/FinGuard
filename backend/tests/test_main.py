from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "environment" in data

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "python_" in response.text or "process_" in response.text or "finguard" in response.text

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "FinGuard" in data["message"]
