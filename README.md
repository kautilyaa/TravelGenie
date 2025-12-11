# TravelGenie - AI Travel Planning Assistant

![TravelGenie](assets/img/Gemini_Generated_Image_36apt236apt236ap.png)

**TravelGenie** is an AI-powered travel planner that helps you coordinate flights, hotels, events, weather, and basically everything else you need for a complete trip itinerary. It's built on Model Context Protocol (MCP) and uses Claude AI to orchestrate 7 specialized servers automatically - so you don't have to juggle a million tabs and apps.

![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What It Does

Ever tried planning a trip and spent hours jumping between Google Flights, Booking.com, checking weather, looking up events, and trying to figure out if you can afford it all? Yeah, me too. That's why I built TravelGenie.

Just ask it something like: *"Plan a trip to Banff, Alberta from Reston, Virginia, June 7-14, 2025. Budget $5000. We like hiking, museums, and dining."*

And TravelGenie will:
- Find flights and hotels that fit your budget
- Check weather forecasts (because who wants to pack wrong?)
- Discover local events that match what you're into
- Convert currencies so you know what things actually cost
- Analyze traffic patterns (because nobody likes being stuck)
- Create a day-by-day itinerary with a budget breakdown

**No manual searching. Just one request, and you get a complete plan.**

---

## Quick Start

### Installation

First things first, clone the repo and install dependencies:

```bash
git clone <repository-url>
cd TravelGenie
pip install -r requirements.txt
```

### API Keys

You'll need a few API keys to get this running:

- **SerpAPI** - Used for flights, hotels, and events. You can get a free key at [serpapi.com](https://serpapi.com/)
- **Anthropic** - For Claude AI. Sign up at [console.anthropic.com](https://console.anthropic.com/)
- **Slack** (optional) - Only if you want to use the Slack bot. Create an app at [api.slack.com/apps](https://api.slack.com/apps)
- **Open-Meteo** & **OpenStreetMap** - These are free, no keys needed!

### Configuration

Copy the example env file and add your keys:

```bash
cp .env.example .env
# Then edit .env and add your keys
```

### Running It

You've got a couple options:

**Web UI (easiest way to start):**
```bash
streamlit run streamlit_app.py
```

**Or use the Slack bot:**
```bash
python slack_bot.py
```

Then just visit `http://localhost:8501` and start planning!

---

## How It Works

So here's the deal - TravelGenie uses **7 specialized servers** that Claude AI coordinates automatically. Each one handles a specific part of travel planning:

| Server | What It Does |
|--------|-------------|
| **Flight** | Finds and compares flights |
| **Hotel** | Discovers accommodations |
| **Event** | Finds local activities & events |
| **Geocoder** | Converts addresses to coordinates |
| **Weather** | Gets forecasts and conditions |
| **Finance** | Converts currencies |
| **Traffic & Crowd** | Analyzes real-time location data |

**Here's how it flows:**
1. You make a request for a trip
2. Claude geocodes your locations
3. Searches flights, hotels, events
4. Checks weather forecasts
5. Analyzes traffic patterns
6. Converts currencies
7. Synthesizes everything into a complete itinerary

All automatically, usually in seconds. Pretty neat, right?

---

## Usage

### Streamlit Web UI

This is probably the easiest way to use TravelGenie:

1. Run `streamlit run streamlit_app.py`
2. Fill in your trip details (origin, destination, dates, budget, interests)
3. Click "Plan My Trip"
4. Get your complete itinerary!

### Slack Bot

If you're already using Slack, you can integrate TravelGenie as a bot:

```bash
python slack_bot.py
```

Then in Slack, just mention it:
```
@travelgenie Plan a weekend trip to Portland for next weekend. 
We want breweries and food trucks. Budget $1500 for 2 people.
```

### Direct API

If you want to integrate it into your own code, you can use the orchestrator directly:

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

If you want to run it in Docker:

```bash
docker build -t travelgenie .
docker run -d -p 8501:8501 --env-file .env travelgenie
```

### AWS

For production deployments, there's CloudFormation setup:

```bash
cd aws/cloudformation
aws cloudformation create-stack \
  --stack-name travelgenie \
  --template-body file://infrastructure.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

This sets up ECS Fargate, DynamoDB, Secrets Manager, and CloudWatch. Check out `aws/Run.md` for more details on the AWS setup.

---

## Server Tools

Each server provides specific tools you can use:

**Flight Server**
- `search_flights` - Find flights with filters
- `get_flight_details` - Get detailed flight info
- `filter_flights_by_price` - Filter by your budget

**Hotel Server**
- `search_hotels` - Find accommodations
- `get_hotel_details` - Property details
- `filter_hotels_by_price` - Budget filtering

**Event Server**
- `search_events` - Find local events
- `get_event_details` - Event information
- `filter_events_by_date` - Filter by date

**Geocoder Server**
- `geocode_location` - Convert address → coordinates
- `reverse_geocode` - Convert coordinates → address
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

Create a `.env` file in the root directory:

```bash
# Required
SERPAPI_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Optional - Slack bot
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
```

### Claude Desktop (MCP Mode)

If you want to use TravelGenie with Claude Desktop, add this to your `claude_desktop_config.json`:

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
- Double-check your API keys in `.env`
- Make sure you're using Python 3.12.1 or higher
- Check the server logs for errors

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Slack bot not connecting?**
- Verify your tokens are correct
- Make sure Socket Mode is enabled in your Slack app settings
- Check that your bot has the right scopes: `chat:write`, `app_mentions:read`

**No search results?**
- Try using airport codes (like "IAD" instead of city names) - sometimes that works better
- Check if you've hit your SerpAPI quota
- Make sure your dates are in the future

---

## Testing

To test things out:

```bash
# Test Slack bot
python slack_bot.py --test

# Test Streamlit UI
streamlit run streamlit_app.py
```

---

## Contributing

Contributions are welcome! There's always room for improvement. Some ideas:
- New server types (restaurants, car rentals, etc.)
- Better filtering algorithms
- Improved caching and performance
- Mobile support
- More tests

**How to contribute:**
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Support

If you run into issues:
- **GitHub Issues**: [github.com/kautilyaa/TravelGenie/issues](https://github.com/kautilyaa/TravelGenie/issues)
- **API Docs**: 
  - [SerpAPI](https://serpapi.com/)
  - [Anthropic](https://docs.anthropic.com/)
  - [Open-Meteo](https://open-meteo.com/en/docs)

---

## License

MIT License - see LICENSE file for details.

---

**Ready to plan your next trip?** Just run `streamlit run streamlit_app.py` or set up the Slack bot and you're good to go!
