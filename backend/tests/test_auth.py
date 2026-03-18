import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "VELIS"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_auth_status():
    response = client.get("/api/v1/auth/status")
    assert response.status_code == 200


def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "testregister@velis.com",
        "password": "test1234"
    })
    assert response.status_code in [201, 400]


def test_login_invalid():
    response = client.post("/api/v1/auth/login", data={
        "username": "wrong@email.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_resume_status():
    response = client.get("/api/v1/resume/status")
    assert response.status_code == 200


def test_interview_status():
    response = client.get("/api/v1/interview/status")
    assert response.status_code == 200


def test_voice_status():
    response = client.get("/api/v1/voice/status")
    assert response.status_code == 200


def test_analytics_status():
    response = client.get("/api/v1/analytics/status")
    assert response.status_code == 200
