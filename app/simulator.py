import random
import asyncio
from datetime import datetime, timedelta
from typing import List
from app.models import Flight, PricingTier, DemandLevel
from app.database import db
from app.pricing import DynamicPricingEngine


class AirlineAPISimulator:
    """
    Simulates external airline schedule APIs
    Generates realistic flight data from multiple airlines
    """
    
    airlines = [
        "SkyHigh Airways",
        "CloudNine Air",
        "Horizon Airlines",
        "Velocity Air",
        "Tranquil Jets",
        "Pacific Wings",
        "Atlantic Express",
        "Continental Connect"
    ]
    
    airports = [
        "JFK", "LAX", "ORD", "DFW", "ATL", "DEN",
        "SFO", "LAS", "MIA", "SEA", "BOS", "IAH",
        "PHX", "MCO", "EWR", "MSP", "DTW", "PHL"
    ]
    
    @staticmethod
    def generate_flights(days_ahead: int = 30) -> List[Flight]:
        """
        Generate flights for the next N days
        
        Args:
            days_ahead: Number of days to generate flights for
            
        Returns:
            List of Flight objects
        """
        flights = []
        flight_count = 0
        
        for day in range(days_ahead):
            date = datetime.now() + timedelta(days=day)
            

            daily_flights = random.randint(15, 25)
            
            for _ in range(daily_flights):
                origin = random.choice(AirlineAPISimulator.airports)
                destination = random.choice(
                    [a for a in AirlineAPISimulator.airports if a != origin]
                )
                
            
                departure_hour = random.randint(6, 22)
                departure_minute = random.choice([0, 15, 30, 45])
                departure_time = date.replace(
                    hour=departure_hour,
                    minute=departure_minute,
                    second=0,
                    microsecond=0
                )
                
            
                duration = random.randint(90, 420)
                arrival_time = departure_time + timedelta(minutes=duration)
                
            
                tier = random.choice(list(PricingTier))
                
            
                base_fare = AirlineAPISimulator._calculate_base_fare(duration, tier)
                
                
                total_seats = AirlineAPISimulator._get_seats_for_tier(tier)
                available_seats = random.randint(
                    int(total_seats * 0.3),
                    total_seats
                )
                
                flight_count += 1
                flights.append(Flight(
                    flight_id=f"FL{flight_count:04d}",
                    airline=random.choice(AirlineAPISimulator.airlines),
                    origin=origin,
                    destination=destination,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    base_fare=base_fare,
                    total_seats=total_seats,
                    available_seats=available_seats,
                    tier=tier
                ))
        
        return flights
    
    @staticmethod
    def _calculate_base_fare(duration: int, tier: PricingTier) -> float:
        """Calculate base fare based on duration and tier"""
        base = duration * 0.5  
        
        multipliers = {
            PricingTier.ECONOMY: 1.0,
            PricingTier.PREMIUM: 1.5,
            PricingTier.BUSINESS: 2.5,
            PricingTier.FIRST: 4.0
        }
        
        return round(base * multipliers[tier], 2)
    
    @staticmethod
    def _get_seats_for_tier(tier: PricingTier) -> int:
        """Get number of seats for tier"""
        seats = {
            PricingTier.ECONOMY: random.randint(150, 200),
            PricingTier.PREMIUM: random.randint(40, 60),
            PricingTier.BUSINESS: random.randint(20, 30),
            PricingTier.FIRST: random.randint(8, 16)
        }
        return seats[tier]


class DemandSimulator:
    """
    Background process that simulates:
    - Random seat bookings
    - Demand level changes
    - Fare history tracking
    """
    
    @staticmethod
    async def simulate_bookings(interval: int = 30):
        """
        Continuously simulate bookings and demand changes
        
        Args:
            interval: Sleep interval in seconds between simulations
        """
        print(f"\n🔄 Background demand simulator started (interval: {interval}s)")
        
        while True:
            await asyncio.sleep(interval)
            
            flights = db.get_all_flights()
            bookings_made = 0
            demand_changes = 0
            
            for flight in flights:
    
                if flight.departure_time < datetime.now():
                    continue
                
        
                if random.random() < 0.2 and flight.available_seats > 0:
                    seats_to_book = random.randint(1, min(5, flight.available_seats))
                    old_seats = flight.available_seats
                    flight.available_seats -= seats_to_book
                    bookings_made += 1
                    
                    
                    demand = DynamicPricingEngine.get_or_calculate_demand(flight)
                    price = DynamicPricingEngine.calculate_price(flight, demand)
                    
                    db.add_fare_history(flight.flight_id, {
                        "timestamp": datetime.now().isoformat(),
                        "price": price,
                        "available_seats": flight.available_seats,
                        "demand_level": demand.value
                    })
                
            
                if random.random() < 0.1:
                    old_demand = db.get_demand_level(flight.flight_id)
                    new_demand = random.choice(list(DemandLevel))
                    db.set_demand_level(flight.flight_id, new_demand)
                    
                    if old_demand != new_demand:
                        demand_changes += 1
            
            if bookings_made > 0 or demand_changes > 0:
                print(f"📊 Simulation cycle: {bookings_made} bookings, "
                      f"{demand_changes} demand changes")