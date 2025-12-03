# Event Server

MCP server for searching events and activities using SerpAPI's Google Events API.

## Features

- **search_events**: Search events by query, location, date filter
- **get_event_details**: Get detailed event information
- **filter_events_by_date**: Filter by date ranges (today, week, month, etc.)
- **filter_events_by_type**: Filter by category (concerts, festivals, etc.)
- **filter_events_by_venue**: Filter by specific venues

## Setup

1. Install dependencies: `uv sync`
2. Set `SERPAPI_KEY` environment variable
3. Configure Claude Desktop to use this server

## Usage

```
Search for concerts in New York this weekend
```

## Requirements

- Python 3.12.1+
- SerpAPI key
- fastmcp, mcp, requests
