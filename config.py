import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') 
    SESSION_TYPE = 'filesystem'  
    SESSION_PERMANENT = False  # If True, makes the session last indefinitely. Default is 31 days
 
