"""
Main FastAPI application - FIXED VERSION
"""

import asyncio
import os
from fastapi import FastAPI, HTTPException, Query, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random
import uuid
import smtplib
import socket

from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.user_database import get_db, User
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import json
import tempfile
import httpx
import os
import json
from dotenv import load_dotenv

# Create FastAPI app
app = FastAPI(
    title="Flight Booking API",
    description="A comprehensive flight booking system with dynamic pricing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Create FastAPI routers
from app.routes.flights_v2 import router as flights_router

# Include routers
app.include_router(flights_router)

# Import in-memory storage
from app.state import flights_data, bookings_data

# Load environment variables
load_dotenv()  # This will automatically look for .env file

# Amadeus API Configuration
AMADEUS_CLIENT_ID = "X5MG313HNu3o3YXHiqemToAUrQxknRwm"
AMADEUS_CLIENT_SECRET = "dGe3yTGET /bookings/email/jistoprakash@gmail.comGET /bookings/email/jistoprakash@gmail.comN6aHoGtmtD"
AMADEUS_BASE_URL = "https://test.api.amadeus.com"
AMADEUS_ACCESS_TOKEN = None
AMADEUS_TOKEN_EXPIRES_AT = None

# Import airports and airlines data from data module
from app.data.airports import AIRPORTS, AIRLINE_NAMES

def get_airline_name(code: str) -> str:
    """Convert airline code to full name"""
    return AIRLINE_NAMES.get(code, code)

def get_airport_info(code: str) -> dict:
    """Get airport information"""
    return AIRPORTS.get(code, {"city": code, "country": "Unknown", "name": f"{code} Airport"})

# Pydantic models
class PassengerDetails(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    passport_number: Optional[str] = None

class PaymentDetails(BaseModel):
    card_number: str
    card_holder_name: str
    expiry_month: int
    expiry_year: int
    cvv: str
    billing_address: str

class BookingRequest(BaseModel):
    flight_id: str
    passenger: PassengerDetails
    payment: PaymentDetails
    seat_preference: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    flight_id: str
    passenger_name: str
    email: str
    total_amount: float
    booking_status: str
    confirmation_code: str
    booking_date: str
    flight_details: Optional[dict] = None
    passenger_details: Optional[dict] = None



class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

async def load_initial_flights(initial_routes):
    """Load initial flight data for startup"""
    global flights_data
    flight_id = 1
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        token = await get_amadeus_token()
        if not token:
            print("⚠️ No Amadeus token available")
            return 0
            
        print("✅ Amadeus API connected")
        loaded = 0
        
        for origin, destination in initial_routes:
            try:
                flights = await search_amadeus_flights(origin, destination, tomorrow)
                for flight in flights[:2]:  # Just 2 flights per route
                    flights_data.append({
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
                        "tier": random.choice(["economy", "premium", "business"]),
                        "demand_level": random.choice(["low", "medium", "high"])
                    })
                    flight_id += 1
                    loaded += 1
                    await asyncio.sleep(0.5)  # Small delay between requests
            except Exception as route_error:
                print(f"⚠️ Error loading flights for {origin}->{destination}: {route_error}")
                continue
                
        return loaded
    except Exception as e:
        print(f"❌ Error loading initial flights: {e}")
        return 0

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup with minimal initial flights"""
    global flights_data
    
    print("\n" + "="*60)
    print("🚀 Flight Booking API Starting...")
    print("="*60)
    
    print("\n📡 Loading initial flight data...")
    
    # Load just a few popular routes for quick startup
    INITIAL_ROUTES = [
        ("JFK", "LAX"),  # New York to Los Angeles
        ("LHR", "JFK"),  # London to New York
        ("SFO", "LAX"),  # San Francisco to Los Angeles
    ]
    
    try:
        # Try to get some real flights with a timeout
        async def load_data():
            loaded = await load_initial_flights(INITIAL_ROUTES)
            
            if loaded < 3:
                print("\n⚠️ Insufficient flights from API, adding fallback data")
                await load_fallback_flight_data(initial_only=True)
                
            if not flights_data:
                print("❌ Failed to load any flights. Server may have limited functionality.")
            else:
                print(f"✅ Successfully loaded {len(flights_data)} flights")
                
        await asyncio.wait_for(load_data(), timeout=10)
        
    except Exception as e:
        print(f"\n❌ Error during startup: {e}")
        print(f"Type: {type(e).__name__}")
        if isinstance(e, httpx.HTTPError):
            print("Network or API error - check your internet connection and API credentials")
        elif isinstance(e, asyncio.TimeoutError):
            print("Operation timed out - API may be slow or unresponsive")
        elif isinstance(e, KeyError):
            print("Data format error - check API response structure")
        else:
            print("Unexpected error - please check logs for details")
        
        try:
            print("\n⚠️ Attempting to load fallback data...")
            await load_fallback_flight_data(initial_only=True)
        except Exception as fallback_error:
            print(f"❌ Failed to load fallback data: {fallback_error}")
            flights_data = []
    
    finally:
        flight_count = len(flights_data)
        status = "✅ Ready" if flight_count > 0 else "⚠️ Limited functionality"
        
        print("\n" + "="*60)
        print(f"✨ Flight Booking API: {status}")
        print("-"*60)
        print(f"📊 Loaded flights: {flight_count}")
        if flight_count > 0:
            routes = {(f['origin'], f['destination']) for f in flights_data}
            airlines = {f['airline'] for f in flights_data}
            print(f"🛫 Routes: {len(routes)}")
            print(f"✈️  Airlines: {len(airlines)}")
        print("="*60)
        print("\n📚 API Documentation: http://localhost:8001/docs\n")

async def get_amadeus_token():
    """Get access token from Amadeus API"""
    global AMADEUS_ACCESS_TOKEN, AMADEUS_TOKEN_EXPIRES_AT

    try:
        if AMADEUS_ACCESS_TOKEN and AMADEUS_TOKEN_EXPIRES_AT:
            if datetime.utcnow() < AMADEUS_TOKEN_EXPIRES_AT:
                return AMADEUS_ACCESS_TOKEN

        if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
            print("⚠️ Amadeus credentials not configured")
            return None

        url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, data=data)

        if resp.status_code == 200:
            token_data = resp.json()
            token = token_data.get("access_token")
            expires_in = int(token_data.get("expires_in", 0))
            if token:
                AMADEUS_ACCESS_TOKEN = token
                AMADEUS_TOKEN_EXPIRES_AT = datetime.utcnow() + timedelta(seconds=max(30, expires_in - 30))
                return AMADEUS_ACCESS_TOKEN
        else:
            print(f"❌ Failed to get Amadeus token: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting Amadeus token: {e}")
        return None

async def search_amadeus_flights(origin, destination, date):
    """Search flights using Amadeus API with retry logic and enhanced error handling"""
    token = await get_amadeus_token()
    if not token:
        return []

    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "max": 10,  # Increased from 5 to get more options
        "currencyCode": "USD",
        "nonStop": "true"  # Prefer non-stop flights
    }

    max_retries = 3
    backoff_factor = 1.5  # For exponential backoff
    
    for attempt in range(1, max_retries + 1):
        try:
            timeout = 30 * attempt  # Increase timeout with each retry
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, headers=headers, params=params)

            if resp.status_code == 200:
                data = resp.json()
                flights = []
                
                # Process flight offers
                for offer in data.get("data", []):
                    # Price calculation with fallback
                    price_info = offer.get("price", {})
                    try:
                        price = float(price_info.get("total", price_info.get("grandTotal", 299.99)))
                        base_fare = float(price_info.get("base", 199.99))
                    except (ValueError, TypeError):
                        price = 299.99
                        base_fare = 199.99

                    for itinerary in offer.get("itineraries", []):
                        segments = itinerary.get("segments", [])
                        if not segments:
                            continue
                        
                        first_segment = segments[0]
                        last_segment = segments[-1]
                        
                        # Enhanced airline info
                        airline_code = first_segment.get("carrierCode", "Unknown")
                        airline_name = get_airline_name(airline_code)
                        
                        # Get times with proper error handling
                        try:
                            departure_time = first_segment.get("departure", {}).get("at", "")
                            arrival_time = last_segment.get("arrival", {}).get("at", "")
                            departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                            arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                        except (ValueError, AttributeError):
                            print(f"⚠️ Invalid time format for flight {airline_code}")
                            continue

                        # Calculate duration
                        duration = calculate_duration_from_times(first_segment.get("departure", {}).get("at", ""),
                                                                 last_segment.get("arrival", {}).get("at", ""))

                        # Enhanced flight object
                        flight_data = {
                            "airline": airline_name,
                            "airline_code": airline_code,
                            "origin": origin,
                            "destination": destination,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "duration": duration,
                            "price": price,
                            "base_fare": base_fare,
                            "cabin_class": offer.get("travelerPricings", [{}])[0].get("fareDetailsBySegment", [{}])[0].get("cabin", "ECONOMY"),
                        }
                        
                        flights.append(flight_data)
                
                if flights:
                    print(f"✅ Found {len(flights)} flights for {origin}->{destination} on {date}")
                    return flights
                else:
                    print(f"⚠️ No flights found for {origin}->{destination} on {date}")
                    return []
                
            elif resp.status_code == 400:
                error_data = resp.json() if resp.text else {}
                print(f"⚠️ Amadeus API 400 error for {origin}->{destination}: {error_data}")
                return []  # Don't retry on 400 errors
                
            elif resp.status_code == 401:
                print(f"⚠️ Amadeus API authentication failed. Refreshing token...")
                global AMADEUS_ACCESS_TOKEN
                AMADEUS_ACCESS_TOKEN = None
                token = await get_amadeus_token()
                if not token:
                    return []
                headers["Authorization"] = f"Bearer {token}"
                continue
                
            elif 500 <= resp.status_code < 600:
                print(f"⚠️ Amadeus API server error {resp.status_code} (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return []
                
            else:
                print(f"⚠️ Amadeus API error {resp.status_code}: {resp.text[:200]}")
                return []
                        
        except httpx.TimeoutException:
            print(f"⚠️ Amadeus API timeout (attempt {attempt}/{max_retries})")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            return []
        except Exception as e:
            print(f"⚠️ Error searching flights {origin}->{destination}: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            return []
    
    return []

def calculate_duration_from_times(departure_str, arrival_str):
    """Calculate duration from departure and arrival time strings"""
    try:
        departure = datetime.fromisoformat(departure_str.replace('Z', '+00:00'))
        arrival = datetime.fromisoformat(arrival_str.replace('Z', '+00:00'))
        duration = arrival - departure
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    except:
        return "2h 30m"

async def load_real_flight_data():
    """Load real flight data from Amadeus API"""
    global flights_data
    
    try:
        token = await get_amadeus_token()
        if not token:
            print("⚠️ No Amadeus token, using fallback data")
            await load_fallback_flight_data()
            return
        
        print("✅ Amadeus API connected")
        
        # More comprehensive list of popular routes
        POPULAR_ROUTES = [
            ("JFK", "LAX"),  # New York to Los Angeles
            ("LHR", "JFK"),  # London to New York
            ("SFO", "JFK"),  # San Francisco to New York
            ("LAX", "ORD"),  # Los Angeles to Chicago
            ("MIA", "JFK"),  # Miami to New York
            ("DFW", "LAS"),  # Dallas to Las Vegas
            ("ATL", "MCO"),  # Atlanta to Orlando
            ("BOS", "CHI"),  # Boston to Chicago
            ("SEA", "SFO"),  # Seattle to San Francisco
            ("DEN", "PHX"),  # Denver to Phoenix
            ("CDG", "LHR"),  # Paris to London
            ("DXB", "LHR"),  # Dubai to London
            ("SIN", "HKG"),  # Singapore to Hong Kong
            ("NRT", "ICN"),  # Tokyo to Seoul
            ("SYD", "MEL"),  # Sydney to Melbourne
        ]
        
        flight_id = 1
        
        # Get flights for the next 7 days
        for days_ahead in range(7):
            date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            print(f"\n📅 Fetching flights for {date}")
            
            # Create tasks for parallel execution
            tasks = []
            for origin, destination in POPULAR_ROUTES:
                tasks.append(search_amadeus_flights(origin, destination, date))
            
            # Execute tasks in parallel with rate limiting
            chunk_size = 3  # Process 3 routes at a time to avoid rate limits
            for i in range(0, len(tasks), chunk_size):
                chunk = tasks[i:i + chunk_size]
                try:
                    results = await asyncio.gather(*chunk)
                    await asyncio.sleep(1)  # Rate limiting delay between chunks
                    
                    for flights in results:
                        for flight in flights[:3]:  # Up to 3 flights per route
                            origin = flight.get("origin")
                            destination = flight.get("destination")
                            
                            flights_data.append({
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
                                "tier": random.choice(["economy", "premium", "business"]),
                                "demand_level": random.choice(["low", "medium", "high", "very_high"])
                            })
                            flight_id += 1
                            
                except Exception as e:
                    print(f"⚠️ Error in chunk {i//chunk_size + 1}: {e}")
                    continue
            
            print(f"✈️  Loaded {len(flights_data)} flights for {date}")
        
        if len(flights_data) < 20:
            print("\n⚠️ Not enough real flights, supplementing with fallback data")
            await load_fallback_flight_data()
        else:
            print(f"\n✅ Successfully loaded {len(flights_data)} real flights")
            
            # Add some statistics
            airlines = set(f["airline"] for f in flights_data)
            routes = set((f["origin"], f["destination"]) for f in flights_data)
            print(f"\n📊 Flight Statistics:")
            print(f"• Airlines: {len(airlines)}")
            print(f"• Routes: {len(routes)}")
            print(f"• Days covered: 7")
            print(f"• Average flights per route: {len(flights_data)/len(routes):.1f}")
            
    except Exception as e:
        print(f"\n❌ Error loading real flights: {e}")
        print("⚠️ Using fallback data instead")
        await load_fallback_flight_data()

async def load_fallback_flight_data(initial_only=False):
    """Load fallback flight data"""
    global flights_data
    
    airlines = list(AIRLINE_NAMES.values())
    airports = list(AIRPORTS.keys())
    
    flight_id = len(flights_data) + 1
    num_days = 1 if initial_only else 7
    flights_per_day = 3 if initial_only else 20
    
    for day in range(num_days):
        date = datetime.now() + timedelta(days=day)
        
        for _ in range(flights_per_day):
            origin = random.choice(airports)
            destination = random.choice([a for a in airports if a != origin])
            
            departure_hour = random.randint(6, 23)
            departure_minute = random.choice([0, 15, 30, 45])
            departure = date.replace(hour=departure_hour, minute=departure_minute, second=0, microsecond=0)
            
            duration_minutes = random.randint(90, 600)
            arrival = departure + timedelta(minutes=duration_minutes)
            
            base_fare = round(duration_minutes * 0.2 + random.uniform(50, 200), 2)
            current_price = round(base_fare * random.uniform(1.0, 1.5), 2)
            
            flights_data.append({
                "flight_id": f"FL{flight_id:04d}",
                "airline": random.choice(airlines),
                "origin": origin,
                "destination": destination,
                "origin_city": get_airport_info(origin)["city"],
                "destination_city": get_airport_info(destination)["city"],
                "departure_time": departure.strftime("%Y-%m-%d %H:%M"),
                "arrival_time": arrival.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{duration_minutes // 60}h {duration_minutes % 60}m",
                "current_price": current_price,
                "base_fare": base_fare,
                "available_seats": random.randint(20, 200),
                "total_seats": random.choice([150, 180, 200]),
                "tier": random.choice(["economy", "premium", "business"]),
                "demand_level": random.choice(["low", "medium", "high"])
            })
            flight_id += 1
            
            if initial_only and len(flights_data) >= 3:
                return  # Stop after 3 flights in initial mode

def validate_payment(payment: PaymentDetails) -> bool:
    """Validate payment details"""
    if len(payment.card_number) >= 13 and len(payment.card_number) <= 19:
        if payment.expiry_year >= datetime.now().year:
            if payment.expiry_year == datetime.now().year:
                return payment.expiry_month >= datetime.now().month
            return True
    return False

def send_confirmation_email(email: str, booking: dict) -> bool:
    """Send booking confirmation email via Gmail SMTP"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")

        # Create email content first
        body = f"""
Dear {booking['passenger']['first_name']} {booking['passenger']['last_name']},

Thank you for booking with SkyBook Airlines!

BOOKING CONFIRMATION
===================
Booking ID: {booking['booking_id']}
Confirmation Code: {booking['confirmation_code']}
Flight: {booking['flight_id']}

FLIGHT DETAILS
==============
Airline: {booking.get('airline', 'N/A')}
Route: {booking['origin']} ({booking.get('origin_city', '')}) → {booking['destination']} ({booking.get('destination_city', '')})
Departure: {booking['departure_time']}
Arrival: {booking['arrival_time']}
Duration: {booking['duration']}
Class: {booking['tier'].upper()}

PAYMENT INFORMATION
===================
Total Amount: ${booking['total_amount']:.2f}
Payment Status: Confirmed

IMPORTANT REMINDERS
==================
• Arrive at the airport 2 hours before departure
• Bring valid photo ID and confirmation code
• Check-in online 24 hours before departure

Have a great flight!

Best regards,
SkyBook Airlines Customer Service
        """

        # Check if SMTP is configured
        if not sender_email or not sender_password:
            print("\n⚠️ SMTP credentials not configured in .env file")
            print("\n📧 EMAIL CONTENT (would be sent to):")
            print(f"To: {email}")
            print(f"Subject: Flight Booking Confirmation - {booking['confirmation_code']}")
            print(body)
            print("="*60)
            print("\n💡 To enable email sending:")
            print("1. Add SMTP_EMAIL and SMTP_PASSWORD to your .env file")
            print("2. For Gmail, use an App Password (not your regular password)")
            print("3. Generate App Password at: https://myaccount.google.com/apppasswords")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"Flight Booking Confirmation - {booking['confirmation_code']}"
        msg.attach(MIMEText(body, 'plain'))

        # Generate and attach PDF
        try:
            pdf_path = generate_booking_pdf(booking)
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=f'booking_{booking["confirmation_code"]}.pdf')
                msg.attach(pdf_attachment)
        except Exception as pdf_err:
            print(f"⚠️ Error generating PDF: {pdf_err}")

        # Attach JSON data
        booking_json = {k: v for k, v in booking.items() if k not in ['payment']}  # Exclude sensitive payment data
        json_attachment = MIMEApplication(
            json.dumps(booking_json, indent=2).encode('utf-8'),
            _subtype='json'
        )
        json_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename=f'booking_{booking["confirmation_code"]}.json')

        # Try sending with detailed error handling
        try:
            # Connect with explicit timeout
            print(f"\n📧 Attempting to send email to {email}...")
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
            server.set_debuglevel(0)  # Set to 1 for detailed SMTP debugging
            
            # Identify ourselves
            server.ehlo()
            
            # Secure the connection
            server.starttls()
            server.ehlo()
            
            # Login
            print(f"🔐 Logging in as {sender_email}...")
            server.login(sender_email, sender_password)
            
            # Send email
            print(f"📤 Sending email...")
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            
            print(f"✅ EMAIL SUCCESSFULLY SENT TO: {email}")
            print(f"    Confirmation Code: {booking['confirmation_code']}")
            print(f"    Booking ID: {booking['booking_id']}")
            return True
            
        except smtplib.SMTPAuthenticationError as auth_err:
            print("\n❌ SMTP Authentication Failed!")
            print(f"    Error: {auth_err}")
            print("\n💡 SOLUTION:")
            print("    For Gmail accounts:")
            print("    1. Enable 2-Factor Authentication on your Google account")
            print("    2. Generate an App Password at: https://myaccount.google.com/apppasswords")
            print("    3. Use the 16-character app password (no spaces) as SMTP_PASSWORD")
            print(f"    4. Current SMTP_EMAIL: {sender_email}")
            print(f"    5. Password format should be: xxxx xxxx xxxx xxxx (16 chars)")
            return False
            
        except smtplib.SMTPRecipientsRefused:
            print(f"\n❌ Recipient email address refused: {email}")
            print("    Please check if the email address is valid")
            return False
            
        except smtplib.SMTPSenderRefused:
            print(f"\n❌ Sender email address refused: {sender_email}")
            print("    Please check your SMTP_EMAIL in .env file")
            return False
            
        except smtplib.SMTPServerDisconnected:
            print("\n❌ SMTP server disconnected unexpectedly")
            print("    This may be a temporary issue. Try again in a moment.")
            return False
            
        except smtplib.SMTPException as smtp_err:
            print(f"\n❌ SMTP Error: {smtp_err}")
            return False
            
        except socket.timeout:
            print("\n❌ Connection timeout - SMTP server not responding")
            print(f"    Server: {smtp_server}:{smtp_port}")
            return False
            
        except Exception as send_err:
            print(f"\n❌ Unexpected error sending email: {send_err}")
            print(f"    Type: {type(send_err).__name__}")
            return False
            
    except Exception as e:
        print(f"\n❌ Email configuration error: {e}")
        print("\n📧 EMAIL CONTENT (fallback):")
        print(f"To: {email}")
        print(f"Booking: {booking['booking_id']}")
        print(f"Confirmation: {booking['confirmation_code']}")
        return False

def generate_confirmation_code() -> str:
    """Generate confirmation code"""
    return f"SKY{random.randint(100000, 999999)}"

def generate_booking_pdf(booking: dict) -> str:
    """Generate PDF for booking confirmation with enhanced design"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf_path = temp_file.name
        
    # Create the PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Add decorative header background
    c.setFillColor(colors.navy)
    c.rect(0, height - 150, width, 150, fill=True)
    
    # Add airline logo/name with shadow effect
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(52, height - 52, "✈")  # Shadow
    c.drawString(50, height - 50, "✈ SkyBook Airlines")
    
    # Add confirmation text
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 90, "Booking Confirmation")
    
    # Add decorative line
    c.setStrokeColor(colors.white)
    c.setLineWidth(2)
    c.line(50, height - 110, width - 50, height - 110)
    
    # Start content area
    y = height - 180
    
    # Helper function for section headers
    def draw_section_header(title, y_pos):
        # Draw gradient-like header
        c.setFillColor(colors.navy)
        c.rect(45, y_pos - 5, width - 90, 30, fill=True)
        
        # Add decorative side bar
        c.setFillColor(colors.lightblue)
        c.rect(45, y_pos - 5, 5, 30, fill=True)
        
        # Add title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, y_pos + 5, title)
        return y_pos - 45
    
    # Helper function for content
    def draw_content_row(label, value, y_pos, highlight=False):
        c.setFillColor(colors.navy if highlight else colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y_pos, label)
        c.setFont("Helvetica", 12)
        c.drawString(200, y_pos, value)
        return y_pos - 20
    
    # Booking Information Section
    y = draw_section_header("Booking Information", y)
    
    y = draw_content_row("Booking ID:", booking['booking_id'], y)
    y = draw_content_row("Confirmation Code:", booking['confirmation_code'], y, True)
    y = draw_content_row("Booking Date:", booking['booking_date'], y)
    y = y - 10  # Extra spacing
    
    y = draw_content_row("Passenger:", f"{booking['passenger']['first_name']} {booking['passenger']['last_name']}", y)
    y = draw_content_row("Email:", booking['passenger']['email'], y)
    y = draw_content_row("Phone:", booking['passenger']['phone'], y)
    
    # Flight Information Section
    y = y - 20  # Extra spacing
    y = draw_section_header("Flight Information", y)
    
    # Add airplane icon and route visualization
    c.setFillColor(colors.navy)
    c.setFont("Helvetica", 24)
    x_start = 60
    x_end = width - 60
    y_route = y - 10
    
    # Draw route line
    c.setStrokeColor(colors.navy)
    c.setLineWidth(1)
    c.line(x_start + 40, y_route, x_end - 40, y_route)
    
    # Draw airports
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_start, y_route + 20, booking['origin'])
    c.drawString(x_end - 60, y_route + 20, booking['destination'])
    
    # Draw cities
    c.setFont("Helvetica", 10)
    c.drawString(x_start, y_route + 5, booking.get('origin_city', ''))
    c.drawString(x_end - 60, y_route + 5, booking.get('destination_city', ''))
    
    # Draw airplane icon
    c.drawString(width/2 - 10, y_route + 10, "✈")
    
    y = y_route - 40  # Continue below the route visualization
    
    y = draw_content_row("Flight ID:", booking['flight_id'], y)
    y = draw_content_row("Airline:", booking.get('airline', 'N/A'), y)
    y = draw_content_row("Departure:", booking['departure_time'], y)
    y = draw_content_row("Arrival:", booking['arrival_time'], y)
    y = draw_content_row("Duration:", booking['duration'], y)
    y = draw_content_row("Class:", booking['tier'].upper(), y, True)
    
    # Payment Information Section
    y = y - 20
    y = draw_section_header("Payment Information", y)
    
    # Add decorative price display
    c.setFillColor(colors.navy)
    c.rect(60, y - 40, 200, 30, fill=True)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(70, y - 20, f"Total Amount: ${booking['total_amount']:.2f}")
    
    y = y - 60
    y = draw_content_row("Payment Status:", "Confirmed", y, True)
    
    # Add footer
    c.setFillColor(colors.navy)
    c.rect(0, 50, width, 2, fill=True)
    c.setFont("Helvetica", 10)
    c.drawString(50, 30, "Thank you for choosing SkyBook Airlines!")
    c.drawString(50, 15, f"Booking Reference: {booking['confirmation_code']}")
    
    # Save the PDF
    c.save()
    
    return pdf_path

# API ENDPOINTS

@app.post("/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Handle user login"""
    print(f"\n🔐 Login attempt for {user_data.email}")
    
    try:
        # Find user in database
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            print(f"❌ User not found: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(user_data.password, user.password_hash):
            print(f"❌ Invalid password for {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate access token
        token_data = {"sub": user.email}
        access_token = create_access_token(token_data)
        print(f"✅ Login successful for {user_data.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
    
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/auth/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    print(f"\n📝 Registration attempt for {user_data.email}")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            print(f"❌ Email already registered: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create password hash
        password_hash = get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Registration successful for {user_data.email}")
        return {
            "message": "Registration successful",
            "user": {
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@app.get("/")
def root():
    """API root"""
    return {
        "message": "Flight Booking API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/airports")
def get_airports():
    """Get list of all airports with city information"""
    return [
        {
            "code": code,
            "city": info["city"],
            "country": info["country"],
            "name": info["name"]
        }
        for code, info in AIRPORTS.items()
    ]

@app.get("/airports/search")
def search_airports(query: str = Query(..., min_length=1)):
    """Search airports by city name or code"""
    query = query.lower()
    results = []
    
    for code, info in AIRPORTS.items():
        if (query in info["city"].lower() or 
            query in code.lower() or 
            query in info["country"].lower()):
            results.append({
                "code": code,
                "city": info["city"],
                "country": info["country"],
                "name": info["name"]
            })
    
    return results

@app.get("/flights")
def get_all_flights(
    sort_by: Optional[str] = Query("price"),
    limit: Optional[int] = Query(100, ge=1, le=500)
):
    """Get all flights"""
    result = flights_data.copy()
    
    if sort_by == "price":
        result.sort(key=lambda x: x["current_price"])
    elif sort_by == "duration":
        result.sort(key=lambda x: int(x["duration"].split('h')[0]) * 60 + 
                    int(x["duration"].split('h')[1].split('m')[0]))
    
    return result[:limit]

# The flight search endpoint is moved to app/routes/flights.py

#
# --- ERROR BLOCK REMOVED ---
# The entire flight search logic (120+ lines) that was here has been
# deleted, as it was not part of any function and caused the crash.
# This logic is correctly handled by your router:
# app.include_router(flights_router)
#

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.user_database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def send_cancellation_email(email: str, booking: dict) -> bool:
    """Send booking cancellation email"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")

        body = f"""
Dear {booking['passenger']['first_name']} {booking['passenger']['last_name']},

Your flight booking has been successfully cancelled.

CANCELLATION DETAILS
===================
Booking ID: {booking['booking_id']}
Flight: {booking['flight_id']}
Route: {booking['origin']} → {booking['destination']}
Departure: {booking['departure_time']}

REFUND INFORMATION
=================
Amount: ${booking['total_amount']:.2f}
Status: Processing
Expected Processing Time: 5-7 business days

Please note that the refund will be processed to the original payment method.
For any queries regarding your refund, please contact our support team.

We hope to serve you again in the future.

Best regards,
SkyBook Airlines Customer Service
        """

        if not sender_email or not sender_password:
            print("\n⚠️ SMTP credentials not configured")
            print("\n📧 CANCELLATION EMAIL (would be sent to):")
            print(f"To: {email}")
            print(f"Subject: Flight Booking Cancellation - {booking['booking_id']}")
            print(body)
            return False

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"Flight Booking Cancellation - {booking['booking_id']}"
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            
            print(f"✅ Cancellation email sent to: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending cancellation email: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str):
    """Cancel a booking and process refund"""
    try:
        # Find the booking
        booking = next((b for b in bookings_data if b["booking_id"] == booking_id), None)
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        # Check if booking can be cancelled
        if booking["booking_status"] != "confirmed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel booking with status: {booking['booking_status']}"
            )
            
        # Find the flight and increase available seats
        flight = next((f for f in flights_data if f["flight_id"] == booking["flight_id"]), None)
        if flight:
            flight["available_seats"] += 1
        
        # Update booking status
        booking["booking_status"] = "cancelled"
        booking["cancellation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send cancellation email
        send_cancellation_email(booking["passenger"]["email"], booking)
        
        # Remove booking from active bookings list
        bookings_data.remove(booking)
        
        return {
            "status": "success",
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "refund_amount": booking["total_amount"],
            "cancellation_date": booking["cancellation_date"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error cancelling booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while cancelling booking: {str(e)}"
        )

@app.get("/auth/user")
async def get_user_details(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get authenticated user details for autofill"""
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/flights/book", response_model=BookingResponse)
def book_flight(booking_request: BookingRequest):
    """Book a flight"""
    flight = next((f for f in flights_data if f["flight_id"] == booking_request.flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    if flight["available_seats"] <= 0:
        raise HTTPException(status_code=400, detail="No seats available")
    
    if not validate_payment(booking_request.payment):
        raise HTTPException(status_code=400, detail="Invalid payment details")
    
    booking_id = str(uuid.uuid4())
    confirmation_code = generate_confirmation_code()
    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    booking_record = {
        "booking_id": booking_id,
        "flight_id": booking_request.flight_id,
        "passenger": booking_request.passenger.dict(),
        "payment": booking_request.payment.dict(),
        "seat_preference": booking_request.seat_preference,
        "total_amount": flight["current_price"],
        "airline": flight.get("airline"),
        "departure_time": flight.get("departure_time"),
        "arrival_time": flight.get("arrival_time"),
        "origin": flight.get("origin"),
        "destination": flight.get("destination"),
        "origin_city": flight.get("origin_city"),
        "destination_city": flight.get("destination_city"),
        "duration": flight.get("duration"),
        "tier": flight.get("tier"),
        "booking_status": "confirmed",
        "confirmation_code": confirmation_code,
        "booking_date": booking_date
    }
    
    flight["available_seats"] -= 1
    bookings_data.append(booking_record)
    
    send_confirmation_email(booking_request.passenger.email, booking_record)
    
    return BookingResponse(
        booking_id=booking_id,
        flight_id=booking_request.flight_id,
        passenger_name=f"{booking_request.passenger.first_name} {booking_request.passenger.last_name}",
        email=booking_request.passenger.email,
        total_amount=flight["current_price"],
        booking_status="confirmed",
        confirmation_code=confirmation_code,
        booking_date=booking_date,
        flight_details={
            "airline": flight.get("airline"),
            "origin": flight.get("origin"),
            "destination": flight.get("destination"),
            "departure_time": flight.get("departure_time"),
            "arrival_time": flight.get("arrival_time"),
            "duration": flight.get("duration"),
            "tier": flight.get("tier")
        },
        passenger_details={
            "first_name": booking_request.passenger.first_name,
            "last_name": booking_request.passenger.last_name,
            "phone": booking_request.passenger.phone,
            "passport_number": booking_request.passenger.passport_number
        }
    )

@app.get("/flights/{flight_id}")
def get_flight(flight_id: str):
    """Get flight details"""
    flight = next((f for f in flights_data if f["flight_id"] == flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@app.get("/bookings")
def get_all_bookings():
    """Get all bookings"""
    try:
        print("\n📋 Fetching all bookings...")
        if not bookings_data:
            print("ℹ️ No bookings found in the system")
            return {
                "total_bookings": 0,
                "bookings": []
            }
            
        confirmed = len([b for b in bookings_data if b["booking_status"] == "confirmed"])
        print(f"✅ Found {len(bookings_data)} total bookings ({confirmed} confirmed)")
        
        return {
            "total_bookings": len(bookings_data),
            "confirmed_bookings": confirmed,
            "bookings": bookings_data
        }
    except Exception as e:
        print(f"❌ Error fetching bookings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching bookings"
        )

@app.get("/bookings/email/{email}")
def get_bookings_by_email(email: str):
    """Get all bookings for a specific email address"""
    try:
        print(f"\n🔍 Looking up bookings for email: {email}")
        
        # Input validation
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email address is required"
            )
        
        # Find all bookings for this email
        user_bookings = [
            booking for booking in bookings_data 
            if booking.get("passenger", {}).get("email", "").lower() == email.lower()
        ]
        
        if not user_bookings:
            print(f"❌ No bookings found for email: {email}")
            return {
                "status": "success",
                "message": "No bookings found for this email address",
                "bookings": []
            }
        
        print(f"✅ Found {len(user_bookings)} bookings for {email}")
        return {
            "status": "success",
            "message": f"Found {len(user_bookings)} bookings",
            "bookings": user_bookings
        }
        
    except Exception as e:
        print(f"❌ Error retrieving bookings for {email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving bookings: {str(e)}"
        )

@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get booking details"""
    try:
        # Verify user is authenticated
        current_user = await get_current_user(token, db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        print(f"\n🔍 Looking up booking: {booking_id}")
        
        # Input validation
        if not booking_id:
            raise HTTPException(
                status_code=400,
                detail="Booking ID is required"
            )
        
        # Find booking
        booking = next((b for b in bookings_data if b["booking_id"] == booking_id), None)
        
        if not booking:
            print(f"❌ Booking not found: {booking_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )

        # Verify user owns this booking
        user_email = current_user.get('email') if isinstance(current_user, dict) else current_user.email
        if booking["passenger"]["email"] != user_email:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this booking"
            )
        
        # Verify booking has required fields
        required_fields = ["booking_id", "flight_id", "passenger", "total_amount", "booking_status"]
        missing_fields = [field for field in required_fields if field not in booking]
        
        if missing_fields:
            print(f"⚠️ Booking data incomplete: missing {', '.join(missing_fields)}")
            raise HTTPException(
                status_code=500,
                detail="Booking data is incomplete or corrupted"
            )
        
        print(f"✅ Found booking {booking_id}")
        print(f"• Status: {booking['booking_status']}")
        print(f"• Flight: {booking['flight_id']}")
        print(f"• Passenger: {booking['passenger']['first_name']} {booking['passenger']['last_name']}")
        
        # Get associated flight details
        flight = next((f for f in flights_data if f["flight_id"] == booking["flight_id"]), None)
        
        if not flight:
            print(f"⚠️ Associated flight {booking['flight_id']} not found")
            # Still return booking but without flight details
            return {
                "booking": booking,
                "status": "success",
                "message": "Booking found successfully (flight details unavailable)"
            }
        
        # Merge flight details into booking
        booking_with_flight = {
            **booking,
            "flight_details": {
                "airline": flight.get("airline"),
                "origin": flight.get("origin"),
                "destination": flight.get("destination"),
                "departure_time": flight.get("departure_time"),
                "arrival_time": flight.get("arrival_time"),
                "duration": flight.get("duration"),
                "tier": flight.get("tier")
            }
        }
        
        return {
            "booking": booking_with_flight,
            "status": "success",
            "message": "Booking found successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving booking: {str(e)}"
        )

@app.get("/stats")
def get_statistics():
    """Get system statistics"""
    total_seats = sum(f["total_seats"] for f in flights_data)
    available_seats = sum(f["available_seats"] for f in flights_data)
    confirmed_bookings = len([b for b in bookings_data if b["booking_status"] == "confirmed"])
    total_revenue = sum(b["total_amount"] for b in bookings_data if b["booking_status"] == "confirmed")
    
    return {
        "total_flights": len(flights_data),
        "total_seats": total_seats,
        "available_seats": available_seats,
        "occupancy_rate": f"{((total_seats - available_seats) / total_seats * 100):.2f}%" if total_seats > 0 else "0%",
        "airports": len(set([f["origin"] for f in flights_data] + [f["destination"] for f in flights_data])),
        "total_bookings": len(bookings_data),
        "confirmed_bookings": confirmed_bookings,
        "total_revenue": f"${total_revenue:.2f}"
    }