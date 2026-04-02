"""
Configuration - Load environment variables
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration from environment variables"""
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_TOKEN = os.getenv("REDIS_TOKEN")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # App
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Slack
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    
    @classmethod
    def has_database(cls) -> bool:
        """Check if database is configured"""
        return cls.DATABASE_URL is not None and cls.DATABASE_URL != "your_neon_connection_string_here"
    
    @classmethod
    def has_redis(cls) -> bool:
        """Check if Redis is configured"""
        return cls.REDIS_URL is not None and cls.REDIS_URL != "your_upstash_rest_url_here"