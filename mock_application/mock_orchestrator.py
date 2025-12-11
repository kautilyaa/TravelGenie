"""
Mock Orchestrator
Simulates the application flow with Llama communication and MCP tool calls
"""

import time
import uuid
import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from llama_client import LlamaClient
from mock_llm_client import MockLLMClient
from mock_mcp_servers import MockMCPServers
from performance_monitor import PerformanceMonitor

class MockOrchestrator:
    """Simulates the orchestrator's decision-making flow"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "app_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Conditionally use mock LLM or real Llama client
        use_mock_llm = self.config.get("use_mock_llm", True)
        if use_mock_llm:
            self.llama_client = MockLLMClient(config_path=config_path)
        else:
            self.llama_client = LlamaClient(config_path=config_path)
        
        self.mcp_servers = MockMCPServers(config_path=config_path)
        self.monitor = PerformanceMonitor()
        
        self.max_turns = self.config.get("max_turns", 10)
        self.max_tools_per_turn = self.config.get("max_tools_per_turn", 5)
        self.platform = self.config.get("platform", "local")
        self.platform_tag = self.config.get("platform_tag", "")
    
    def get_system_prompt(self) -> str:
        """Get system prompt for Llama"""
        return """You are an intelligent travel planning assistant. 
You help users plan trips by using available tools to search for flights, hotels, events, weather, and convert currencies.
When a user asks about travel, use the available tools to gather information and provide a comprehensive response."""
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for Llama"""
        return [
            {
                "name": "geocode_location",
                "description": "Convert a location name to coordinates",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "search_flights",
                "description": "Search for flights between airports",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "departure_id": {"type": "string"},
                        "arrival_id": {"type": "string"},
                        "outbound_date": {"type": "string"},
                        "return_date": {"type": "string"}
                    },
                    "required": ["departure_id", "arrival_id", "outbound_date"]
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for hotels in a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "check_in_date": {"type": "string"},
                        "check_out_date": {"type": "string"}
                    },
                    "required": ["location", "check_in_date", "check_out_date"]
                }
            },
            {
                "name": "search_events",
                "description": "Search for events in a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "location": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "convert_currency",
                "description": "Convert currency amounts",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "from_currency": {"type": "string"},
                        "to_currency": {"type": "string"}
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            }
        ]
    
    def process_query(self, user_query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query through the mock orchestrator
        Returns response and performance metrics
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        request_id = f"{session_id}_{int(time.time())}"
        self.monitor.start_request(request_id)
        
        start_time = time.time()
        messages = []
        tool_calls_made = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.get_system_prompt()
        })
        
        # Add user query
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        # Simulate conversation loop
        for turn in range(self.max_turns):
            # Call Llama to get response/tool calls
            llama_start = time.time()
            llama_response = self.llama_client.chat_completion(
                messages=messages,
                tools=self.get_tool_definitions()
            )
            llama_latency = (time.time() - llama_start) * 1000
            
            if not llama_response.get("success"):
                return {
                    "success": False,
                    "error": llama_response.get("error"),
                    "latency_ms": (time.time() - start_time) * 1000
                }
            
            llama_data = llama_response.get("response", {})
            self.monitor.record_llama_call(
                latency_ms=llama_latency,
                tokens=llama_data.get("usage", {}).get("total_tokens"),
                success=True
            )
            
            # Extract tool calls from response
            choices = llama_data.get("choices", [])
            if not choices:
                break
            
            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            # Limit tool calls per turn
            tools_to_execute = tool_calls[:self.max_tools_per_turn]
            
            if not tools_to_execute:
                # No more tool calls, get final response
                final_response = message.get("content", "")
                break
            
            # Execute tool calls
            tool_results = []
            for tool_call in tools_to_execute:
                tool_name = tool_call.get("function", {}).get("name")
                tool_input = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                
                # Execute tool
                tool_start = time.time()
                tool_result = self.mcp_servers.execute_tool(tool_name, **tool_input)
                tool_latency = (time.time() - tool_start) * 1000
                
                self.monitor.record_tool_call(tool_name, tool_latency)
                tool_calls_made.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "latency_ms": tool_latency
                })
                
                # Format tool result for Llama
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.get("id"),
                    "content": json.dumps(tool_result.get("result", {}))
                })
            
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": tools_to_execute
            })
            
            # Add tool results
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        total_latency = (time.time() - start_time) * 1000
        trace_summary = self.monitor.end_request()
        
        # Add platform information to response
        result = {
            "success": True,
            "response": final_response if 'final_response' in locals() else "No response generated",
            "tool_calls": tool_calls_made,
            "total_turns": turn + 1,
            "latency_ms": total_latency,
            "trace_summary": trace_summary,
            "request_id": request_id,
            "platform": self.platform,
            "platform_tag": self.platform_tag
        }
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.monitor.get_metrics()
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed performance analysis"""
        return self.monitor.get_detailed_analysis()
