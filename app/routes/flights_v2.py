from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta
import random
import asyncio
from app.models import FlightResponse, SearchParams, SortBy
from app.data.airports import get_airport_info, AIRPORTS, AIRLINE_NAMES
from app.state import flights_data
from app.amadeus_client import amadeus_client

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.post("/search", response_model=List[dict])
async def search_flights(search_request: SearchParams):
    """Search flights with real-time Amadeus API integration"""
    origin = search_request.origin.upper()
    destination = search_request.destination.upper()
    date = search_request.date
    sort_by = search_request.sort_by
    
    # Validate airports
    if origin not in AIRPORTS:
        raise HTTPException(status_code=400, detail=f"Invalid origin airport code: {origin}")
    if destination not in AIRPORTS:
        raise HTTPException(status_code=400, detail=f"Invalid destination airport code: {destination}")
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination must be different")
        
    # Parse and validate date
    try:
        search_date = datetime.strptime(date, "%Y-%m-%d")
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if search_date < current_date:
            raise HTTPException(
                status_code=400, 
                detail=f"Flight date {date} is in the past. Current date is {current_date.strftime('%Y-%m-%d')}"
            )
            
        # Don't allow dates more than 1 year in advance
        max_future_date = current_date + timedelta(days=365)
        if search_date > max_future_date:
            raise HTTPException(
                status_code=400, 
                detail=f"Flight date {date} is too far in the future. Maximum allowed date is {max_future_date.strftime('%Y-%m-%d')}"
            )
            
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date}. Use YYYY-MM-DD format")
    
    # Check cached flights
    matching = [
        f for f in flights_data
        if f["origin"] == origin
        and f["destination"] == destination
        and f["departure_time"].startswith(date)
    ]
    
    # If no matching flights found, try Amadeus API
    if not matching:
        try:
            async with asyncio.timeout(15):
                real_flights = await amadeus_client.search_flights(origin, destination, date)
                
                if real_flights:
                    flight_id = len(flights_data) + 1
                    for flight in real_flights:
                        new_flight = {
                            "flight_id": f"FL{flight_id:04d}",
                            "airline": flight.get("airline"),
                            "airline_code": flight.get("airline_code", ""),
                            "origin": origin,
                            "destination": destination,
                            "origin_city": get_airport_info(origin)["city"],
                            "destination_city": get_airport_info(destination)["city"],
                            "departure_time": flight.get("departure_time", ""),
                            "arrival_time": flight.get("arrival_time", ""),
                            "duration": flight.get("duration", "2h 30m"),
                            "current_price": flight.get("price", 299.99),
                            "base_fare": flight.get("base_fare", 199.99),
                            "available_seats": random.randint(20, 200),
                            "total_seats": random.choice([150, 180, 200]),
                            "tier": flight.get("cabin_class", "economy").lower(),
                            "demand_level": random.choice(["low", "medium", "high"])
                        }
                        matching.append(new_flight)
                        flights_data.append(new_flight)
                        flight_id += 1
                        
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Search request timed out. Please try again."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching flights: {str(e)}"
            )
    
    # If still no matches, generate fallback flights
    if not matching:
        org = get_airport_info(origin)
        dst = get_airport_info(destination)
        
        # Check route viability
        is_domestic = org["country"] == dst["country"]
        is_regional = False
        
        regions = {
            "North America": ["USA", "Canada", "Mexico"],
            "Europe": ["UK", "France", "Germany", "Italy", "Spain", "Netherlands", "Switzerland", "Austria", "Ireland"],
            "Middle East": ["UAE", "Qatar", "Saudi Arabia"],
            "Asia": ["Japan", "South Korea", "China", "Singapore", "Thailand", "India", "Hong Kong"],
            "Oceania": ["Australia", "New Zealand"],
        }
        
        for region, countries in regions.items():
            if org["country"] in countries and dst["country"] in countries:
                is_regional = True
                break
        
        if not is_domestic and not is_regional:
            raise HTTPException(
                status_code=404,
                detail=f"No direct flights available from {origin} ({org['city']}) to {destination} ({dst['city']}). This route may require connecting flights."
            )
        
        # Generate 3 fallback flights
        flight_id = len(flights_data) + 1
        for _ in range(3):
            departure_hour = random.randint(6, 23)
            departure_minute = random.choice([0, 15, 30, 45])
            departure = datetime.strptime(f"{date} {departure_hour:02d}:{departure_minute:02d}", "%Y-%m-%d %H:%M")
            
            duration_minutes = random.randint(90, 360) if is_domestic else random.randint(180, 840)
            arrival = departure + timedelta(minutes=duration_minutes)
            
            base_fare = round(duration_minutes * 0.3 + random.uniform(100, 300), 2)
            demand_multiplier = random.uniform(1.0, 1.8)
            current_price = round(base_fare * demand_multiplier, 2)
            
            demand_level = "high" if demand_multiplier > 1.5 else "medium" if demand_multiplier > 1.2 else "low"
            
            potential_airlines = [
                name for code, name in AIRLINE_NAMES.items()
                if is_domestic and code[:2] in [origin[:2], destination[:2]] or not is_domestic
            ]
            
            airline = random.choice(potential_airlines) if potential_airlines else random.choice(list(AIRLINE_NAMES.values()))
            
            fallback_flight = {
                "flight_id": f"FL{flight_id:04d}",
                "airline": airline,
                "origin": origin,
                "destination": destination,
                "origin_city": org["city"],
                "destination_city": dst["city"],
                "departure_time": departure.strftime("%Y-%m-%d %H:%M"),
                "arrival_time": arrival.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{duration_minutes // 60}h {duration_minutes % 60}m",
                "current_price": current_price,
                "base_fare": base_fare,
                "available_seats": random.randint(20, 200),
                "total_seats": random.choice([150, 180, 200]),
                "tier": random.choice(["economy"] * 6 + ["premium"] * 3 + ["business"]),
                "demand_level": demand_level
            }
            matching.append(fallback_flight)
            flights_data.append(fallback_flight)
            flight_id += 1
    
    # Sort results
    if sort_by == "price":
        matching.sort(key=lambda x: x["current_price"])
    else:  # sort by duration
        def get_duration_minutes(flight):
            try:
                h, m = map(int, flight["duration"].replace("h ", " ").replace("m", "").split())
                return h * 60 + m
            except:
                return 0
        matching.sort(key=get_duration_minutes)
    
    return matching

@router.get("/{flight_id}")
def get_flight(flight_id: str):
    """Get details for a specific flight"""
    flight = next((f for f in flights_data if f["flight_id"] == flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@router.get("")
def get_all_flights(
    sort_by: Optional[str] = Query("price", regex="^(price|duration)$"),
    limit: Optional[int] = Query(100, ge=1, le=500)
):
    """Get list of all available flights"""
    result = flights_data.copy()
    
    if sort_by == "price":
        result.sort(key=lambda x: x["current_price"])
    elif sort_by == "duration":
        def get_duration_minutes(flight):
            try:
                h, m = map(int, flight["duration"].replace("h ", " ").replace("m", "").split())
                return h * 60 + m
            except:
                return 0
        result.sort(key=get_duration_minutes)
    
    return result[:limit]