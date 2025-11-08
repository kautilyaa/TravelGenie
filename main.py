"""
TravelGenie - AI-Powered Travel Assistant
Main FastAPI Application
Python 3.12+ Required
"""

import os
import sys
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import uvicorn
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import modules
from config.settings import settings
from modules.mcp_client import MCPClient
from modules.intent_detector import IntentDetector
from modules.places import PlacesAPI
from modules.weather import WeatherAPI
from modules.routing import RoutingAPI
from modules.images import ImagesAPI
from modules.events import EventsAPI
from modules.currency import CurrencyAPI
from modules.response_composer import ResponseComposer
from modules.profile import UserProfileManager

os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Configure logging
logger.add(
    "logs/travelgenie.log",
    rotation="10 MB",
    retention="7 days",
    level=settings.LOG_LEVEL
)

# Initialize components
mcp_client = MCPClient()
intent_detector = IntentDetector()
places_api = PlacesAPI()
weather_api = WeatherAPI()
routing_api = RoutingAPI()
images_api = ImagesAPI()
events_api = EventsAPI()
currency_api = CurrencyAPI()
response_composer = ResponseComposer()
profile_manager = UserProfileManager()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting TravelGenie API...")
    await mcp_client.initialize()
    logger.info("✅ TravelGenie API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TravelGenie API...")
    await mcp_client.close()
    logger.info("👋 TravelGenie API shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title="TravelGenie API",
    description="AI-Powered Travel Assistant with Free APIs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Query request model."""
    q: str = Field(..., description="User query in natural language")
    lat: Optional[float] = Field(48.8566, description="Latitude")
    lon: Optional[float] = Field(2.3522, description="Longitude")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class QueryResponse(BaseModel):
    """Query response model."""
    intent: str = Field(..., description="Detected intent")
    reply: str = Field(..., description="Natural language response")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    suggestions: Optional[list] = Field(None, description="Follow-up suggestions")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    services: Dict[str, bool] = Field(..., description="Service statuses")


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health and service status."""
    services = {
        "mcp": await mcp_client.is_connected(),
        "database": True,  # Add actual DB check
        "cache": True,     # Add actual cache check
    }
    
    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        version="1.0.0",
        services=services
    )


@app.get("/query", response_model=QueryResponse, tags=["Core"])
async def process_query(
    q: str = Query(..., description="User query"),
    lat: float = Query(48.8566, description="Latitude"),
    lon: float = Query(2.3522, description="Longitude"),
    user_id: Optional[str] = Query(None, description="User ID")
):
    """
    Process a natural language travel query.
    
    Examples:
    - "What's the weather in Paris?"
    - "Find museums near me"
    - "Plan a day trip in Tokyo"
    - "How to get from Louvre to Eiffel Tower?"
    """
    try:
        logger.info(f"Processing query: {q} at ({lat}, {lon})")
        
        # Detect intent
        intent = await intent_detector.detect(q)
        logger.info(f"Detected intent: {intent}")
        
        # Get user profile if available
        user_profile = None
        if user_id:
            user_profile = await profile_manager.get_profile(user_id)
        
        # Process based on intent
        data = {}
        
        if intent == "weather":
            data = await weather_api.get_weather(lat, lon)
            
        elif intent == "places":
            data = await places_api.search_places(q, lat, lon)
            
        elif intent == "route":
            # Extract destination from query (simplified)
            data = await routing_api.get_route(
                start=(lat, lon),
                end=(48.8606, 2.3376)  # Example: Louvre
            )
            
        elif intent == "events":
            data = await events_api.search_events(lat, lon)
            
        elif intent == "currency":
            data = await currency_api.get_exchange_rates()
            
        elif intent == "image":
            location = q.replace("photo of", "").replace("image of", "").strip()
            data = await images_api.get_image(location)
            
        elif intent == "plan_day":
            # Complex intent - use MCP for intelligent planning
            context = {
                "location": (lat, lon),
                "query": q,
                "user_profile": user_profile
            }
            data = await mcp_client.plan_itinerary(context)
            
        else:
            # Default: Use MCP for general queries
            data = await mcp_client.process_query(q, lat, lon)
        
        # Compose response
        reply = await response_composer.compose(intent, data, q)
        
        # Generate suggestions
        suggestions = await response_composer.generate_suggestions(intent, data)
        
        return QueryResponse(
            intent=intent,
            reply=reply,
            data=data if settings.DEBUG else None,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", tags=["User"])
async def submit_feedback(
    query_id: str,
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = None
):
    """Submit feedback for a query response."""
    # Store feedback for improvement
    logger.info(f"Feedback received: {rating}/5 for query {query_id}")
    return {"status": "success", "message": "Thank you for your feedback!"}


@app.get("/places", tags=["Direct APIs"])
async def get_places(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: int = Query(3000, description="Search radius in meters"),
    category: Optional[str] = Query(None, description="Place category")
):
    """Direct access to places API."""
    return await places_api.get_places(lat, lon, radius, category)


@app.get("/weather", tags=["Direct APIs"])
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Direct access to weather API."""
    return await weather_api.get_weather(lat, lon)


@app.get("/events", tags=["Direct APIs"])
async def get_events(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: int = Query(10, description="Search radius in km")
):
    """Direct access to events API."""
    return await events_api.search_events(lat, lon, radius)


@app.get("/", tags=["System"])
async def root():
    """API root endpoint."""
    return {
        "name": "TravelGenie API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
        "health": "/health"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )