# Event Search MCP Server

An MCP (Model Context Protocol) server that enables Claude to search for events using SerpAPI's Google Events API. This server provides comprehensive event discovery capabilities including searching, filtering, and analyzing events by location, date, type, and venue.

## Features

### Tools
- **search_events**: Search for events by query, location, date, and type
- **get_event_details**: Retrieve detailed information about searched events
- **filter_events_by_date**: Filter events by date ranges (today, tomorrow, week, etc.)
- **filter_events_by_type**: Filter events by category (concerts, festivals, etc.)
- **filter_events_by_venue**: Filter events by specific venues

### Resources
- **events://searches**: List all saved event searches
- **events://{search_id}**: Get detailed information about a specific search

### Prompts
- **event_discovery_prompt**: Generate comprehensive event discovery queries
- **event_comparison_prompt**: Analyze and compare events from searches

## Prerequisites

1. **Python 3.8+**
2. **UV** (Ultra-fast Python package installer)
3. **SerpAPI Account** with API key
4. **Claude Desktop** application

## Installation

### 1. Install UV
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone/Create Project Directory
```bash
mkdir event-search-mcp-server
cd event-search-mcp-server
```

### 3. Create Project Files
Save the provided files in your project directory:
- `event_search_server.py` (main server code)
- `pyproject.toml` (project configuration)
- `requirements.txt` (dependencies)

### 4. Get SerpAPI Key
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Note your API key for the next step

### 5. Install Dependencies
```bash
uv sync
```

## Configuration

### 1. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**On macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**On Windows:**
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

Add the server configuration:

```json
{
  "mcpServers": {
    "event-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/full/path/to/your/event-search-mcp-server",
        "run",
        "python",
        "event_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_actual_serpapi_key_here"
      }
    }
  }
}
```

**Important:** Replace `/full/path/to/your/event-search-mcp-server` with the actual full path to your project directory and `your_actual_serpapi_key_here` with your SerpAPI key.

### 2. Restart Claude Desktop
Close and restart Claude Desktop for the changes to take effect.

## Usage

Once configured, you can use the event search functionality in Claude Desktop:

### Basic Event Search
```
Search for concerts in New York this weekend
```

### Filtered Event Search
```
Find virtual events today in San Francisco
```

### Event Analysis
```
Compare different festivals in Austin this month and recommend the best ones
```

### Advanced Usage
```
Help me plan my weekend - find art exhibitions and food festivals in Chicago, then analyze which ones would work best for a date
```

## API Parameters

### search_events
- `query` (required): Search query for events
- `location` (optional): Location to search in
- `date_filter` (optional): Time filter (today, tomorrow, week, weekend, next_week, month, next_month)
- `event_type` (optional): Event type (Virtual-Event for online events)
- `language` (optional): Language code (default: 'en')
- `country` (optional): Country code (default: 'us')
- `max_results` (optional): Maximum results to return (default: 20)

### Date Filters Available
- `today`: Today's events
- `tomorrow`: Tomorrow's events
- `week`: This week's events
- `weekend`: This weekend's events
- `next_week`: Next week's events
- `month`: This month's events
- `next_month`: Next month's events

### Event Types
- `Virtual-Event`: Online/virtual events
- Mix with date filters: `Virtual-Event,date:today`

## Project Structure

```
event-search-mcp-server/
├── event_search_server.py      # Main server code
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── events/                     # Created automatically
│   └── *.json                 # Stored search results
└── claude_desktop_config.json  # Example configuration
```

## Troubleshooting

### Server Not Connecting
1. Check that the path in `claude_desktop_config.json` is correct and absolute
2. Ensure your SerpAPI key is valid and has remaining credits
3. Verify UV is installed correctly: `uv --version`
4. Check Claude Desktop logs for error messages

### API Errors
1. Verify your SerpAPI key is correct
2. Check your SerpAPI account has remaining credits
3. Ensure you have internet connectivity

### No Events Found
1. Try broader search terms
2. Remove location constraints
3. Check if the location name is spelled correctly
4. Try different date filters

## Example Queries

### Finding Local Events
- "What concerts are happening in Seattle this month?"
- "Find art galleries and museums events in Portland this weekend"
- "Show me food festivals in Austin next month"

### Virtual Events
- "Search for online networking events today"
- "Find virtual conferences this week"

### Event Planning
- "Help me plan a cultural weekend in Boston - find theater, music, and art events"
- "Compare different music festivals in Chicago and recommend the best value"

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
```

### Linting
```bash
uv run flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review SerpAPI documentation
3. Check Claude Desktop MCP documentation
4. Create an issue in the project repository