# TravelGenie - Intelligent Travel Planning Assistant

![TravelGenie](assets/img/Gemini_Generated_Image_36apt236apt236ap.png)

**TravelGenie** is a comprehensive, AI-powered travel planning ecosystem that orchestrates multiple specialized services to create detailed travel itineraries. Built on the Model Context Protocol (MCP), it enables Claude AI to seamlessly coordinate flights, hotels, events, weather, currency conversion, and real-time traffic analysis—all in one intelligent system.

![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Travel](https://img.shields.io/badge/Travel-Planning-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What Makes TravelGenie Special?

Imagine asking an AI assistant: *"Plan a trip to Banff and Jasper in Alberta from Reston, Virginia during June 7-14, 2025. Find flights, hotels, and events based on weather conditions. We like hiking, sight-seeing, dining, and museums. Budget is $5000 USD."*

**TravelGenie doesn't just search—it orchestrates.** It intelligently sequences multiple specialized servers, understands dependencies (like needing coordinates before weather forecasts), filters results based on your preferences, converts currencies automatically, and synthesizes everything into a comprehensive, day-by-day itinerary with budget breakdowns.

### Key Highlights

- **Intelligent Orchestration**: Claude AI coordinates 7 specialized MCP servers automatically
- **Multi-Modal Access**: Use via Slack bot, Streamlit web UI, or direct API integration
- **Real-Time Data**: Live flight prices, weather forecasts, traffic conditions, and currency rates
- **Context-Aware**: Remembers conversation history and builds on previous interactions
- **Budget Management**: Automatic currency conversion and budget tracking
- **Production-Ready**: Docker support and AWS CloudFormation templates included

---

## System Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        A[Slack Bot] 
        B[Streamlit Web UI]
        C[Direct API]
    end
    
    subgraph "Orchestration Layer"
        D[Claude Orchestrator]
        E[Tool Definitions]
        F[Context Manager]
    end
    
    subgraph "MCP Servers"
        G1[Flight Server<br/>SerpAPI]
        G2[Hotel Server<br/>SerpAPI]
        G3[Event Server<br/>SerpAPI]
        G4[Geocoder Server<br/>OpenStreetMap]
        G5[Weather Server<br/>Open-Meteo]
        G6[Finance Server<br/>SerpAPI]
        G7[Traffic & Crowd Server<br/>Computer Vision]
    end
    
    subgraph "Data Storage"
        H1[(SQLite/DynamoDB<br/>Chat History)]
        H2[(Local Files<br/>Search Results)]
    end
    
    subgraph "External APIs"
        I1[SerpAPI]
        I2[Open-Meteo]
        I3[OpenStreetMap]
        I4[YouTube/Video Feeds]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    D --> F
    F --> H1
    
    D --> G1
    D --> G2
    D --> G3
    D --> G4
    D --> G5
    D --> G6
    D --> G7
    
    G1 --> I1
    G2 --> I1
    G3 --> I1
    G4 --> I3
    G5 --> I2
    G6 --> I1
    G7 --> I4
    
    G1 --> H2
    G2 --> H2
    G3 --> H2
    
    style D fill:#4A90E2,color:#fff
    style A fill:#611F69,color:#fff
    style B fill:#FF4B4B,color:#fff
    style G7 fill:#FF6B6B,color:#fff
```

---

## The Complete Server Orchestra

TravelGenie consists of **7 specialized MCP servers**, each an expert in its domain:

| Server | What It Does | Key Features |
|--------|-------------|--------------|
| **Flight Server** | Finds and compares flights | Price analysis, airline filtering, schedule optimization |
| **Hotel Server** | Discovers accommodations | Amenity filtering, price comparison, availability checking |
| **Event Server** | Finds local events & activities | Interest-based filtering, date range searches, festival discovery |
| **Geocoder Server** | Location intelligence | Address → coordinates, distance calculations, reverse geocoding |
| **Weather Server** | Weather forecasts & conditions | Daily/hourly forecasts, weather alerts, activity recommendations |
| **Finance Server** | Currency & financial data | Real-time exchange rates, currency conversion, market data |
| **Traffic & Crowd Server** | Real-time location analysis | Crowd density, traffic patterns, video frame analysis, YouTube stream analysis |

---

## Quick Start

### Prerequisites

- **Python 3.12.1+** (required for MCP servers)
- **UV package manager** (recommended) or pip
- **API Keys**:
  - **SerpAPI Key** (for flights, hotels, events, finance) - [Get free key](https://serpapi.com/)
  - **Anthropic API Key** (for Claude AI) - [Get key](https://console.anthropic.com/)
  - **Slack Tokens** (optional, for Slack bot) - [Create Slack app](https://api.slack.com/apps)
  - **Open-Meteo** (weather) - Free, no key required
  - **OpenStreetMap** (geocoding) - Free, no key required

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd TravelGenie
```

2. **Install dependencies:**
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
# Create a .env file
cp .env.example .env

# Edit .env and add your API keys:
# SERPAPI_KEY=your_serpapi_key
# ANTHROPIC_API_KEY=your_anthropic_key
# SLACK_BOT_TOKEN=your_slack_bot_token (optional)
# SLACK_APP_TOKEN=your_slack_app_token (optional)
```

4. **Run the Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

Visit `http://localhost:8501` and start planning trips!

---

## Usage Examples

### Example 1: Complete Trip Planning via Streamlit

1. Open the Streamlit UI
2. Fill in the trip form:
   - **Origin**: Reston, Virginia
   - **Destination**: Banff, Alberta
   - **Dates**: June 7-14, 2025
   - **Travelers**: 2 adults
   - **Budget**: $5000 USD
   - **Interests**: Hiking, Sight-seeing, Dining, Museums
3. Click "Plan My Trip"
4. Watch as TravelGenie orchestrates all servers and presents a complete itinerary!

### Example 2: Slack Bot Integration

```bash
# Start the Slack bot
python slack_bot.py

# In Slack, mention the bot:
@travelgenie Plan a weekend trip to Portland, Oregon for next weekend. 
We want to visit breweries and food trucks. Budget is $1500 for 2 people.
```

The bot will:
- Search for flights
- Find hotels
- Discover events matching your interests
- Check weather forecasts
- Convert currencies
- Analyze traffic conditions
- Present everything in Slack-friendly format

### Example 3: Direct API Usage

```python
from claude_orchestrator import execute_tool

# Search for flights
flights = execute_tool(
    "search_flights",
    departure_id="IAD",
    arrival_id="YYC",
    outbound_date="2025-06-07",
    return_date="2025-06-14",
    adults=2
)

# Get weather forecast
weather = execute_tool(
    "get_weather_forecast",
    location="Banff, Alberta",
    forecast_days=7
)

# Convert currency
conversion = execute_tool(
    "convert_currency",
    amount=1000,
    from_currency="CAD",
    to_currency="USD"
)
```

---

## Real-World Example: How TravelGenie Orchestrates

**User Request**: *"I'm planning a trip to Banff and Jasper in Alberta from Reston, Virginia during June 7-14, 2025. Find flights, hotels, and events based on weather. We like hiking, sight-seeing, dining, and museums. Budget is $5000 USD."*

### The Orchestration Sequence

1. **Geocoding** (Step 1)
   - Converts "Reston, Virginia" → coordinates
   - Converts "Banff, Alberta" → coordinates
   - Converts "Jasper, Alberta" → coordinates
   - Calculates distances between locations

2. **Flight Discovery** (Step 2)
   - Searches flights: IAD (nearest to Reston) → YYC (nearest to Banff/Jasper)
   - Filters by dates, passengers, preferences
   - Returns top options with prices

3. **Accommodation Search** (Step 3)
   - Searches hotels in Banff and Jasper
   - Filters by dates, guests, amenities
   - Compares prices and ratings

4. **Weather Analysis** (Step 4)
   - Gets 7-day forecast for Banff and Jasper
   - Identifies best days for outdoor activities
   - Suggests backup indoor activities for rainy days

5. **Event Discovery** (Step 5)
   - Searches for hiking trails, museums, restaurants
   - Filters by dates and interests
   - Finds festivals and local events

6. **Traffic Analysis** (Step 6)
   - Analyzes crowd conditions at popular locations
   - Recommends optimal visit times
   - Compares traffic across multiple locations

7. **Financial Analysis** (Step 7)
   - Converts all CAD prices to USD
   - Calculates total trip cost
   - Ensures budget compliance
   - Provides cost breakdown

8. **Intelligent Synthesis** (Final Step)
   - Creates day-by-day itinerary
   - Optimizes schedule based on weather
   - Suggests activities matching interests
   - Provides complete budget breakdown
   - Includes traffic-aware timing recommendations

**Result**: A comprehensive travel plan with flights, hotels, daily activities, weather-appropriate scheduling, traffic-aware timing, and complete budget breakdown—all automatically generated!

---

## Installation & Setup Guide

### Option 1: Local Development

```bash
# 1. Clone repository
git clone <repository-url>
cd TravelGenie

# 2. Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run Streamlit UI
streamlit run streamlit_app.py
```

### Option 2: Docker Deployment

```bash
# Build Docker image
docker build -t travelgenie .

# Run container
docker run -d \
  --name travelgenie \
  -p 8501:8501 \
  -e SERPAPI_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  travelgenie

# Or use docker-compose
docker-compose up -d
```

### Option 3: AWS Deployment

TravelGenie includes CloudFormation templates for production deployment:

```bash
cd aws/cloudformation

# Deploy infrastructure
aws cloudformation create-stack \
  --stack-name travelgenie-production \
  --template-body file://infrastructure.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

**Infrastructure includes:**
- ECS Fargate cluster for containerized deployment
- DynamoDB tables for chat history
- Secrets Manager for API keys
- Application Load Balancer
- CloudWatch logging and monitoring

See `aws/Run.md` for detailed deployment instructions.

---

## Server Capabilities Deep Dive

### Flight Server

**Tools:**
- `search_flights` - Search flights with filters
- `get_flight_details` - Get detailed flight information
- `filter_flights_by_price` - Filter by budget

**Example:**
```python
flights = search_flights(
    departure_id="IAD",
    arrival_id="YYC",
    outbound_date="2025-06-07",
    return_date="2025-06-14",
    adults=2,
    currency="USD",
    max_results=10
)
```

### Hotel Server

**Tools:**
- `search_hotels` - Search accommodations
- `get_hotel_details` - Detailed property info
- `filter_hotels_by_price` - Budget filtering

**Example:**
```python
hotels = search_hotels(
    location="Banff, Alberta",
    check_in_date="2025-06-07",
    check_out_date="2025-06-14",
    adults=2,
    currency="USD"
)
```

### Event Server

**Tools:**
- `search_events` - Find local events
- `get_event_details` - Event information
- `filter_events_by_date` - Date-based filtering

**Example:**
```python
events = search_events(
    query="hiking, museums, dining",
    location="Banff, Alberta",
    date_filter="month",
    max_results=20
)
```

### Geocoder Server

**Tools:**
- `geocode_location` - Address → coordinates
- `reverse_geocode` - Coordinates → address
- `calculate_distance` - Distance between locations

**Example:**
```python
coords = geocode_location("Banff, Alberta")
# Returns: {"latitude": 51.1784, "longitude": -115.5708, ...}

distance = calculate_distance("Banff, Alberta", "Jasper, Alberta")
# Returns: {"distance_km": 288.5, ...}
```

### Weather Server

**Tools:**
- `get_weather_forecast` - Multi-day forecasts
- `get_current_weather` - Current conditions

**Example:**
```python
forecast = get_weather_forecast(
    location="Banff, Alberta",
    forecast_days=7,
    hourly=False
)
```

### Finance Server

**Tools:**
- `convert_currency` - Currency conversion
- `get_market_overview` - Market data

**Example:**
```python
conversion = convert_currency(
    amount=1000,
    from_currency="CAD",
    to_currency="USD"
)
# Returns: {"converted_amount": 735.50, "rate": 0.7355, ...}
```

### Traffic & Crowd Server

**Tools:**
- `analyze_location_traffic` - Real-time traffic analysis
- `analyze_video_frame_realtime` - Video frame analysis
- `analyze_youtube_video` - YouTube/live stream analysis
- `get_traffic_patterns` - Historical patterns
- `compare_location_traffic` - Multi-location comparison

**Example:**
```python
# Analyze real-time traffic
traffic = analyze_location_traffic(
    location="Times Square, New York",
    analysis_type="comprehensive"
)

# Analyze YouTube live stream
youtube_analysis = analyze_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=...",
    location="Central Park",
    sample_frames=10,
    frame_interval=15
)
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
SERPAPI_KEY=your_serpapi_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional - for Slack bot
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
PROJECT_NAME=travel-assistant-slack-bot
ENVIRONMENT=production

# Optional - for AWS deployment
AWS_REGION=us-east-1
DYNAMODB_CHAT_SESSIONS_TABLE=travel-assistant-chat-sessions
DYNAMODB_MESSAGES_TABLE=travel-assistant-messages
DYNAMODB_TOOL_CALLS_TABLE=travel-assistant-tool-calls
```

### Claude Desktop Configuration (MCP Mode)

To use TravelGenie servers directly with Claude Desktop, configure `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "flight-search": {
      "command": "uv",
      "args": ["--directory", "/path/to/TravelGenie/servers/flight_server", "run", "python", "flight_server.py"],
      "env": {"SERPAPI_KEY": "your_key"}
    },
    "hotel-search": {
      "command": "uv",
      "args": ["--directory", "/path/to/TravelGenie/servers/hotel_server", "run", "python", "hotel_server.py"],
      "env": {"SERPAPI_KEY": "your_key"}
    }
    // ... add other servers similarly
  }
}
```

---

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t travelgenie:latest .

# Run container
docker run -d \
  --name travelgenie \
  -p 8501:8501 \
  --env-file .env \
  travelgenie:latest

# View logs
docker logs -f travelgenie
```

### Docker Compose

```yaml
version: '3.8'
services:
  travelgenie:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./servers:/app/servers
      - ./flights:/app/flights
      - ./hotels:/app/hotels
```

---

## AWS Deployment

TravelGenie includes production-ready AWS infrastructure:

### Infrastructure Components

- **ECS Fargate**: Containerized application hosting
- **DynamoDB**: Chat history and session storage
- **Secrets Manager**: Secure API key storage
- **Application Load Balancer**: Traffic distribution
- **CloudWatch**: Logging and monitoring
- **VPC**: Isolated network environment

### Deployment Steps

1. **Prepare CloudFormation parameters:**
```bash
cd aws/cloudformation
# Edit parameters.json with your values
```

2. **Deploy stack:**
```bash
aws cloudformation create-stack \
  --stack-name travelgenie-production \
  --template-body file://infrastructure.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

3. **Store secrets in Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name travel-assistant-slack-bot/production/anthropic-api-key \
  --secret-string "your_anthropic_key"
```

See `aws/Run.md` for complete deployment guide.

---

## Testing

### Test Individual Servers

```bash
# Test flight server
cd servers/flight_server
python -m pytest tests/

# Test hotel server
cd servers/hotel_server
python -m pytest tests/
```

### Test Slack Bot

```bash
# Run in test mode
python slack_bot.py --test

# This will verify:
# - Anthropic API connection
# - Slack API connection
# - Database initialization
# - Tool definitions loading
```

### Test Streamlit UI

```bash
streamlit run streamlit_app.py
# Navigate to http://localhost:8501
# Use the "Individual Searches" tab to test each server
```

---

## Troubleshooting

### Common Issues

**Problem**: Servers not responding  
**Solution**: 
- Check API keys in `.env` file
- Verify Python version is 3.12.1+
- Check server logs for errors

**Problem**: Import errors  
**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or with UV
uv sync
```

**Problem**: Slack bot not connecting  
**Solution**:
- Verify `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are correct
- Check Socket Mode is enabled in Slack app settings
- Ensure bot has necessary scopes: `chat:write`, `app_mentions:read`

**Problem**: Flight/hotel searches return no results  
**Solution**:
- Try using airport codes (e.g., "IAD" instead of "Reston, Virginia")
- Check SerpAPI quota hasn't been exceeded
- Verify dates are in the future

**Problem**: Weather forecasts inaccurate  
**Solution**:
- Weather forecasts become less accurate beyond 7 days
- Use specific location names (city, state/country)
- Consider using coordinates for remote locations

---

## Performance & Optimization

### Caching Strategy

- **Geocoding**: Results cached locally to reduce API calls
- **Flight/Hotel Searches**: Results saved to JSON files for quick access
- **Weather Data**: Cached for 1 hour to reduce API load

### Rate Limiting

- **SerpAPI**: Respects rate limits automatically
- **Open-Meteo**: Free tier has generous limits
- **OpenStreetMap**: Uses rate limiter to respect usage policies

### Parallel Processing

Claude orchestrator can execute multiple independent server calls in parallel when dependencies allow, significantly reducing total response time.

---

## Contributing

We welcome contributions! Here's how you can help:

### Areas for Contribution

1. **New Server Types**: Restaurant reservations, car rentals, travel insurance
2. **Enhanced Filtering**: More sophisticated preference matching algorithms
3. **Better Integration**: Cross-server data sharing and caching improvements
4. **Mobile Support**: Extend to mobile travel apps
5. **Documentation**: Improve guides and examples
6. **Testing**: Add unit and integration tests

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes
- Include comments for complex logic

---

##  License

This project is licensed under the MIT License. See LICENSE file for details.

Individual servers may have different licenses—check each server's README.

---

## Support & Resources

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/kautilyaa/TravelGenie/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kautilyaa/TravelGenie/discussions)
- **Documentation**: Check individual server READMEs in `servers/*/README.md`

### API Provider Support

- **SerpAPI**: [Documentation](https://serpapi.com/) | [Support](https://serpapi.com/support)
- **Anthropic Claude**: [Documentation](https://docs.anthropic.com/) | [Support](https://support.anthropic.com/)
- **Open-Meteo**: [Documentation](https://open-meteo.com/en/docs)
- **OpenStreetMap**: [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)

### Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/download)

---

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/) for seamless AI integration
- Powered by [Claude AI](https://www.anthropic.com/) for intelligent orchestration
- Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP server framework
- Thanks to all API providers: SerpAPI, Open-Meteo, OpenStreetMap

---

**Ready to plan your next adventure?** Start with the Streamlit UI or integrate the Slack bot into your workspace!

---

*Last updated: 2025*
