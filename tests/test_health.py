"""
Tests for the health check endpoint.
"""


def test_health_check(client):
    """Test the health check endpoint returns correct status."""
    response = client.get("/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Luna API Service"


def test_health_check_structure(client):
    """Test the health check response has expected structure."""
    response = client.get("/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert isinstance(data["status"], str)
    assert isinstance(data["service"], str)
