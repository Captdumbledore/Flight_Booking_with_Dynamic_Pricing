
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    import uvicorn
    """
from fastapi import FastAPI
from app.main import app as api_app
from app.frontend import app as frontend_app

# Create a root FastAPI app
app = FastAPI()

# Mount both applications
app.mount("/api", api_app)
app.mount("/", frontend_app)

if __name__ == "__main__":
    import uvicorn
    print("""
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )