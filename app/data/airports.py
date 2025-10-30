"""
Airport and airline data
"""

# AIRLINE CODE TO NAME MAPPING (IATA codes)
AIRLINE_NAMES = {
    "AA": "American Airlines", "DL": "Delta Air Lines", "UA": "United Airlines",
    "WN": "Southwest Airlines", "B6": "JetBlue Airways", "AS": "Alaska Airlines",
    "NK": "Spirit Airlines", "F9": "Frontier Airlines", "HA": "Hawaiian Airlines",
    "G4": "Allegiant Air", "SY": "Sun Country Airlines", "VX": "Virgin America",
    "BA": "British Airways", "LH": "Lufthansa", "AF": "Air France",
    "KL": "KLM Royal Dutch Airlines", "IB": "Iberia", "AZ": "ITA Airways",
    "LX": "Swiss International Air Lines", "OS": "Austrian Airlines", "SN": "Brussels Airlines",
    "EI": "Aer Lingus", "SK": "Scandinavian Airlines", "AY": "Finnair",
    "TP": "TAP Air Portugal", "EK": "Emirates", "QR": "Qatar Airways",
    "EY": "Etihad Airways", "SV": "Saudia", "MS": "EgyptAir",
    "TK": "Turkish Airlines", "JL": "Japan Airlines", "NH": "All Nippon Airways",
    "KE": "Korean Air", "OZ": "Asiana Airlines", "CA": "Air China",
    "MU": "China Eastern Airlines", "CZ": "China Southern Airlines", "SQ": "Singapore Airlines",
    "TG": "Thai Airways", "MH": "Malaysia Airlines", "AI": "Air India",
    "9W": "Jet Airways", "QF": "Qantas", "NZ": "Air New Zealand",
    "LA": "LATAM Airlines", "AM": "Aeroméxico", "CM": "Copa Airlines",
    "AV": "Avianca", "AR": "Aerolíneas Argentinas", "SA": "South African Airways",
    "ET": "Ethiopian Airlines", "KQ": "Kenya Airways", "U2": "easyJet",
    "FR": "Ryanair", "W6": "Wizz Air", "VY": "Vueling", "U9": "Tatarstan Airlines",
    "HU": "Hainan Airlines", "3U": "Sichuan Airlines", "MF": "Xiamen Airlines"
}

# AIRPORT CODE TO CITY/COUNTRY MAPPING
AIRPORTS = {
    # USA
    "ATL": {"city": "Atlanta", "country": "USA", "name": "Hartsfield-Jackson Atlanta International Airport"},
    "LAX": {"city": "Los Angeles", "country": "USA", "name": "Los Angeles International Airport"},
    "ORD": {"city": "Chicago", "country": "USA", "name": "O'Hare International Airport"},
    "DFW": {"city": "Dallas", "country": "USA", "name": "Dallas/Fort Worth International Airport"},
    "DEN": {"city": "Denver", "country": "USA", "name": "Denver International Airport"},
    "JFK": {"city": "New York", "country": "USA", "name": "John F. Kennedy International Airport"},
    "LAS": {"city": "Las Vegas", "country": "USA", "name": "Harry Reid International Airport"},
    "SEA": {"city": "Seattle", "country": "USA", "name": "Seattle-Tacoma International Airport"},
    "MIA": {"city": "Miami", "country": "USA", "name": "Miami International Airport"},
    "CLT": {"city": "Charlotte", "country": "USA", "name": "Charlotte Douglas International Airport"},
    "PHX": {"city": "Phoenix", "country": "USA", "name": "Phoenix Sky Harbor International Airport"},
    "EWR": {"city": "Newark", "country": "USA", "name": "Newark Liberty International Airport"},
    "MCO": {"city": "Orlando", "country": "USA", "name": "Orlando International Airport"},
    "IAH": {"city": "Houston", "country": "USA", "name": "George Bush Intercontinental Airport"},
    "BOS": {"city": "Boston", "country": "USA", "name": "Logan International Airport"},
    "SFO": {"city": "San Francisco", "country": "USA", "name": "San Francisco International Airport"},
    
    # Europe
    "LHR": {"city": "London", "country": "UK", "name": "Heathrow Airport"},
    "CDG": {"city": "Paris", "country": "France", "name": "Charles de Gaulle Airport"},
    "FRA": {"city": "Frankfurt", "country": "Germany", "name": "Frankfurt Airport"},
    "AMS": {"city": "Amsterdam", "country": "Netherlands", "name": "Schiphol Airport"},
    "MAD": {"city": "Madrid", "country": "Spain", "name": "Adolfo Suárez Madrid-Barajas Airport"},
    "BCN": {"city": "Barcelona", "country": "Spain", "name": "Barcelona-El Prat Airport"},
    "MXP": {"city": "Milan", "country": "Italy", "name": "Malpensa Airport"},
    "FCO": {"city": "Rome", "country": "Italy", "name": "Leonardo da Vinci-Fiumicino Airport"},
    "DUB": {"city": "Dublin", "country": "Ireland", "name": "Dublin Airport"},
    "ZRH": {"city": "Zurich", "country": "Switzerland", "name": "Zurich Airport"},
    "VIE": {"city": "Vienna", "country": "Austria", "name": "Vienna International Airport"},
    
    # Middle East
    "DXB": {"city": "Dubai", "country": "UAE", "name": "Dubai International Airport"},
    "DOH": {"city": "Doha", "country": "Qatar", "name": "Hamad International Airport"},
    "AUH": {"city": "Abu Dhabi", "country": "UAE", "name": "Abu Dhabi International Airport"},
    
    # Asia
    "HND": {"city": "Tokyo", "country": "Japan", "name": "Haneda Airport"},
    "NRT": {"city": "Tokyo", "country": "Japan", "name": "Narita International Airport"},
    "ICN": {"city": "Seoul", "country": "South Korea", "name": "Incheon International Airport"},
    "SIN": {"city": "Singapore", "country": "Singapore", "name": "Singapore Changi Airport"},
    "HKG": {"city": "Hong Kong", "country": "Hong Kong", "name": "Hong Kong International Airport"},
    "BKK": {"city": "Bangkok", "country": "Thailand", "name": "Suvarnabhumi Airport"},
    
    # India
    "DEL": {"city": "New Delhi", "country": "India", "name": "Indira Gandhi International Airport"},
    "BOM": {"city": "Mumbai", "country": "India", "name": "Chhatrapati Shivaji Maharaj International Airport"},
    "BLR": {"city": "Bengaluru", "country": "India", "name": "Kempegowda International Airport"},
    "HYD": {"city": "Hyderabad", "country": "India", "name": "Rajiv Gandhi International Airport"},
    "MAA": {"city": "Chennai", "country": "India", "name": "Chennai International Airport"},
    "CCU": {"city": "Kolkata", "country": "India", "name": "Netaji Subhas Chandra Bose International Airport"},
    "COK": {"city": "Kochi", "country": "India", "name": "Cochin International Airport"},
    "PNQ": {"city": "Pune", "country": "India", "name": "Pune Airport"},
    "AMD": {"city": "Ahmedabad", "country": "India", "name": "Sardar Vallabhbhai Patel International Airport"},
    "GOI": {"city": "Goa", "country": "India", "name": "Goa International Airport"},
    "TRV": {"city": "Thiruvananthapuram", "country": "India", "name": "Trivandrum International Airport"},
    "JAI": {"city": "Jaipur", "country": "India", "name": "Jaipur International Airport"},
    "LKO": {"city": "Lucknow", "country": "India", "name": "Chaudhary Charan Singh International Airport"},
    "IXC": {"city": "Chandigarh", "country": "India", "name": "Chandigarh International Airport"},
    "IXB": {"city": "Siliguri", "country": "India", "name": "Bagdogra International Airport"},
    "PAT": {"city": "Patna", "country": "India", "name": "Jay Prakash Narayan International Airport"},
    
    # Oceania
    "SYD": {"city": "Sydney", "country": "Australia", "name": "Sydney Kingsford Smith Airport"},
    "MEL": {"city": "Melbourne", "country": "Australia", "name": "Melbourne Airport"},
    "AKL": {"city": "Auckland", "country": "New Zealand", "name": "Auckland Airport"},
    
    # Latin America
    "GRU": {"city": "São Paulo", "country": "Brazil", "name": "São Paulo/Guarulhos International Airport"},
    "MEX": {"city": "Mexico City", "country": "Mexico", "name": "Mexico City International Airport"},
}

def get_airline_name(code: str) -> str:
    """Convert airline code to full name"""
    return AIRLINE_NAMES.get(code, code)

def get_airport_info(code: str) -> dict:
    """Get airport information"""
    return AIRPORTS.get(code, {"city": code, "country": "Unknown", "name": f"{code} Airport"})