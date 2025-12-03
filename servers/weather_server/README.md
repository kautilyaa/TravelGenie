# Weather Server

MCP server for weather forecasts and current conditions using Open-Meteo API.

## Features

- **get_current_weather**: Get current weather conditions
- **get_weather_forecast**: Get daily or hourly forecasts (up to 16 days)
- **get_location_info**: Get grid coordinates for locations
- **get_weather_alerts**: Search for weather alerts
- **filter_forecast_by_conditions**: Filter by temperature, precipitation, wind

## Setup

1. Install dependencies: `uv sync`
2. Configure Claude Desktop to use this server

## Usage

```
What's the current weather in San Francisco?
Give me a 7-day forecast for Denver, Colorado
```

## Requirements

- Python 3.12.1+
- fastmcp, mcp, requests
- No API key required (uses free Open-Meteo API)
