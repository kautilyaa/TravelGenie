"""
Maps MCP Server - Handles location services and geographical data
Uses FastMCP with stdio transport for efficient process management
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Any
from fastmcp import FastMCP

# Initialize FastMCP server for maps and location services
mcp = FastMCP("travel-maps")


@mcp.tool()
async def get_location_info(
    location: str,
    include_nearby: bool = False
) -> Dict[str, Any]:
    """
    Get detailed information about a location.
    
    Args:
        location: Name or address of the location
        include_nearby: Include nearby points of interest
    
    Returns:
        Location information including coordinates and details
    """
    # Mock location data - in production, would use real geocoding API
    mock_locations = {
        "Paris, France": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "country": "France",
            "region": "Île-de-France",
            "timezone": "Europe/Paris",
            "population": "2.2 million"
        },
        "Tokyo, Japan": {
            "latitude": 35.6762,
            "longitude": 139.6503,
            "country": "Japan",
            "region": "Kantō",
            "timezone": "Asia/Tokyo",
            "population": "14 million"
        },
        "New York, USA": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "country": "United States",
            "region": "New York",
            "timezone": "America/New_York",
            "population": "8.3 million"
        }
    }
    
    # Find closest match
    location_key = None
    for key in mock_locations:
        if location.lower() in key.lower():
            location_key = key
            break
    
    if not location_key:
        # Default location data
        location_data = {
            "latitude": 0.0,
            "longitude": 0.0,
            "country": "Unknown",
            "region": "Unknown",
            "timezone": "UTC",
            "population": "Unknown"
        }
    else:
        location_data = mock_locations[location_key]
    
    result = {
        "success": True,
        "location": location,
        "details": location_data
    }
    
    if include_nearby:
        result["nearby_attractions"] = [
            "Historical monument - 0.5 km",
            "Museum - 1.2 km",
            "Park - 0.8 km",
            "Shopping district - 2.0 km"
        ]
    
    return result


@mcp.tool()
async def calculate_distance(
    origin: str,
    destination: str,
    unit: str = "km"
) -> Dict[str, Any]:
    """
    Calculate distance between two locations.
    
    Args:
        origin: Starting location
        destination: End location
        unit: Unit of measurement ('km' or 'miles')
    
    Returns:
        Distance information between locations
    """
    # Mock calculation using Haversine formula
    # In production, would use real geocoding and routing APIs
    
    # Sample coordinates (would be fetched from geocoding API)
    coords = {
        "paris": (48.8566, 2.3522),
        "london": (51.5074, -0.1278),
        "rome": (41.9028, 12.4964),
        "berlin": (52.5200, 13.4050)
    }
    
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    # Find coordinates for origin and destination
    origin_key = origin.lower().split(',')[0].strip()
    dest_key = destination.lower().split(',')[0].strip()
    
    if origin_key in coords and dest_key in coords:
        lat1, lon1 = coords[origin_key]
        lat2, lon2 = coords[dest_key]
        distance_km = haversine(lat1, lon1, lat2, lon2)
    else:
        # Default distance for unknown locations
        distance_km = 500  # Mock value
    
    distance_miles = distance_km * 0.621371
    
    return {
        "success": True,
        "origin": origin,
        "destination": destination,
        "distance": {
            "kilometers": round(distance_km, 2),
            "miles": round(distance_miles, 2)
        },
        "estimated_travel_time": {
            "driving": f"{round(distance_km / 80, 1)} hours",
            "train": f"{round(distance_km / 150, 1)} hours",
            "flight": f"{round(distance_km / 800 + 2, 1)} hours"  # +2 for airport time
        },
        "unit": unit,
        "value": round(distance_km if unit == "km" else distance_miles, 2)
    }


@mcp.tool()
async def get_route(
    origin: str,
    destination: str,
    waypoints: Optional[List[str]] = None,
    mode: str = "driving"
) -> Dict[str, Any]:
    """
    Get route information between locations.
    
    Args:
        origin: Starting point
        destination: End point
        waypoints: Optional intermediate stops
        mode: Transportation mode ('driving', 'walking', 'transit', 'cycling')
    
    Returns:
        Route information with directions
    """
    # Mock route data - in production, would use real routing API
    route_info = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "waypoints": waypoints or [],
        "total_distance": "342 km",
        "total_duration": "4h 15min",
        "steps": [
            {
                "instruction": f"Start from {origin}",
                "distance": "0 km",
                "duration": "0 min"
            },
            {
                "instruction": "Take highway A1 North",
                "distance": "150 km",
                "duration": "1h 45min"
            }
        ]
    }
    
    # Add waypoint steps if provided
    if waypoints:
        for i, waypoint in enumerate(waypoints):
            route_info["steps"].append({
                "instruction": f"Stop at {waypoint}",
                "distance": f"{50 * (i + 1)} km",
                "duration": f"{30 * (i + 1)} min"
            })
    
    route_info["steps"].append({
        "instruction": f"Arrive at {destination}",
        "distance": "342 km",
        "duration": "4h 15min"
    })
    
    return {
        "success": True,
        "route": route_info,
        "alternative_routes": [
            {
                "name": "Scenic route",
                "distance": "385 km",
                "duration": "5h 30min",
                "highlights": ["Mountain views", "Historic towns"]
            },
            {
                "name": "Fastest route",
                "distance": "325 km",
                "duration": "3h 45min",
                "tolls": "$45"
            }
        ]
    }


@mcp.tool()
async def find_nearby_places(
    location: str,
    category: str,
    radius_km: float = 5.0,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find nearby places of a specific category.
    
    Args:
        location: Center location for search
        category: Category of places ('restaurant', 'hotel', 'attraction', etc.)
        radius_km: Search radius in kilometers
        limit: Maximum number of results
    
    Returns:
        List of nearby places matching the category
    """
    # Mock nearby places - in production, would use Places API
    categories_map = {
        "restaurant": [
            {"name": "Le Bistro Local", "rating": 4.5, "distance": "0.3 km", "price": "$$"},
            {"name": "Pasta Paradise", "rating": 4.2, "distance": "0.5 km", "price": "$$$"},
            {"name": "Street Food Market", "rating": 4.7, "distance": "0.8 km", "price": "$"},
            {"name": "Fine Dining Experience", "rating": 4.9, "distance": "1.2 km", "price": "$$$$"}
        ],
        "hotel": [
            {"name": "Grand Hotel", "rating": 4.6, "distance": "0.2 km", "stars": 5},
            {"name": "Budget Inn", "rating": 3.8, "distance": "0.7 km", "stars": 2},
            {"name": "Boutique Suites", "rating": 4.4, "distance": "1.0 km", "stars": 4},
            {"name": "Hostel Central", "rating": 4.1, "distance": "0.4 km", "stars": 2}
        ],
        "attraction": [
            {"name": "Historic Museum", "rating": 4.7, "distance": "0.5 km", "type": "museum"},
            {"name": "City Park", "rating": 4.3, "distance": "0.3 km", "type": "park"},
            {"name": "Art Gallery", "rating": 4.5, "distance": "1.1 km", "type": "gallery"},
            {"name": "Famous Monument", "rating": 4.8, "distance": "0.9 km", "type": "landmark"}
        ],
        "shopping": [
            {"name": "Main Shopping Street", "rating": 4.2, "distance": "0.4 km", "type": "street"},
            {"name": "Local Market", "rating": 4.6, "distance": "0.6 km", "type": "market"},
            {"name": "Shopping Mall", "rating": 3.9, "distance": "2.1 km", "type": "mall"},
            {"name": "Artisan Shops", "rating": 4.4, "distance": "0.8 km", "type": "boutique"}
        ]
    }
    
    places = categories_map.get(category.lower(), [])
    
    # Filter by radius
    filtered_places = []
    for place in places:
        distance_str = place.get("distance", "0 km")
        distance = float(distance_str.replace(" km", ""))
        if distance <= radius_km:
            filtered_places.append(place)
    
    # Limit results
    filtered_places = filtered_places[:limit]
    
    return {
        "success": True,
        "location": location,
        "category": category,
        "radius_km": radius_km,
        "places_found": len(filtered_places),
        "places": filtered_places
    }


@mcp.tool()
async def get_weather_forecast(
    location: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get weather forecast for a location.
    
    Args:
        location: Location for weather forecast
        days: Number of days to forecast (max 14)
    
    Returns:
        Weather forecast information
    """
    # Mock weather data - in production, would use weather API
    import random
    
    forecast = []
    for i in range(min(days, 14)):
        day_forecast = {
            "day": i + 1,
            "date": f"2025-12-{1 + i:02d}",
            "temperature": {
                "high": random.randint(15, 30),
                "low": random.randint(5, 15)
            },
            "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]),
            "precipitation": f"{random.randint(0, 60)}%",
            "humidity": f"{random.randint(40, 80)}%",
            "wind": f"{random.randint(5, 25)} km/h"
        }
        forecast.append(day_forecast)
    
    return {
        "success": True,
        "location": location,
        "forecast_days": len(forecast),
        "forecast": forecast,
        "summary": f"{days}-day forecast for {location}"
    }


@mcp.resource("maps://current-location")
async def get_current_location() -> str:
    """
    Get the current user location.
    
    Returns:
        JSON string of current location
    """
    # Mock current location
    current = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "accuracy": "high",
        "city": "New York",
        "country": "USA",
        "timestamp": "2025-11-08T10:30:00Z"
    }
    return json.dumps(current, indent=2)


# Main entry point for stdio server
if __name__ == "__main__":
    # Run the FastMCP server with stdio transport
    mcp.run(transport="stdio")
