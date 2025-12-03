"""
Main entry point for the traffic & crowd server MCP.
This file can be used to run the server directly if needed.
"""

if __name__ == "__main__":
    from traffic_crowd_server import mcp
    mcp.run(transport='stdio')

