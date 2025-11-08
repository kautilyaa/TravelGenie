"""
Response Composer Module
Generates natural language responses from API data
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class ResponseComposer:
    """Compose natural language responses from structured data."""
    
    def __init__(self):
        """Initialize response composer."""
        self.response_templates = {
            "weather": self._compose_weather_response,
            "places": self._compose_places_response,
            "route": self._compose_route_response,
            "events": self._compose_events_response,
            "currency": self._compose_currency_response,
            "image": self._compose_image_response,
            "plan_day": self._compose_itinerary_response,
            "general": self._compose_general_response
        }
    
    async def compose(
        self,
        intent: str,
        data: Dict[str, Any],
        original_query: str
    ) -> str:
        """
        Compose a natural language response.
        
        Args:
            intent: Detected intent
            data: Data from APIs
            original_query: Original user query
            
        Returns:
            Natural language response
        """
        try:
            # Get the appropriate composer function
            composer_func = self.response_templates.get(
                intent,
                self._compose_general_response
            )
            
            # Compose the response
            response = composer_func(data, original_query)
            
            # Add error handling for empty responses
            if not response or response == "":
                response = self._get_fallback_response(intent)
            
            return response
            
        except Exception as e:
            logger.error(f"Error composing response: {str(e)}")
            return self._get_fallback_response(intent)
    
    def _compose_weather_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose weather response."""
        if "error" in data:
            return "I'm having trouble getting weather information right now. Please try again later."
        
        current = data.get("current", {})
        daily = data.get("daily", [])
        advisory = data.get("advisory", {})
        
        response = f"🌡️ **Current Weather**\n"
        response += f"{current.get('weather_description', 'Unknown conditions')}\n"
        response += f"Temperature: {current.get('temperature', 'N/A')}°C\n"
        response += f"Wind: {current.get('windspeed', 'N/A')} km/h\n"
        
        # Add forecast if available
        if daily and len(daily) > 0:
            response += "\n📅 **3-Day Forecast:**\n"
            for day in daily[:3]:
                date = datetime.fromisoformat(day['date']).strftime("%A, %b %d")
                response += f"• {date}: {day['weather']}\n"
                response += f"  High: {day['temperature_max']}°C, Low: {day['temperature_min']}°C\n"
        
        # Add travel advisory if available
        if advisory and "recommendations" in advisory:
            recs = advisory.get("recommendations", [])
            if recs:
                response += "\n💡 **Travel Tips:**\n"
                for rec in recs:
                    response += f"• {rec}\n"
        
        return response
    
    def _compose_places_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose places response."""
        if "error" in data or not data:
            return "I couldn't find any places matching your search. Try being more specific or changing your search terms."
        
        places = data.get("features", [])[:5]  # Limit to 5 places
        
        if not places:
            return "No places found in this area. Try expanding your search radius or looking for different types of places."
        
        response = f"📍 **Places Near You:**\n\n"
        
        for i, place in enumerate(places, 1):
            props = place.get("properties", {})
            name = props.get("name", "Unnamed Place")
            
            # Get place details
            categories = props.get("categories", "").replace(",", ", ")
            distance = props.get("dist", 0)
            
            response += f"**{i}. {name}**\n"
            if categories:
                response += f"   Type: {categories}\n"
            if distance:
                response += f"   Distance: {distance:.0f}m away\n"
            
            # Add rating if available
            rate = props.get("rate", 0)
            if rate > 0:
                stars = "⭐" * min(rate, 5)
                response += f"   Rating: {stars}\n"
            
            response += "\n"
        
        return response
    
    def _compose_route_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose routing response."""
        if "error" in data:
            return "I couldn't calculate a route. Please check your start and end locations."
        
        routes = data.get("routes", [])
        if not routes:
            return "No route found between these locations."
        
        route = routes[0]  # Take the first/best route
        summary = route.get("summary", {})
        
        # Extract route details
        distance = summary.get("distance", 0) / 1000  # Convert to km
        duration = summary.get("duration", 0) / 60  # Convert to minutes
        
        response = f"🗺️ **Route Information:**\n\n"
        response += f"📏 Distance: {distance:.1f} km\n"
        response += f"⏱️ Estimated time: {duration:.0f} minutes\n"
        
        # Add turn-by-turn if available
        segments = route.get("segments", [])
        if segments:
            response += "\n**Directions:**\n"
            steps = segments[0].get("steps", [])[:5]  # First 5 steps
            for i, step in enumerate(steps, 1):
                instruction = step.get("instruction", "Continue")
                response += f"{i}. {instruction}\n"
            
            if len(segments[0].get("steps", [])) > 5:
                response += "... and more steps\n"
        
        return response
    
    def _compose_events_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose events response."""
        if "error" in data:
            return "I couldn't find any events in this area. Try checking local event websites."
        
        events = data.get("events", [])[:5]  # Limit to 5 events
        
        if not events:
            return "No upcoming events found in this area. Check back later or try a different location."
        
        response = f"🎉 **Upcoming Events:**\n\n"
        
        for i, event in enumerate(events, 1):
            name = event.get("name", {}).get("text", "Unnamed Event")
            start = event.get("start", {}).get("local", "")
            venue = event.get("venue", {}).get("name", "Venue TBA")
            
            response += f"**{i}. {name}**\n"
            if start:
                try:
                    event_date = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    response += f"   📅 {event_date.strftime('%B %d, %Y at %I:%M %p')}\n"
                except:
                    response += f"   📅 {start}\n"
            response += f"   📍 {venue}\n"
            
            # Add price if available
            if event.get("is_free"):
                response += "   💰 Free event!\n"
            
            response += "\n"
        
        return response
    
    def _compose_currency_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose currency response."""
        if "error" in data:
            return "I couldn't get current exchange rates. Please try again later."
        
        rates = data.get("rates", {})
        base = data.get("base", "EUR")
        
        if not rates:
            return "No exchange rate data available."
        
        response = f"💱 **Exchange Rates (Base: {base}):**\n\n"
        
        # Show major currencies
        major_currencies = ["USD", "EUR", "GBP", "JPY", "CNY", "AUD", "CAD", "CHF"]
        
        for currency in major_currencies:
            if currency in rates and currency != base:
                rate = rates[currency]
                response += f"• 1 {base} = {rate:.4f} {currency}\n"
        
        response += f"\n_Rates updated: {data.get('date', 'Today')}_"
        
        return response
    
    def _compose_image_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose image response."""
        if "error" in data:
            return "I couldn't find any images for this location."
        
        image_url = data.get("url")
        description = data.get("description", "Location image")
        photographer = data.get("photographer")
        
        if not image_url:
            return "No images found for this location. Try searching for a different place."
        
        response = f"📸 **Image Found:**\n\n"
        response += f"[View Image]({image_url})\n"
        response += f"_{description}_\n"
        
        if photographer:
            response += f"Photo by {photographer} on Unsplash"
        
        return response
    
    def _compose_itinerary_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose itinerary/day plan response."""
        if "error" in data:
            return "I couldn't create an itinerary. Please try again with more specific requirements."
        
        itinerary = data.get("itinerary", [])
        raw_response = data.get("raw_response", "")
        
        if raw_response:
            # If we have a raw response from Claude, use it
            return raw_response
        
        if not itinerary:
            return "I couldn't generate an itinerary for your request."
        
        response = f"📅 **Your Day Itinerary:**\n\n"
        
        for item in itinerary:
            time = item.get("time", "")
            activity = item.get("activity", "")
            details = item.get("details", [])
            
            response += f"**{time}** - {activity}\n"
            for detail in details:
                response += f"  • {detail}\n"
            response += "\n"
        
        response += "\n💡 _Tip: Check weather and opening hours before visiting!_"
        
        return response
    
    def _compose_general_response(
        self,
        data: Dict[str, Any],
        query: str
    ) -> str:
        """Compose general response."""
        if "response" in data:
            return data["response"]
        
        if "error" in data:
            return f"I encountered an issue: {data.get('error')}. Please try rephrasing your question."
        
        return "I can help you with weather, places to visit, directions, events, and travel planning. What would you like to know?"
    
    async def generate_suggestions(
        self,
        intent: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate follow-up suggestions based on intent and data.
        
        Args:
            intent: Current intent
            data: Current response data
            
        Returns:
            List of suggestion strings
        """
        suggestions = {
            "weather": [
                "What should I pack for this weather?",
                "Show me a 7-day forecast",
                "Is it good weather for outdoor activities?"
            ],
            "places": [
                "Show me restaurants nearby",
                "What are the top attractions here?",
                "Find museums in the area",
                "Show me places with good reviews"
            ],
            "route": [
                "What's the public transport option?",
                "Show me alternative routes",
                "How long by walking?",
                "Any traffic on this route?"
            ],
            "events": [
                "Show me free events",
                "What's happening this weekend?",
                "Find family-friendly events",
                "Are there any festivals?"
            ],
            "plan_day": [
                "Add restaurant recommendations",
                "Include indoor alternatives",
                "What's the total travel time?",
                "Create a budget breakdown"
            ],
            "currency": [
                "Convert 100 USD to EUR",
                "What's the best place to exchange money?",
                "Show me ATM locations",
                "Currency trend this week"
            ]
        }
        
        return suggestions.get(intent, [
            "Tell me about this place",
            "What's the weather like?",
            "Find things to do nearby",
            "Plan my day"
        ])
    
    def _get_fallback_response(self, intent: str) -> str:
        """Get fallback response for an intent."""
        fallbacks = {
            "weather": "I can help you check the weather. Please specify a location or let me use your current location.",
            "places": "I can find places for you. Try asking about restaurants, attractions, or things to do.",
            "route": "I can help with directions. Please tell me where you want to go from and to.",
            "events": "I can find events in your area. Try asking about concerts, festivals, or what's happening today.",
            "currency": "I can help with currency exchange rates. Ask me about specific currencies.",
            "image": "I can show you images of places. Tell me what location you'd like to see.",
            "plan_day": "I can help plan your day. Tell me where you are and what kind of activities you enjoy."
        }
        
        return fallbacks.get(
            intent,
            "I'm here to help with your travel needs. You can ask me about weather, places to visit, directions, events, and more!"
        )


# Export the composer class
__all__ = ["ResponseComposer"]