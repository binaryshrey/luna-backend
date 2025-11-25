"""
Tests for the users API endpoints.
"""
import pytest


def test_create_user(client):
    """Test creating a new user."""
    user_data = {
        "handle": "testuser",
        "name": "Test User",
        "home_lat": 37.7749,
        "home_lng": -122.4194,
        "age": 25
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["handle"] == user_data["handle"]
    assert data["name"] == user_data["name"]
    assert data["home_lat"] == user_data["home_lat"]
    assert data["home_lng"] == user_data["home_lng"]
    assert data["age"] == user_data["age"]
    assert "id" in data


def test_create_user_minimal(client):
    """Test creating a user with minimal required fields."""
    user_data = {
        "handle": "minimaluser",
        "name": "Minimal User"
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["handle"] == user_data["handle"]
    assert data["name"] == user_data["name"]
    assert "id" in data


def test_create_duplicate_user(client):
    """Test that creating a user with duplicate handle fails."""
    user_data = {
        "handle": "duplicate",
        "name": "First User"
    }
    
    # Create first user
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == 200
    
    # Try to create duplicate
    user_data2 = {
        "handle": "duplicate",
        "name": "Second User"
    }
    response2 = client.post("/users/", json=user_data2)
    
    assert response2.status_code == 400
    assert "Handle already taken" in response2.json()["detail"]


def test_list_users_empty(client):
    """Test listing users when database is empty."""
    response = client.get("/users/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_users(client):
    """Test listing users after creating some."""
    # Create test users
    users = [
        {"handle": "user1", "name": "User One"},
        {"handle": "user2", "name": "User Two"},
        {"handle": "user3", "name": "User Three"}
    ]
    
    for user in users:
        response = client.post("/users/", json=user)
        assert response.status_code == 200
    
    # List all users
    response = client.get("/users/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Verify all users are present
    handles = [user["handle"] for user in data]
    assert "user1" in handles
    assert "user2" in handles
    assert "user3" in handles
