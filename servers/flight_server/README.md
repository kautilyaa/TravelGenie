# Flight Server

MCP server for searching flights using SerpAPI's Google Flights API.

## Features

- **search_flights**: Search flights by departure/arrival, dates, passengers
- **get_flight_details**: Get detailed flight information
- **filter_flights_by_price**: Filter flights by price range
- **filter_flights_by_airline**: Filter by specific airlines

## Setup

1. Install dependencies: `uv sync`
2. Set `SERPAPI_KEY` environment variable
3. Configure Claude Desktop to use this server

## Usage

```
Search for flights from JFK to LAX departing 2025-06-15, returning 2025-06-22 for 2 adults
```

## Requirements

- Python 3.12.1+
- SerpAPI key
- fastmcp, mcp, requests

