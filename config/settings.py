"""
Configuration settings for TravelGenie
Loads environment variables and provides centralized config
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    ANTHROPIC_API_KEY: str = Field(..., description="Claude API key")
    OPENTRIPMAP_KEY: Optional[str] = Field(None, description="OpenTripMap API key")
    OPENROUTESERVICE_KEY: Optional[str] = Field(None, description="OpenRouteService API key")
    UNSPLASH_ACCESS_KEY: Optional[str] = Field(None, description="Unsplash API key")
    EVENTBRITE_TOKEN: Optional[str] = Field(None, description="Eventbrite token")
    
    # Optional Bot Tokens
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(None, description="Telegram bot token")
    DISCORD_BOT_TOKEN: Optional[str] = Field(None, description="Discord bot token")
    SLACK_BOT_TOKEN: Optional[str] = Field(None, description="Slack bot token")
    SLACK_APP_TOKEN: Optional[str] = Field(None, description="Slack app token")
    
    # Database
    DATABASE_URL: str = Field(
        "sqlite:///./data/travelgenie.db",
        description="Database connection URL"
    )
    
    # Application
    ENVIRONMENT: str = Field("development", description="Environment")
    DEBUG: bool = Field(True, description="Debug mode")
    HOST: str = Field("0.0.0.0", description="Host")
    PORT: int = Field(8000, description="Port")
    WORKERS: int = Field(1, description="Number of workers")
    
    # API Settings
    API_VERSION: str = Field("v1", description="API version")
    API_PREFIX: str = Field("/api/v1", description="API prefix")
    DOCS_URL: str = Field("/docs", description="Docs URL")
    
    # MCP Settings
    MCP_SERVER_URL: str = Field("http://localhost:8001", description="MCP server URL")
    MCP_TIMEOUT: int = Field(30, description="MCP timeout in seconds")
    MCP_MAX_RETRIES: int = Field(3, description="MCP max retries")
    MCP_RETRY_DELAY: int = Field(1, description="MCP retry delay")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, description="Rate limit per minute")
    RATE_LIMIT_PER_DAY: int = Field(1000, description="Rate limit per day")
    
    # Caching
    CACHE_BACKEND: str = Field("memory", description="Cache backend")
    REDIS_URL: Optional[str] = Field(None, description="Redis URL")
    CACHE_TTL: int = Field(3600, description="Cache TTL in seconds")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Log level")
    LOG_FILE: str = Field("logs/travelgenie.log", description="Log file path")
    LOG_MAX_SIZE: int = Field(10485760, description="Max log file size")
    LOG_BACKUP_COUNT: int = Field(5, description="Log backup count")
    
    # Security
    SECRET_KEY: str = Field(
        "your-secret-key-change-this-in-production",
        description="Secret key for JWT"
    )
    CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(True, description="Allow credentials")
    CORS_ALLOW_METHODS: List[str] = Field(["GET", "POST"], description="Allowed methods")
    CORS_ALLOW_HEADERS: List[str] = Field(["*"], description="Allowed headers")
    
    # Feature Flags
    ENABLE_CACHE: bool = Field(True, description="Enable caching")
    ENABLE_RATE_LIMITING: bool = Field(True, description="Enable rate limiting")
    ENABLE_USER_PROFILES: bool = Field(True, description="Enable user profiles")
    ENABLE_TRIP_PLANNING: bool = Field(True, description="Enable trip planning")
    ENABLE_VOICE_INPUT: bool = Field(False, description="Enable voice input")
    ENABLE_IMAGE_GENERATION: bool = Field(False, description="Enable image generation")
    
    # Default Location
    DEFAULT_LATITUDE: float = Field(48.8566, description="Default latitude (Paris)")
    DEFAULT_LONGITUDE: float = Field(2.3522, description="Default longitude (Paris)")
    DEFAULT_RADIUS: int = Field(5000, description="Default search radius in meters")
    
    # API Timeouts
    API_TIMEOUT_OPENTRIPMAP: int = Field(10, description="OpenTripMap timeout")
    API_TIMEOUT_WEATHER: int = Field(5, description="Weather API timeout")
    API_TIMEOUT_ROUTING: int = Field(15, description="Routing API timeout")
    API_TIMEOUT_UNSPLASH: int = Field(10, description="Unsplash timeout")
    API_TIMEOUT_EVENTBRITE: int = Field(10, description="Eventbrite timeout")
    API_TIMEOUT_CLAUDE: int = Field(30, description="Claude API timeout")
    

    # class Config:
    #     """Pydantic configuration."""
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    #     case_sensitive = True
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from env file
    }


# Create global settings instance
settings = Settings()

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)