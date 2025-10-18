"""
Tests for flight endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.database import db
from app.models import Flight, PricingTier
from app.simulator import AirlineAPISimulator

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Setup test database before each test"""
    db.clear()
    flights = AirlineAPISimulator.generate_flights(days_ahead=7)
    for flight in flights:
        db.add_flight(flight)
    yield
    db.clear()


def test_get_all_flights():
    """Test getting all flights"""
    response = client.get("/flights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_search_flights():
    """Test flight search"""
    
    flights = db.get_all_flights()
    if flights:
        flight = flights[0]
        search_data = {
            "origin": flight.origin,
            "destination": flight.destination,
            "date": flight.departure_time.strftime("%Y-%m-%d"),
            "sort_by": "price"
        }
        response = client.post("/flights/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


def test_search_invalid_date():
    """Test search with invalid date"""
    search_data = {
        "origin": "JFK",
        "destination": "LAX",
        "date": "2020-01-01"  # Past date
    }
    response = client.post("/flights/search", json=search_data)
    assert response.status_code == 422


def test_get_flight_by_id():
    """Test getting specific flight"""
    flights = db.get_all_flights()
    if flights:
        flight = flights[0]
        response = client.get(f"/flights/{flight.flight_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["flight_id"] == flight.flight_id


def test_get_nonexistent_flight():
    """Test getting non-existent flight"""
    response = client.get("/flights/INVALID123")
    assert response.status_code == 404


def test_sorting_by_price():
    """Test sorting by price"""
    response = client.get("/flights?sort_by=price&limit=10")
    assert response.status_code == 200
    data = response.json()
    prices = [flight["current_price"] for flight in data]
    assert prices == sorted(prices)


def test_sorting_by_duration():
    """Test sorting by duration"""
    response = client.get("/flights?sort_by=duration&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0