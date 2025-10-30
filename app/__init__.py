"""
Flight Booking API - A comprehensive flight booking system with dynamic pricing
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

__version__ = "1.0.0"
__author__ = "Flight Booking Team"