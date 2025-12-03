# Weather Search MCP Server

A Model Context Protocol (MCP) server that provides comprehensive weather data using the Weatherstack API. This server enables Claude to access current weather, forecasts, historical data, and location-based weather comparisons.

## Features

### MCP Tools
- **get_current_weather**: Get real-time weather conditions for any location
- **get_weather_forecast**: Get weather forecasts up to 14 days (Professional Plan required)
- **get_historical_weather**: Access historical weather data back to 2015 (Standard Plan required)
- **search_locations**: Search and autocomplete location names (Standard Plan required)
- **get_weather_details**: Retrieve detailed information from saved weather searches
- **compare_weather**: Compare current weather across multiple locations

### MCP Resources
- **weather://searches**: List all saved weather searches
- **weather://{search_id}**: Get detailed information about a specific weather search

### MCP Prompts
- **weather_analysis_prompt**: Generate comprehensive weather analysis for any location
- **weather_comparison_prompt**: Create detailed weather comparisons across multiple locations

## Prerequisites

1. **Weatherstack API Key**: Sign up at [weatherstack.com](https://weatherstack.com) to get your API key
2. **Python 3.8+**: Ensure Python is installed on your system
3. **UV Package Manager**: Install UV for Python dependency management
4. **Claude Desktop**: For using the MCP server with Claude

## Installation

1. **Clone or download the project files**:
   ```bash
   mkdir weather-search-mcp
   cd weather-search-mcp
   ```

2. **Save the provided files**:
   - `weather_search_mcp.py` (main server code)
   - `pyproject.toml` (project configuration)
   - `server_config.json` (Claude Desktop configuration)

3. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

4. **Set up your Weatherstack API key**:
   - Get your API key from [weatherstack.com/dashboard](https://weatherstack.com/dashboard)
   - Set it as an environment variable:
     ```bash
     export WEATHERSTACK_API_KEY="your_api_key_here"
     ```

## Configuration for Claude Desktop

1. **Update server_config.json**:
   - Replace `/path/to/your/weather-search-mcp` with the actual path to your project directory
   - Replace `your_weatherstack_api_key_here` with your actual API key

2. **Add to Claude Desktop configuration**:
   - Open Claude Desktop settings
   - Navigate to the MCP servers section
   - Add the configuration from `server_config.json`

## Usage Examples

### Basic Weather Queries

```python
# Get current weather
get_current_weather("London, UK")

# Get weather forecast
get_weather_forecast("New York", forecast_days=7, hourly=True)

# Get historical weather
get_historical_weather("Tokyo", "2024-01-15")

# Search for locations
search_locations("Paris")
```

### Advanced Features

```python
# Compare weather across multiple cities
compare_weather(["London", "Paris", "Berlin", "Madrid"])

# Get detailed weather analysis using prompts
weather_analysis_prompt(
    location="San Francisco",
    analysis_type="forecast",
    days=10,
    units="f"
)

# Location comparison for travel planning
weather_comparison_prompt(
    locations=["Bali", "Thailand", "Philippines"],
    comparison_focus="travel",
    units="m"
)
```

### Temperature Units
- `"m"`: Metric (Celsius, km/h, mm)
- `"f"`: Fahrenheit (Fahrenheit, mph, inches)  
- `"s"`: Scientific (Kelvin, km/h, mm)

### Language Support
The API supports 40+ languages. Use ISO language codes:
- `"en"`: English
- `"es"`: Spanish
- `"fr"`: French
- `"de"`: German
- `"zh"`: Chinese
- And many more...

## Weatherstack API Plan Requirements

Different features require different Weatherstack plans:

- **Free Plan**: Current weather only
- **Standard Plan**: Current + Historical + Marine + Location search
- **Professional Plan**: All features + Weather forecasts + Multiple languages
- **Business Plan**: Higher request limits + Priority support

## Data Storage

Weather search results are automatically saved locally in the `weather_data/` directory:
- Each search gets a unique ID
- Data is stored in JSON format
- Use `get_weather_details(search_id)` to retrieve saved data
- Use the `weather://searches` resource to list all searches

## Error Handling

The server handles various error conditions:
- Invalid API keys
- Network connectivity issues
- Invalid location queries
- API rate limit exceeded
- Plan limitations (e.g., forecast on Free plan)

## Example Claude Interactions

**Basic Weather Check**:
```
Get the current weather in Tokyo with temperature in Fahrenheit
```

**Weather Comparison**:
```
Compare the weather in London, Paris, and Berlin right now
```

**Travel Planning**:
```
I'm planning a trip to Southeast Asia. Compare weather in Bangkok, Singapore, and Manila for the next week
```

**Historical Analysis**:
```  
What was the weather like in New York exactly one year ago today?
```

## Development

### Project Structure
```
weather-search-mcp/
├── weather_search_mcp.py    # Main MCP server
├── pyproject.toml          # Project configuration
├── server_config.json      # Claude Desktop config
├── README.md              # This file
└── weather_data/          # Auto-created for storing results
```

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black weather_search_mcp.py
```

## API Reference

### Weatherstack Endpoints Used
- **Current Weather**: `https://api.weatherstack.com/current`
- **Forecast**: `https://api.weatherstack.com/forecast`
- **Historical**: `https://api.weatherstack.com/historical`
- **Autocomplete**: `https://api.weatherstack.com/autocomplete`

### Response Data Includes
- Temperature (current, feels-like, min/max)
- Weather conditions and descriptions
- Wind speed, direction, and gusts
- Humidity and atmospheric pressure
- Visibility and cloud cover
- UV index and sun hours
- Air quality data (CO, NO2, O3, PM2.5, etc.)
- Astronomical data (sunrise, sunset, moon phase)
- Location details (coordinates, timezone)

## Troubleshooting

**API Key Issues**:
- Verify your API key is correct
- Check that the environment variable is set
- Ensure your plan supports the requested features

**Network Issues**:
- Check internet connectivity
- Verify Weatherstack API is accessible
- Check for firewall blocking

**Location Not Found**:
- Try different location formats (city name, coordinates, ZIP code)
- Use the `search_locations` tool to find valid location names
- Check spelling and try more specific location names

## Support

- **Weatherstack API Documentation**: [weatherstack.com/documentation](https://weatherstack.com/documentation)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **FastMCP Documentation**: [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)

## License

MIT License - see the project files for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

Built with ❤️ using FastMCP and the Weatherstack API