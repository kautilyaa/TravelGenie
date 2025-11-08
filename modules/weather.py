"""
Weather API Module
Integration with Open-Meteo (Free, no API key required)
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from config.settings import settings


class WeatherAPI:
    """Open-Meteo Weather API integration."""
    
    def __init__(self):
        """Initialize Weather API client."""
        self.base_url = "https://api.open-meteo.com/v1"
        self.timeout = settings.API_TIMEOUT_WEATHER
    
    async def get_weather(
        self,
        lat: float,
        lon: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather information for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of forecast days (1-16)
            
        Returns:
            Weather data dictionary
        """
        try:
            # Prepare parameters
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "hourly": "temperature_2m,relativehumidity_2m,precipitation,weathercode,windspeed_10m",
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,windspeed_10m_max",
                "timezone": "auto",
                "forecast_days": min(days, 16)
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/forecast",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_weather_data(data)
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_error_response()
                        
        except asyncio.TimeoutError:
            logger.error("Weather API timeout")
            return self._get_error_response()
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return self._get_error_response()
    
    def _format_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format weather data for response.
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Formatted weather data
        """
        try:
            current = data.get("current_weather", {})
            daily = data.get("daily", {})
            hourly = data.get("hourly", {})
            
            # Weather code descriptions
            weather_codes = {
                0: "Clear sky ☀️",
                1: "Mainly clear 🌤️",
                2: "Partly cloudy ⛅",
                3: "Overcast ☁️",
                45: "Foggy 🌫️",
                48: "Depositing rime fog 🌫️",
                51: "Light drizzle 🌦️",
                53: "Moderate drizzle 🌦️",
                55: "Dense drizzle 🌦️",
                61: "Slight rain 🌧️",
                63: "Moderate rain 🌧️",
                65: "Heavy rain 🌧️",
                71: "Slight snow ❄️",
                73: "Moderate snow ❄️",
                75: "Heavy snow ❄️",
                77: "Snow grains ❄️",
                80: "Slight rain showers 🌦️",
                81: "Moderate rain showers 🌦️",
                82: "Violent rain showers ⛈️",
                85: "Slight snow showers 🌨️",
                86: "Heavy snow showers 🌨️",
                95: "Thunderstorm ⛈️",
                96: "Thunderstorm with slight hail ⛈️",
                99: "Thunderstorm with heavy hail ⛈️"
            }
            
            # Format current weather
            formatted = {
                "current": {
                    "temperature": current.get("temperature", 0),
                    "temperature_unit": "°C",
                    "windspeed": current.get("windspeed", 0),
                    "windspeed_unit": "km/h",
                    "wind_direction": current.get("winddirection", 0),
                    "weather_code": current.get("weathercode", 0),
                    "weather_description": weather_codes.get(
                        current.get("weathercode", 0),
                        "Unknown"
                    ),
                    "is_day": current.get("is_day", 1) == 1,
                    "time": current.get("time", "")
                },
                "location": {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "elevation": data.get("elevation"),
                    "timezone": data.get("timezone")
                }
            }
            
            # Format daily forecast
            if daily and "time" in daily:
                formatted["daily"] = []
                for i, date in enumerate(daily["time"][:7]):  # Limit to 7 days
                    formatted["daily"].append({
                        "date": date,
                        "weather_code": daily["weathercode"][i] if i < len(daily["weathercode"]) else 0,
                        "weather": weather_codes.get(
                            daily["weathercode"][i] if i < len(daily["weathercode"]) else 0,
                            "Unknown"
                        ),
                        "temperature_max": daily["temperature_2m_max"][i] if i < len(daily["temperature_2m_max"]) else 0,
                        "temperature_min": daily["temperature_2m_min"][i] if i < len(daily["temperature_2m_min"]) else 0,
                        "precipitation": daily["precipitation_sum"][i] if i < len(daily["precipitation_sum"]) else 0,
                        "windspeed_max": daily["windspeed_10m_max"][i] if i < len(daily["windspeed_10m_max"]) else 0,
                        "sunrise": daily["sunrise"][i] if i < len(daily["sunrise"]) else "",
                        "sunset": daily["sunset"][i] if i < len(daily["sunset"]) else ""
                    })
            
            # Add next 24 hours hourly forecast
            if hourly and "time" in hourly:
                formatted["hourly"] = []
                for i in range(min(24, len(hourly["time"]))):
                    formatted["hourly"].append({
                        "time": hourly["time"][i],
                        "temperature": hourly["temperature_2m"][i] if i < len(hourly["temperature_2m"]) else 0,
                        "humidity": hourly["relativehumidity_2m"][i] if i < len(hourly["relativehumidity_2m"]) else 0,
                        "precipitation": hourly["precipitation"][i] if i < len(hourly["precipitation"]) else 0,
                        "windspeed": hourly["windspeed_10m"][i] if i < len(hourly["windspeed_10m"]) else 0,
                        "weather_code": hourly["weathercode"][i] if i < len(hourly["weathercode"]) else 0
                    })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting weather data: {str(e)}")
            return self._get_error_response()
    
    async def get_weather_summary(
        self,
        lat: float,
        lon: float
    ) -> str:
        """
        Get a human-readable weather summary.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather summary string
        """
        data = await self.get_weather(lat, lon, days=3)
        
        if "error" in data:
            return "Unable to get weather information at this time."
        
        current = data.get("current", {})
        daily = data.get("daily", [])
        
        summary = f"Current weather: {current.get('weather_description', 'Unknown')}\n"
        summary += f"Temperature: {current.get('temperature', 'N/A')}°C\n"
        summary += f"Wind: {current.get('windspeed', 'N/A')} km/h\n"
        
        if daily and len(daily) > 0:
            tomorrow = daily[0] if len(daily) > 0 else {}
            summary += f"\nTomorrow: {tomorrow.get('weather', 'Unknown')}\n"
            summary += f"High: {tomorrow.get('temperature_max', 'N/A')}°C, "
            summary += f"Low: {tomorrow.get('temperature_min', 'N/A')}°C"
        
        return summary
    
    async def get_travel_advisory(
        self,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """
        Get travel advisory based on weather conditions.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Travel advisory with recommendations
        """
        weather_data = await self.get_weather(lat, lon, days=3)
        
        if "error" in weather_data:
            return {
                "advisory": "Unable to provide weather advisory",
                "recommendations": []
            }
        
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        
        advisory = {
            "conditions": current.get("weather_description", "Unknown"),
            "recommendations": []
        }
        
        # Temperature-based recommendations
        temp = current.get("temperature", 20)
        if temp < 10:
            advisory["recommendations"].append("🧥 Bring warm clothing")
        elif temp > 30:
            advisory["recommendations"].append("☀️ Use sunscreen and stay hydrated")
        
        # Weather code-based recommendations
        weather_code = current.get("weather_code", 0)
        if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:  # Rain
            advisory["recommendations"].append("☔ Bring an umbrella or raincoat")
        elif weather_code in [71, 73, 75, 77, 85, 86]:  # Snow
            advisory["recommendations"].append("❄️ Prepare for snowy conditions")
        elif weather_code in [95, 96, 99]:  # Thunderstorm
            advisory["recommendations"].append("⛈️ Avoid outdoor activities during storms")
        
        # Wind-based recommendations
        windspeed = current.get("windspeed", 0)
        if windspeed > 40:
            advisory["recommendations"].append("💨 Strong winds - secure loose items")
        
        # Check upcoming days
        rain_expected = any(
            d.get("precipitation", 0) > 5 
            for d in daily[:3]
        )
        if rain_expected:
            advisory["recommendations"].append("🌧️ Rain expected in coming days")
        
        return advisory
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Weather data unavailable",
            "current": {
                "temperature": None,
                "weather_description": "Data unavailable",
                "windspeed": None
            }
        }


# Export the API class
__all__ = ["WeatherAPI"]