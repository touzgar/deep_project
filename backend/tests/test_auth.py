"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.core.database import Base, engine
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_signup(setup_database):
    """Test user signup"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "teacher"
        }
    )
    assert response.status_code == 201
    assert "email" in response.json()

def test_login():
    """Test user login"""
    # First create a user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "testpass123",
            "role": "teacher"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "logintest",
            "password": "testpass123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
