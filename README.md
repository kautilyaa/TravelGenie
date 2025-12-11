# TravelGenie - AI Travel Planning Assistant

![TravelGenie](assets/img/Gemini_Generated_Image_36apt236apt236ap.png)

**TravelGenie** is an AI-powered travel planner that coordinates flights, hotels, events, weather, and more into complete itineraries. Built on Model Context Protocol (MCP), it uses Claude AI to orchestrate 7 specialized servers automatically.

![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What It Does

Ask: *"Plan a trip to Banff, Alberta from Reston, Virginia, June 7-14, 2025. Budget $5000. We like hiking, museums, and dining."*

TravelGenie automatically:
- Finds flights and hotels
- Checks weather forecasts
- Discovers local events matching your interests
- Converts currencies
- Analyzes traffic patterns
- Creates a day-by-day itinerary with budget breakdown

**No manual searching. Just one request, complete plan.**

---

## Quick Start

### 1. Install

```bash
git clone <repository-url>
cd TravelGenie
pip install -r requirements.txt
```

### 2. Get API Keys

- **SerpAPI** (flights, hotels, events) - [Free key](https://serpapi.com/)
- **Anthropic** (Claude AI) - [Get key](https://console.anthropic.com/)
- **Slack** (optional, for bot) - [Create app](https://api.slack.com/apps)
- **Open-Meteo** & **OpenStreetMap** - Free, no keys needed

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your keys
```

### 4. Run

```bash
# Web UI
streamlit run streamlit_app.py

# Or Slack bot
python slack_bot.py
```

Visit `http://localhost:8501` to start planning!

---

## How It Works

TravelGenie uses **7 specialized servers** that Claude AI coordinates automatically:

| Server | Purpose |
|--------|---------|
| **Flight** | Find and compare flights |
| **Hotel** | Discover accommodations |
| **Event** | Find local activities & events |
| **Geocoder** | Convert addresses to coordinates |
| **Weather** | Get forecasts and conditions |
| **Finance** | Convert currencies |
| **Traffic & Crowd** | Analyze real-time location data |

**Example Flow:**
1. You request a trip
2. Claude geocodes locations
3. Searches flights, hotels, events
4. Checks weather forecasts
5. Analyzes traffic patterns
6. Converts currencies
7. Synthesizes everything into a complete itinerary

All automatically, in seconds.

---

## Usage

### Streamlit Web UI

1. Run `streamlit run streamlit_app.py`
2. Fill in trip details (origin, destination, dates, budget, interests)
3. Click "Plan My Trip"
4. Get your complete itinerary!

### Slack Bot

```bash
python slack_bot.py
```

Then in Slack:
```
@travelgenie Plan a weekend trip to Portland for next weekend. 
We want breweries and food trucks. Budget $1500 for 2 people.
```

### Direct API

```python
from claude_orchestrator import execute_tool

# Search flights
flights = execute_tool("search_flights",
    departure_id="IAD",
    arrival_id="YYC",
    outbound_date="2025-06-07",
    return_date="2025-06-14",
    adults=2
)

# Get weather
weather = execute_tool("get_weather_forecast",
    location="Banff, Alberta",
    forecast_days=7
)
```

---

## Deployment

### Docker

```bash
docker build -t travelgenie .
docker run -d -p 8501:8501 --env-file .env travelgenie
```

### AWS

```bash
cd aws/cloudformation
aws cloudformation create-stack \
  --stack-name travelgenie \
  --template-body file://infrastructure.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

Includes: ECS Fargate, DynamoDB, Secrets Manager, CloudWatch. See `aws/Run.md` for details.

---

## Server Tools

Each server provides specific tools:

**Flight Server**
- `search_flights` - Find flights with filters
- `get_flight_details` - Detailed flight info
- `filter_flights_by_price` - Budget filtering

**Hotel Server**
- `search_hotels` - Find accommodations
- `get_hotel_details` - Property details
- `filter_hotels_by_price` - Budget filtering

**Event Server**
- `search_events` - Find local events
- `get_event_details` - Event information
- `filter_events_by_date` - Date filtering

**Geocoder Server**
- `geocode_location` - Address → coordinates
- `reverse_geocode` - Coordinates → address
- `calculate_distance` - Distance between locations

**Weather Server**
- `get_weather_forecast` - Multi-day forecasts
- `get_current_weather` - Current conditions

**Finance Server**
- `convert_currency` - Currency conversion
- `get_market_overview` - Market data

**Traffic & Crowd Server**
- `analyze_location_traffic` - Real-time analysis
- `analyze_youtube_video` - Video stream analysis
- `get_traffic_patterns` - Historical patterns

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Required
SERPAPI_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Optional - Slack bot
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
```

### Claude Desktop (MCP Mode)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flight-search": {
      "command": "uv",
      "args": ["--directory", "/path/to/TravelGenie/servers/flight_server", 
               "run", "python", "flight_server.py"],
      "env": {"SERPAPI_KEY": "your_key"}
    }
  }
}
```

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

---

## Troubleshooting

**Servers not responding?**
- Check API keys in `.env`
- Verify Python 3.12.1+
- Check server logs

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Slack bot not connecting?**
- Verify tokens are correct
- Enable Socket Mode in Slack app settings
- Check bot scopes: `chat:write`, `app_mentions:read`

**No search results?**
- Try airport codes (e.g., "IAD" instead of city names)
- Check SerpAPI quota
- Verify dates are in the future

---

## Testing

```bash
# Test Slack bot
python slack_bot.py --test

# Test Streamlit UI
streamlit run streamlit_app.py
```

---

## Contributing

We welcome contributions! Areas for improvement:
- New server types (restaurants, car rentals)
- Enhanced filtering algorithms
- Better caching and performance
- Mobile support
- More tests

**Process:**
1. Fork the repo
2. Create feature branch
3. Make changes
4. Submit pull request

---

## Support

- **Issues**: [GitHub Issues](https://github.com/kautilyaa/TravelGenie/issues)
- **API Docs**: 
  - [SerpAPI](https://serpapi.com/)
  - [Anthropic](https://docs.anthropic.com/)
  - [Open-Meteo](https://open-meteo.com/en/docs)

---

## License

MIT License - see LICENSE file for details.

---

**Ready to plan your next trip?** Start with `streamlit run streamlit_app.py` or integrate the Slack bot!
