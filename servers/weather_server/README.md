# Weather Search MCP Server

A comprehensive Model Context Protocol (MCP) server that provides weather information using the National Weather Service API. This server allows Claude to access current weather conditions, forecasts, and weather alerts for any location in the United States.

## Features

### 🛠️ MCP Tools
- **`get_location_info`**: Get grid coordinates and weather station information for any latitude/longitude
- **`get_current_conditions`**: Retrieve current weather observations from nearby weather stations
- **`get_weather_forecast`**: Get daily or hourly weather forecasts for specific locations
- **`get_weather_alerts`**: Search for weather alerts by area, severity, urgency, and other filters
- **`get_weather_data_details`**: Retrieve detailed information from previous weather searches
- **`filter_forecast_by_conditions`**: Filter forecast data by temperature, precipitation, and wind conditions

### 📖 MCP Resources
- **`weather://searches`**: Browse all saved weather searches
- **`weather://{search_id}`**: Get detailed information about specific weather searches

### 🎯 MCP Prompts
- **`weather_planning_prompt`**: Comprehensive weather planning for activities and events
- **`severe_weather_alert_prompt`**: Detailed severe weather monitoring and safety recommendations

## Installation

### Prerequisites
- Python 3.11 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- Claude Desktop application

### Setup

1. **Clone or create the project directory:**
```bash
mkdir weather-search-mcp
cd weather-search-mcp
```

2. **Create the server files:**
   - Save the main server code as `weather_search_server.py`
   - Save the pyproject.toml configuration
   - Save the server_config.json (update the path)

3. **Install dependencies using UV:**
```bash
uv install
```

4. **Configure Claude Desktop:**
   - Open Claude Desktop
   - Go to Settings → Developer
   - Edit your `server_config.json` file (typically located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS)
   - Update the `cwd` path in the configuration to point to your project directory

5. **Restart Claude Desktop** to load the new MCP server

## Configuration

### Server Config for Claude Desktop

Update your Claude Desktop configuration file with the correct path:

```json
{
  "mcpServers": {
    "weather-search": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "3.11",
        "weather_search_server.py"
      ],
      "cwd": "/path/to/your/weather-search-mcp",
      "env": {
        "PYTHONPATH": "/path/to/your/weather-search-mcp"
      }
    }
  }
}
```

Replace `/path/to/your/weather-search-mcp` with the actual path to your project directory.

## Usage Examples

### Getting Current Weather Conditions

```
What's the current weather in San Francisco, California?
```

The server will:
1. Convert the location to coordinates (37.7749, -122.4194)
2. Find nearby weather stations
3. Retrieve current observations
4. Provide temperature, humidity, wind, pressure, and other conditions

### Getting Weather Forecasts

```
Give me a 7-day forecast for Denver, Colorado with hourly details for tomorrow.
```

The server will:
1. Get location coordinates and grid information
2. Retrieve both daily and hourly forecasts
3. Present organized forecast data with temperatures, precipitation chances, and conditions

### Monitoring Weather Alerts

```
Check for any severe weather alerts in Kansas and provide safety recommendations.
```

The server will:
1. Query active alerts for Kansas (area=KS)
2. Analyze severity and urgency levels
3. Provide detailed safety recommendations

### Weather Activity Planning

```
Plan outdoor activities for next weekend in Austin, Texas. I'm considering hiking and barbecuing.
```

The server will use the weather planning prompt to:
1. Get comprehensive forecast data
2. Analyze conditions for outdoor activities
3. Recommend optimal timing for hiking and barbecuing
4. Suggest necessary preparations

## API Endpoints Used

The server utilizes the following National Weather Service API endpoints:

- **Points**: `https://api.weather.gov/points/{lat},{lon}` - Location and grid information
- **Gridpoint Forecasts**: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast` - Daily forecasts
- **Hourly Forecasts**: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast/hourly` - Hourly forecasts
- **Observations**: `https://api.weather.gov/stations/{stationId}/observations/latest` - Current conditions
- **Alerts**: `https://api.weather.gov/alerts` - Weather alerts and warnings

## Data Storage

The server automatically saves all weather searches to the `weather_data/` directory as JSON files. This allows for:
- Historical weather data reference
- Filtering and analysis of past searches
- Caching to improve performance
- Data persistence across sessions

## Rate Limiting

The National Weather Service API has reasonable rate limits for typical use. The server includes:
- Proper User-Agent headers as required by NWS
- Error handling for rate limit responses
- Retry logic with exponential backoff
- Request timeout handling

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid coordinates or locations
- Missing or corrupted data
- File system errors

## Development

### Running in Development Mode

```bash
# Install development dependencies
uv install --dev

# Run the server directly
uv run weather_search_server.py

# Run with debugging
PYTHONPATH=. uv run weather_search_server.py
```

### Code Quality Tools

```bash
# Format code
uv run black weather_search_server.py

# Sort imports
uv run isort weather_search_server.py

# Type checking
uv run mypy weather_search_server.py

# Run tests
uv run pytest
```

## Troubleshooting

### Common Issues

1. **Server not loading in Claude Desktop:**
   - Check that the `cwd` path in server_config.json is correct
   - Ensure UV is installed and accessible
   - Restart Claude Desktop after configuration changes

2. **API request failures:**
   - Check internet connectivity
   - Verify the National Weather Service API is accessible
   - Check for rate limiting (wait 5 seconds and retry)

3. **Location not found:**
   - Ensure coordinates are within the United States
   - Try different coordinate formats (decimal degrees)
   - Check that the location has nearby weather stations

### Debug Logging

The server includes console logging for debugging. Check the Claude Desktop logs or run the server directly to see detailed error messages.

## API Reference

### National Weather Service API Documentation
- [Main Documentation](https://www.weather.gov/documentation/services-web-api)
- [API Specification](https://api.weather.gov/openapi.json)
- [GitHub Repository](https://github.com/weather-gov/api)

### Data Formats
- All timestamps are in ISO-8601 format
- Coordinates use decimal degrees (WGS84)
- Temperature units vary by endpoint (Celsius for observations, Fahrenheit for forecasts)
- Wind speeds in various units (km/h, mph, m/s)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run code quality checks
6. Submit a pull request

## License

This project is open source and available under the MIT License. The National Weather Service API is provided by NOAA as a public service.

## Support

For issues related to:
- **This MCP Server**: Create an issue in the project repository
- **National Weather Service API**: Contact nco.ops@noaa.gov
- **Claude Desktop**: Visit the Anthropic support documentation

---

**Note**: This server provides weather data for locations within the United States and its territories. For international weather data, consider using additional weather APIs or services.