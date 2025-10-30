"""
FastAPI main application file for serving frontend
"""

import os
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app for static files
app = FastAPI(title="Flight Booking Frontend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the frontend directory path
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Mount static files
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files"""
    if path == "" or path == "/":
        file_path = os.path.join(frontend_dir, "index.html")
    else:
        # Check if the file exists in the frontend directory
        file_path = os.path.join(frontend_dir, path)
        if not os.path.exists(file_path):
            # If file doesn't exist, serve index.html for client-side routing
            file_path = os.path.join(frontend_dir, "index.html")
    
    try:
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))