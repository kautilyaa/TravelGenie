# Hotel Search MCP Server

A comprehensive Model Context Protocol (MCP) server for hotel and vacation rental search using SerpAPI's Google Hotels API. This server provides powerful tools for finding, filtering, and analyzing accommodation options through Claude Desktop.

## Features

### 🏨 Core Search Capabilities
- **Comprehensive Hotel Search**: Search hotels and vacation rentals by location, dates, and guest count
- **Advanced Filtering**: Filter by price, rating, amenities, hotel class, and more
- **Property Details**: Get detailed information about specific properties
- **Multiple Property Types**: Support for hotels, resorts, and vacation rentals

### 🔧 MCP Tools
- `search_hotels`: Main search functionality with extensive parameters
- `get_hotel_details`: Retrieve detailed search results
- `get_property_details`: Get comprehensive property information using property tokens
- `filter_hotels_by_price`: Filter results by price range
- `filter_hotels_by_rating`: Filter by minimum rating
- `filter_hotels_by_amenities`: Filter by required amenities
- `filter_hotels_by_class`: Filter by hotel star rating

### 📚 MCP Resources
- `hotels://searches`: List all saved hotel searches
- `hotels://{search_id}`: Get detailed information about a specific search

### 🎯 MCP Prompts
- `hotel_planning_prompt`: Comprehensive hotel planning assistance
- `hotel_comparison_prompt`: Detailed hotel comparison and analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- UV (Python package manager)
- SerpAPI account and API key

### Setup Steps

1. **Clone or download the server files**
   ```bash
   mkdir hotel-search-server
   cd hotel-search-server
   ```

2. **Create the main server file**
   Save the hotel search server code as `hotel_search_server.py`

3. **Create project configuration**
   Save the pyproject.toml configuration file

4. **Install dependencies using UV**
   ```bash
   uv sync
   ```

5. **Get your SerpAPI key**
   - Sign up at [SerpAPI](https://serpapi.com/)
   - Get your API key from the dashboard
   - Free tier includes 100 searches per month

6. **Set up environment variables**
   Create a `.env` file:
   ```bash
   SERPAPI_KEY=your_serpapi_key_here
   ```

## Configuration for Claude Desktop

### Server Configuration

Add to your Claude Desktop `server_config.json`:

```json
{
  "mcpServers": {
    "hotel-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/hotel-search-server",
        "run",
        "python",
        "hotel_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_actual_serpapi_key_here"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/hotel-search-server` with the actual path to your server directory and `your_actual_serpapi_key_here` with your real SerpAPI key.

### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Usage Examples

### Basic Hotel Search

```
Search for hotels in Paris from June 15-20, 2025 for 2 adults
```

This will use the `search_hotels` tool with parameters:
- location: "Paris"
- check_in_date: "2025-06-15"
- check_out_date: "2025-06-20"
- adults: 2

### Advanced Search with Filters

```
Find luxury 5-star hotels in Bali from July 10-17, 2025 for 2 adults and 1 child, 
with pool, spa, and free WiFi amenities, budget under $500 per night
```

### Property Details and Comparison

```
Get detailed information about the top 3 hotels from my last search and compare their amenities, location ratings, and pricing
```

### Vacation Rental Search

```
Search for vacation rentals in Tuscany for a family of 4, 
minimum 2 bedrooms, from August 5-12, 2025
```

## API Parameters Reference

### Main Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `location` | string | Search location | "New York", "Bali Resorts" |
| `check_in_date` | string | Check-in date (YYYY-MM-DD) | "2025-06-15" |
| `check_out_date` | string | Check-out date (YYYY-MM-DD) | "2025-06-20" |
| `adults` | int | Number of adults | 2 |
| `children` | int | Number of children | 1 |
| `currency` | string | Price currency | "USD", "EUR", "GBP" |

### Filter Parameters

| Parameter | Type | Description | Values |
|-----------|------|-------------|---------|
| `sort_by` | int | Sort results | 3=Lowest price, 8=Highest rating, 13=Most reviewed |
| `hotel_class` | list[int] | Hotel star rating | [3, 4, 5] |
| `free_cancellation` | bool | Free cancellation only | true/false |
| `special_offers` | bool | Special offers only | true/false |
| `vacation_rentals` | bool | Search vacation rentals | true/false |

### Common Amenity Examples

- Free Wi-Fi
- Pool / Pools
- Spa
- Fitness center / Gym
- Free parking
- Airport shuttle
- Beach access
- Restaurant
- Bar
- Room service
- Air conditioning
- Pet-friendly

## Response Data Structure

### Hotel Property Data

Each hotel result includes:
- **Basic Info**: Name, type, description, star rating
- **Pricing**: Rate per night, total rate, before/after taxes
- **Location**: GPS coordinates, nearby places, location rating
- **Quality**: Overall rating, review count, rating breakdown
- **Amenities**: Available and excluded amenities
- **Images**: Thumbnail and original image URLs
- **Details**: Check-in/out times, contact information

### Search Metadata

Each search includes:
- Search ID for referencing results
- Search parameters and filters applied
- Total properties found
- Price range analysis
- Search timestamp

## Error Handling

The server includes comprehensive error handling for:
- Invalid API keys
- Network connectivity issues
- Invalid date formats
- Missing required parameters
- API rate limits
- Malformed search queries

## File Storage

Search results are automatically saved as JSON files in the `hotels/` directory:
- Enables offline analysis of previous searches
- Supports comparison across multiple searches
- Provides data persistence for filtering operations

## Advanced Features

### Property Token System
- Each property has a unique token for detailed information
- Use `get_property_details` for comprehensive property data
- Includes pricing from multiple booking sources

### Filtering Pipeline
- Chain multiple filters for precise results
- Price range filtering
- Rating threshold filtering
- Amenity requirement filtering
- Hotel class filtering

### Multi-Source Pricing
- Compares prices across booking platforms
- Shows before/after taxes and fees
- Identifies special deals and offers

## Best Practices

1. **Specific Locations**: Use specific location names for better results
2. **Realistic Date Ranges**: Search within reasonable future dates
3. **Filter Progressively**: Start broad, then apply filters to narrow results
4. **Check Multiple Sources**: Use property details to compare booking sources
5. **Consider Total Costs**: Factor in taxes, fees, and additional costs

## Troubleshooting

### Common Issues

**"SERPAPI_KEY environment variable is required"**
- Ensure your API key is set in the environment variables
- Check the server_config.json has the correct SERPAPI_KEY

**"No hotel search found with ID"**
- Verify the search ID is correct
- Check if the hotels directory exists and has the JSON file

**API rate limits**
- SerpAPI free tier: 100 searches/month
- Consider upgrading for higher usage
- Implement caching strategies for repeated searches

**No results found**
- Try broader location terms
- Check date formats (YYYY-MM-DD)
- Verify location name spelling

## Support and Documentation

- [SerpAPI Google Hotels API Documentation](https://serpapi.com/google-hotels-api)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## Contributing

Feel free to submit issues, feature requests, or improvements to this MCP server. The codebase is designed to be easily extensible for additional hotel search features.

## License

This project is available under the MIT License. See individual dependencies for their respective licenses.