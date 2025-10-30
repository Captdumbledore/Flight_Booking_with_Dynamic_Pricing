"""Models package for the flight booking API"""
from app.models.user import UserBase, UserCreate, UserResponse, UserInDB, UserLogin, TokenResponse
from app.models.database import Base, User
from app.models.flight import (
    Flight, FlightResponse, SearchParams, SortBy,
    PricingTier, DemandLevel, FareHistoryEntry,
    FareHistoryResponse, StatsResponse
)

__all__ = [
    # User models
    "UserBase",
    "UserCreate", 
    "UserResponse",
    "UserInDB",
    "UserLogin",
    "TokenResponse",
    "Base",
    "User",

    # Flight models
    "Flight",
    "FlightResponse",
    "SearchParams",
    "SortBy",
    "PricingTier",
    "DemandLevel",
    "FareHistoryEntry",
    "FareHistoryResponse",
    "StatsResponse"
]