from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
import hashlib
import binascii
import os
from app.user_database import get_db, User

# Configure JWT settings
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        salt, stored_hash = hashed_password.split('$')
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
            plain_password.encode('utf-8'), 
            salt.encode('ascii'), 
            100000,
            dklen=64
        )
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_hash
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2."""
    salt = os.urandom(16).hex()
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
        password.encode('utf-8'), 
        salt.encode('ascii'), 
        100000,
        dklen=64
    )
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return f"{salt}${pwdhash}"

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

async def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user from database using token."""
    email = verify_token(token)
    if not email:
        return None
        
    # Query the database for user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
        
    # Return user info without password
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone
    }