"""
Places API Module (Stub)
Integration with OpenTripMap for places and attractions
Note: Full implementation requires API key from OpenTripMap
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger

from config.settings import settings


class PlacesAPI:
    """OpenTripMap Places API integration."""
    
    def __init__(self):
        """Initialize Places API client."""
        self.base_url = "https://api.opentripmap.com/0.1/en/places"
        self.api_key = settings.OPENTRIPMAP_KEY
        self.timeout = settings.API_TIMEOUT_OPENTRIPMAP
    
    async def get_places(
        self,
        lat: float,
        lon: float,
        radius: int = 3000,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get places near a location.
        
        Args:
            lat: Latitude
            lon: Longitude  
            radius: Search radius in meters
            category: Optional category filter
            
        Returns:
            Places data dictionary
        """
        # Return mock data if no API key
        if not self.api_key:
            return self._get_mock_places(lat, lon, radius, category)
        
        try:
            params = {
                "radius": radius,
                "lon": lon,
                "lat": lat,
                "apikey": self.api_key,
                "limit": 20
            }
            
            if category:
                params["kinds"] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/radius",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"features": data.get("features", [])}
                    else:
                        logger.error(f"Places API error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Places API error: {str(e)}")
            return self._get_error_response()
    
    async def search_places(
        self,
        query: str,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """
        Search for places by query.
        
        Args:
            query: Search query
            lat: Latitude
            lon: Longitude
            
        Returns:
            Search results
        """
        # Extract category from query
        category = self._extract_category(query)
        return await self.get_places(lat, lon, category=category)
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract OpenTripMap category from query."""
        categories = {
            "restaurant": "catering",
            "museum": "museums",
            "park": "natural",
            "hotel": "accomodations",
            "shopping": "shops",
            "historic": "historic",
            "entertainment": "amusements"
        }
        
        query_lower = query.lower()
        for keyword, category in categories.items():
            if keyword in query_lower:
                return category
        
        return None
    
    def _get_mock_places(
        self,
        lat: float,
        lon: float,
        radius: int,
        category: Optional[str]
    ) -> Dict[str, Any]:
        """Get mock places data for testing."""
        return {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Eiffel Tower",
                        "categories": "historic,cultural,tourism",
                        "rate": 5,
                        "dist": 1200
                    },
                    "geometry": {
                        "coordinates": [2.2945, 48.8584]
                    }
                },
                {
                    "type": "Feature", 
                    "properties": {
                        "name": "Louvre Museum",
                        "categories": "museums,cultural,tourism",
                        "rate": 5,
                        "dist": 2500
                    },
                    "geometry": {
                        "coordinates": [2.3376, 48.8606]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Notre-Dame Cathedral",
                        "categories": "religion,historic,tourism",
                        "rate": 4,
                        "dist": 1800
                    },
                    "geometry": {
                        "coordinates": [2.3499, 48.8530]
                    }
                }
            ],
            "note": "Using mock data - configure OPENTRIPMAP_KEY for real data"
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Places data unavailable",
            "features": []
        }


# Export the API class
__all__ = ["PlacesAPI"]