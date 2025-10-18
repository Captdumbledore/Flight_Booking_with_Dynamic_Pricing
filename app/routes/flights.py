from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.models import (
    FlightResponse, SearchParams, SortBy,
    FareHistoryResponse, FareHistoryEntry, StatsResponse
)
from app.database import db
from app.pricing import DynamicPricingEngine


router = APIRouter(prefix="/flights", tags=["Flights"])


def format_flight_response(flight) -> FlightResponse:
    """Helper to format flight as response"""
    demand = DynamicPricingEngine.get_or_calculate_demand(flight)
    price = DynamicPricingEngine.calculate_price(flight, demand)
    
    return FlightResponse(
        flight_id=flight.flight_id,
        airline=flight.airline,
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time.strftime("%Y-%m-%d %H:%M"),
        arrival_time=flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
        duration=f"{flight.duration_minutes // 60}h {flight.duration_minutes % 60}m",
        current_price=price,
        base_fare=flight.base_fare,
        available_seats=flight.available_seats,
        total_seats=flight.total_seats,
        tier=flight.tier.value,
        demand_level=demand.value
    )


@router.get("", response_model=List[FlightResponse])
def get_all_flights(
    sort_by: Optional[SortBy] = Query(SortBy.PRICE, description="Sort by price or duration"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Maximum number of results")
):
    """
    Retrieve all active flights
    
    - **sort_by**: Sort results by price or duration
    - **limit**: Maximum number of flights to return (1-500)
    """
    # Filter out past flights
    active_flights = [
        f for f in db.get_all_flights()
        if f.departure_time > datetime.now()
    ]
    
    # Format responses
    responses = [format_flight_response(f) for f in active_flights]
    
    # Sort
    if sort_by == SortBy.PRICE:
        responses.sort(key=lambda x: x.current_price)
    else:  # Sort by duration
        responses.sort(key=lambda x: (
            int(x.duration.split('h')[0]) * 60 +
            int(x.duration.split('h')[1].split('m')[0])
        ))
    
    return responses[:limit]


@router.post("/search", response_model=List[FlightResponse])
def search_flights(params: SearchParams):
    """
    Search flights by origin, destination, and date
    
    Request body:
    - **origin**: 3-letter airport code (e.g., JFK)
    - **destination**: 3-letter airport code (e.g., LAX)
    - **date**: Date in YYYY-MM-DD format
    - **sort_by**: Optional sorting (price or duration)
    """
    try:
        search_date = datetime.strptime(params.date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Filter flights
    matching_flights = [
        f for f in db.get_all_flights()
        if f.origin == params.origin
        and f.destination == params.destination
        and f.departure_time.date() == search_date
        and f.departure_time > datetime.now()
    ]
    
    if not matching_flights:
        return []
    
    # Format responses
    responses = [format_flight_response(f) for f in matching_flights]
    
    # Sort
    if params.sort_by == SortBy.PRICE:
        responses.sort(key=lambda x: x.current_price)
    else:
        responses.sort(key=lambda x: (
            int(x.duration.split('h')[0]) * 60 +
            int(x.duration.split('h')[1].split('m')[0])
        ))
    
    return responses


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: str):
    """
    Get specific flight details by ID
    
    - **flight_id**: Unique flight identifier (e.g., FL0001)
    """
    flight = db.get_flight_by_id(flight_id)
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return format_flight_response(flight)


@router.get("/{flight_id}/fare-history", response_model=FareHistoryResponse)
def get_fare_history(
    flight_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of history entries")
):
    """
    Get fare history for a specific flight
    
    - **flight_id**: Unique flight identifier
    - **limit**: Maximum number of history entries to return
    """
    flight = db.get_flight_by_id(flight_id)
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    history = db.get_fare_history(flight_id)
    
    return FareHistoryResponse(
        flight_id=flight_id,
        airline=flight.airline,
        route=f"{flight.origin} -> {flight.destination}",
        departure_time=flight.departure_time.strftime("%Y-%m-%d %H:%M"),
        base_fare=flight.base_fare,
        history_entries=len(history),
        history=[FareHistoryEntry(**entry) for entry in history[-limit:]]
    )