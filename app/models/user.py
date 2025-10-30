from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base User schema with common attributes"""
    email: EmailStr
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)


class UserCreate(UserBase):
    """Schema for user creation/registration"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response without sensitive data"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Internal User DB model with hashed password"""
    id: int
    hashed_password: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"