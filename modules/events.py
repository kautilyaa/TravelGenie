"""
Events API Module
Integration with Eventbrite for local events
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from loguru import logger

from config.settings import settings


class EventsAPI:
    """Eventbrite Events API integration."""
    
    def __init__(self):
        """Initialize Events API client."""
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.api_key = settings.EVENTBRITE_TOKEN
        self.timeout = settings.API_TIMEOUT_EVENTBRITE
    
    async def search_events(
        self,
        lat: float,
        lon: float,
        radius: int = 10,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Search for events near a location.
        
        Note: Eventbrite deprecated public location-based search in December 2019.
        This method returns mock data as the public search endpoint is no longer available.
        To access real Eventbrite events, use organization-specific endpoints.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in kilometers
            days_ahead: Number of days to look ahead
            
        Returns:
            Events data dictionary
        """
        if not self.api_key:
            return self._get_mock_events(lat, lon, radius)
        
        # Eventbrite deprecated the public /events/search/ endpoint in December 2019
        # The endpoint returns 404. Return mock data with an informative message.
        logger.warning(
            f"Eventbrite public search API is deprecated. "
            f"Returning mock data for location: {lat}, {lon}"
        )
        return self._get_mock_events(lat, lon, radius)
    
    async def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific event."""
        if not self.api_key:
            return self._get_mock_event_details(event_id)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/events/{event_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_event_details(data)
                    else:
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Event details API error: {str(e)}")
            return self._get_error_response()
    
    def _format_events_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format events search results."""
        try:
            events = data.get("events", [])
            formatted_events = []
            
            for event in events[:10]:  # Limit to 10 events
                formatted_event = {
                    "id": event.get("id", ""),
                    "name": event.get("name", {}).get("text", "Unnamed Event"),
                    "description": event.get("description", {}).get("text", ""),
                    "start": event.get("start", {}),
                    "end": event.get("end", {}),
                    "venue": event.get("venue", {}),
                    "is_free": event.get("is_free", False),
                    "url": event.get("url", ""),
                    "category": event.get("category", {}),
                    "subcategory": event.get("subcategory", {})
                }
                formatted_events.append(formatted_event)
            
            return {
                "events": formatted_events,
                "total": len(formatted_events)
            }
            
        except Exception as e:
            logger.error(f"Error formatting events data: {str(e)}")
            return self._get_error_response()
    
    def _format_event_details(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format detailed event information."""
        try:
            return {
                "id": event.get("id", ""),
                "name": event.get("name", {}).get("text", ""),
                "description": event.get("description", {}).get("text", ""),
                "start": event.get("start", {}),
                "end": event.get("end", {}),
                "venue": event.get("venue", {}),
                "is_free": event.get("is_free", False),
                "url": event.get("url", ""),
                "capacity": event.get("capacity"),
                "status": event.get("status", ""),
                "category": event.get("category", {}),
                "subcategory": event.get("subcategory", {}),
                "format": event.get("format", {}),
                "language": event.get("language", "")
            }
            
        except Exception as e:
            logger.error(f"Error formatting event details: {str(e)}")
            return self._get_error_response()
    
    def _get_mock_events(
        self,
        lat: float,
        lon: float,
        radius: int
    ) -> Dict[str, Any]:
        """
        Get mock events data for testing.
        
        Note: Eventbrite deprecated public location-based search in December 2019.
        This returns sample events as the public search API is no longer available.
        """
        return {
            "events": [
                {
                    "id": "mock_event_1",
                    "name": {"text": "Local Music Festival"},
                    "description": {"text": "A wonderful music festival featuring local artists"},
                    "start": {"local": "2024-02-15T18:00:00"},
                    "end": {"local": "2024-02-15T23:00:00"},
                    "venue": {"name": "Central Park"},
                    "is_free": True,
                    "url": "https://example.com/event1"
                },
                {
                    "id": "mock_event_2", 
                    "name": {"text": "Art Exhibition Opening"},
                    "description": {"text": "Contemporary art exhibition featuring local artists"},
                    "start": {"local": "2024-02-16T19:00:00"},
                    "end": {"local": "2024-02-16T21:00:00"},
                    "venue": {"name": "City Art Gallery"},
                    "is_free": False,
                    "url": "https://example.com/event2"
                }
            ],
            "total": 2,
            "note": "Eventbrite public location-based search is deprecated (as of Dec 2019). Using mock data. For real events, consider using alternative APIs or Eventbrite's organization-specific endpoints."
        }
    
    def _get_mock_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get mock event details."""
        return {
            "id": event_id,
            "name": {"text": "Sample Event"},
            "description": {"text": "This is a sample event description"},
            "start": {"local": "2024-02-15T18:00:00"},
            "end": {"local": "2024-02-15T23:00:00"},
            "venue": {"name": "Sample Venue"},
            "is_free": True,
            "url": "https://example.com/sample-event",
            "capacity": 100,
            "status": "live"
        }
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Events data unavailable",
            "events": []
        }


# Export the API class
__all__ = ["EventsAPI"]