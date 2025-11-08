"""
Itinerary MCP Server - Manages travel itineraries and trip planning
Uses FastMCP with stdio transport for efficient process management
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Initialize FastMCP server for itinerary management
mcp = FastMCP("travel-itinerary")


@mcp.tool()
async def create_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int = 1,
    preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new travel itinerary with basic trip information.
    
    Args:
        destination: Travel destination city/country
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        travelers: Number of travelers
        preferences: List of travel preferences (e.g., ['adventure', 'culture', 'food'])
    
    Returns:
        Dictionary containing the created itinerary
    """
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1
        
        # Create itinerary structure
        itinerary = {
            "id": f"itin_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration,
            "travelers": travelers,
            "preferences": preferences or [],
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "activities": [],
            "accommodations": [],
            "transportation": []
        }
        
        return {
            "success": True,
            "itinerary": itinerary,
            "message": f"Created {duration}-day itinerary for {destination}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create itinerary"
        }


@mcp.tool()
async def add_activity(
    itinerary_id: str,
    activity_name: str,
    date: str,
    time: str,
    duration_hours: float = 2.0,
    location: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add an activity to an existing itinerary.
    
    Args:
        itinerary_id: ID of the itinerary
        activity_name: Name of the activity
        date: Activity date (YYYY-MM-DD)
        time: Activity start time (HH:MM)
        duration_hours: Duration in hours
        location: Activity location/address
        notes: Additional notes
    
    Returns:
        Updated activity information
    """
    activity = {
        "id": f"act_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "itinerary_id": itinerary_id,
        "name": activity_name,
        "date": date,
        "time": time,
        "duration_hours": duration_hours,
        "location": location,
        "notes": notes,
        "added_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "activity": activity,
        "message": f"Added activity: {activity_name}"
    }


@mcp.tool()
async def suggest_activities(
    destination: str,
    preferences: List[str],
    duration_days: int = 3
) -> Dict[str, Any]:
    """
    Suggest activities based on destination and preferences.
    
    Args:
        destination: Travel destination
        preferences: List of travel preferences
        duration_days: Number of days for activities
    
    Returns:
        List of suggested activities
    """
    # Mock suggestions - in production, this would connect to real APIs
    suggestions = {
        "cultural": [
            "Visit local museums",
            "Historical walking tour",
            "Traditional craft workshop",
            "Local theater performance"
        ],
        "adventure": [
            "Hiking excursion",
            "Water sports",
            "Zip-lining",
            "Rock climbing"
        ],
        "food": [
            "Food market tour",
            "Cooking class",
            "Wine/beer tasting",
            "Restaurant crawl"
        ],
        "relaxation": [
            "Spa day",
            "Beach time",
            "Yoga session",
            "Sunset viewing"
        ]
    }
    
    # Filter based on preferences
    recommended = []
    for pref in preferences:
        if pref.lower() in suggestions:
            recommended.extend(suggestions[pref.lower()])
    
    # If no preferences match, provide general recommendations
    if not recommended:
        recommended = [
            f"Explore {destination} city center",
            "Visit top-rated local restaurants",
            "Take a guided tour",
            "Shop at local markets"
        ]
    
    return {
        "success": True,
        "destination": destination,
        "suggestions": recommended[:duration_days * 2],  # 2 activities per day
        "message": f"Generated {len(recommended)} activity suggestions"
    }


@mcp.tool()
async def optimize_schedule(
    itinerary_id: str,
    optimization_type: str = "distance"
) -> Dict[str, Any]:
    """
    Optimize the itinerary schedule based on various factors.
    
    Args:
        itinerary_id: ID of the itinerary to optimize
        optimization_type: Type of optimization ('distance', 'time', 'cost')
    
    Returns:
        Optimized schedule information
    """
    # Mock optimization - in production, would use routing algorithms
    optimizations = {
        "distance": "Activities reordered to minimize travel distance",
        "time": "Schedule adjusted to avoid peak hours and maximize efficiency",
        "cost": "Activities rearranged to take advantage of group discounts and off-peak pricing"
    }
    
    return {
        "success": True,
        "itinerary_id": itinerary_id,
        "optimization_type": optimization_type,
        "result": optimizations.get(optimization_type, "Standard optimization applied"),
        "savings": {
            "time_saved": "2.5 hours",
            "distance_saved": "45 km",
            "cost_saved": "$150"
        },
        "message": f"Itinerary optimized for {optimization_type}"
    }


@mcp.resource("itinerary://current")
async def get_current_itinerary() -> str:
    """
    Get the current active itinerary.
    
    Returns:
        JSON string of the current itinerary
    """
    # Mock current itinerary
    current = {
        "id": "itin_current",
        "destination": "Paris, France",
        "start_date": "2025-12-01",
        "end_date": "2025-12-07",
        "status": "active",
        "progress": "Day 2 of 7"
    }
    return json.dumps(current, indent=2)


@mcp.resource("itinerary://templates")
async def get_itinerary_templates() -> str:
    """
    Get available itinerary templates.
    
    Returns:
        JSON string of available templates
    """
    templates = [
        {
            "name": "Weekend City Break",
            "duration": 3,
            "style": "Urban exploration"
        },
        {
            "name": "Beach Vacation",
            "duration": 7,
            "style": "Relaxation"
        },
        {
            "name": "Cultural Immersion",
            "duration": 10,
            "style": "Educational"
        }
    ]
    return json.dumps(templates, indent=2)


# Main entry point for stdio server
if __name__ == "__main__":
    # Run the FastMCP server with stdio transport
    mcp.run(transport="stdio")
