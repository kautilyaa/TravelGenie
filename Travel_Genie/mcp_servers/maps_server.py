"""
Maps MCP Server - Handles location services using OpenStreetMap (free)
Uses Nominatim for geocoding and OpenStreetMap for maps
"""

import json
import math
import requests
from typing import Dict, List, Optional, Tuple, Any
from fastmcp import FastMCP

# Initialize FastMCP server for maps and location services
mcp = FastMCP("travel-maps")

# OpenStreetMap Nominatim API (free, no key required)
NOMINATIM_API = "https://nominatim.openstreetmap.org"


@mcp.tool()
async def get_location_info(
    location: str,
    include_nearby: bool = False
) -> Dict[str, Any]:
    """
    Get detailed information about a location using OpenStreetMap Nominatim.
    
    Args:
        location: Name or address of the location
        include_nearby: Include nearby points of interest
    
    Returns:
        Location information including coordinates and details
    """
    try:
        # Use Nominatim API for geocoding (free, no API key needed)
        params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "TravelGenie/1.0"  # Required by Nominatim
        }
        
        response = requests.get(f"{NOMINATIM_API}/search", params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {
                "success": False,
                "error": "Location not found",
                "location": location
            }
        
        result_data = data[0]
        
        location_info = {
            "latitude": float(result_data["lat"]),
            "longitude": float(result_data["lon"]),
            "display_name": result_data.get("display_name", location),
            "address": result_data.get("address", {}),
            "country": result_data.get("address", {}).get("country", "Unknown"),
            "region": result_data.get("address", {}).get("state", "Unknown"),
        }
        
        result = {
            "success": True,
            "location": location,
            "details": location_info,
            "osm_id": result_data.get("osm_id"),
            "osm_type": result_data.get("osm_type")
        }
        
        if include_nearby:
            # Get nearby places using Overpass API (free)
            nearby = await _get_nearby_places(
                location_info["latitude"],
                location_info["longitude"]
            )
            result["nearby_attractions"] = nearby
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "location": location
        }


async def _get_nearby_places(lat: float, lon: float, radius: float = 1000) -> List[Dict]:
    """Get nearby places using Overpass API."""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"~"attraction|museum|monument"](around:{radius},{lat},{lon});
          node["amenity"~"restaurant|cafe"](around:{radius},{lat},{lon});
        );
        out body;
        """
        
        response = requests.post(overpass_url, data={"data": query})
        response.raise_for_status()
        data = response.json()
        
        places = []
        for element in data.get("elements", [])[:10]:
            places.append({
                "name": element.get("tags", {}).get("name", "Unknown"),
                "type": element.get("tags", {}).get("tourism") or element.get("tags", {}).get("amenity"),
                "distance": "~500m"  # Approximate
            })
        
        return places
    except:
        return []


@mcp.tool()
async def calculate_distance(
    origin: str,
    destination: str,
    unit: str = "km"
) -> Dict[str, Any]:
    """
    Calculate distance between two locations using Haversine formula.
    Uses OpenStreetMap for geocoding.
    """
    try:
        # Get coordinates for both locations
        origin_info = await get_location_info(origin)
        dest_info = await get_location_info(destination)
        
        if not origin_info.get("success") or not dest_info.get("success"):
            return {
                "success": False,
                "error": "Could not geocode one or both locations"
            }
        
        lat1 = origin_info["details"]["latitude"]
        lon1 = origin_info["details"]["longitude"]
        lat2 = dest_info["details"]["latitude"]
        lon2 = dest_info["details"]["longitude"]
        
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c
        
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
                "flight": f"{round(distance_km / 800 + 2, 1)} hours"
            },
            "unit": unit,
            "value": round(distance_km if unit == "km" else distance_miles, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def get_route(
    origin: str,
    destination: str,
    waypoints: Optional[List[str]] = None,
    mode: str = "driving"
) -> Dict[str, Any]:
    """
    Get route information using OpenRouteService (free tier available).
    Falls back to simple calculation if API unavailable.
    """
    try:
        # Get coordinates
        origin_info = await get_location_info(origin)
        dest_info = await get_location_info(destination)
        
        if not origin_info.get("success") or not dest_info.get("success"):
            return {"success": False, "error": "Could not geocode locations"}
        
        # Use OpenRouteService API (free tier: 2000 requests/day)
        # Alternative: Use OSRM (completely free, self-hosted or public instance)
        osrm_url = "https://router.project-osrm.org/route/v1"
        
        coords = f"{origin_info['details']['longitude']},{origin_info['details']['latitude']};{dest_info['details']['longitude']},{dest_info['details']['latitude']}"
        
        params = {
            "overview": "full",
            "geometries": "geojson"
        }
        
        response = requests.get(f"{osrm_url}/driving/{coords}", params=params)
        
        if response.status_code == 200:
            data = response.json()
            route = data["routes"][0]
            
            return {
                "success": True,
                "route": {
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "distance": f"{route['distance']/1000:.1f} km",
                    "duration": f"{route['duration']/60:.1f} minutes",
                    "geometry": route.get("geometry")
                }
            }
        else:
            # Fallback to simple calculation
            distance_result = await calculate_distance(origin, destination)
            return {
                "success": True,
                "route": {
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "total_distance": distance_result.get("distance", {}).get("kilometers", 0),
                    "estimated_duration": distance_result.get("estimated_travel_time", {}).get("driving", "Unknown")
                },
                "note": "Using estimated route (detailed routing unavailable)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_weather_forecast(
    location: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get weather forecast for a location.
    Uses free weather API (OpenWeatherMap requires API key, but you can use wttr.in as free alternative)
    """
    try:
        # Option 1: Use wttr.in (completely free, no API key)
        import requests
        
        # Get coordinates first
        location_info = await get_location_info(location)
        if not location_info.get("success"):
            return {"success": False, "error": "Location not found"}
        
        lat = location_info["details"]["latitude"]
        lon = location_info["details"]["longitude"]
        
        # Use wttr.in API (free, no key required)
        url = f"https://wttr.in/{lat},{lon}?format=j1"
        response = requests.get(url, headers={"User-Agent": "TravelGenie/1.0"})
        
        if response.status_code == 200:
            data = response.json()
            forecast = []
            
            for i, day in enumerate(data.get("weather", [])[:min(days, 3)]):
                forecast.append({
                    "day": i + 1,
                    "date": day.get("date", ""),
                    "temperature": {
                        "high": day.get("maxtempC", "N/A"),
                        "low": day.get("mintempC", "N/A")
                    },
                    "conditions": day.get("hourly", [{}])[0].get("weatherDesc", [{}])[0].get("value", "Unknown"),
                    "precipitation": f"{day.get('hourly', [{}])[0].get('precipMM', 0)}mm",
                })
            
            return {
                "success": True,
                "location": location,
                "forecast_days": len(forecast),
                "forecast": forecast
            }
        else:
            return {"success": False, "error": "Weather service unavailable"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Main entry point
if __name__ == "__main__":
    import os
    
    # Get transport type from environment or default to stdio
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    if transport in ["sse", "http"]:
        # Get host and port from environment
        host = os.getenv("MCP_HOST", "localhost")
        port = int(os.getenv("MCP_PORT", 8001))
        
        # Run with SSE transport on specified port
        mcp.run(transport="sse", host=host, port=port)
        print(f"Starting MCP server on {host}:{port} with {transport} transport")
    else:
        # Run with stdio transport (default, backward compatible)
        mcp.run(transport="stdio")
        port = os.getenv("MCP_PORT", "N/A")
        print(f"Starting MCP server with stdio transport (configured port: {port})")
