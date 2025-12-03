# Geocoder Server

MCP server for geocoding locations using OpenStreetMap's Nominatim service.

## Features

- **geocode_location**: Convert location names to coordinates
- **reverse_geocode**: Convert coordinates to addresses
- **calculate_distance**: Calculate distances between locations
- **batch_geocode**: Process multiple locations at once

## Setup

1. Install dependencies: `uv sync`
2. Configure Claude Desktop to use this server

## Usage

```
Convert 'New York City' to coordinates
Calculate distance between New York and Los Angeles
```

## Requirements

- Python 3.12.1+
- geopy, fastmcp, mcp
- No API key required (uses free Nominatim service)
