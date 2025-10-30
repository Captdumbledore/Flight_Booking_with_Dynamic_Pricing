"""
Flight search request models
"""
from pydantic import BaseModel
from typing import Optional

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    date: str
    sort_by: Optional[str] = "price"