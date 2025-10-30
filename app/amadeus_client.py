"""
Amadeus API Client for fetching real flight data
"""

import os
from datetime import datetime, timedelta
import httpx
import random
from typing import List, Optional, Dict

from app.data.airports import get_airline_name, get_airport_info

class AmadeusClient:
    BASE_URL = "https://test.api.amadeus.com"
    
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
        # Load credentials from environment variables
        self.client_id = os.getenv('AMADEUS_CLIENT_ID')
        self.client_secret = os.getenv('AMADEUS_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Amadeus credentials not found in environment variables")
    
    async def get_token(self) -> Optional[str]:
        """Get or refresh Amadeus API access token"""
        try:
            if self.access_token and self.token_expires_at:
                if datetime.utcnow() < self.token_expires_at:
                    return self.access_token

            url = f"{self.BASE_URL}/v1/security/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, headers=headers, data=data)

            if resp.status_code == 200:
                token_data = resp.json()
                self.access_token = token_data.get("access_token")
                expires_in = int(token_data.get("expires_in", 0))
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=max(30, expires_in - 30))
                return self.access_token
                
            print(f"❌ Failed to get Amadeus token: {resp.status_code}")
            return None

        except Exception as e:
            print(f"❌ Error getting Amadeus token: {e}")
            return None

    async def search_flights(self, origin: str, destination: str, date: str, max_results: int = 10) -> List[Dict]:
        """
        Search for flights using Amadeus API
        
        Args:
            origin: Origin airport code (e.g., 'JFK')
            destination: Destination airport code (e.g., 'LAX')
            date: Date in YYYY-MM-DD format
            max_results: Maximum number of results to return
            
        Returns:
            List of flight dictionaries with standardized format
        """
        token = await self.get_token()
        if not token:
            print("⚠️ No Amadeus token available")
            return []

        url = f"{self.BASE_URL}/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "max": max_results,
            "currencyCode": "USD"
        }

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(url, headers=headers, params=params)

                if resp.status_code == 200:
                    data = resp.json()
                    flights = []
                    
                    for offer in data.get("data", []):
                        for itinerary in offer.get("itineraries", []):
                            segments = itinerary.get("segments", [])
                            if not segments:
                                continue
                            
                            first_segment = segments[0]
                            last_segment = segments[-1]
                            
                            # Process carrier info
                            carrier_code = first_segment.get("carrierCode", "")
                            
                            # Process times
                            departure_time = first_segment.get("departure", {}).get("at", "")
                            arrival_time = last_segment.get("arrival", {}).get("at", "")
                            
                            # Calculate duration
                            try:
                                dep = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                                arr = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
                                duration = arr - dep
                                duration_str = f"{int(duration.total_seconds() // 3600)}h {int((duration.total_seconds() % 3600) // 60)}m"
                            except:
                                duration_str = "Unknown"

                            # Process price
                            price_info = offer.get("price", {})
                            try:
                                price = float(price_info.get("total", price_info.get("grandTotal", 0)))
                                base_fare = float(price_info.get("base", price_info.get("grandTotal", 0)))
                            except:
                                continue  # Skip if no valid price

                            # Format flight data
                            flight = {
                                "flight_id": f"AM{len(flights):04d}",  # AM prefix for Amadeus flights
                                "airline": get_airline_name(carrier_code),
                                "origin": origin,
                                "destination": destination,
                                "departure_time": departure_time,
                                "arrival_time": arrival_time,
                                "duration": duration_str,
                                "current_price": price,
                                "base_fare": base_fare,
                                # Add some randomized data for UI features
                                "available_seats": random.randint(5, 50),
                                "total_seats": random.choice([150, 180, 200]),
                                "tier": random.choice(["economy", "business", "premium"]),
                                "demand_level": random.choice(["low", "medium", "high"])
                            }
                            flights.append(flight)
                    
                    return flights[:max_results]
                
                elif resp.status_code == 400:
                    print(f"⚠️ Amadeus API 400 error for {origin}->{destination}: {resp.text}")
                    return []
                
                elif resp.status_code == 401:
                    print("⚠️ Amadeus token expired, refreshing...")
                    self.access_token = None
                    token = await self.get_token()
                    if not token:
                        return []
                    headers["Authorization"] = f"Bearer {token}"
                    continue
                
                else:
                    print(f"⚠️ Amadeus API error {resp.status_code}")
                    if attempt < max_retries:
                        await httpx.AsyncClient().aclose()
                        continue
                    return []

            except Exception as e:
                print(f"⚠️ Error searching flights {origin}->{destination}: {e}")
                if attempt < max_retries:
                    await httpx.AsyncClient().aclose()
                    continue
                return []

        return []  # If all retries failed

    async def get_initial_flights(self, num_routes: int = 5) -> List[Dict]:
        """
        Get a set of initial flights for the homepage
        
        Args:
            num_routes: Number of different routes to fetch
            
        Returns:
            List of flight dictionaries
        """
        # Popular airport pairs for initial display
        POPULAR_ROUTES = [
            ("JFK", "LAX"),  # New York to Los Angeles
            ("LHR", "JFK"),  # London to New York
            ("SFO", "JFK"),  # San Francisco to New York
            ("LAX", "ORD"),  # Los Angeles to Chicago
            ("MIA", "JFK"),  # Miami to New York
            ("BOS", "LAX"),  # Boston to Los Angeles
            ("SEA", "SFO"),  # Seattle to San Francisco
            ("DFW", "LAX"),  # Dallas to Los Angeles
            ("ORD", "LAS"),  # Chicago to Las Vegas
            ("ATL", "MIA"),  # Atlanta to Miami
        ]
        
        # Get tomorrow's date for searching
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        all_flights = []
        
        # Select random routes from the popular ones
        selected_routes = random.sample(POPULAR_ROUTES, min(num_routes, len(POPULAR_ROUTES)))
        
        for origin, destination in selected_routes:
            try:
                flights = await self.search_flights(origin, destination, tomorrow, max_results=3)
                all_flights.extend(flights)
            except Exception as e:
                print(f"Error fetching {origin}->{destination}: {e}")
                continue
        
        return all_flights

# Create a singleton instance
amadeus_client = AmadeusClient()