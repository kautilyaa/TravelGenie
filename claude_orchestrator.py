"""Claude API orchestrator for travel planning."""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "flight_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "hotel_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "event_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "geocoder_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "weather_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "finance_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "traffic_crowd_server"))

try:
    from servers.flight_server.flight_server import search_flights, get_flight_details, filter_flights_by_price
    from servers.hotel_server.hotel_server import search_hotels, get_hotel_details, filter_hotels_by_price
    from servers.event_server.event_server import search_events, get_event_details, filter_events_by_date
    from servers.geocoder_server.geocoder_server import geocode_location, reverse_geocode, calculate_distance
    from servers.weather_server.weather_server import get_current_weather, get_weather_forecast
    from servers.finance_server.finance_server import convert_currency, get_market_overview
    from servers.traffic_crowd_server.traffic_crowd_server import analyze_location_traffic, analyze_video_frame_realtime, analyze_youtube_video, get_traffic_patterns, compare_location_traffic
except ImportError as e:
    print(f"Warning: Could not import some server functions: {e}")


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Returns tool definitions for Claude to interact with MCP servers."""
    return [
        {
            "name": "geocode_location",
            "description": "Convert a location name (city, address, etc.) to coordinates (latitude, longitude). Use this before getting weather forecasts or calculating distances.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name (e.g., 'Banff, Alberta', 'New York, NY', 'Reston, Virginia')"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "calculate_distance",
            "description": "Calculate the distance between two locations. Both locations must be geocoded first.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location1": {
                        "type": "string",
                        "description": "First location name or coordinates (lat,lon)"
                    },
                    "location2": {
                        "type": "string",
                        "description": "Second location name or coordinates (lat,lon)"
                    }
                },
                "required": ["location1", "location2"]
            }
        },
        {
            "name": "search_flights",
            "description": "Search for flights between two locations. Use airport codes (e.g., 'IAD', 'YYC') or city names. Returns flight options with prices, airlines, and schedules.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "departure_id": {
                        "type": "string",
                        "description": "Departure airport code or city name (e.g., 'IAD', 'LAX', 'Reston, Virginia')"
                    },
                    "arrival_id": {
                        "type": "string",
                        "description": "Arrival airport code or city name (e.g., 'YYC', 'JFK', 'Banff, Alberta')"
                    },
                    "outbound_date": {
                        "type": "string",
                        "description": "Departure date in YYYY-MM-DD format (e.g., '2025-06-07')"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date in YYYY-MM-DD format (e.g., '2025-06-14'). Required for round trips."
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult passengers",
                        "default": 1
                    },
                    "children": {
                        "type": "integer",
                        "description": "Number of child passengers",
                        "default": 0
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (e.g., 'USD', 'CAD', 'EUR')",
                        "default": "USD"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["departure_id", "arrival_id", "outbound_date"]
            }
        },
        {
            "name": "search_hotels",
            "description": "Search for hotels and accommodations in a destination. Returns hotel options with prices, ratings, amenities, and availability.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Destination location (e.g., 'Banff, Alberta', 'New York, NY')"
                    },
                    "check_in_date": {
                        "type": "string",
                        "description": "Check-in date in YYYY-MM-DD format (e.g., '2025-06-07')"
                    },
                    "check_out_date": {
                        "type": "string",
                        "description": "Check-out date in YYYY-MM-DD format (e.g., '2025-06-14')"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult guests",
                        "default": 2
                    },
                    "children": {
                        "type": "integer",
                        "description": "Number of child guests",
                        "default": 0
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (e.g., 'USD', 'CAD', 'EUR')",
                        "default": "USD"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["location", "check_in_date", "check_out_date"]
            }
        },
        {
            "name": "search_events",
            "description": "Search for local events, activities, festivals, and things to do in a location. Can filter by interests like hiking, dining, museums, etc.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query describing interests or event types (e.g., 'hiking, sight-seeing, dining, museums', 'concerts', 'festivals')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location to search for events (e.g., 'Banff, Alberta', 'New York, NY')"
                    },
                    "date_filter": {
                        "type": "string",
                        "description": "Time period filter: 'today', 'tomorrow', 'week', 'weekend', 'month'",
                        "default": "month"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20
                    }
                },
                "required": ["query", "location"]
            }
        },
        {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for a location. Use location name or coordinates. Returns daily forecast with temperature, conditions, and precipitation.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name (e.g., 'Banff, Alberta') or coordinates (lat,lon)"
                    },
                    "forecast_days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-16)",
                        "default": 5
                    },
                    "hourly": {
                        "type": "boolean",
                        "description": "Include hourly forecast data",
                        "default": False
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_current_weather",
            "description": "Get current weather conditions for a location.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name (e.g., 'Banff, Alberta') or coordinates (lat,lon)"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "convert_currency",
            "description": "Convert currency amounts between different currencies. Use this to convert costs (hotels, flights) to the user's preferred currency.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to convert"
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g., 'USD', 'CAD', 'EUR')"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g., 'USD', 'CAD', 'EUR')"
                    }
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        },
        {
            "name": "analyze_location_traffic",
            "description": "Get real-time traffic and crowd data for a specific location. Returns vehicle traffic, foot traffic, and crowd density information to help plan optimal visit times.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name or coordinates (lat,lon) (e.g., 'Times Square, New York', 'Central Park')"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis: 'comprehensive' (all data), 'crowd' (crowd only), 'traffic' (vehicle traffic only), 'foot_traffic' (pedestrian traffic only)",
                        "default": "comprehensive",
                        "enum": ["comprehensive", "crowd", "traffic", "foot_traffic"]
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "analyze_video_frame_realtime",
            "description": "Analyze a real-time video frame for crowd, foot traffic, and vehicle detection. Use this when you have video/image data from a location to get live activity analysis.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "frame_data": {
                        "type": "string",
                        "description": "Base64 encoded image string or file path to image"
                    },
                    "frame_type": {
                        "type": "string",
                        "description": "Type of input: 'base64' (for base64 encoded images) or 'file_path' (for file paths)",
                        "default": "base64",
                        "enum": ["base64", "file_path"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional location name for context (e.g., 'Times Square')"
                    }
                },
                "required": ["frame_data"]
            }
        },
        {
            "name": "get_traffic_patterns",
            "description": "Get historical traffic patterns for a location to understand peak hours, best visit times, and traffic trends.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name or coordinates (lat,lon)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (optional, defaults to 7 days ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (optional, defaults to today)"
                    },
                    "pattern_type": {
                        "type": "string",
                        "description": "Pattern type: 'daily', 'hourly', or 'weekly'",
                        "default": "daily",
                        "enum": ["daily", "hourly", "weekly"]
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "compare_location_traffic",
            "description": "Compare traffic and crowd data across multiple locations to help users choose the best location or time to visit.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of location names or coordinates to compare (e.g., ['Times Square', 'Central Park', 'Brooklyn Bridge'])"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis: 'comprehensive' (all data), 'crowd' (crowd only), 'traffic' (vehicle traffic only), 'foot_traffic' (pedestrian traffic only)",
                        "default": "comprehensive",
                        "enum": ["comprehensive", "crowd", "traffic", "foot_traffic"]
                    }
                },
                "required": ["locations"]
            }
        },
        {
            "name": "analyze_youtube_video",
            "description": "Analyze a YouTube video (including live streams) for real-time crowd, foot traffic, and vehicle detection. Extracts frames from the video and performs analysis. Perfect for analyzing live camera feeds from locations.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "youtube_url": {
                        "type": "string",
                        "description": "YouTube video URL (supports regular videos and live streams, e.g., 'https://www.youtube.com/watch?v=...' or 'https://youtu.be/...')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional location name for context (e.g., 'Times Square, New York')"
                    },
                    "sample_frames": {
                        "type": "integer",
                        "description": "Number of frames to sample and analyze (default: 5)",
                        "default": 5
                    },
                    "frame_interval": {
                        "type": "integer",
                        "description": "Interval between sampled frames in seconds (default: 10)",
                        "default": 10
                    }
                },
                "required": ["youtube_url"]
            }
        }
    ]


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Executes a tool function by name with the given parameters."""
    try:
        if tool_name == "geocode_location":
            return geocode_location(kwargs.get("location"))
        
        elif tool_name == "calculate_distance":
            return calculate_distance(kwargs.get("location1"), kwargs.get("location2"))
        
        elif tool_name == "search_flights":
            return search_flights(
                departure_id=kwargs.get("departure_id"),
                arrival_id=kwargs.get("arrival_id"),
                outbound_date=kwargs.get("outbound_date"),
                return_date=kwargs.get("return_date"),
                adults=kwargs.get("adults", 1),
                children=kwargs.get("children", 0),
                currency=kwargs.get("currency", "USD"),
                max_results=kwargs.get("max_results", 10)
            )
        
        elif tool_name == "search_hotels":
            return search_hotels(
                location=kwargs.get("location"),
                check_in_date=kwargs.get("check_in_date"),
                check_out_date=kwargs.get("check_out_date"),
                adults=kwargs.get("adults", 2),
                children=kwargs.get("children", 0),
                currency=kwargs.get("currency", "USD"),
                max_results=kwargs.get("max_results", 10)
            )
        
        elif tool_name == "search_events":
            return search_events(
                query=kwargs.get("query"),
                location=kwargs.get("location"),
                date_filter=kwargs.get("date_filter", "month"),
                max_results=kwargs.get("max_results", 20)
            )
        
        elif tool_name == "get_weather_forecast":
            return get_weather_forecast(
                location=kwargs.get("location"),
                forecast_days=kwargs.get("forecast_days", 5),
                hourly=kwargs.get("hourly", False)
            )
        
        elif tool_name == "get_current_weather":
            return get_current_weather(location=kwargs.get("location"))
        
        elif tool_name == "convert_currency":
            return convert_currency(
                amount=kwargs.get("amount"),
                from_currency=kwargs.get("from_currency"),
                to_currency=kwargs.get("to_currency")
            )
        
        elif tool_name == "analyze_location_traffic":
            return analyze_location_traffic(
                location=kwargs.get("location"),
                analysis_type=kwargs.get("analysis_type", "comprehensive")
            )
        
        elif tool_name == "analyze_video_frame_realtime":
            return analyze_video_frame_realtime(
                frame_data=kwargs.get("frame_data"),
                frame_type=kwargs.get("frame_type", "base64"),
                location=kwargs.get("location")
            )
        
        elif tool_name == "get_traffic_patterns":
            return get_traffic_patterns(
                location=kwargs.get("location"),
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                pattern_type=kwargs.get("pattern_type", "daily")
            )
        
        elif tool_name == "compare_location_traffic":
            return compare_location_traffic(
                locations=kwargs.get("locations"),
                analysis_type=kwargs.get("analysis_type", "comprehensive")
            )
        
        elif tool_name == "analyze_youtube_video":
            return analyze_youtube_video(
                youtube_url=kwargs.get("youtube_url"),
                location=kwargs.get("location"),
                sample_frames=kwargs.get("sample_frames", 5),
                frame_interval=kwargs.get("frame_interval", 10)
            )
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"error": str(e), "tool": tool_name}


def get_system_prompt() -> str:
    """Returns the system prompt explaining Claude's role and capabilities."""
    return """You are an intelligent travel planning assistant powered by multiple specialized services. 
You help users plan comprehensive trips by orchestrating searches across flights, hotels, events, weather, and currency conversion.

Your capabilities include:
- Finding flights between locations with dates, prices, and schedules
- Searching for hotels and accommodations with prices and amenities
- Discovering local events, activities, and things to do
- Getting weather forecasts to help plan activities
- Converting currencies for international travel
- Geocoding locations and calculating distances
- Analyzing real-time traffic and crowd conditions at locations
- Analyzing video frames for crowd, vehicle, and foot traffic detection
- Analyzing YouTube videos and live streams for real-time location analysis
- Getting traffic patterns to identify best visit times

When a user asks about travel planning:
1. Extract key information: origin, destination, dates, number of travelers, budget, interests
2. Use geocoding to get coordinates for locations (needed for weather and distances)
3. Search for flights, hotels, and events based on the user's requirements
4. Get weather forecasts to suggest appropriate activities
5. Analyze traffic and crowd conditions at destinations to recommend optimal visit times
6. Convert all costs to the user's preferred currency
7. Synthesize all information into a comprehensive travel plan with:
   - Flight recommendations with prices
   - Hotel recommendations with prices per night
   - Day-by-day itinerary based on weather, traffic, and interests
   - Event and activity suggestions with optimal visit times
   - Traffic and crowd analysis for popular locations
   - Budget breakdown in the requested currency
   - Distance and travel time information

Always be helpful, thorough, and provide specific recommendations with prices and details. 
If you need clarification on dates, locations, or preferences, ask the user.
Present information in a clear, organized format that's easy to understand."""

