"""
Routing API Module
Integration with OpenRouteService for directions and navigation
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger

from config.settings import settings


class RoutingAPI:
    """OpenRouteService Routing API integration."""
    
    def __init__(self):
        """Initialize Routing API client."""
        self.base_url = "https://api.openrouteservice.org/v2"
        self.api_key = settings.OPENROUTESERVICE_KEY
        self.timeout = settings.API_TIMEOUT_ROUTING
    
    async def get_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        profile: str = "driving-car"
    ) -> Dict[str, Any]:
        """
        Get route between two points.
        
        Args:
            start: (lat, lon) start coordinates
            end: (lat, lon) end coordinates
            profile: Routing profile (driving-car, walking, cycling)
            
        Returns:
            Route data dictionary
        """
        if not self.api_key:
            return self._get_mock_route(start, end, profile)
        
        try:
            start_lon, start_lat = start[1], start[0]
            end_lon, end_lat = end[1], end[0]
            
            url = f"{self.base_url}/directions/{profile}"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "coordinates": [[start_lon, start_lat], [end_lon, end_lat]],
                "format": "json",
                "instructions": True,
                "geometry": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_route_data(result)
                    else:
                        logger.error(f"Routing API error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Routing API error: {str(e)}")
            return self._get_error_response()
    
    async def get_directions(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        profile: str = "driving-car"
    ) -> Dict[str, Any]:
        """Get turn-by-turn directions."""
        route_data = await self.get_route(start, end, profile)
        
        if "error" in route_data:
            return route_data
        
        # Extract turn-by-turn instructions
        routes = route_data.get("routes", [])
        if routes:
            segments = routes[0].get("segments", [])
            if segments:
                steps = segments[0].get("steps", [])
                instructions = []
                
                for step in steps:
                    instructions.append({
                        "instruction": step.get("instruction", ""),
                        "distance": step.get("distance", 0),
                        "duration": step.get("duration", 0)
                    })
                
                route_data["instructions"] = instructions
        
        return route_data
    
    def _format_route_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format route data for response."""
        try:
            features = data.get("features", [])
            if not features:
                return self._get_error_response()
            
            route = features[0]
            properties = route.get("properties", {})
            summary = properties.get("summary", {})
            segments = properties.get("segments", [])
            
            return {
                "routes": [{
                    "summary": {
                        "distance": summary.get("distance", 0),
                        "duration": summary.get("duration", 0)
                    },
                    "segments": segments
                }],
                "geometry": route.get("geometry", {})
            }
            
        except Exception as e:
            logger.error(f"Error formatting route data: {str(e)}")
            return self._get_error_response()
    
    def _get_mock_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        profile: str
    ) -> Dict[str, Any]:
        """Get mock route data for testing."""
        return {
            "routes": [{
                "summary": {
                    "distance": 5000,  # 5km
                    "duration": 600   # 10 minutes
                },
                "segments": [{
                    "steps": [
                        {
                            "instruction": "Head north on Main Street",
                            "distance": 1000,
                            "duration": 120
                        },
                        {
                            "instruction": "Turn right onto Oak Avenue",
                            "distance": 2000,
                            "duration": 240
                        },
                        {
                            "instruction": "Continue straight to destination",
                            "distance": 2000,
                            "duration": 240
                        }
                    ]
                }]
            }],
            "note": "Using mock data - configure OPENROUTESERVICE_KEY for real data"
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Routing data unavailable",
            "routes": []
        }


# Export the API class
__all__ = ["RoutingAPI"]