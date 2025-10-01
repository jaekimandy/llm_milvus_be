import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_login():
    """Test user login"""
    # First register
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123"
        }
    )

    # Then login
    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user():
    """Test get current user endpoint"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "currentuser",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
