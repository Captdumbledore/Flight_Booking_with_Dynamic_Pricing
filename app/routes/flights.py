from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from app.models import (
    FlightResponse, SearchParams, SortBy,
    FareHistoryResponse, FareHistoryEntry, StatsResponse
)
from app.state import flights_data  # Import flight data
from app.models.search import FlightSearchRequest  # Import the request model
from app.database import db
from app.pricing import DynamicPricingEngine
from app.amadeus_client import amadeus_client

# In-memory cache for flights
cached_flights = []


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
async def get_all_flights(
    sort_by: Optional[SortBy] = Query(SortBy.PRICE, description="Sort by price or duration"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Maximum number of results")
):
    """
    Retrieve all active flights
    Uses real-time Amadeus data with caching
    """
    global cached_flights
    
    # If cache is empty, fetch initial flights
    if not cached_flights:
        cached_flights = await amadeus_client.get_initial_flights(num_routes=5)
    
    # Sort flights
    if sort_by == SortBy.PRICE:
        sorted_flights = sorted(cached_flights, key=lambda x: x["current_price"])
    else:  # Sort by duration
        def duration_minutes(flight):
            try:
                hours = int(flight["duration"].split('h')[0])
                minutes = int(flight["duration"].split('h')[1].split('m')[0])
                return hours * 60 + minutes
            except:
                return 0
        sorted_flights = sorted(cached_flights, key=duration_minutes)
    
    return sorted_flights[:limit]


@router.post("/search", response_model=List[dict])
async def search_flights(search_request: FlightSearchRequest):
    """
    Search flights with real-time Amadeus API integration
    """
    print(f"🔍 Flight Search Request")
    print("="*60)
    
    origin = search_request.origin.upper()
    destination = search_request.destination.upper()
    date = search_request.date
    sort_by = search_request.sort_by
    
    print(f"\nSearch parameters:")
    print(f"• Origin: {origin}")
    print(f"• Destination: {destination}")
    print(f"• Date: {date}")
    print(f"• Sort by: {sort_by}")
    
    try:
        # Validate date format
        search_date = datetime.strptime(date, '%Y-%m-%d').date()
        current_date = datetime.now().date()
        
        if search_date < current_date:
            error_msg = f"Flight date {date} is in the past"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Don't allow dates more than 1 year in advance
        max_future_date = current_date + timedelta(days=365)
        if search_date > max_future_date:
            error_msg = f"Flight date {date} is too far in the future"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Format the date for the API
        date_str = search_date.strftime('%Y-%m-%d')
        
        print("✅ Date validation successful")
        
        print("\n📡 Querying Amadeus API...")
        async def get_amadeus_flights():
            try:
                # Search Amadeus for flights
                flights = await amadeus_client.search_flights(
                    origin=origin,
                    destination=destination,
                    date=date_str,
                    max_results=10
                )
                
                if not flights:
                    print("\n❌ No flights found")
                    return []
                
                # Sort results
                if sort_by == "price":
                    flights.sort(key=lambda x: x["current_price"])
                    print("\n💰 Flights sorted by price")
                else:
                    def duration_minutes(flight):
                        try:
                            hours = int(flight["duration"].split('h')[0])
                            minutes = int(flight["duration"].split('h')[1].split('m')[0])
                            return hours * 60 + minutes
                        except:
                            return 0
                    flights.sort(key=duration_minutes)
                    print("\n⏱️ Flights sorted by duration")
                
                print(f"\n✅ Found {len(flights)} flights")
                return flights
            except Exception as e:
                print(f"\n❌ Error searching flights: {e}")
                return []
        
        return await asyncio.wait_for(get_amadeus_flights(), timeout=15)
        
    except ValueError as ve:
        error_msg = "Invalid date format. Use YYYY-MM-DD"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while searching flights"
        )


@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: str):
    """
    Get specific flight details by ID
    Checks cached flights from Amadeus
    """
    # Check cached flights
    flight = next((f for f in cached_flights if f["flight_id"] == flight_id), None)
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return flight


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