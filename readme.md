# ✈️ Flight Booking API - Dynamic Pricing System

A comprehensive REST API for flight booking with intelligent dynamic pricing, built using **FastAPI**.

---

## 🌐 Live Hosted Version

A live version of this project is available here:  
👉 **[https://dynamic-flight-booking-render-hosted.onrender.com](https://dynamic-flight-booking-render-hosted.onrender.com)**

> **Note:**  
> - The hosted version is deployed using a **copy** of this repository, available here:  
>   🔗 [https://github.com/Captdumbledore/Dynamic_flight_booking_render_hosted_version](https://github.com/Captdumbledore/Dynamic_flight_booking_render_hosted_version)  
> - SMTP (email) services are **disabled** due to limitations in Render’s free hosting tier.  
> - This repository represents the **original version** submitted for evaluation.

---

## 🎯 Features

- ✅ REST APIs for flight management  
- ✅ Advanced search by origin, destination, and date  
- ✅ Dynamic pricing based on multiple factors  
- ✅ Real-time seat availability  
- ✅ Comprehensive API documentation (Swagger UI)  
- ✅ Background demand simulation  

---

## 🚀 Installation

### Prerequisites
- Python 3.9+  
- pip  

---

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Captdumbledore/flight-booking-api.git
   cd flight-booking-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the API**
   - API Documentation: http://localhost:8001/docs  
   - API Home: http://localhost:8001  
   - Statistics: http://localhost:8001/stats  

---

## 📚 API Endpoints

| Method | Endpoint | Description |
|:-------|:----------|:-------------|
| **GET** | `/flights` | Get all available flights |
| **POST** | `/flights/search` | Search flights by origin, destination, and date |
| **GET** | `/flights/{flight_id}` | Get details of a specific flight |
| **GET** | `/stats` | Retrieve system statistics |

---

## 💡 Dynamic Pricing

The pricing engine dynamically adjusts fares based on several real-world factors:

- 🪑 **Seat Availability (Scarcity Pricing)** — Prices rise as seats fill up.  
- ⏱️ **Time Until Departure (Urgency Pricing)** — Prices increase closer to departure.  
- 📈 **Demand Levels (Market Pricing)** — High-demand routes are priced higher.  
- 💰 **Base Fare and Tier System** — Each route starts with a fixed base fare and adjusts per tier.

This model closely simulates real-world airline pricing logic.

---

## 🔧 Technology Stack

- **Framework:** FastAPI  
- **Server:** Uvicorn  
- **Validation:** Pydantic  
- **Language:** Python 3.9+  
- **Environment Management:** python-dotenv  
- **Hosting Platform:** Render  

---

## 🧪 Example Usage

### Get All Flights
```bash
curl http://localhost:8001/flights?limit=5
```

### Search Flights
```bash
curl -X POST http://localhost:8001/flights/search \
-H "Content-Type: application/json" \
-d '{"origin":"JFK","destination":"LAX","date":"2025-10-20"}'
```

---

## 🧰 Project Structure

```
flight-booking-api/
├── .env
├── run.py
├── app/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   ├── utils/
│   └── ...
├── requirements.txt
├── README.md
└── ...
```

---

## 🧾 License

This project is created **for educational purposes** and may be reused with proper attribution.

---

## 👨‍💻 Author

**Captdumbledore (Jisto Prakash)**  
🔗 [GitHub Profile](https://github.com/Captdumbledore)

---

## 🗒️ Acknowledgements

- [FastAPI Documentation](https://fastapi.tiangolo.com/)  
- [Render Deployment Guide](https://render.com/docs)  
- [Pydantic Documentation](https://docs.pydantic.dev/)  

---

> 💬 *“The sky is not the limit when your code can fly.”* ✈️
