"""
Images API Module
Integration with Unsplash for location photos
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger

from config.settings import settings


class ImagesAPI:
    """Unsplash Images API integration."""
    
    def __init__(self):
        """Initialize Images API client."""
        self.base_url = "https://api.unsplash.com"
        self.api_key = settings.UNSPLASH_ACCESS_KEY
        self.timeout = settings.API_TIMEOUT_UNSPLASH
    
    async def get_image(
        self,
        location: str,
        orientation: str = "landscape"
    ) -> Dict[str, Any]:
        """
        Get image for a location.
        
        Args:
            location: Location name to search for
            orientation: Image orientation (landscape, portrait, squarish)
            
        Returns:
            Image data dictionary
        """
        if not self.api_key:
            return self._get_mock_image(location)
        
        try:
            params = {
                "query": location,
                "per_page": 1,
                "orientation": orientation
            }
            
            headers = {
                "Authorization": f"Client-ID {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search/photos",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_image_data(data, location)
                    else:
                        logger.error(f"Images API error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Images API error: {str(e)}")
            return self._get_error_response()
    
    async def get_random_travel_image(self) -> Dict[str, Any]:
        """Get a random travel-related image."""
        if not self.api_key:
            return self._get_mock_image("travel")
        
        try:
            headers = {
                "Authorization": f"Client-ID {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/photos/random",
                    params={"query": "travel", "orientation": "landscape"},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_single_image_data(data)
                    else:
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Random image API error: {str(e)}")
            return self._get_error_response()
    
    def _format_image_data(self, data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Format image search results."""
        try:
            results = data.get("results", [])
            if not results:
                return self._get_error_response()
            
            image = results[0]
            return self._format_single_image_data(image)
            
        except Exception as e:
            logger.error(f"Error formatting image data: {str(e)}")
            return self._get_error_response()
    
    def _format_single_image_data(self, image: Dict[str, Any]) -> Dict[str, Any]:
        """Format single image data."""
        try:
            urls = image.get("urls", {})
            user = image.get("user", {})
            
            return {
                "url": urls.get("regular", ""),
                "description": image.get("description", "Travel image"),
                "photographer": user.get("name", "Unknown"),
                "photographer_url": user.get("links", {}).get("html", ""),
                "download_url": urls.get("full", ""),
                "thumb_url": urls.get("thumb", ""),
                "alt_description": image.get("alt_description", "")
            }
            
        except Exception as e:
            logger.error(f"Error formatting single image: {str(e)}")
            return self._get_error_response()
    
    def _get_mock_image(self, location: str) -> Dict[str, Any]:
        """Get mock image data for testing."""
        return {
            "url": f"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
            "description": f"Beautiful view of {location}",
            "photographer": "Mock Photographer",
            "photographer_url": "https://unsplash.com/@mock",
            "download_url": f"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop",
            "thumb_url": f"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=150&fit=crop",
            "alt_description": f"Scenic view of {location}",
            "note": "Using mock data - configure UNSPLASH_ACCESS_KEY for real data"
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Image data unavailable",
            "url": "",
            "description": "No image available"
        }


# Export the API class
__all__ = ["ImagesAPI"]