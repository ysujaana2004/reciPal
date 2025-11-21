# tests/test_main.py
"""
Tests for main.py:

- Verifies that FastAPI app is created
- Verifies /health endpoint works
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
