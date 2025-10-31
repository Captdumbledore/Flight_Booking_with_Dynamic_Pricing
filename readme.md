**# ✈️Flight Booking API - Dynamic Pricing System**



**A comprehensive REST API for flight booking with intelligent dynamic pricing, built with FastAPI.**



**## 🎯 Features**



**- ✅ REST APIs for flight management**

**- ✅ Advanced search by origin, destination, and date**

**- ✅ Dynamic pricing based on multiple factors**

**- ✅ Real-time seat availability**

**- ✅ Comprehensive API documentation (Swagger UI)**

**- ✅ Background demand simulation**



**## 🚀 Installation**



**### Prerequisites**

**- Python 3.9+**

**- pip**



**### Setup**



**1. \*\*Clone the repository\*\***

**```bash**

**git clone https://github.com/YOUR\_USERNAME/flight-booking-api.git**

**cd flight-booking-api**

**```**



**2. \*\*Create virtual environment\*\***

**```bash**

**python -m venv venv**

**```**



**3. \*\*Activate virtual environment\*\***

**```bash**

**# Windows**

**venv\\Scripts\\activate**



**# macOS/Linux**

**source venv/bin/activate**

**```**



**4. \*\*Install dependencies\*\***

**```bash**

**pip install fastapi uvicorn pydantic python-dotenv**

**```**



**5. \*\*Run the application\*\***

**```bash**

**python run.py**

**```**



**6. \*\*Access the API\*\***

**- API Documentation: http://localhost:8001/docs**

**- API Home: http://localhost:8001**

**- Statistics: http://localhost:8001/stats**



**## 📚 API Endpoints**



**- `GET /flights` - Get all flights**

**- `POST /flights/search` - Search flights by origin, destination, date**

**- `GET /flights/{flight\\\_id}` - Get specific flight details**

**- `GET /stats` - Get system statistics**



**## 🔧 Technology Stack**



**- \*\*Framework\*\*: FastAPI**

**- \*\*Server\*\*: Uvicorn**

**- \*\*Validation\*\*: Pydantic**

**- \*\*Language\*\*: Python 3.9+**



**## 📝 Example Usage**



**### Get All Flights**

**```bash**

**curl http://localhost:8001/flights?limit=5**

**```**



**### Search Flights**

**```bash**

**curl -X POST http://localhost:8001/flights/search \\**

**-H "Content-Type: application/json" \\**

**-d '{"origin":"JFK","destination":"LAX","date":"2025-10-20"}'**

**```**



**## 💡 Dynamic Pricing**



**The pricing engine considers:**

**- Seat availability (scarcity pricing)**

**- Time until departure (urgency pricing)**

**- Demand levels (market pricing)**

**- Base fare and pricing tiers**



**## 📄 License**



**This project is for educational purposes.**



**## 👨‍💻 Author**



**Your Name - Captdumbledore**

