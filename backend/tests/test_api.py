from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "model_available" in r.json()

def test_empty_registration_rejected():
    r = client.post("/auth/register", json={"name":"A","email":"bad","password":"1"})
    assert r.status_code == 422
