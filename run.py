
from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   Flight Booking API - PostgreSQL Database Version                    ║
    ║                                                                       ║
    ╚══════════════════════════════════════════════════════════╝
    
    🌐 Server: http://0.0.0.0:8001
    📚 Docs:   http://0.0.0.0:8001/docs
    🗄️ Database: PostgreSQL
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )