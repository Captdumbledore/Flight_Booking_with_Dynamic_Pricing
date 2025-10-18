
from typing import List
from collections import defaultdict
from app.models import Flight, DemandLevel


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
