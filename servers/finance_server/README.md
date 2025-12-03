# Finance Search MCP Server

A Model Context Protocol (MCP) server that provides financial data and analysis capabilities using SerpAPI's Google Finance API. This server enables currency conversion, stock price lookup, market overview, and historical data analysis.

## Features

### 🔧 MCP Tools
- **`lookup_stock`** - Get current stock information and price data
- **`convert_currency`** - Convert between different currencies with real-time rates
- **`get_market_overview`** - Retrieve overview of major markets (US, Europe, Asia, crypto, etc.)
- **`get_historical_data`** - Fetch historical price data with customizable time windows
- **`get_finance_details`** - Get detailed information about previous searches
- **`filter_stocks_by_price_movement`** - Filter market data by price movement criteria

### 📋 MCP Resources
- **`finance://searches`** - List all finance searches with metadata
- **`finance://{search_id}`** - Detailed view of specific finance search results

### 🎯 MCP Prompts
- **`stock_analysis_prompt`** - Comprehensive stock analysis template
- **`currency_analysis_prompt`** - Multi-currency analysis and conversion template  
- **`market_overview_prompt`** - Market overview analysis template

## Prerequisites

- Python 3.8 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- SerpAPI account and API key
- Claude Desktop (for MCP integration)

## Installation

### 1. Clone/Download the Server Code
Save the `finance_search_server.py` file to your desired directory.

### 2. Set up the Project
```bash
# Navigate to your server directory
cd /path/to/finance-search-server

# Initialize UV project (if not already done)
uv init

# Install dependencies
uv add fastmcp requests mcp
```

### 3. Get SerpAPI Key
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Set it as an environment variable:
   ```bash
   export SERPAPI_KEY="your_serpapi_key_here"
   ```

### 4. Configure Claude Desktop
Add the server configuration to your Claude Desktop config file.

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "finance-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/finance-search-server",
        "run",
        "python",
        "finance_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/finance-search-server` with the actual path to your server directory.

### 5. Restart Claude Desktop
Restart Claude Desktop to load the new MCP server.

## Usage Examples

### Stock Analysis
```
Can you analyze AAPL stock over the past year? Include current price, historical performance, and key events.
```

### Currency Conversion
```
Convert $1,000 USD to EUR, GBP, and JPY. Show me the current exchange rates and recent trends.
```

### Market Overview
```
Give me an overview of current market conditions across US, European, and Asian markets.
```

### Historical Analysis
```
Show me the 5-year historical data for Tesla (TSLA) including key events that affected the stock price.
```

## API Coverage

The server utilizes SerpAPI's Google Finance API to provide:

- **Stock Data**: Current prices, historical data, company information, financial statements
- **Currency Exchange**: Real-time exchange rates and conversion
- **Market Data**: Major indices, crypto, futures, and regional markets
- **News & Events**: Financial news and key events affecting stock prices
- **Technical Data**: Price charts, volume data, and market statistics

## Supported Queries

### Stock Symbols
- Format: `SYMBOL:EXCHANGE` (e.g., `GOOGL:NASDAQ`, `AAPL:NASDAQ`)
- Major exchanges: NYSE, NASDAQ, LSE, TSE, etc.

### Currency Pairs
- Format: `FROM-TO` (e.g., `USD-EUR`, `GBP-USD`, `BTC-USD`)
- Supports major fiat currencies and cryptocurrencies

### Time Windows
- `1D`, `5D`, `1M`, `6M`, `1Y`, `5Y`, `MAX`

## Data Storage

The server stores search results locally in a `finance/` directory:
- Each search gets a unique ID and timestamp
- Results are saved as JSON files for later retrieval
- Use `get_finance_details` tool to access stored data

## Error Handling

The server includes comprehensive error handling for:
- Invalid API keys
- Network connectivity issues
- Invalid stock symbols or currency codes
- Rate limiting and API quota management
- Malformed requests

## Development

### Project Structure
```
finance-search-server/
├── finance_search_server.py    # Main server code
├── pyproject.toml             # UV project configuration
├── finance/                   # Stored search results (created automatically)
└── README.md                  # This file
```

### Running Locally
```bash
# Run the server directly
uv run python finance_search_server.py

# Or activate the environment and run
uv shell
python finance_search_server.py
```

### Testing
```bash
# Install dev dependencies
uv add --dev pytest black flake8

# Run tests (if you create them)
uv run pytest

# Format code
uv run black finance_search_server.py
```

## Troubleshooting

### Common Issues

1. **"SERPAPI_KEY environment variable is required"**
   - Make sure your SerpAPI key is set in the environment
   - Check the Claude Desktop config has the correct key

2. **"No finance search found with ID"**
   - The search ID doesn't exist or the file was deleted
   - Use `finance://searches` resource to list available searches

3. **Server not appearing in Claude**
   - Check the path in `claude_desktop_config.json` is correct
   - Restart Claude Desktop after configuration changes
   - Check UV is installed and accessible

4. **API request failures**
   - Verify your SerpAPI key is valid and has remaining quota
   - Check internet connectivity
   - Some symbols may not be available in Google Finance

### Debugging
Enable detailed logging by setting:
```bash
export PYTHONPATH="/path/to/your/server"
export DEBUG=1
```

## API Rate Limits

SerpAPI has different rate limits based on your plan:
- Free plan: 100 searches/month
- Paid plans: Higher limits available

The server respects rate limits and will return appropriate error messages when limits are exceeded.

## Contributing

Feel free to extend the server with additional features:
- More financial indicators and calculations
- Additional data sources
- Enhanced filtering capabilities
- Portfolio tracking features

## License

This server is provided as-is for educational and development purposes. Please respect SerpAPI's terms of service and rate limits.