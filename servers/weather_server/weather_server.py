"""
Weather Server MCP - Using Open-Meteo API (Free, No API Key Required)

This server provides weather data using Open-Meteo, a free and open-source weather API.
No API key is required, making it easy to use without registration.

Features:
- Current weather data
- Weather forecasts (up to 16 days)
- Historical weather data (back to 1940)
- Location geocoding/search
- Weather comparisons across multiple locations

API Documentation: https://open-meteo.com/en/docs
"""

import requests
import json
import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Directory to store weather search results
WEATHER_DIR = "weather_data"

# Initialize FastMCP server
mcp = FastMCP("weather-assistant")

# Open-Meteo API endpoints (free, no API key required)
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_API = "https://archive-api.open-meteo.com/v1/archive"

def geocode_location(location: str) -> Tuple[float, float, Dict[str, Any]]:
    """
    Geocode a location name to coordinates using Open-Meteo geocoding API.
    
    Args:
        location: Location name, coordinates (lat,lon), or ZIP code
        
    Returns:
        Tuple of (latitude, longitude, location_info)
    """
    # Check if location is already coordinates
    if ',' in location:
        try:
            parts = location.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon, {"name": location, "latitude": lat, "longitude": lon}
        except ValueError:
            pass
    
    # Use geocoding API
    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    try:
        response = requests.get(GEOCODING_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return (
                result["latitude"],
                result["longitude"],
                {
                    "name": result.get("name", location),
                    "country": result.get("country", "Unknown"),
                    "admin1": result.get("admin1", ""),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"]
                }
            )
        else:
            raise ValueError(f"Location '{location}' not found")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

@mcp.tool()
def get_current_weather(
    location: str,
    units: str = "m",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get current weather information for a specific location using Open-Meteo (free API).
    
    Args:
        location: Location name, coordinates (lat,lon), or ZIP code
        units: Temperature unit - 'm' for Celsius, 'f' for Fahrenheit, 's' for Kelvin
        language: Language code (e.g., 'en', 'es', 'fr', 'de') - Note: Open-Meteo uses English for descriptions
        
    Returns:
        Dict containing current weather data and metadata
    """
    
    try:
        # Geocode location to get coordinates
        lat, lon, location_info = geocode_location(location)
        
        # Build request parameters for Open-Meteo
        temp_unit = "fahrenheit" if units == "f" else "celsius"
        wind_unit = "mph" if units == "f" else "kmh"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover,is_day",
            "temperature_unit": temp_unit,
            "wind_speed_unit": wind_unit,
            "timezone": "auto"
        }
        
        # Make API request
        response = requests.get(WEATHER_API, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Create search identifier
        search_id = f"current_{location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(WEATHER_DIR, exist_ok=True)
        
        # Process current weather data
        current = weather_data.get("current", {})
        current_time = current.get("time", datetime.now().isoformat())
        
        # Weather code to description mapping (WMO Weather interpretation codes)
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            4: "Fog", 5: "Drizzle", 6: "Rain", 7: "Snow", 8: "Shower", 9: "Thunderstorm"
        }
        weather_code = current.get("weather_code", 0)
        weather_desc = weather_codes.get(weather_code, "Unknown")
        
        # Process and store weather data
        processed_data = {
            "search_metadata": {
                "search_id": search_id,
                "location_query": location,
                "units": units,
                "language": language,
                "search_type": "current",
                "search_timestamp": datetime.now().isoformat()
            },
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "latitude": lat,
                "longitude": lon
            },
            "current": current
        }
        
        # Save results to file
        file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print(f"Current weather data saved to: {file_path}")
        
        # Format temperature unit symbol
        temp_symbol = "°C" if units == "m" else "°F" if units == "f" else "K"
        if units == "s":
            temp_val = current.get("temperature_2m", 0) + 273.15
        else:
            temp_val = current.get("temperature_2m", "N/A")
        
        # Return summary for the user
        summary = {
            "search_id": search_id,
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "coordinates": f"{lat}, {lon}",
                "local_time": current_time,
                "timezone": weather_data.get("timezone", "N/A")
            },
            "current_weather": {
                "temperature": f"{temp_val}{temp_symbol}",
                "description": weather_desc,
                "feels_like": f"{temp_val}{temp_symbol}",  # Open-Meteo doesn't provide feels_like
                "humidity": f"{current.get('relative_humidity_2m', 'N/A')}%",
                "wind": f"{current.get('wind_speed_10m', 'N/A')} {wind_unit} {current.get('wind_direction_10m', '')}°",
                "pressure": f"{current.get('pressure_msl', 'N/A')} hPa",
                "cloud_cover": f"{current.get('cloud_cover', 'N/A')}%",
                "is_day": "Day" if current.get("is_day", 1) == 1 else "Night"
            },
            "search_parameters": processed_data["search_metadata"]
        }
        
        return summary
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_weather_forecast(
    location: str,
    forecast_days: int = 5,
    hourly: bool = False,
    units: str = "m",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get weather forecast for a specific location using Open-Meteo (free API).
    
    Args:
        location: Location name, coordinates (lat,lon), or ZIP code
        forecast_days: Number of forecast days (1-16)
        hourly: Include hourly forecast data
        units: Temperature unit - 'm' for Celsius, 'f' for Fahrenheit, 's' for Kelvin
        language: Language code (e.g., 'en', 'es', 'fr', 'de') - Note: Open-Meteo uses English for descriptions
        
    Returns:
        Dict containing weather forecast data and metadata
    """
    
    try:
        # Validate forecast_days
        if not 1 <= forecast_days <= 16:
            return {"error": "forecast_days must be between 1 and 16"}
        
        # Geocode location to get coordinates
        lat, lon, location_info = geocode_location(location)
        
        # Build request parameters for Open-Meteo
        temp_unit = "fahrenheit" if units == "f" else "celsius"
        wind_unit = "mph" if units == "f" else "kmh"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": forecast_days,
            "temperature_unit": temp_unit,
            "wind_speed_unit": wind_unit,
            "timezone": "auto"
        }
        
        # Add daily parameters
        params["daily"] = "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant"
        
        # Add hourly parameters if requested
        if hourly:
            params["hourly"] = "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,precipitation"
        
        # Make API request
        response = requests.get(WEATHER_API, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Create search identifier
        search_id = f"forecast_{location.replace(' ', '_')}_{forecast_days}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(WEATHER_DIR, exist_ok=True)
        
        # Process and store weather data
        processed_data = {
            "search_metadata": {
                "search_id": search_id,
                "location_query": location,
                "forecast_days": forecast_days,
                "hourly": hourly,
                "units": units,
                "language": language,
                "search_type": "forecast",
                "search_timestamp": datetime.now().isoformat()
            },
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "latitude": lat,
                "longitude": lon
            },
            "current": weather_data.get("current", {}),
            "daily": weather_data.get("daily", {}),
            "hourly": weather_data.get("hourly", {}) if hourly else {}
        }
        
        # Save results to file
        file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print(f"Weather forecast data saved to: {file_path}")
        
        # Return summary for the user
        daily_data = weather_data.get("daily", {})
        dates = daily_data.get("time", [])
        
        summary = {
            "search_id": search_id,
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "coordinates": f"{lat}, {lon}",
                "timezone": weather_data.get("timezone", "N/A")
            },
            "forecast_summary": {
                "total_days": len(dates),
                "date_range": f"{dates[0] if dates else 'N/A'} to {dates[-1] if dates else 'N/A'}",
                "includes_hourly": hourly
            },
            "search_parameters": processed_data["search_metadata"]
        }
        
        return summary
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_historical_weather(
    location: str,
    date: str,
    end_date: Optional[str] = None,
    hourly: bool = False,
    units: str = "m",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get historical weather data for a specific location and date(s) using Open-Meteo (free API).
    
    Args:
        location: Location name, coordinates (lat,lon), or ZIP code
        date: Historical date in YYYY-MM-DD format (back to 1940)
        end_date: End date for date range queries (optional)
        hourly: Include hourly historical data
        units: Temperature unit - 'm' for Celsius, 'f' for Fahrenheit, 's' for Kelvin
        language: Language code (e.g., 'en', 'es', 'fr', 'de') - Note: Open-Meteo uses English for descriptions
        
    Returns:
        Dict containing historical weather data and metadata
    """
    
    try:
        # Geocode location to get coordinates
        lat, lon, location_info = geocode_location(location)
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Date must be in YYYY-MM-DD format"}
        
        # Build request parameters for Open-Meteo Historical API
        temp_unit = "fahrenheit" if units == "f" else "celsius"
        wind_unit = "mph" if units == "f" else "kmh"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": end_date if end_date else date,
            "temperature_unit": temp_unit,
            "wind_speed_unit": wind_unit,
            "timezone": "auto"
        }
        
        # Add daily parameters
        params["daily"] = "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant"
        
        # Add hourly parameters if requested
        if hourly:
            params["hourly"] = "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,precipitation"
        
        # Make API request to historical archive
        response = requests.get(HISTORICAL_API, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Create search identifier
        date_range = f"{date}_to_{end_date}" if end_date else date
        search_id = f"historical_{location.replace(' ', '_')}_{date_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(WEATHER_DIR, exist_ok=True)
        
        # Process and store weather data
        processed_data = {
            "search_metadata": {
                "search_id": search_id,
                "location_query": location,
                "start_date": date,
                "end_date": end_date,
                "hourly": hourly,
                "units": units,
                "language": language,
                "search_type": "historical",
                "search_timestamp": datetime.now().isoformat()
            },
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "latitude": lat,
                "longitude": lon
            },
            "daily": weather_data.get("daily", {}),
            "hourly": weather_data.get("hourly", {}) if hourly else {}
        }
        
        # Save results to file
        file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print(f"Historical weather data saved to: {file_path}")
        
        # Return summary for the user
        daily_data = weather_data.get("daily", {})
        dates = daily_data.get("time", [])
        
        summary = {
            "search_id": search_id,
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "coordinates": f"{lat}, {lon}",
                "timezone": weather_data.get("timezone", "N/A")
            },
            "historical_summary": {
                "total_days": len(dates),
                "date_range": f"{date} to {end_date}" if end_date else date,
                "includes_hourly": hourly
            },
            "search_parameters": processed_data["search_metadata"]
        }
        
        return summary
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def search_locations(query: str) -> Dict[str, Any]:
    """
    Search for locations using Open-Meteo geocoding API (free).
    
    Args:
        query: Location search query (city name, partial name, etc.)
        
    Returns:
        Dict containing location search results
    """
    
    try:
        # Build request parameters
        params = {
            "name": query,
            "count": 10,  # Limit to 10 results
            "language": "en",
            "format": "json"
        }
        
        # Make API request
        response = requests.get(GEOCODING_API, params=params, timeout=10)
        response.raise_for_status()
        
        location_data = response.json()
        
        # Process results
        results = location_data.get("results", [])
        formatted_results = []
        
        for result in results:
            formatted_results.append({
                "name": result.get("name", ""),
                "country": result.get("country", ""),
                "admin1": result.get("admin1", ""),
                "latitude": result.get("latitude", 0),
                "longitude": result.get("longitude", 0),
                "country_code": result.get("country_code", ""),
                "elevation": result.get("elevation", 0)
            })
        
        return {
            "query": query,
            "results_count": len(formatted_results),
            "locations": formatted_results
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_weather_details(search_id: str) -> str:
    """
    Get detailed information about a specific weather search.
    
    Args:
        search_id: The search ID returned from weather tools
        
    Returns:
        JSON string with detailed weather information
    """
    
    file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No weather search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            weather_data = json.load(f)
        return json.dumps(weather_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading weather data for {search_id}: {str(e)}"

@mcp.tool()
def compare_weather(
    locations: List[str],
    units: str = "m",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Compare current weather across multiple locations.
    
    Args:
        locations: List of location names to compare
        units: Temperature unit - 'm' for Celsius, 'f' for Fahrenheit, 's' for Kelvin
        language: Language code (e.g., 'en', 'es', 'fr', 'de')
        
    Returns:
        Dict containing weather comparison data
    """
    
    if len(locations) < 2:
        return {"error": "At least 2 locations required for comparison"}
    
    if len(locations) > 10:
        return {"error": "Maximum 10 locations allowed for comparison"}
    
    comparison_data = {
        "comparison_timestamp": datetime.now().isoformat(),
        "units": units,
        "language": language,
        "locations": [],
        "summary": {
            "hottest": {"location": "", "temperature": float('-inf')},
            "coldest": {"location": "", "temperature": float('inf')},
            "windiest": {"location": "", "wind_speed": 0},
            "most_humid": {"location": "", "humidity": 0}
        }
    }
    
    for location in locations:
        try:
            weather_result = get_current_weather(location, units, language)
            
            if "error" in weather_result:
                comparison_data["locations"].append({
                    "location": location,
                    "error": weather_result["error"]
                })
                continue
            
            current_weather = weather_result["current_weather"]
            location_info = weather_result["location"]
            
            # Extract numeric temperature for comparison
            temp_str = current_weather["temperature"].replace("°C", "").replace("°F", "").replace("°K", "")
            try:
                temperature = float(temp_str)
            except ValueError:
                temperature = None
            
            location_data = {
                "location": location_info["name"],
                "country": location_info["country"],
                "temperature": current_weather["temperature"],
                "description": current_weather["description"],
                "feels_like": current_weather["feels_like"],
                "humidity": current_weather["humidity"],
                "wind": current_weather["wind"],
                "pressure": current_weather["pressure"],
                "local_time": location_info["local_time"]
            }
            
            comparison_data["locations"].append(location_data)
            
            # Update summary statistics
            if temperature is not None:
                if temperature > comparison_data["summary"]["hottest"]["temperature"]:
                    comparison_data["summary"]["hottest"] = {
                        "location": location_info["name"],
                        "temperature": temperature
                    }
                
                if temperature < comparison_data["summary"]["coldest"]["temperature"]:
                    comparison_data["summary"]["coldest"] = {
                        "location": location_info["name"],
                        "temperature": temperature
                    }
            
            # Extract humidity for comparison
            humidity_str = current_weather["humidity"].replace("%", "")
            try:
                humidity = float(humidity_str)
                if humidity > comparison_data["summary"]["most_humid"]["humidity"]:
                    comparison_data["summary"]["most_humid"] = {
                        "location": location_info["name"],
                        "humidity": humidity
                    }
            except ValueError:
                pass
            
            # Extract wind speed for comparison
            wind_parts = current_weather["wind"].split()
            if wind_parts:
                try:
                    wind_speed = float(wind_parts[0])
                    if wind_speed > comparison_data["summary"]["windiest"]["wind_speed"]:
                        comparison_data["summary"]["windiest"] = {
                            "location": location_info["name"],
                            "wind_speed": wind_speed
                        }
                except ValueError:
                    pass
                    
        except Exception as e:
            comparison_data["locations"].append({
                "location": location,
                "error": f"Failed to get weather data: {str(e)}"
            })
    
    return comparison_data

@mcp.resource("weather://searches")
def get_weather_searches() -> str:
    """
    List all available weather searches.
    
    This resource provides a list of all saved weather searches.
    """
    searches = []
    
    if os.path.exists(WEATHER_DIR):
        for filename in os.listdir(WEATHER_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(WEATHER_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        location = data.get('location', {})
                        location_name = location.get('name', 'N/A')
                        country = location.get('country', 'N/A')
                        region = location.get('region') or location.get('admin1', '')
                        location_str = f"{location_name}, {country}"
                        if region:
                            location_str = f"{location_name}, {region}, {country}"
                        
                        searches.append({
                            'search_id': search_id,
                            'search_type': metadata.get('search_type', 'unknown'),
                            'location': location_str,
                            'query': metadata.get('location_query', 'N/A'),
                            'search_time': metadata.get('search_timestamp', 'N/A'),
                            'units': metadata.get('units', 'N/A')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Weather Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        
        # Group by search type
        search_types = {}
        for search in searches:
            search_type = search['search_type']
            if search_type not in search_types:
                search_types[search_type] = []
            search_types[search_type].append(search)
        
        for search_type, type_searches in search_types.items():
            content += f"## {search_type.title()} Weather Searches\n\n"
            for search in type_searches:
                content += f"### {search['search_id']}\n"
                content += f"- **Location**: {search['location']}\n"
                content += f"- **Query**: {search['query']}\n"
                content += f"- **Units**: {search['units']}\n"
                content += f"- **Search Time**: {search['search_time']}\n\n"
                content += "---\n\n"
    else:
        content += "No weather searches found.\n\n"
        content += "Use the weather search tools to get weather data:\n"
        content += "- `get_current_weather()` for current weather\n"
        content += "- `get_weather_forecast()` for weather forecasts\n"
        content += "- `get_historical_weather()` for historical data\n"
    
    return content

@mcp.resource("weather://{search_id}")
def get_weather_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific weather search.
    
    Args:
        search_id: The weather search ID to retrieve details for
    """
    file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Weather Search Not Found: {search_id}\n\nNo weather search found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            weather_data = json.load(f)
        
        metadata = weather_data.get('search_metadata', {})
        location = weather_data.get('location', {})
        current = weather_data.get('current', {})
        daily = weather_data.get('daily', {})
        hourly = weather_data.get('hourly', {})
        
        content = f"# Weather Search: {search_id}\n\n"
        
        # Search Details
        content += f"## Search Details\n"
        content += f"- **Type**: {metadata.get('search_type', 'unknown').title()}\n"
        content += f"- **Location Query**: {metadata.get('location_query', 'N/A')}\n"
        content += f"- **Units**: {metadata.get('units', 'N/A')}\n"
        content += f"- **Language**: {metadata.get('language', 'N/A')}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"
        
        # Location Information
        if location:
            content += f"## Location Information\n"
            content += f"- **Name**: {location.get('name', 'N/A')}\n"
            content += f"- **Country**: {location.get('country', 'N/A')}\n"
            region = location.get('region') or location.get('admin1', 'N/A')
            content += f"- **Region**: {region}\n"
            content += f"- **Coordinates**: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n"
            content += "\n"
        
        # Current Weather
        if current:
            weather_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                4: "Fog", 5: "Drizzle", 6: "Rain", 7: "Snow", 8: "Shower", 9: "Thunderstorm"
            }
            weather_code = current.get('weather_code', 0)
            weather_desc = weather_codes.get(weather_code, "Unknown")
            
            content += f"## Current Weather\n"
            content += f"- **Temperature**: {current.get('temperature_2m', 'N/A')}°\n"
            content += f"- **Condition**: {weather_desc}\n"
            content += f"- **Humidity**: {current.get('relative_humidity_2m', 'N/A')}%\n"
            content += f"- **Wind**: {current.get('wind_speed_10m', 'N/A')} {current.get('wind_direction_10m', '')}°\n"
            content += f"- **Pressure**: {current.get('pressure_msl', 'N/A')} hPa\n"
            content += f"- **Cloud Cover**: {current.get('cloud_cover', 'N/A')}%\n"
            content += f"- **Time**: {current.get('time', 'N/A')}\n"
            content += "\n"
        
        # Forecast Data (daily)
        if daily and daily.get('time'):
            dates = daily.get('time', [])
            max_temps = daily.get('temperature_2m_max', [])
            min_temps = daily.get('temperature_2m_min', [])
            weather_codes_daily = daily.get('weather_code', [])
            precip = daily.get('precipitation_sum', [])
            
            content += f"## Weather Forecast ({len(dates)} days)\n\n"
            for i, date in enumerate(dates[:5]):  # Show first 5 days
                content += f"### {date}\n"
                if i < len(max_temps) and i < len(min_temps):
                    content += f"- **Temperature**: {min_temps[i]}° - {max_temps[i]}°\n"
                if i < len(weather_codes_daily):
                    code = weather_codes_daily[i]
                    desc = weather_codes.get(code, "Unknown")
                    content += f"- **Condition**: {desc}\n"
                if i < len(precip):
                    content += f"- **Precipitation**: {precip[i]} mm\n"
                content += "\n"
            
            if len(dates) > 5:
                content += f"... and {len(dates) - 5} more days\n\n"
        
        # Historical Data (daily)
        if daily and metadata.get('search_type') == 'historical':
            dates = daily.get('time', [])
            max_temps = daily.get('temperature_2m_max', [])
            min_temps = daily.get('temperature_2m_min', [])
            weather_codes_daily = daily.get('weather_code', [])
            precip = daily.get('precipitation_sum', [])
            
            content += f"## Historical Weather ({len(dates)} days)\n\n"
            for i, date in enumerate(dates[:5]):  # Show first 5 days
                content += f"### {date}\n"
                if i < len(max_temps) and i < len(min_temps):
                    content += f"- **Temperature**: {min_temps[i]}° - {max_temps[i]}°\n"
                if i < len(weather_codes_daily):
                    code = weather_codes_daily[i]
                    desc = weather_codes.get(code, "Unknown")
                    content += f"- **Condition**: {desc}\n"
                if i < len(precip):
                    content += f"- **Precipitation**: {precip[i]} mm\n"
                content += "\n"
            
            if len(dates) > 5:
                content += f"... and {len(dates) - 5} more days\n\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted weather data for search ID: {search_id}"

@mcp.prompt()
def weather_analysis_prompt(
    location: str,
    analysis_type: str = "current",
    days: int = 5,
    units: str = "m",
    include_comparison: bool = False,
    comparison_locations: List[str] = []
) -> str:
    """Generate a comprehensive weather analysis prompt for Claude."""
    
    unit_display = "Celsius" if units == "m" else "Fahrenheit" if units == "f" else "Kelvin"
    
    prompt = f"""Provide a comprehensive weather analysis for {location} using the Weather Search MCP tools."""
    
    if analysis_type == "current":
        prompt += f"""

**Current Weather Analysis**

1. **Get Current Weather**: Use get_current_weather('{location}', '{units}') to retrieve current conditions
2. **Detailed Analysis**: Provide insights on:
   - Current temperature and feels-like temperature in {unit_display}
   - Weather conditions and visibility
   - Wind patterns and direction
   - Humidity and pressure analysis
   - Air quality assessment (if available)
   - UV index and sun exposure recommendations
   - Astronomical information (sunrise, sunset, moon phase)

3. **Location Context**: Include information about:
   - Exact location coordinates and timezone
   - Regional weather patterns
   - Seasonal considerations for this time of year"""

    elif analysis_type == "forecast":
        prompt += f"""

**Weather Forecast Analysis**

1. **Get Forecast Data**: Use get_weather_forecast('{location}', {days}, True, '{units}') for detailed forecast
2. **Forecast Analysis**: Provide insights on:
   - Daily temperature trends and ranges
   - Weather pattern changes over the {days}-day period  
   - Precipitation probability and amounts
   - Wind speed and direction changes
   - Pressure trends and weather system movements
   - Best days for outdoor activities
   - Days to avoid due to severe weather

3. **Planning Recommendations**: Include advice for:
   - Clothing and preparation suggestions
   - Travel and outdoor activity planning
   - Weather alerts or warnings to watch for"""

    elif analysis_type == "historical":
        today = datetime.now()
        historical_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        prompt += f"""

**Historical Weather Analysis**

1. **Get Historical Data**: Use get_historical_weather('{location}', '{historical_date}', None, True, '{units}') 
2. **Historical Analysis**: Compare with current conditions:
   - Temperature trends year-over-year
   - Seasonal weather patterns
   - Climate change indicators
   - Historical weather extremes
   - Typical weather for this time of year"""

    if include_comparison and comparison_locations:
        locations_str = ', '.join(comparison_locations)
        prompt += f"""

4. **Weather Comparison**: Use compare_weather(['{location}'] + {comparison_locations}, '{units}') to compare:
   - Temperature differences across locations
   - Regional weather variations
   - Climate zone comparisons
   - Travel destination weather analysis"""

    prompt += f"""

**Presentation Format**:
- Use clear headings and bullet points
- Include specific numerical data with units
- Provide practical recommendations
- Highlight any notable weather conditions or warnings
- Create easy-to-scan summaries for key information

**Additional Tools Available**:
- search_locations() for location disambiguation
- get_weather_details() for accessing saved searches
- Multiple weather searches for trend analysis

Focus on providing actionable insights that help with daily planning, travel decisions, and weather awareness."""

    return prompt

@mcp.prompt()
def weather_comparison_prompt(
    locations: List[str],
    comparison_focus: str = "general",
    units: str = "m"
) -> str:
    """Generate a prompt for detailed weather comparison across multiple locations."""
    
    locations_str = ', '.join(locations)
    
    return f"""Compare current weather conditions across multiple locations: {locations_str}

**Weather Comparison Analysis**

1. **Data Collection**: 
   - Use compare_weather({locations}, '{units}') to get comparative data
   - Use get_current_weather() for each location to get detailed individual data

2. **Comparison Analysis Focus - {comparison_focus.title()}**:"""

    if comparison_focus == "travel":
        prompt += """
   - Best weather for travel and sightseeing  
   - Clothing and packing recommendations for each location
   - Outdoor activity suitability
   - Transportation weather considerations
   - UV protection needs"""
    
    elif comparison_focus == "business":
        prompt += """
   - Weather impact on business operations
   - Commuting and transportation conditions
   - Office comfort and energy considerations
   - Meeting and event planning implications
   - Supply chain weather effects"""
    
    elif comparison_focus == "agriculture":
        prompt += """
   - Growing conditions and crop suitability
   - Irrigation and water management needs
   - Pest and disease pressure indicators
   - Harvest timing considerations
   - Livestock comfort and care requirements"""
    
    else:  # general
        prompt += """
   - Temperature and comfort level comparison
   - Precipitation and weather condition differences
   - Air quality variations
   - Wind and atmospheric pressure analysis
   - Seasonal weather pattern comparison"""

    prompt += f"""

3. **Detailed Comparison Table**: Create a side-by-side comparison showing:
   - Location name and local time
   - Temperature (actual and feels-like)
   - Weather conditions and descriptions
   - Humidity and precipitation
   - Wind speed and direction
   - Pressure and visibility
   - Air quality indices (if available)

4. **Key Insights**:
   - Identify the location with the most favorable conditions
   - Highlight significant weather differences
   - Note any extreme or unusual weather patterns
   - Provide recommendations based on the comparison focus

5. **Recommendations**:
   - Best location for current conditions
   - Locations to avoid due to weather
   - Timing recommendations for activities
   - Follow-up weather monitoring suggestions

**Format Requirements**:
- Use clear tables and bullet points
- Include all relevant units of measurement
- Highlight key differences and similarities
- Provide actionable conclusions
- Include data timestamps for reference

Make the comparison practical and decision-focused, helping users choose between locations or plan activities accordingly."""

    return prompt

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')