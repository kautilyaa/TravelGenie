"""
MCP Server Orchestrator - Manages and coordinates multiple MCP servers
Uses stdio transport for efficient process management
"""

import asyncio
import json
import os
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
    Manages multiple MCP servers using stdio or HTTP/SSE transport.
    Handles server lifecycle, communication, and coordination.
    Supports port and host configuration.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        Initialize MCP Server Manager.
        
        Args:
            config: Optional ServerConfig instance. If None, loads from utils.config
        """
        # Import here to avoid circular imports
        if config is None:
            from utils.config import get_config
            config = get_config().server_config
        
        self.config = config
        self.servers: Dict[str, subprocess.Popen] = {}
        
        # Build server configs from config object, with fallback to defaults
        self.server_configs = {}
        default_configs = {
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
        
        # Merge config with defaults
        for server_type, default in default_configs.items():
            server_cfg = config.servers.get(server_type, {})
            self.server_configs[server_type] = {
                **default,
                **server_cfg,
                "path": server_cfg.get("path", default["path"]),
                "host": server_cfg.get("host", "localhost"),
                "port": server_cfg.get("port", 8000 + list(default_configs.keys()).index(server_type)),
                "transport": server_cfg.get("transport", "stdio")
            }
        
        self.server_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.server_urls: Dict[str, str] = {}  # Store server URLs for HTTP/SSE transport
    
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
            transport = config.get("transport", "stdio")
            host = config.get("host", "localhost")
            port = config.get("port", 8000)
            
            if transport in ["sse", "http"]:
                # Start server with HTTP/SSE transport on specific port
                env = os.environ.copy()
                env["MCP_HOST"] = str(host)
                env["MCP_PORT"] = str(port)
                env["MCP_TRANSPORT"] = transport
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(server_path),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                self.server_urls[server_type] = f"http://{host}:{port}"
                logger.info(f"Started {server_type} server on {host}:{port} with {transport} transport (PID: {process.pid})")
            else:
                # Start server with stdio transport (default, backward compatible)
                # Optionally pass port/host as env vars for future use
                env = os.environ.copy()
                env["MCP_HOST"] = str(host)
                env["MCP_PORT"] = str(port)
                env["MCP_TRANSPORT"] = "stdio"
                
                process = await asyncio.create_subprocess_exec(
                    sys.executable, str(server_path),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                logger.info(f"Started {server_type} server with stdio transport on port {port} (PID: {process.pid})")
            
            self.server_processes[server_type] = process
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
        Send a JSON-RPC request to an MCP server.
        Supports both stdio and HTTP/SSE transports.
        
        Args:
            server_type: Target server type
            method: Method name to call
            params: Optional parameters for the method
        
        Returns:
            Server response
        """
        if server_type not in self.server_processes:
            logger.error(f"Server {server_type} is not running")
            return {
                "error": f"Server {server_type} is not running",
                "error_code": "SERVER_NOT_RUNNING"
            }
        
        config = self.server_configs.get(server_type, {})
        transport = config.get("transport", "stdio")
        
        # Route to appropriate transport method
        if transport in ["sse", "http"]:
            return await self._send_http_request(server_type, method, params)
        else:
            # Default to stdio (backward compatible)
            return await self._send_stdio_request(server_type, method, params)
    
    async def _send_stdio_request(
        self,
        server_type: str,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send request via stdio transport (existing implementation).
        Maintains backward compatibility.
        """
        process = self.server_processes[server_type]
        
        # Check if process is still alive
        if process.returncode is not None:
            logger.error(f"Server {server_type} process has terminated (returncode: {process.returncode})")
            # Remove dead process
            del self.server_processes[server_type]
            return {
                "error": f"Server {server_type} process terminated",
                "error_code": "PROCESS_TERMINATED"
            }
        
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
            if process.stdin is None:
                return {
                    "error": "Server stdin is not available",
                    "error_code": "STDIN_UNAVAILABLE"
                }
            
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response from stdout with timeout
            if process.stdout is None:
                return {
                    "error": "Server stdout is not available",
                    "error_code": "STDOUT_UNAVAILABLE"
                }
            
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=10.0
            )
            
            if not response_line:
                return {
                    "error": "Empty response from server",
                    "error_code": "EMPTY_RESPONSE"
                }
            
            response = json.loads(response_line.decode())
            
            # Check for errors in response
            if "error" in response:
                logger.warning(f"Server returned error: {response['error']}")
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {server_type}.{method}")
            return {
                "error": "Request timeout",
                "error_code": "TIMEOUT",
                "server": server_type,
                "method": method
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from {server_type}: {e}")
            return {
                "error": f"Invalid JSON response: {str(e)}",
                "error_code": "JSON_DECODE_ERROR"
            }
        except BrokenPipeError:
            logger.error(f"Broken pipe to {server_type} server")
            # Remove dead process
            if server_type in self.server_processes:
                del self.server_processes[server_type]
            return {
                "error": "Connection to server lost",
                "error_code": "BROKEN_PIPE"
            }
        except Exception as e:
            logger.error(f"Unexpected error communicating with {server_type}: {e}")
            return {
                "error": str(e),
                "error_code": "UNEXPECTED_ERROR",
                "server": server_type,
                "method": method
            }
    
    async def _send_http_request(
        self,
        server_type: str,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send request via HTTP/SSE transport.
        """
        server_url = self.server_urls.get(server_type)
        if not server_url:
            return {
                "error": "Server URL not found for HTTP transport",
                "error_code": "URL_NOT_FOUND"
            }
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{server_url}/mcp",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        except ImportError:
            logger.error("httpx not installed. Install with: pip install httpx")
            return {
                "error": "HTTP transport requires httpx package",
                "error_code": "MISSING_DEPENDENCY"
            }
        except Exception as e:
            logger.error(f"HTTP request failed for {server_type}: {e}")
            return {
                "error": str(e),
                "error_code": "HTTP_ERROR",
                "server": server_type,
                "method": method
            }
    
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
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all running servers.
        
        Returns:
            Dictionary with detailed health status for each server
        """
        health = {}
        for server_type in list(self.server_processes.keys()):
            process = self.server_processes.get(server_type)
            
            if process is None:
                health[server_type] = {
                    "status": "not_running",
                    "healthy": False
                }
                continue
            
            # Check if process is alive
            if process.returncode is not None:
                health[server_type] = {
                    "status": "terminated",
                    "healthy": False,
                    "returncode": process.returncode
                }
                # Clean up dead process
                del self.server_processes[server_type]
                continue
            
            # Try to send a health check request
            try:
                # Try to list tools as a health check (more reliable than ping)
                # Note: This is a generic check - actual implementation depends on server
                health[server_type] = {
                    "status": "running",
                    "healthy": True,
                    "pid": process.pid
                }
            except Exception as e:
                health[server_type] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
        
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
