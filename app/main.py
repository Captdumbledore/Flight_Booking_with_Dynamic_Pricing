import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import flights_router
from app.database import db
from app.simulator import AirlineAPISimulator, DemandSimulator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("\n" + "="*60)
    print("🚀 Flight Booking API Starting...")
    print("="*60)
    
    # Load flights from simulated airline APIs
    print("\n📡 Loading flights from airline APIs...")
    flights = AirlineAPISimulator.generate_flights(days_ahead=30)
    for flight in flights:
        db.add_flight(flight)
    print(f"✅ Loaded {len(flights)} flights from {len(set(f.airline for f in flights))} airlines")
    
    # Start background demand simulator
    print("\n🔄 Starting background demand simulator...")
    asyncio.create_task(DemandSimulator.simulate_bookings(interval=30))
    
    print("\n" + "="*60)
    print("✨ Server is ready!")
    print("="*60)
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Flight Booking API",
    description="A comprehensive flight booking system with dynamic pricing",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flights_router)


@app.get("/")
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
            "GET /flights/{flight_id}/fare-history": "Get fare history",
            "GET /stats": "Get system statistics"
        }
    }


@app.get("/stats", response_model=dict)
def get_statistics():
    """Get system statistics"""
    flights = db.get_all_flights()
    active_flights = [f for f in flights if f.departure_time > datetime.now()]
    
    total_seats = sum(f.total_seats for f in active_flights)
    available_seats = sum(f.available_seats for f in active_flights)
    
    return {
        "total_flights": len(flights),
        "active_flights": len(active_flights),
        "total_seats": total_seats,
        "available_seats": available_seats,
        "occupancy_rate": f"{((total_seats - available_seats) / total_seats * 100):.2f}%",
        "airports": len(set([f.origin for f in flights] + [f.destination for f in flights])),
        "airlines": len(set(f.airline for f in flights)),
        "tracked_fare_histories": len(db.fare_history)
    }


from datetime import datetime