"""
Main entry point for the weather server MCP.
This file can be used to run the server directly if needed.
"""

if __name__ == "__main__":
    from weather_server import mcp
    mcp.run(transport='stdio')
