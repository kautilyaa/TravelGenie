# MCP Server Port and Host Configuration Guide

This guide explains how to configure MCP servers to run on specific ports and hosts.

## Overview

The MCP servers now support:
- **Port configuration** - Specify which port each server runs on
- **Host configuration** - Specify which host/address to bind to
- **Transport selection** - Choose between `stdio` (default) or `sse` (HTTP/Server-Sent Events)

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set environment variables in your `.env` file:

```env
# Transport Type
MCP_TRANSPORT=stdio  # or "sse" for HTTP transport

# Server Hosts
MCP_ITINERARY_HOST=localhost
MCP_MAPS_HOST=localhost
MCP_BOOKING_HOST=localhost

# Server Ports
MCP_ITINERARY_PORT=8000
MCP_MAPS_PORT=8001
MCP_BOOKING_PORT=8002
```

### Method 2: Configuration File

The `ServerConfig` class in `utils/config.py` automatically reads from environment variables and provides defaults:

- **Default ports**: 8000 (itinerary), 8001 (maps), 8002 (booking)
- **Default host**: localhost
- **Default transport**: stdio

### Method 3: Programmatic Configuration

```python
from utils.config import get_config

config = get_config()
config.server_config.servers["itinerary"]["port"] = 9000
config.server_config.servers["itinerary"]["host"] = "0.0.0.0"
config.server_config.servers["itinerary"]["transport"] = "sse"
```

## Transport Types

### stdio (Default)
- **Description**: Standard input/output transport
- **Use case**: Local development, single process
- **Port**: Configured but not actively used (for future HTTP support)
- **Advantages**: Simple, no network overhead
- **Limitations**: Only works within same process

### sse/http
- **Description**: HTTP/Server-Sent Events transport
- **Use case**: Remote servers, distributed architecture
- **Port**: Actively used - server listens on specified port
- **Advantages**: Can run on remote hosts, network accessible
- **Requirements**: `httpx` package installed

## Usage Examples

### Example 1: Default Configuration (stdio)

```bash
# No configuration needed - uses defaults
streamlit run ui/app.py
```

Servers will run with:
- Transport: stdio
- Ports: 8000, 8001, 8002 (configured but not used)
- Host: localhost

### Example 2: Custom Ports (stdio)

```bash
# Set custom ports in .env
export MCP_ITINERARY_PORT=9000
export MCP_MAPS_PORT=9001
export MCP_BOOKING_PORT=9002

streamlit run ui/app.py
```

### Example 3: HTTP/SSE Transport

```bash
# Enable HTTP transport
export MCP_TRANSPORT=sse
export MCP_ITINERARY_PORT=8000
export MCP_MAPS_PORT=8001
export MCP_BOOKING_PORT=8002

streamlit run ui/app.py
```

Servers will be accessible at:
- `http://localhost:8000` (itinerary)
- `http://localhost:8001` (maps)
- `http://localhost:8002` (booking)

### Example 4: Remote Host Configuration

```bash
# Run on different host
export MCP_ITINERARY_HOST=192.168.1.100
export MCP_ITINERARY_PORT=8000
export MCP_TRANSPORT=sse

streamlit run ui/app.py
```

## Running Servers Manually

You can also run servers manually with port configuration:

```bash
# Set environment variables
export MCP_HOST=localhost
export MCP_PORT=8000
export MCP_TRANSPORT=stdio  # or "sse"

# Run server
python mcp_servers/itinerary_server.py
```

## Checking Server Status

The orchestrator logs server startup information:

```
INFO - Started itinerary server with stdio transport on port 8000 (PID: 12345)
INFO - Started maps server on localhost:8001 with sse transport (PID: 12346)
```

## Backward Compatibility

**All existing code continues to work without changes!**

- Default behavior: stdio transport (no ports needed)
- Existing methods: Unchanged
- New features: Optional port/host configuration

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Use a different port
export MCP_ITINERARY_PORT=9000
```

### HTTP Transport Not Working

```bash
# Install httpx if using HTTP transport
pip install httpx

# Verify transport setting
echo $MCP_TRANSPORT
```

### Server Not Starting

```bash
# Check logs for errors
# Verify port is available
# Check host is correct (use 0.0.0.0 for all interfaces)
```

## Configuration Priority

1. **Environment variables** (highest priority)
2. **Config file** (`config.json`)
3. **Default values** (lowest priority)

## Summary

- ✅ Ports are configurable via environment variables
- ✅ Hosts are configurable via environment variables  
- ✅ Transport type is configurable (stdio or sse)
- ✅ All existing functionality preserved
- ✅ Backward compatible - no breaking changes
- ✅ Defaults work out of the box

For questions or issues, check the logs or review `mcp_servers/orchestrator.py` for implementation details.

