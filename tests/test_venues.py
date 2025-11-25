"""
Tests for the venues API endpoints.
"""


def test_create_venue(client):
    """Test creating a new venue."""
    venue_data = {
        "name": "Test Cafe",
        "description": "A cozy test cafe",
        "category": "cafe",
        "lat": 37.7749,
        "lng": -122.4194,
        "price_level": 2,
        "rating": 4.5
    }
    
    response = client.post("/venues/", json=venue_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == venue_data["name"]
    assert data["description"] == venue_data["description"]
    assert data["category"] == venue_data["category"]
    assert data["lat"] == venue_data["lat"]
    assert data["lng"] == venue_data["lng"]
    assert data["price_level"] == venue_data["price_level"]
    assert data["rating"] == venue_data["rating"]
    assert "id" in data


def test_create_venue_minimal(client):
    """Test creating a venue with minimal required fields."""
    venue_data = {
        "name": "Minimal Venue",
        "lat": 40.7128,
        "lng": -74.0060
    }
    
    response = client.post("/venues/", json=venue_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == venue_data["name"]
    assert data["lat"] == venue_data["lat"]
    assert data["lng"] == venue_data["lng"]
    assert "id" in data


def test_list_venues_empty(client):
    """Test listing venues when database is empty."""
    response = client.get("/venues/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_venues(client):
    """Test listing venues after creating some."""
    # Create test venues
    venues = [
        {"name": "Venue One", "lat": 37.7749, "lng": -122.4194},
        {"name": "Venue Two", "lat": 37.7750, "lng": -122.4195},
        {"name": "Venue Three", "lat": 37.7751, "lng": -122.4196}
    ]
    
    for venue in venues:
        response = client.post("/venues/", json=venue)
        assert response.status_code == 200
    
    # List all venues
    response = client.get("/venues/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Verify all venues are present
    names = [venue["name"] for venue in data]
    assert "Venue One" in names
    assert "Venue Two" in names
    assert "Venue Three" in names
