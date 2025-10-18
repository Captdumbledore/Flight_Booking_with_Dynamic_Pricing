"""
Standalone Flight Booking API - No external imports needed
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import random

# Create FastAPI app
app = FastAPI(
    title="Flight Booking API",
    description="A comprehensive flight booking system with dynamic pricing",
    version="1.0.0"
)

# In-memory storage
flights_data = []


# Pydantic Models
class FlightResponse(BaseModel):
    flight_id: str
    airline: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    current_price: float
    base_fare: float
    available_seats: int
    total_seats: int
    tier: str
    demand_level: str


class SearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')  # Fixed: pattern instead of regex
    sort_by: Optional[str] = "price"


class StatsResponse(BaseModel):
    total_flights: int
    total_seats: int
    available_seats: int
    occupancy_rate: str
    airports: int
    airlines: int


@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    global flights_data
    
    print("\n" + "="*60)
    print("🚀 Flight Booking API Starting...")
    print("="*60)
    
    # Generate sample flights
    print("\n📡 Generating sample flights...")
    
    airlines = [
        "SkyHigh Airways", "CloudNine Air", "Horizon Airlines", 
        "Velocity Air", "Tranquil Jets", "Pacific Wings"
    ]
    airports = [
        "JFK", "LAX", "ORD", "DFW", "ATL", "DEN", 
        "SFO", "LAS", "MIA", "SEA", "BOS", "IAH"
    ]
    
    flight_id = 1
    for day in range(7):  # 7 days of flights
        date = datetime.now() + timedelta(days=day)
        
        for _ in range(15):  # 15 flights per day
            origin = random.choice(airports)
            destination = random.choice([a for a in airports if a != origin])
            
            departure_hour = random.randint(6, 22)
            departure_minute = random.choice([0, 15, 30, 45])
            departure = date.replace(
                hour=departure_hour, 
                minute=departure_minute, 
                second=0, 
                microsecond=0
            )
            
            duration = random.randint(120, 420)  # 2-7 hours
            arrival = departure + timedelta(minutes=duration)
            
            base_fare = round(duration * 0.5, 2)
            available_seats = random.randint(30, 180)
            total_seats = 200
            
            # Calculate dynamic price
            occupancy = 1 - (available_seats / total_seats)
            price_multiplier = 1 + (occupancy * 0.5)
            current_price = round(base_fare * price_multiplier, 2)
            
            flights_data.append({
                "flight_id": f"FL{flight_id:04d}",
                "airline": random.choice(airlines),
                "origin": origin,
                "destination": destination,
                "departure_time": departure.strftime("%Y-%m-%d %H:%M"),
                "arrival_time": arrival.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{duration // 60}h {duration % 60}m",
                "current_price": current_price,
                "base_fare": base_fare,
                "available_seats": available_seats,
                "total_seats": total_seats,
                "tier": random.choice(["economy", "premium", "business"]),
                "demand_level": random.choice(["low", "medium", "high", "very_high"])
            })
            flight_id += 1
    
    print(f"✅ Generated {len(flights_data)} flights from {len(airlines)} airlines")
    print("\n" + "="*60)
    print("✨ Server is ready!")
    print("="*60)
    print("\n📚 API Documentation: http://localhost:8001/docs\n")


@app.get("/", tags=["Root"])
def root():
    """API root endpoint"""
    return {
        "message": "Flight Booking API with Dynamic Pricing",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "GET /flights": "Get all flights",
            "POST /flights/search": "Search flights by origin, destination, and date",
            "GET /flights/{flight_id}": "Get specific flight details",
            "GET /stats": "Get system statistics"
        }
    }


@app.get("/flights", response_model=List[FlightResponse], tags=["Flights"])
def get_all_flights(
    sort_by: Optional[str] = Query("price", description="Sort by price or duration"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Maximum results")
):
    """
    Get all flights with optional sorting
    
    - **sort_by**: Sort by 'price' or 'duration'
    - **limit**: Maximum number of flights to return (1-500)
    """
    
    result = flights_data.copy()
    
    # Sort
    if sort_by == "price":
        result.sort(key=lambda x: x["current_price"])
    elif sort_by == "duration":
        result.sort(key=lambda x: (
            int(x["duration"].split('h')[0]) * 60 + 
            int(x["duration"].split('h')[1].split('m')[0])
        ))
    
    return result[:limit]


@app.post("/flights/search", response_model=List[FlightResponse], tags=["Flights"])
def search_flights(search: SearchRequest):
    """
    Search flights by origin, destination, and date
    
    Request body:
    - **origin**: 3-letter airport code (e.g., JFK)
    - **destination**: 3-letter airport code (e.g., LAX)
    - **date**: Date in YYYY-MM-DD format
    - **sort_by**: Optional sorting (price or duration)
    """
    
    origin = search.origin.upper()
    destination = search.destination.upper()
    
    # Validate date
    try:
        search_date = datetime.strptime(search.date, '%Y-%m-%d')
        if search_date.date() < datetime.now().date():
            raise HTTPException(status_code=400, detail="Date cannot be in the past")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Filter flights
    matching = [
        f for f in flights_data
        if f["origin"] == origin
        and f["destination"] == destination
        and f["departure_time"].startswith(search.date)
    ]
    
    # Sort
    if search.sort_by == "price":
        matching.sort(key=lambda x: x["current_price"])
    elif search.sort_by == "duration":
        matching.sort(key=lambda x: (
            int(x["duration"].split('h')[0]) * 60 + 
            int(x["duration"].split('h')[1].split('m')[0])
        ))
    
    return matching


@app.get("/flights/{flight_id}", response_model=FlightResponse, tags=["Flights"])
def get_flight(flight_id: str):
    """
    Get specific flight details by ID
    
    - **flight_id**: Unique flight identifier (e.g., FL0001)
    """
    
    flight = next((f for f in flights_data if f["flight_id"] == flight_id), None)
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return flight


@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
def get_statistics():
    """Get system statistics"""
    
    if not flights_data:
        return {
            "total_flights": 0,
            "total_seats": 0,
            "available_seats": 0,
            "occupancy_rate": "0.00%",
            "airports": 0,
            "airlines": 0
        }
    
    total_seats = sum(f["total_seats"] for f in flights_data)
    available_seats = sum(f["available_seats"] for f in flights_data)
    
    return {
        "total_flights": len(flights_data),
        "total_seats": total_seats,
        "available_seats": available_seats,
        "occupancy_rate": f"{((total_seats - available_seats) / total_seats * 100):.2f}%",
        "airports": len(set([f["origin"] for f in flights_data] + [f["destination"] for f in flights_data])),
        "airlines": len(set(f["airline"] for f in flights_data))
    }