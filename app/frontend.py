"""
FastAPI main application file
"""

import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Create FastAPI app for static files
app = FastAPI(title="Flight Booking Frontend")

# Get the frontend directory path
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Mount static files
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def get_index():
    """Serve the index.html file"""
    try:
        index_path = os.path.join(frontend_dir, "index.html")
        return FileResponse(index_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/login")
async def get_login():
    """Serve the login.html file"""
    try:
        login_path = os.path.join(frontend_dir, "login.html")
        return FileResponse(login_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/register")
async def get_register():
    """Serve the register.html file"""
    try:
        register_path = os.path.join(frontend_dir, "register.html")
        return FileResponse(register_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))