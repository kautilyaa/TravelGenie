# Hotel Server

MCP server for searching hotels and vacation rentals using SerpAPI's Google Hotels API.

## Features

- **search_hotels**: Search hotels by location, dates, guests
- **get_hotel_details**: Get detailed property information
- **filter_hotels_by_price**: Filter by price range
- **filter_hotels_by_rating**: Filter by minimum rating
- **filter_hotels_by_amenities**: Filter by required amenities
- **filter_hotels_by_class**: Filter by hotel star rating

## Setup

1. Install dependencies: `uv sync`
2. Set `SERPAPI_KEY` environment variable
3. Configure Claude Desktop to use this server

## Usage

```
Search for hotels in Paris from June 15-20, 2025 for 2 adults
```

## Requirements

- Python 3.12.1+
- SerpAPI key
- fastmcp, mcp, requests
