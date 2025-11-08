"""
FastMCP Client Example - Demonstrates how to connect to MCP servers using FastMCP client
This shows the proper way to interact with MCP servers via stdio transport
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from fastmcp import Client
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("FastMCP client not available. Using subprocess approach.")


class FastMCPClientWrapper:
    """
    Wrapper for FastMCP client to connect to MCP servers.
    This provides a clean interface for interacting with MCP servers.
    """
    
    def __init__(self, server_script_path: str):
        """
        Initialize FastMCP client wrapper.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        self.server_script_path = Path(server_script_path)
        self.client: Optional[Client] = None
        self.connected = False
    
    async def connect(self):
        """Connect to the MCP server."""
        if not FASTMCP_AVAILABLE:
            raise RuntimeError("FastMCP client library not available")
        
        if not self.server_script_path.exists():
            raise FileNotFoundError(f"Server script not found: {self.server_script_path}")
        
        try:
            # Initialize FastMCP client with stdio transport
            self.client = Client(str(self.server_script_path))
            await self.client.__aenter__()
            self.connected = True
            print(f"Connected to MCP server: {self.server_script_path.name}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.client and self.connected:
            try:
                await self.client.__aexit__(None, None, None)
                self.connected = False
                print("Disconnected from MCP server")
            except Exception as e:
                print(f"Error disconnecting: {e}")
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
        
        Returns:
            Tool execution result
        """
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to server")
        
        try:
            result = await self.client.call_tool(tool_name, params)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def list_tools(self) -> list:
        """List available tools on the server."""
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to server")
        
        try:
            tools = await self.client.list_tools()
            return tools
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []
    
    async def get_resources(self) -> list:
        """Get available resources from the server."""
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to server")
        
        try:
            resources = await self.client.list_resources()
            return resources
        except Exception as e:
            print(f"Error getting resources: {e}")
            return []


async def example_itinerary_server():
    """Example: Connect to itinerary server and create an itinerary."""
    print("\n=== Itinerary Server Example ===")
    
    server_path = Path(__file__).parent.parent / "mcp_servers" / "itinerary_server.py"
    
    if not FASTMCP_AVAILABLE:
        print("FastMCP client not available. Please install: pip install fastmcp")
        return
    
    client_wrapper = FastMCPClientWrapper(str(server_path))
    
    try:
        # Connect to server
        await client_wrapper.connect()
        
        # List available tools
        print("\nAvailable tools:")
        tools = await client_wrapper.list_tools()
        for tool in tools:
            print(f"  - {tool.get('name', 'Unknown')}")
        
        # Create an itinerary
        print("\nCreating itinerary...")
        result = await client_wrapper.call_tool(
            "create_itinerary",
            {
                "destination": "Paris, France",
                "start_date": "2025-12-15",
                "end_date": "2025-12-22",
                "travelers": 2,
                "preferences": ["culture", "food"]
            }
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Get resources
        print("\nAvailable resources:")
        resources = await client_wrapper.get_resources()
        for resource in resources:
            print(f"  - {resource.get('uri', 'Unknown')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client_wrapper.disconnect()


async def example_booking_server():
    """Example: Connect to booking server and search for flights."""
    print("\n=== Booking Server Example ===")
    
    server_path = Path(__file__).parent.parent / "mcp_servers" / "booking_server.py"
    
    if not FASTMCP_AVAILABLE:
        print("FastMCP client not available. Please install: pip install fastmcp")
        return
    
    client_wrapper = FastMCPClientWrapper(str(server_path))
    
    try:
        await client_wrapper.connect()
        
        # Search for flights
        print("\nSearching for flights...")
        result = await client_wrapper.call_tool(
            "search_flights",
            {
                "origin": "New York",
                "destination": "Paris",
                "departure_date": "2025-12-15",
                "passengers": 2,
                "class_type": "economy"
            }
        )
        print(f"Found flights: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client_wrapper.disconnect()


async def example_maps_server():
    """Example: Connect to maps server and get location info."""
    print("\n=== Maps Server Example ===")
    
    server_path = Path(__file__).parent.parent / "mcp_servers" / "maps_server.py"
    
    if not FASTMCP_AVAILABLE:
        print("FastMCP client not available. Please install: pip install fastmcp")
        return
    
    client_wrapper = FastMCPClientWrapper(str(server_path))
    
    try:
        await client_wrapper.connect()
        
        # Get location info
        print("\nGetting location information...")
        result = await client_wrapper.call_tool(
            "get_location_info",
            {
                "location": "Paris, France",
                "include_nearby": True
            }
        )
        print(f"Location info: {json.dumps(result, indent=2)}")
        
        # Get weather forecast
        print("\nGetting weather forecast...")
        weather = await client_wrapper.call_tool(
            "get_weather_forecast",
            {
                "location": "Paris, France",
                "days": 7
            }
        )
        print(f"Weather: {json.dumps(weather, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client_wrapper.disconnect()


async def main():
    """Run all examples."""
    print("FastMCP Client Examples")
    print("=" * 50)
    
    if not FASTMCP_AVAILABLE:
        print("\n⚠️  FastMCP client library not available.")
        print("Install it with: pip install fastmcp")
        print("\nThe orchestrator will use subprocess approach instead.")
        return
    
    # Run examples
    await example_itinerary_server()
    await example_booking_server()
    await example_maps_server()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

