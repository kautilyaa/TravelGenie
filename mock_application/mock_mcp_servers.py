"""
Mock MCP Servers
Returns cached JSON responses with configurable delays
"""

import time
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

from utils.data_loader import DataLoader
from utils.response_simulator import ResponseSimulator

class MockMCPServers:
    """Mock MCP servers that return cached data"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "app_config.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.data_loader = DataLoader()
        self.simulator = ResponseSimulator(
            base_delay_ms=config.get("mcp_response_delay_ms", 50),
            variance_ms=config.get("mcp_response_delay_variance", 20)
        )
        self.simulator.enabled = config.get("enable_mcp_delays", True)
    
    def geocode_location(self, location: str) -> Dict[str, Any]:
        """Mock geocode_location tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Return mock data (simplified - in real implementation, load from cache)
        result = {
            "success": True,
            "latitude": 51.1784,
            "longitude": -115.5708,
            "display_name": location,
            "address": {
                "city": location.split(",")[0] if "," in location else location,
                "country": "Canada" if "Alberta" in location else "USA"
            }
        }
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def search_flights(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock search_flights tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Load matching flight data
        flight_data = self.data_loader.find_matching_flight(
            departure=departure_id,
            arrival=arrival_id,
            date=outbound_date
        )
        
        if not flight_data:
            # Return empty result
            result = {
                "best_flights": [],
                "other_flights": [],
                "search_metadata": {
                    "departure": departure_id,
                    "arrival": arrival_id,
                    "outbound_date": outbound_date
                }
            }
        else:
            result = flight_data
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def search_hotels(
        self,
        location: str,
        check_in_date: str,
        check_out_date: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock search_hotels tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Load matching hotel data
        hotel_data = self.data_loader.find_matching_hotel(
            location=location,
            check_in=check_in_date
        )
        
        if not hotel_data:
            result = {
                "properties": [],
                "search_information": {"total_results": 0}
            }
        else:
            result = hotel_data
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def search_events(
        self,
        query: str,
        location: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock search_events tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Load matching event data
        event_data = self.data_loader.find_matching_event(
            query=query,
            location=location
        )
        
        if not event_data:
            result = {
                "events_results": [],
                "search_information": {}
            }
        else:
            result = event_data
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def get_weather_forecast(
        self,
        location: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock get_weather_forecast tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Return mock weather data
        result = {
            "success": True,
            "location": location,
            "forecast": {
                "daily": [
                    {
                        "date": "2025-06-07",
                        "temperature_max": 20,
                        "temperature_min": 10,
                        "condition": "sunny"
                    }
                ]
            }
        }
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict[str, Any]:
        """Mock convert_currency tool"""
        start_time = time.time()
        
        # Simulate delay
        self.simulator.simulate_delay()
        
        # Simple mock conversion (CAD to USD ~0.74)
        conversion_rates = {
            "CAD": {"USD": 0.74, "EUR": 0.68},
            "USD": {"CAD": 1.35, "EUR": 0.92},
            "EUR": {"USD": 1.09, "CAD": 1.48}
        }
        
        rate = conversion_rates.get(from_currency, {}).get(to_currency, 1.0)
        converted_amount = amount * rate
        
        result = {
            "from_amount": amount,
            "from_currency": from_currency,
            "to_amount": round(converted_amount, 2),
            "to_currency": to_currency,
            "exchange_rate": rate
        }
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "result": result,
            "duration_ms": duration
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool_map = {
            "geocode_location": self.geocode_location,
            "search_flights": self.search_flights,
            "search_hotels": self.search_hotels,
            "search_events": self.search_events,
            "get_weather_forecast": self.get_weather_forecast,
            "convert_currency": self.convert_currency
        }
        
        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return {
                "result": {"error": f"Unknown tool: {tool_name}"},
                "duration_ms": 0
            }
        
        return tool_func(**kwargs)
