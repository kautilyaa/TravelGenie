# Travel Assistant MCP Server

A comprehensive travel planning MCP (Model Context Protocol) server that integrates with SerpAPI's Google Flights API to search for flights, analyze options, and provide travel recommendations.

## Features

### MCP Tools
- **search_flights**: Search for flights between two locations with comprehensive filtering options
- **get_flight_details**: Retrieve detailed information about a specific flight search
- **filter_flights_by_price**: Filter flights by price range
- **filter_flights_by_airline**: Filter flights by specific airlines

### MCP Resources
- **flights://searches**: List all saved flight searches
- **flights://{search_id}**: Get detailed information about a specific flight search

### MCP Prompts
- **travel_planning_prompt**: Generate comprehensive travel planning workflows
- **flight_comparison_prompt**: Create detailed flight comparison and analysis prompts

## Setup Instructions

### Prerequisites
1. **SerpAPI Account**: Sign up at [SerpAPI](https://serpapi.com/) and get your API key
2. **Python 3.8+**: Ensure you have Python installed
3. **Claude Desktop**: Install Claude Desktop application

### Installation

1. **Clone or create the project directory**:
```bash
mkdir travel-assistant
cd travel-assistant
```

2. **Create the files**: Save the provided `travel_assistant.py` file in your project directory

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variable**:
   - **Option 1**: Create a `.env` file:
   ```bash
   echo "SERPAPI_KEY=your_actual_serpapi_key_here" > .env
   ```
   
   - **Option 2**: Set environment variable directly:
   ```bash
   export SERPAPI_KEY=your_actual_serpapi_key_here
   ```

5. **Configure Claude Desktop**:
   - Open Claude Desktop
   - Go to Settings → Developer → MCP Servers
   - Add the server configuration from `server_config.json`
   - Update the `cwd` path to your actual project directory
   - Update the `SERPAPI_KEY` with your actual API key

### Claude Desktop Configuration

Update your Claude Desktop configuration file (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "travel-assistant": {
      "command": "python",
      "args": [
        "travel_assistant.py"
      ],
      "cwd": "/path/to/your/travel-assistant",
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

## Usage Examples

### Basic Flight Search
```
Search for flights from JFK to LAX departing on 2024-12-15 and returning on 2024-12-22 for 2 adults
```

### Advanced Flight Search with Preferences
```
Find business class flights from London (LHR) to Tokyo (NRT) for one passenger, departing January 10, 2025, one way trip, budget around $3000
```

### Using the Travel Planning Prompt
```
@travel_planning_prompt departure="New York" destination="Paris" departure_date="2024-12-20" return_date="2024-12-27" passengers=2 budget="$2000 per person" preferences="prefer direct flights, flexible with times"
```

### Flight Analysis and Comparison
After getting a search_id from a flight search:
```
@flight_comparison_prompt search_id="JFK_LAX_2024-12-15_2024-12-22_20241128_143022"
```

## API Parameters

### search_flights Tool Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| departure_id | str | Required | Departure airport code (e.g., 'JFK', 'LAX') |
| arrival_id | str | Required | Arrival airport code (e.g., 'CDG', 'NRT') |
| outbound_date | str | Required | Departure date (YYYY-MM-DD format) |
| return_date | str | Optional | Return date (required for round trips) |
| trip_type | int | 1 | 1=Round trip, 2=One way, 3=Multi-city |
| adults | int | 1 | Number of adult passengers |
| children | int | 0 | Number of child passengers |
| infants_in_seat | int | 0 | Number of infants in seat |
| infants_on_lap | int | 0 | Number of infants on lap |
| travel_class | int | 1 | 1=Economy, 2=Premium economy, 3=Business, 4=First |
| currency | str | 'USD' | Currency for prices |
| country | str | 'us' | Country code for search |
| language | str | 'en' | Language code |
| max_results | int | 10 | Maximum number of results to store |

### Common Airport Codes
- **New York**: JFK, LGA, EWR
- **Los Angeles**: LAX
- **London**: LHR, LGW, STN
- **Paris**: CDG, ORY
- **Tokyo**: NRT, HND
- **Sydney**: SYD
- **Dubai**: DXB

## Features Supported

### Flight Search Capabilities
- Round trip, one way, and multi-city flights
- Multiple passenger types (adults, children, infants)
- All travel classes (Economy to First)
- Currency and localization support
- Comprehensive flight details including:
  - Flight times and durations
  - Airlines and aircraft types
  - Layover information
  - Carbon emissions data
  - Price insights and trends

### Data Storage and Retrieval
- Persistent storage of flight searches
- Unique search identifiers for easy retrieval
- JSON-based data structure for easy processing
- Comprehensive metadata tracking

### Filtering and Analysis
- Price range filtering
- Airline-specific filtering
- Best vs. other flights categorization
- Price insights and trends
- Carbon emissions analysis

## File Structure
```
travel-assistant/
├── travel_assistant.py      # Main MCP server file
├── requirements.txt         # Python dependencies
├── server_config.json       # Claude Desktop configuration
├── README.md               # This file
└── flights/                # Directory for storing flight search results (created automatically)
    ├── search_id_1.json
    ├── search_id_2.json
    └── ...
```

## Troubleshooting

### Common Issues

1. **"SERPAPI_KEY environment variable is required"**
   - Ensure your SerpAPI key is set in the environment variables
   - Check that the key is correctly specified in the server configuration

2. **"API request failed"**
   - Verify your SerpAPI key is valid and has remaining credits
   - Check your internet connection
   - Ensure airport codes are valid (3-letter IATA codes)

3. **"No flight search found with ID"**
   - Verify the search_id is correct
   - Check that the flights directory exists and contains the search file

### Getting Help
- Check the SerpAPI documentation: https://serpapi.com/google-flights-api
- Verify airport codes: https://www.iata.org/en/publications/directories/code-search/
- Ensure your MCP server configuration matches your actual file paths

## License
This project is provided as-is for educational and personal use. Please ensure compliance with SerpAPI's terms of service when using their API.