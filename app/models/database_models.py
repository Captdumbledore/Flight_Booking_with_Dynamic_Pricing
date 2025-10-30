from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flight(Base):
    """SQLAlchemy Flight model"""
    __tablename__ = "flights"

    flight_id = Column(String, primary_key=True, index=True)
    airline = Column(String, nullable=False)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    base_fare = Column(Integer, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)


class User(Base):
    """SQLAlchemy User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)