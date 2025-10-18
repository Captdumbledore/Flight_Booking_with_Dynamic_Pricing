from datetime import datetime
from app.models import Flight, DemandLevel
from app.database import db


class DynamicPricingEngine:
    """
    Calculates dynamic pricing based on multiple factors:
    - Remaining seat percentage (scarcity)
    - Time until departure (urgency)
    - Simulated demand level (market demand)
    - Base fare and pricing tier (base cost)
    """
    
    @staticmethod
    def calculate_price(flight: Flight, demand_level: DemandLevel) -> float:
        """
        Calculate dynamic price for a flight
        
        Args:
            flight: Flight object
            demand_level: Current demand level
            
        Returns:
            Dynamic price as float
        """
        base_price = flight.base_fare
    
        seat_occupancy = 1 - (flight.available_seats / flight.total_seats)
        availability_multiplier = 1 + (seat_occupancy * 0.8) 
        

        time_until_departure = (flight.departure_time - datetime.now()).total_seconds() / 3600
        
        if time_until_departure < 0:
            return 0  
        elif time_until_departure < 24:
            time_multiplier = 1.5  
        elif time_until_departure < 72:
            time_multiplier = 1.3  
        elif time_until_departure < 168: 
            time_multiplier = 1.1
        elif time_until_departure > 720:  
            time_multiplier = 0.9  
        else:
            time_multiplier = 1.0 
        
    
        demand_multipliers = {
            DemandLevel.LOW: 0.85,      
            DemandLevel.MEDIUM: 1.0,    
            DemandLevel.HIGH: 1.25,     
            DemandLevel.VERY_HIGH: 1.6  
        }
        demand_multiplier = demand_multipliers[demand_level]
        

        dynamic_price = base_price * availability_multiplier * time_multiplier * demand_multiplier
        
        
        min_price = base_price * 0.5
        dynamic_price = max(dynamic_price, min_price)
        
        return round(dynamic_price, 2)
    
    @staticmethod
    def get_or_calculate_demand(flight: Flight) -> DemandLevel:
        """
        Get existing demand level or calculate new one
        
        Args:
            flight: Flight object
            
        Returns:
            DemandLevel enum
        """
        
        existing_demand = db.get_demand_level(flight.flight_id)
        if existing_demand:
            return existing_demand
        
    
        seat_occupancy = 1 - (flight.available_seats / flight.total_seats)
        hour = flight.departure_time.hour
        
        
        is_peak = 6 <= hour <= 9 or 17 <= hour <= 20
        
        
        score = seat_occupancy
        if is_peak:
            score += 0.3
        
    
        if score < 0.4:
            demand = DemandLevel.LOW
        elif score < 0.6:
            demand = DemandLevel.MEDIUM
        elif score < 0.8:
            demand = DemandLevel.HIGH
        else:
            demand = DemandLevel.VERY_HIGH
        
        db.set_demand_level(flight.flight_id, demand)
        
        return demand