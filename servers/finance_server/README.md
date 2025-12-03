# Finance Server

MCP server for financial data using SerpAPI's Google Finance API.

## Features

- **convert_currency**: Convert between currencies with real-time rates
- **lookup_stock**: Get stock information and prices
- **get_market_overview**: Get overview of major markets (US, Europe, Asia, crypto)
- **get_historical_data**: Fetch historical price data
- **filter_stocks_by_price_movement**: Filter market data by price movement

## Setup

1. Install dependencies: `uv sync`
2. Set `SERPAPI_KEY` environment variable
3. Configure Claude Desktop to use this server

## Usage

```
Convert $1,000 USD to EUR, GBP, and JPY
Analyze AAPL stock over the past year
```

## Requirements

- Python 3.12.1+
- SerpAPI key
- fastmcp, mcp, requests
