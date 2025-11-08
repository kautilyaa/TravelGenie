"""
MCP Server Orchestrator - Manages and coordinates multiple MCP servers
Uses stdio transport for efficient process management
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Manages multiple MCP servers using stdio transport.
    Handles server lifecycle, communication, and coordination.
    """
    
    def __init__(self):
        self.servers: Dict[str, subprocess.Popen] = {}
        self.server_configs = {
            "itinerary": {
                "path": "mcp_servers/itinerary_server.py",
                "name": "travel-itinerary",
                "description": "Manages travel itineraries and trip planning"
            },
            "maps": {
                "path": "mcp_servers/maps_server.py",
                "name": "travel-maps",
                "description": "Handles location services and geographical data"
            },
            "booking": {
                "path": "mcp_servers/booking_server.py",
                "name": "travel-booking",
                "description": "Handles reservations and bookings"
            }
        }
        self.server_processes: Dict[str, asyncio.subprocess.Process] = {}
    
    async def start_server(self, server_type: str) -> bool:
        """
        Start an individual MCP server.
        
        Args:
            server_type: Type of server to start ('itinerary', 'maps', 'booking')
        
        Returns:
            True if server started successfully
        """
        if server_type not in self.server_configs:
            logger.error(f"Unknown server type: {server_type}")
            return False
        
        if server_type in self.server_processes:
            logger.warning(f"Server {server_type} is already running")
            return True
        
        config = self.server_configs[server_type]
        server_path = Path(config["path"])
        
        if not server_path.exists():
            logger.error(f"Server file not found: {server_path}")
            return False
        
        try:
            # Start the server process with stdio transport
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.server_processes[server_type] = process
            logger.info(f"Started {server_type} server (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {server_type} server: {e}")
            return False
    
    async def stop_server(self, server_type: str) -> bool:
        """
        Stop an individual MCP server.
        
        Args:
            server_type: Type of server to stop
        
        Returns:
            True if server stopped successfully
        """
        if server_type not in self.server_processes:
            logger.warning(f"Server {server_type} is not running")
            return True
        
        try:
            process = self.server_processes[server_type]
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
            del self.server_processes[server_type]
            logger.info(f"Stopped {server_type} server")
            return True
            
        except asyncio.TimeoutError:
            # Force kill if graceful shutdown fails
            process.kill()
            await process.wait()
            del self.server_processes[server_type]
            logger.warning(f"Force killed {server_type} server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {server_type} server: {e}")
            return False
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """
        Start all configured MCP servers.
        
        Returns:
            Dictionary with server status
        """
        results = {}
        for server_type in self.server_configs:
            results[server_type] = await self.start_server(server_type)
        return results
    
    async def stop_all_servers(self) -> Dict[str, bool]:
        """
        Stop all running MCP servers.
        
        Returns:
            Dictionary with server stop status
        """
        results = {}
        for server_type in list(self.server_processes.keys()):
            results[server_type] = await self.stop_server(server_type)
        return results
    
    async def send_request(
        self, 
        server_type: str, 
        method: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to an MCP server via stdio.
        
        Args:
            server_type: Target server type
            method: Method name to call
            params: Optional parameters for the method
        
        Returns:
            Server response
        """
        if server_type not in self.server_processes:
            return {
                "error": f"Server {server_type} is not running"
            }
        
        process = self.server_processes[server_type]
        
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request via stdin
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response from stdout
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=10.0
            )
            response = json.loads(response_line.decode())
            
            return response
            
        except asyncio.TimeoutError:
            return {"error": "Request timeout"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
        except Exception as e:
            return {"error": str(e)}
    
    async def coordinate_request(
        self,
        request_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate a request across multiple MCP servers.
        
        Args:
            request_type: Type of coordinated request
            params: Request parameters
        
        Returns:
            Combined response from multiple servers
        """
        results = {}
        
        if request_type == "plan_trip":
            # Coordinate trip planning across all servers
            destination = params.get("destination")
            dates = params.get("dates", {})
            
            # Get itinerary from itinerary server
            itinerary_response = await self.send_request(
                "itinerary",
                "create_itinerary",
                {
                    "destination": destination,
                    "start_date": dates.get("start"),
                    "end_date": dates.get("end")
                }
            )
            results["itinerary"] = itinerary_response
            
            # Get location info from maps server
            maps_response = await self.send_request(
                "maps",
                "get_location_info",
                {"location": destination, "include_nearby": True}
            )
            results["location"] = maps_response
            
            # Search for flights and hotels from booking server
            booking_tasks = [
                self.send_request(
                    "booking",
                    "search_flights",
                    {
                        "origin": params.get("origin", "New York"),
                        "destination": destination,
                        "departure_date": dates.get("start")
                    }
                ),
                self.send_request(
                    "booking",
                    "search_hotels",
                    {
                        "location": destination,
                        "check_in": dates.get("start"),
                        "check_out": dates.get("end")
                    }
                )
            ]
            
            flights, hotels = await asyncio.gather(*booking_tasks)
            results["flights"] = flights
            results["hotels"] = hotels
            
        elif request_type == "check_weather_route":
            # Get weather and route information
            location = params.get("location")
            destination = params.get("destination")
            
            tasks = [
                self.send_request(
                    "maps",
                    "get_weather_forecast",
                    {"location": location}
                ),
                self.send_request(
                    "maps",
                    "get_route",
                    {
                        "origin": location,
                        "destination": destination,
                        "mode": params.get("mode", "driving")
                    }
                )
            ]
            
            weather, route = await asyncio.gather(*tasks)
            results["weather"] = weather
            results["route"] = route
        
        else:
            results["error"] = f"Unknown request type: {request_type}"
        
        return results
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all MCP servers.
        
        Returns:
            Dictionary with server status information
        """
        status = {}
        for server_type, config in self.server_configs.items():
            is_running = server_type in self.server_processes
            status[server_type] = {
                "name": config["name"],
                "description": config["description"],
                "running": is_running,
                "pid": self.server_processes[server_type].pid if is_running else None
            }
        return status
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Perform health check on all running servers.
        
        Returns:
            Dictionary with health status for each server
        """
        health = {}
        for server_type in self.server_processes:
            try:
                # Send a simple ping request
                response = await self.send_request(
                    server_type,
                    "ping",
                    {}
                )
                health[server_type] = "error" not in response
            except:
                health[server_type] = False
        return health


class MCPOrchestrator:
    """
    High-level orchestrator for managing MCP server operations.
    """
    
    def __init__(self):
        self.manager = MCPServerManager()
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the orchestrator and start all servers.
        
        Returns:
            True if initialization successful
        """
        if self.initialized:
            logger.warning("Orchestrator already initialized")
            return True
        
        logger.info("Initializing MCP Orchestrator...")
        results = await self.manager.start_all_servers()
        
        if all(results.values()):
            self.initialized = True
            logger.info("MCP Orchestrator initialized successfully")
            return True
        else:
            logger.error("Some servers failed to start")
            await self.cleanup()
            return False
    
    async def cleanup(self):
        """Stop all servers and cleanup resources."""
        logger.info("Cleaning up MCP Orchestrator...")
        await self.manager.stop_all_servers()
        self.initialized = False
        logger.info("Cleanup completed")
    
    async def process_travel_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a complex travel request using multiple MCP servers.
        
        Args:
            request: Travel request details
        
        Returns:
            Processed response
        """
        if not self.initialized:
            return {"error": "Orchestrator not initialized"}
        
        request_type = request.get("type", "unknown")
        params = request.get("params", {})
        
        try:
            result = await self.manager.coordinate_request(
                request_type,
                params
            )
            return {
                "success": True,
                "request_id": request.get("id"),
                "type": request_type,
                "data": result
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request.get("id")
            }
    
    @asynccontextmanager
    async def session(self):
        """Context manager for orchestrator session."""
        try:
            await self.initialize()
            yield self
        finally:
            await self.cleanup()


# Example usage and testing
async def main():
    """Example usage of the MCP Orchestrator."""
    orchestrator = MCPOrchestrator()
    
    async with orchestrator.session():
        # Check server status
        status = orchestrator.manager.get_server_status()
        print("Server Status:")
        print(json.dumps(status, indent=2))
        
        # Example travel request
        travel_request = {
            "id": "req_001",
            "type": "plan_trip",
            "params": {
                "destination": "Paris, France",
                "origin": "New York, USA",
                "dates": {
                    "start": "2025-12-15",
                    "end": "2025-12-22"
                }
            }
        }
        
        print("\nProcessing travel request...")
        response = await orchestrator.process_travel_request(travel_request)
        print("Response:")
        print(json.dumps(response, indent=2))
        
        # Health check
        health = await orchestrator.manager.health_check()
        print("\nHealth Check:")
        print(json.dumps(health, indent=2))


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
