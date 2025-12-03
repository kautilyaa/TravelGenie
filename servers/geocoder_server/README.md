# 🗺️ Geocoder MCP Server

A powerful Model Context Protocol (MCP) server that provides comprehensive geocoding capabilities using OpenStreetMap's Nominatim service. Convert location names to coordinates, perform reverse geocoding, calculate distances between points, and efficiently manage your geocoded locations.

![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### Tools
- **`geocode_location`**: Convert location names/addresses to latitude and longitude coordinates
- **`reverse_geocode`**: Convert coordinates back to human-readable addresses
- **`batch_geocode`**: Process multiple locations in a single request
- **`calculate_distance`**: Calculate distances between two geographic points
- **`search_locations`**: Search through previously geocoded locations

### Resources
- **`geocoder://locations`**: List all previously geocoded locations
- **`geocoder://{location_id}`**: Get detailed information about a specific geocoded location

### Prompts
- **`location_analysis_prompt`**: Generate comprehensive location analysis
- **`distance_calculation_prompt`**: Analyze distance and travel between locations
- **`batch_location_prompt`**: Process multiple locations with various analysis options

## Installation

### Prerequisites
- Python 3.8 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone or create the project directory:**
   ```bash
   mkdir geocoder-mcp-server
   cd geocoder-mcp-server
   ```

2. **Save the server files:**
   - Save the server code as `geocoder_server.py`
   - Save the project configuration as `pyproject.toml`

3. **Install dependencies using UV:**
   ```bash
   uv sync
   ```

4. **Test the server:**
   ```bash
   uv run python geocoder_server.py
   ```

## Configuration for Claude Desktop

### Step 1: Update the server_config.json

Replace `/path/to/your/geocoder/project` in the `server_config.json` with the actual path to your project directory:

```json
{
  "mcpServers": {
    "geocoder": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/geocoder-mcp-server",
        "run",
        "python",
        "geocoder_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/geocoder-mcp-server"
      }
    }
  }
}
```

### Step 2: Add to Claude Desktop Configuration

1. **Find your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Merge the server configuration:**
   ```json
   {
     "mcpServers": {
       "geocoder": {
         "command": "uv",
         "args": [
           "--directory",
           "/absolute/path/to/your/geocoder-mcp-server",
           "run",
           "python",
           "geocoder_server.py"
         ],
         "env": {
           "PYTHONPATH": "/absolute/path/to/your/geocoder-mcp-server"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Usage Examples

### Basic Geocoding
```python
# Through Claude Desktop, you can now use:
# "Convert 'Ashburn, Virginia' to coordinates"
# "What are the coordinates of the Eiffel Tower?"
# "Geocode the address '1600 Pennsylvania Avenue, Washington, DC'"
```

### Reverse Geocoding
```python
# "What address is at coordinates 39.0458, -77.5011?"
# "Where is latitude 48.8566, longitude 2.3522?"
```

### Distance Calculations
```python
# "Calculate the distance between New York City and Los Angeles"
# "How far is it from London to Paris?"
```

### Batch Processing
```python
# "Geocode these cities: London, Paris, Rome, Madrid, Berlin"
# "Get coordinates for all US state capitals"
```

## API Reference

### geocode_location(location, exactly_one=True, timeout=10, language="en", addressdetails=True, country_codes=None)

Converts a location name or address to coordinates.

**Parameters:**
- `location` (str): The location to geocode
- `exactly_one` (bool): Return only one result if True
- `timeout` (int): Request timeout in seconds
- `language` (str): Language for results
- `addressdetails` (bool): Include detailed address components
- `country_codes` (str): Limit search to specific countries (e.g., "us,ca")

**Returns:**
- Dictionary with geocoding results including coordinates, address, and metadata

### reverse_geocode(latitude, longitude, exactly_one=True, timeout=10, language="en", zoom=18)

Converts coordinates to a human-readable address.

**Parameters:**
- `latitude` (float): Latitude coordinate
- `longitude` (float): Longitude coordinate
- `exactly_one` (bool): Return only one result
- `timeout` (int): Request timeout in seconds
- `language` (str): Language for results
- `zoom` (int): Level of detail (1-18, higher = more detailed)

### calculate_distance(lat1, lon1, lat2, lon2, unit="km")

Calculates distance between two geographic points.

**Parameters:**
- `lat1`, `lon1` (float): First point coordinates
- `lat2`, `lon2` (float): Second point coordinates
- `unit` (str): Distance unit ("km", "miles", "nm")

## Data Storage

The server stores geocoded results in the `geocoded_locations/` directory as JSON files. This allows for:
- Persistent storage of geocoding results
- Quick access to previously geocoded locations
- Resource-based browsing of location data

## Rate Limiting

The server implements automatic rate limiting to comply with Nominatim's usage policy:
- Minimum 1-second delay between requests
- Unique user agent for each session
- Respectful usage of the free Nominatim service

## Troubleshooting

### Common Issues

1. **Server won't start:**
   - Check Python version (3.8+ required)
   - Ensure all dependencies are installed: `uv sync`
   - Verify file paths in configuration

2. **Geocoding fails:**
   - Check internet connection
   - Verify location spelling and format
   - Try with more specific address details

3. **Claude Desktop doesn't recognize server:**
   - Verify absolute paths in config file
   - Restart Claude Desktop after config changes
   - Check server logs for errors

### Debug Mode

Run the server directly to see error messages:
```bash
uv run python geocoder_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses [OpenStreetMap](https://www.openstreetmap.org/) data via [Nominatim](https://nominatim.openstreetmap.org/)
- Built with [FastMCP](https://github.com/pydantic/fastmcp)
- Geocoding powered by [GeoPy](https://github.com/geopy/geopy)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [MCP specification](https://spec.modelcontextprotocol.io/)
3. Open an issue in the project repository