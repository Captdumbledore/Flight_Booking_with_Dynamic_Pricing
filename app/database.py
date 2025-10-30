
from typing import List
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.models import Base, User
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Flight(BaseModel):
    """Pydantic model for flights"""
    flight_id: str
    airline: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    base_fare: float
    total_seats: int
    available_seats: int
    tier: str
    
    @property
    def duration_minutes(self) -> int:
        """Calculate flight duration in minutes"""
        return int((self.arrival_time - self.departure_time).total_seconds() / 60)
from enum import Enum

class DemandLevel(str, Enum):
    """Demand level for flights"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# SQLite database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./flight_booking.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FlightDatabase:
    """In-memory flight database"""
    
    def __init__(self):
        self.flights: List[Flight] = []
        self.fare_history: defaultdict = defaultdict(list)
        self.demand_levels: dict = {}
    
    def add_flight(self, flight: Flight) -> None:
        """Add a flight to the database"""
        self.flights.append(flight)
    
    def get_all_flights(self) -> List[Flight]:
        """Get all flights"""
        return self.flights
    
    def get_flight_by_id(self, flight_id: str) -> Flight | None:
        """Get flight by ID"""
        return next((f for f in self.flights if f.flight_id == flight_id), None)
    
    def add_fare_history(self, flight_id: str, entry: dict) -> None:
        """Add fare history entry"""
        self.fare_history[flight_id].append(entry)
    
    def get_fare_history(self, flight_id: str) -> list:
        """Get fare history for a flight"""
        return self.fare_history.get(flight_id, [])
    
    def set_demand_level(self, flight_id: str, demand: DemandLevel) -> None:
        """Set demand level for a flight"""
        self.demand_levels[flight_id] = demand
    
    def get_demand_level(self, flight_id: str) -> DemandLevel | None:
        """Get demand level for a flight"""
        return self.demand_levels.get(flight_id)
    
    def clear(self) -> None:
        """Clear all data"""
        self.flights.clear()
        self.fare_history.clear()
        self.demand_levels.clear()


db = FlightDatabase()
