
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SortBy(str, Enum):
    """Sorting options for flight results"""
    PRICE = "price"
    DURATION = "duration"


class PricingTier(str, Enum):
    """Available pricing tiers"""
    ECONOMY = "economy"
    PREMIUM = "premium"
    BUSINESS = "business"
    FIRST = "first"


class DemandLevel(str, Enum):
    """Demand level categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Flight(BaseModel):
    """Internal flight model"""
    flight_id: str
    airline: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    base_fare: float
    total_seats: int
    available_seats: int
    tier: PricingTier
    
    @property
    def duration_minutes(self) -> int:
        """Calculate flight duration in minutes"""
        return int((self.arrival_time - self.departure_time).total_seconds() / 60)


class FlightResponse(BaseModel):
    """API response model for flights"""
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


class SearchParams(BaseModel):
    """Search parameters with validation"""
    origin: str = Field(..., min_length=3, max_length=3, description="Origin airport code")
    destination: str = Field(..., min_length=3, max_length=3, description="Destination airport code")
    date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$', description="Date in YYYY-MM-DD format")
    sort_by: Optional[SortBy] = SortBy.PRICE
    
    @validator('origin', 'destination')
    def validate_airport_code(cls, v):
        """Convert airport codes to uppercase"""
        return v.upper()
    
    @validator('date')
    def validate_date(cls, v):
        """Validate date is not in the past"""
        try:
            date = datetime.strptime(v, '%Y-%m-%d')
            if date.date() < datetime.now().date():
                raise ValueError('Date cannot be in the past')
            return v
        except ValueError as e:
            raise ValueError(f'Invalid date: {str(e)}')


class FareHistoryEntry(BaseModel):
    """Single fare history entry"""
    timestamp: str
    price: float
    available_seats: int
    demand_level: str


class FareHistoryResponse(BaseModel):
    """Fare history response"""
    flight_id: str
    airline: str
    route: str
    departure_time: str
    base_fare: float
    history_entries: int
    history: list[FareHistoryEntry]


class StatsResponse(BaseModel):
    """System statistics response"""
    total_flights: int
    active_flights: int
    total_seats: int
    available_seats: int
    occupancy_rate: str
    airports: int
    airlines: int
    tracked_fare_histories: int