import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://docker:docker@localhost:5432/docker')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_APP = os.getenv('FLASK_APP', 'app')
    
    # API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    CORS_HEADERS = ['Content-Type', 'X-Session-Token']
    CORS_METHODS = ['GET', 'POST', 'OPTIONS']

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('__') and not callable(value)}
    