"""
Mock LLM Client
Intelligently generates tool calls based on queries without requiring external API calls
"""

import time
import json
import re
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yaml
from pathlib import Path

from utils.response_simulator import ResponseSimulator


class MockLLMClient:
    """Mock LLM client that generates intelligent tool calls based on query analysis"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "app_config.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.simulator = ResponseSimulator(
            base_delay_ms=config.get("mock_llm_delay_ms", 200),
            variance_ms=config.get("mock_llm_delay_variance", 100)
        )
        
        # Metrics tracking
        self.latency_history = []
        self.total_requests = 0
        self.error_count = 0
        
        # Tool call patterns
        self.tool_patterns = {
            "geocode_location": [
                r"location|city|address|place|where is|coordinates",
                r"banff|alberta|reston|virginia|new york|san francisco"
            ],
            "search_flights": [
                r"flight|fly|airline|airport|departure|arrival",
                r"from.*to|IAD|JFK|YYC|LAX|depart|return"
            ],
            "search_hotels": [
                r"hotel|accommodation|stay|lodging|room|book",
                r"check.in|check.out|night|nights"
            ],
            "search_events": [
                r"event|activity|things to do|festival|concert|museum",
                r"hiking|sight.seeing|dining|shopping"
            ],
            "get_weather_forecast": [
                r"weather|forecast|temperature|rain|sunny|cloudy",
                r"temperature|conditions|climate"
            ],
            "convert_currency": [
                r"currency|convert|USD|CAD|EUR|exchange rate|dollar",
                r"budget|cost|price|amount"
            ]
        }
    
    def _extract_locations(self, query: str) -> List[str]:
        """Extract location names from query"""
        # Common location patterns
        location_patterns = [
            r"([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)",  # City, State format
            r"(Banff|Jasper|Alberta|Virginia|New York|San Francisco|Los Angeles)",
            r"(IAD|JFK|YYC|LAX|DCA|BZN)",  # Airport codes
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            locations.extend(matches)
        
        return list(set(locations))
    
    def _extract_dates(self, query: str) -> Dict[str, str]:
        """Extract dates from query"""
        dates = {}
        
        # Date patterns
        date_patterns = [
            (r"(\d{4}-\d{2}-\d{2})", "iso"),  # ISO format
            (r"(June|July|August|September|October|November|December)\s+(\d{1,2})", "month_day"),
            (r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", "mdy"),
        ]
        
        # Default dates (7 days from now)
        default_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        # Try to extract dates
        iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", query)
        if iso_match:
            dates["outbound_date"] = iso_match.group(1)
            return_match = re.search(r"(\d{4}-\d{2}-\d{2})", query[iso_match.end():])
            if return_match:
                dates["return_date"] = return_match.group(1)
            else:
                dates["return_date"] = return_date
        else:
            dates["outbound_date"] = default_date
            dates["return_date"] = return_date
        
        return dates
    
    def _extract_currency_info(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract currency conversion information"""
        currency_match = re.search(r"(\$?\d+(?:,\d{3})*(?:\.\d{2})?)\s*(USD|CAD|EUR|GBP)?", query, re.IGNORECASE)
        if currency_match:
            amount_str = currency_match.group(1).replace("$", "").replace(",", "")
            try:
                amount = float(amount_str)
                from_currency = currency_match.group(2) or "USD"
                # Determine target currency
                to_currency = "CAD" if "canada" in query.lower() or "alberta" in query.lower() else "USD"
                return {
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency
                }
            except ValueError:
                pass
        return None
    
    def _determine_tool_calls(self, query: str, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Intelligently determine which tools to call based on query"""
        query_lower = query.lower()
        tool_calls = []
        
        # Check if we're in a follow-up turn (have tool results)
        is_follow_up = any(msg.get("role") == "user" and isinstance(msg.get("content"), list) for msg in messages)
        
        if is_follow_up:
            # Generate final response based on tool results
            return []
        
        # Extract locations
        locations = self._extract_locations(query)
        dates = self._extract_dates(query)
        
        # Determine which tools to call
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["geocode_location"]):
            if locations:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": "geocode_location",
                        "arguments": json.dumps({"location": locations[0]})
                    }
                })
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["search_flights"]):
            if len(locations) >= 2:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": "search_flights",
                        "arguments": json.dumps({
                            "departure_id": locations[0],
                            "arrival_id": locations[1],
                            "outbound_date": dates.get("outbound_date", "2025-06-07"),
                            "return_date": dates.get("return_date")
                        })
                    }
                })
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["search_hotels"]):
            if locations:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": "search_hotels",
                        "arguments": json.dumps({
                            "location": locations[0],
                            "check_in_date": dates.get("outbound_date", "2025-06-07"),
                            "check_out_date": dates.get("return_date", "2025-06-14")
                        })
                    }
                })
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["search_events"]):
            event_query = "things to do" if "things to do" in query_lower else "events"
            tool_calls.append({
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": "search_events",
                    "arguments": json.dumps({
                        "query": event_query,
                        "location": locations[0] if locations else "destination"
                    })
                }
            })
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["get_weather_forecast"]):
            if locations:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": "get_weather_forecast",
                        "arguments": json.dumps({"location": locations[0]})
                    }
                })
        
        currency_info = self._extract_currency_info(query)
        if currency_info or any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.tool_patterns["convert_currency"]):
            if currency_info:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": "convert_currency",
                        "arguments": json.dumps(currency_info)
                    }
                })
        
        return tool_calls
    
    def _generate_final_response(self, query: str, tool_results: List[Dict[str, Any]]) -> str:
        """Generate a final response based on query and tool results"""
        if not tool_results:
            return "I've gathered the information you requested. Here's a summary of your travel options."
        
        response_parts = ["Based on the information I've gathered:"]
        
        if any("flight" in str(result).lower() for result in tool_results):
            response_parts.append("- I found several flight options for your trip.")
        
        if any("hotel" in str(result).lower() for result in tool_results):
            response_parts.append("- I've identified hotel options in your destination.")
        
        if any("event" in str(result).lower() for result in tool_results):
            response_parts.append("- I found various activities and events you might enjoy.")
        
        if any("weather" in str(result).lower() for result in tool_results):
            response_parts.append("- I've checked the weather forecast for your travel dates.")
        
        response_parts.append("\nWould you like me to provide more details about any of these options?")
        
        return "\n".join(response_parts)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a mock chat completion response with tool calls
        Returns OpenAI-compatible response format
        """
        start_time = time.time()
        
        # Simulate processing delay
        self.simulator.simulate_delay()
        
        # Get the last user message
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    user_query = content
                    break
        
        # Check if we have tool results (follow-up turn)
        has_tool_results = any(
            msg.get("role") == "user" and isinstance(msg.get("content"), list)
            for msg in messages
        )
        
        if has_tool_results:
            # Generate final response
            tool_results = []
            for msg in messages:
                if msg.get("role") == "user" and isinstance(msg.get("content"), list):
                    tool_results = msg.get("content", [])
                    break
            
            final_response = self._generate_final_response(user_query, tool_results)
            
            response_data = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "mock-llm-3.2",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": final_response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_query.split()) * 1.3,  # Rough estimate
                    "completion_tokens": len(final_response.split()) * 1.3,
                    "total_tokens": (len(user_query.split()) + len(final_response.split())) * 1.3
                }
            }
        else:
            # Generate tool calls
            tool_calls = self._determine_tool_calls(user_query, messages, tools or [])
            
            if tool_calls:
                response_data = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "mock-llm-3.2",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": tool_calls
                        },
                        "finish_reason": "tool_calls"
                    }],
                    "usage": {
                        "prompt_tokens": len(user_query.split()) * 1.3,
                        "completion_tokens": 0,
                        "total_tokens": len(user_query.split()) * 1.3
                    }
                }
            else:
                # No tool calls needed, generate direct response
                response_data = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "mock-llm-3.2",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I can help you plan your trip. Please provide more details about your destination, dates, and preferences."
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(user_query.split()) * 1.3,
                        "completion_tokens": 50,
                        "total_tokens": len(user_query.split()) * 1.3 + 50
                    }
                }
        
        total_time = (time.time() - start_time) * 1000
        
        # Track metrics
        self.total_requests += 1
        self.latency_history.append({
            "total_time": total_time,
            "timestamp": time.time()
        })
        
        return {
            "success": True,
            "response": response_data,
            "latency_ms": total_time
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if mock LLM is healthy (always true)"""
        return {
            "healthy": True,
            "latency_ms": 0,
            "status": "mock_mode"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.latency_history:
            return {
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "error_rate": 0.0
            }
        
        latencies = [h["total_time"] for h in self.latency_history]
        
        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.total_requests if self.total_requests > 0 else 0.0,
            "mean_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "recent_latencies": latencies[-10:]
        }
