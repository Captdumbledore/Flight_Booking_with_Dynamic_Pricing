"""
Application entry point
"""

import uvicorn

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        Flight Booking API - Dynamic Pricing System      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    🌐 Server: http://0.0.0.0:8001
    📚 Docs:   http://0.0.0.0:8001/docs
    🔍 ReDoc:  http://0.0.0.0:8001/redoc
    """)
    
    uvicorn.run(
        "main_standalone:app",  # Changed this line
        host="0.0.0.0",
        port=8001,
        reload=True
    )