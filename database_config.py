from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random

from database_config import (
    get_db, Flight, Airline, Airport, Passenger, Booking, engine, Base
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flight Booking API with Database",
    description="Complete flight booking system with PostgreSQL",
    version="2.0.0"
)

# CORS Middleware - CRITICAL FOR FRONTEND CONNECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for API
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
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    sort_by: Optional[str] = "price"

class BookingRequest(BaseModel):
    flight_id: str
    passenger_name: str
    passenger_email: str
    passenger_phone: str

class BookingResponse(BaseModel):
    booking_id: str
    flight_id: str
    passenger_name: str
    seat_no: str
    status: str
    booking_date: str
    total_price: float

@app.on_event("startup")
async def startup_event():
    """Generate sample flights and insert into database"""
    
    print("\n" + "="*60)
    print("🚀 Flight Booking API with Database Starting...")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Check if flights already exist
        existing_flights = db.query(Flight).count()
        
        if existing_flights > 0:
            print(f"✅ Database already has {existing_flights} flights")
        else:
            print("\n📡 Generating and inserting flights into database...")
            
            airlines = db.query(Airline).all()
            airports = db.query(Airport).all()
            
            if not airlines or not airports:
                print("❌ Error: Airlines or Airports not found in database!")
                print("Please run the SQL setup script first.")
                return
            
            flight_count = 1
            for day in range(7):
                date = datetime.now() + timedelta(days=day)
                
                for _ in range(15):
                    origin_airport = random.choice(airports)
                    dest_airports = [a for a in airports if a.code != origin_airport.code]
                    destination_airport = random.choice(dest_airports)
                    
                    airline = random.choice(airlines)
                    
                    departure_hour = random.randint(6, 22)
                    departure_minute = random.choice([0, 15, 30, 45])
                    departure = date.replace(
                        hour=departure_hour,
                        minute=departure_minute,
                        second=0,
                        microsecond=0
                    )
                    
                    duration_minutes = random.randint(120, 420)
                    arrival = departure + timedelta(minutes=duration_minutes)
                    
                    base_fare = round(duration_minutes * 0.5, 2)
                    available_seats = random.randint(30, 180)
                    total_seats = 200
                    
                    occupancy = 1 - (available_seats / total_seats)
                    price_multiplier = 1 + (occupancy * 0.5)
                    current_price = round(base_fare * price_multiplier, 2)
                    
                    flight = Flight(
                        flight_id=f"FL{flight_count:04d}",
                        airline_id=airline.airline_id,
                        source_airport=origin_airport.code,
                        destination_airport=destination_airport.code,
                        departure_time=departure,
                        arrival_time=arrival,
                        base_fare=base_fare,
                        current_price=current_price,
                        total_seats=total_seats,
                        available_seats=available_seats,
                        tier=random.choice(["economy", "premium", "business"]),
                        demand_level=random.choice(["low", "medium", "high", "very_high"]),
                        duration=f"{duration_minutes // 60}h {duration_minutes % 60}m"
                    )
                    
                    db.add(flight)
                    flight_count += 1
            
            db.commit()
            print(f"✅ Successfully inserted {flight_count - 1} flights into database")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("✨ Server is ready!")
    print("="*60)
    print("\n📚 API Docs: http://localhost:8001/docs")
    print("🗄️ Database: PostgreSQL connected")
    print("🌐 CORS: Enabled for frontend\n")

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Flight Booking API with PostgreSQL Database",
        "version": "2.0.0",
        "status": "running",
        "database": "PostgreSQL",
        "documentation": "/docs"
    }

@app.get("/flights", response_model=List[FlightResponse])
def get_all_flights(
    sort_by: Optional[str] = Query("price"),
    limit: Optional[int] = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get all flights from database"""
    
    # Query flights with joins to get airline names
    flights = db.query(
        Flight, Airline.name
    ).join(
        Airline, Flight.airline_id == Airline.airline_id
    ).limit(limit).all()
    
    result = []
    for flight, airline_name in flights:
        result.append({
            "flight_id": flight.flight_id,
            "airline": airline_name,
            "origin": flight.source_airport,
            "destination": flight.destination_airport,
            "departure_time": flight.departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
            "duration": flight.duration,
            "current_price": flight.current_price,
            "base_fare": flight.base_fare,
            "available_seats": flight.available_seats,
            "total_seats": flight.total_seats,
            "tier": flight.tier,
            "demand_level": flight.demand_level
        })
    
    # Sort
    if sort_by == "price":
        result.sort(key=lambda x: x["current_price"])
    elif sort_by == "duration":
        result.sort(key=lambda x: (
            int(x["duration"].split('h')[0]) * 60 +
            int(x["duration"].split('h')[1].split('m')[0])
        ))
    
    return result

@app.post("/flights/search", response_model=List[FlightResponse])
def search_flights(search: SearchRequest, db: Session = Depends(get_db)):
    """Search flights in database"""
    
    origin = search.origin.upper()
    destination = search.destination.upper()
    
    try:
        search_date = datetime.strptime(search.date, '%Y-%m-%d').date()
        if search_date < datetime.now().date():
            raise HTTPException(status_code=400, detail="Date cannot be in the past")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Query with filters
    flights = db.query(
        Flight, Airline.name
    ).join(
        Airline, Flight.airline_id == Airline.airline_id
    ).filter(
        Flight.source_airport == origin,
        Flight.destination_airport == destination,
        Flight.departure_time >= datetime.combine(search_date, datetime.min.time()),
        Flight.departure_time < datetime.combine(search_date + timedelta(days=1), datetime.min.time())
    ).all()
    
    result = []
    for flight, airline_name in flights:
        result.append({
            "flight_id": flight.flight_id,
            "airline": airline_name,
            "origin": flight.source_airport,
            "destination": flight.destination_airport,
            "departure_time": flight.departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
            "duration": flight.duration,
            "current_price": flight.current_price,
            "base_fare": flight.base_fare,
            "available_seats": flight.available_seats,
            "total_seats": flight.total_seats,
            "tier": flight.tier,
            "demand_level": flight.demand_level
        })
    
    # Sort
    if search.sort_by == "price":
        result.sort(key=lambda x: x["current_price"])
    elif search.sort_by == "duration":
        result.sort(key=lambda x: (
            int(x["duration"].split('h')[0]) * 60 +
            int(x["duration"].split('h')[1].split('m')[0])
        ))
    
    return result

@app.get("/flights/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: str, db: Session = Depends(get_db)):
    """Get specific flight from database"""
    
    flight_data = db.query(
        Flight, Airline.name
    ).join(
        Airline, Flight.airline_id == Airline.airline_id
    ).filter(Flight.flight_id == flight_id).first()
    
    if not flight_data:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    flight, airline_name = flight_data
    
    return {
        "flight_id": flight.flight_id,
        "airline": airline_name,
        "origin": flight.source_airport,
        "destination": flight.destination_airport,
        "departure_time": flight.departure_time.strftime("%Y-%m-%d %H:%M"),
        "arrival_time": flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
        "duration": flight.duration,
        "current_price": flight.current_price,
        "base_fare": flight.base_fare,
        "available_seats": flight.available_seats,
        "total_seats": flight.total_seats,
        "tier": flight.tier,
        "demand_level": flight.demand_level
    }

@app.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingRequest, db: Session = Depends(get_db)):
    """Create booking in database"""
    
    # Get flight
    flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    if flight.available_seats <= 0:
        raise HTTPException(status_code=400, detail="No seats available")
    
    # Create or get passenger
    passenger = db.query(Passenger).filter(Passenger.email == booking.passenger_email).first()
    
    if not passenger:
        passenger = Passenger(
            name=booking.passenger_name,
            email=booking.passenger_email,
            phone=booking.passenger_phone
        )
        db.add(passenger)
        db.commit()
        db.refresh(passenger)
    
    # Generate booking ID
    booking_count = db.query(Booking).count()
    booking_id = f"BK{booking_count + 1:04d}"
    
    # Generate seat number
    seat_no = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
    
    # Create booking
    new_booking = Booking(
        booking_id=booking_id,
        flight_id=booking.flight_id,
        passenger_id=passenger.passenger_id,
        booking_date=datetime.now(),
        seat_no=seat_no,
        status="Confirmed",
        total_price=flight.current_price
    )
    
    db.add(new_booking)
    
    # Update available seats
    flight.available_seats -= 1
    
    db.commit()
    db.refresh(new_booking)
    
    return {
        "booking_id": new_booking.booking_id,
        "flight_id": new_booking.flight_id,
        "passenger_name": passenger.name,
        "seat_no": new_booking.seat_no,
        "status": new_booking.status,
        "booking_date": new_booking.booking_date.strftime("%Y-%m-%d"),
        "total_price": new_booking.total_price
    }

@app.get("/bookings", response_model=List[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    """Get all bookings from database"""
    
    bookings = db.query(Booking, Passenger.name).join(
        Passenger, Booking.passenger_id == Passenger.passenger_id
    ).all()
    
    result = []
    for booking, passenger_name in bookings:
        result.append({
            "booking_id": booking.booking_id,
            "flight_id": booking.flight_id,
            "passenger_name": passenger_name,
            "seat_no": booking.seat_no,
            "status": booking.status,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d"),
            "total_price": booking.total_price
        })
    
    return result

@app.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Get statistics from database"""
    
    total_flights = db.query(Flight).count()
    total_airlines = db.query(Airline).count()
    total_airports = db.query(Airport).count()
    total_bookings = db.query(Booking).count()
    
    flights = db.query(Flight).all()
    total_seats = sum(f.total_seats for f in flights)
    available_seats = sum(f.available_seats for f in flights)
    
    occupancy_rate = 0
    if total_seats > 0:
        occupancy_rate = ((total_seats - available_seats) / total_seats * 100)
    
    return {
        "total_flights": total_flights,
        "total_seats": total_seats,
        "available_seats": available_seats,
        "occupancy_rate": f"{occupancy_rate:.2f}%",
        "airports": total_airports,
        "airlines": total_airlines,
        "total_bookings": total_bookings
    }

# Import SessionLocal
from database_config import SessionLocal