
A comprehensive REST API for flight booking with intelligent dynamic pricing, built with FastAPI.

## 🎯 Features

### ✅ Complete Implementation

1. **REST APIs** - Full CRUD operations for flights
2. **Advanced Search** - Filter by origin, destination, and date
3. **Input Validation** - Robust Pydantic models with validators
4. **Flexible Sorting** - By price or duration
5. **Airline API Simulation** - Generates realistic flight schedules
6. **Dynamic Pricing Engine** with 4 factors:
   - 💺 Remaining seat percentage (scarcity pricing)
   - ⏰ Time until departure (urgency pricing)
   - 📈 Simulated demand levels (market pricing)
   - 💰 Base fare and pricing tiers
7. **Integrated Pricing** - Real-time dynamic price calculations
8. **Background Simulation** - Automatic demand/availability changes
9. **Fare History Tracking** - Complete price change history

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env if needed
```

4. **Run the server**
```bash
python run.py
```

The API will be available at:
- 🌐 **Main API**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs
- 🔍 **ReDoc**: http://localhost:8000/redoc

## 🚀 API Endpoints

### 1. Get All Flights
```bash
GET /flights?sort_by=price&limit=100

# Example
curl "http://localhost:8000/flights?sort_by=price&limit=10"
```

**Query Parameters:**
- `sort_by`: `price` or `duration` (default: `price`)
- `limit`: Max results 1-500 (default: `100`)

### 2. Search Flights
```bash
POST /flights/search

# Example
curl -X POST http://localhost:8000/flights/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX",
    "date": "2025-10-20",
    "sort_by": "price"
  }'
```

**Request Body:**
```json
{
  "origin": "JFK",
  "destination": "LAX",
  "date": "2025-10-20",
  "sort_by": "price"
}
```

### 3. Get Flight Details
```bash
GET /flights/{flight_id}

# Example
curl http://localhost:8000/flights/FL0001
```

### 4. Get Fare History
```bash
GET /flights/{flight_id}/fare-history?limit=50

# Example
curl http://localhost:8000/flights/FL0001/fare-history
```

### 5. Get Statistics
```bash
GET /stats

# Example
curl http://localhost:8000/stats
```

## 💡 Response Examples

### Flight Response
```json
{
  "flight_id": "FL0001",
  "airline": "SkyHigh Airways",
  "origin": "JFK",
  "destination": "LAX",
  "departure_time": "2025-10-20 08:00",
  "arrival_time": "2025-10-20 13:30",
  "duration": "5h 30m",
  "current_price": 387.50,
  "base_fare": 300.00,
  "available_seats": 45,
  "total_seats": 180,
  "tier": "economy",
  "demand_level": "high"
}
```

### Fare History Response
```json
{
  "flight_id": "FL0001",
  "airline": "SkyHigh Airways",
  "route": "JFK -> LAX",
  "departure_time": "2025-10-20 08:00",
  "base_fare": 300.00,
  "history_entries": 15,
  "history": [
    {
      "timestamp": "2025-10-18T10:30:00",
      "price": 387.50,
      "available_seats": 45,
      "demand_level": "high"
    }
  ]
}
```

## 🎨 Dynamic Pricing Logic

### Pricing Factors

1. **Seat Availability (Scarcity)**
   - More occupied → Higher price
   - Up to 80% increase when nearly full

2. **Time Until Departure (Urgency)**
   - < 24 hours: 1.5x multiplier
   - < 72 hours: 1.3x multiplier
   - < 7 days: 1.1x multiplier
   - > 30 days: 0.9x multiplier (early bird discount)

3. **Demand Level (Market)**
   - Low: 0.85x multiplier
   - Medium: 1.0x multiplier
   - High: 1.25x multiplier
   - Very High: 1.6x multiplier

4. **Base Fare & Tier**
   - Economy: 1.0x base
   - Premium: 1.5x base
   - Business: 2.5x base
   - First: 4.0x base

### Price Formula
```
Final Price = Base Fare × Availability Multiplier × Time Multiplier × Demand Multiplier
```

**Minimum Price**: Always ≥ 50% of base fare

## 🔄 Background Simulation

The system automatically simulates:
- **Random Bookings**: 20% chance per cycle (every 30s)
- **Demand Changes**: 10% chance per cycle
- **Fare History**: Automatic tracking of all changes

## 🧪 Testing

Run the test suite:
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_flights.py
```

## 📊 Available Data

### Airlines (8)
- SkyHigh Airways
- CloudNine Air
- Horizon Airlines
- Velocity Air
- Tranquil Jets
- Pacific Wings
- Atlantic Express
- Continental Connect

### Airports (18)
JFK, LAX, ORD, DFW, ATL, DEN, SFO, LAS, MIA, SEA, BOS, IAH, PHX, MCO, EWR, MSP, DTW, PHL

### Pricing Tiers
- Economy
- Premium Economy
- Business Class
- First Class

### Demand Levels
- Low
- Medium
- High
- Very High

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│          FastAPI Application               │
│  ┌─────────────────────────────────────┐   │
│  │      API Routes                     │   │
│  │  • GET /flights                     │   │
│  │  • POST /flights/search             │   │
│  │  • GET /flights/{id}                │   │
│  │  • GET /flights/{id}/fare-history   │   │
│  └─────────────────────────────────────┘   │
│                    ↓                       │
│  ┌─────────────────────────────────────┐   │
│  │   Dynamic Pricing Engine            │   │
│  │  • Seat availability calculation    │   │
│  │  • Time-based pricing               │   │
│  │  • Demand level analysis            │   │
│  └─────────────────────────────────────┘   │
│                    ↓                       │
│  ┌─────────────────────────────────────┐   │
│  │      In-Memory Database             │   │
│  │  • Flights storage                  │   │
│  │  • Fare history                     │   │
│  │  • Demand levels                    │   │
│  └─────────────────────────────────────┘   │
│                    ↑                       │
│  ┌─────────────────────────────────────┐   │
│  │   Background Simulator              │   │
│  │  • Booking simulation               │   │
│  │  • Demand changes                   │   │
│  │  • Fare tracking                    │   │
│  └─────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## 📁 Project Structure

```
flight-booking-api/
│
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app & startup logic
│   ├── models.py                # Pydantic models
│   ├── database.py              # In-memory database
│   ├── pricing.py               # Dynamic pricing engine
│   ├── simulator.py             # Airline API & demand simulator
│   └── routes/
│       ├── __init__.py          # Routes package
│       └── flights.py           # Flight endpoints
│
├── tests/
│   ├── __init__.py              # Test package
│   ├── test_flights.py          # Flight API tests
│   └── test_pricing.py          # Pricing logic tests
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
└── run.py                       # Application entry point
```

## 🔧 Configuration

Create a `.env` file to customize settings:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Simulation Settings
SIMULATION_INTERVAL=30
DAYS_AHEAD=30
```

## 🌟 Features Highlights

### ✨ Smart Pricing
- Real-time dynamic pricing based on multiple factors
- Prevents prices from dropping below 50% of base fare
- Automatic price adjustments as seats are booked

### 🔍 Powerful Search
- Filter by origin, destination, and date
- Flexible sorting options
- Input validation with helpful error messages

### 📈 Live Simulation
- Continuous background process simulating real bookings
- Automatic demand level updates
- Fare history tracking for price trends

### 🚀 Performance
- Fast in-memory database
- Efficient async operations
- Handles hundreds of flights seamlessly

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in .env file
PORT=8001

# Or specify when running
uvicorn app.main:app --port 8001
```

### Import Errors
```bash
# Ensure you're in the project root
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### No Flights Returned
- Check if your search date is in the future
- Verify airport codes are 3 letters (e.g., JFK, not KJFK)
- The system generates flights for 30 days ahead

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing
  - Request/response examples
  - Schema definitions

- **ReDoc**: http://localhost:8000/redoc
  - Clean, readable documentation
  - Comprehensive API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

## 🔗 Related Projects

- Extend with database (PostgreSQL, MongoDB)
- Add user authentication (JWT)
- Implement booking/payment system
- Add email notifications
- Create frontend application

## 📞 Support

For issues, questions, or suggestions:
- Open an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

---

**Built with ❤️ using FastAPI**

*Happy Flying! ✈️*
```

---

## 📄 Additional Files

### File: `requirements.txt`

```txt
# FastAPI Framework
fastapi==0.104.1

# ASGI Server
uvicorn[standard]==0.24.0

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Environment Variables
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.1

# Type Hints
typing-extensions==4.8.0

# Optional: Production Server
# gunicorn==21.2.0

# Optional: Database (if extending)
# sqlalchemy==2.0.23
# psycopg2-binary==2.9.9
# asyncpg==0.29.0
```

---

### File: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# OS
Thumbs.db
```

---

### File: `docker-compose.yml` (Optional - For Docker Deployment)

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: flight-booking-api
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=True
    volumes:
      - ./app:/app/app
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### File: `Dockerfile` (Optional - For Docker Deployment)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run.py"]
```

---

## 🚀 Quick Start Guide

### Option 1: Standard Setup

```bash
# 1. Create project directory
mkdir flight-booking-api
cd flight-booking-api

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python run.py
```

### Option 2: Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or with Docker only
docker build -t flight-api .
docker run -p 8000:8000 flight-api
```

### Option 3: Development Mode

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📥 Download Instructions

To get this project as a downloadable file:

1. **Copy all files** into your project directory following the structure above
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run the application**: `python run.py`
4. **Access the API**: http://localhost:8000/docs