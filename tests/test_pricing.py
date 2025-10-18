"""
Tests for dynamic pricing engine
"""

import pytest
from datetime import datetime, timedelta
from app.models import Flight, PricingTier, DemandLevel
from app.pricing import DynamicPricingEngine


def create_test_flight(
    available_seats: int = 100,
    total_seats: int = 200,
    hours_until_departure: int = 168
) -> Flight:
    """Helper to create test flight"""
    departure = datetime.now() + timedelta(hours=hours_until_departure)
    return Flight(
        flight_id="TEST001",
        airline="Test Airlines",
        origin="JFK",
        destination="LAX",
        departure_time=departure,
        arrival_time=departure + timedelta(hours=5),
        base_fare=300.0,
        total_seats=total_seats,
        available_seats=available_seats,
        tier=PricingTier.ECONOMY
    )


def test_price_increases_with_demand():
    """Test that price increases with demand level"""
    flight = create_test_flight()
    
    price_low = DynamicPricingEngine.calculate_price(flight, DemandLevel.LOW)
    price_medium = DynamicPricingEngine.calculate_price(flight, DemandLevel.MEDIUM)
    price_high = DynamicPricingEngine.calculate_price(flight, DemandLevel.HIGH)
    price_very_high = DynamicPricingEngine.calculate_price(flight, DemandLevel.VERY_HIGH)
    
    assert price_low < price_medium < price_high < price_very_high


def test_price_increases_with_seat_occupancy():
    """Test that price increases as seats fill up"""
    flight_many_seats = create_test_flight(available_seats=180, total_seats=200)
    flight_few_seats = create_test_flight(available_seats=20, total_seats=200)
    
    price_many = DynamicPricingEngine.calculate_price(flight_many_seats, DemandLevel.MEDIUM)
    price_few = DynamicPricingEngine.calculate_price(flight_few_seats, DemandLevel.MEDIUM)
    
    assert price_few > price_many


def test_last_minute_booking_premium():
    """Test that last-minute bookings are more expensive"""
    flight_early = create_test_flight(hours_until_departure=720)  # 30 days
    flight_late = create_test_flight(hours_until_departure=12)    # 12 hours
    
    price_early = DynamicPricingEngine.calculate_price(flight_early, DemandLevel.MEDIUM)
    price_late = DynamicPricingEngine.calculate_price(flight_late, DemandLevel.MEDIUM)
    
    assert price_late > price_early


def test_minimum_price_enforcement():
    """Test that price never goes below 50% of base fare"""
    flight = create_test_flight(available_seats=199, total_seats=200)  # Almost empty
    
    price = DynamicPricingEngine.calculate_price(flight, DemandLevel.LOW)
    
    assert price >= flight.base_fare * 0.5