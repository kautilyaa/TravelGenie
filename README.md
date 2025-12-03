[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/skarlekar-mcp-travelassistant-badge.png)](https://mseep.ai/app/skarlekar-mcp-travelassistant)

# 🌍 Travel Assistant MCP Server Ecosystem

A comprehensive suite of Model Context Protocol (MCP) servers that work together to provide intelligent travel planning and assistance. This ecosystem enables Claude to orchestrate multiple specialized services to create detailed travel itineraries, find optimal flights and accommodations, discover local events, analyze weather conditions, and manage budget considerations across different currencies.

![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Travel](https://img.shields.io/badge/Travel-Planning-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 System Overview

The Travel Assistant MCP Ecosystem consists of six specialized servers that work in harmony:

- **🛫 Flight Search Server** - Find and compare flights, analyze pricing, filter by preferences
- **🏨 Hotel Search Server** - Discover accommodations, compare amenities, filter by budget and preferences  
- **🎭 Event Search Server** - Find local events, festivals, and activities
- **🗺️ Geocoder Server** - Convert locations to coordinates, calculate distances, reverse geocoding
- **🌤️ Weather Search Server** - Get forecasts, current conditions, weather alerts
- **💰 Finance Search Server** - Currency conversion, exchange rates, financial analysis

## 🚀 Real-World Example: Orchestrating a Comprehensive Travel Plan using a LLM

**User Request**: *"I am planning a trip to Banff and Jasper in Alberta from Reston, Virginia during June 7th 2025 to June 14th 2025. Find flights, hotels and events that are happening in Banff, Alberta and things to do for me and my wife during the time based on weather conditions. We like to hike, go sight-seeing, dining, and going to museums. My budget is $5000 USD. Make sure to convert cost from Canadian dollars to USD before presenting."*

### 🎼 Orchestrated Response Sequence

Here's how Claude orchestrates the MCP servers to fulfill this complex request:

#### Step 1: Location Intelligence 🗺️
- Use the **Geocoder Server** to convert "Reston, Virginia", "Banff, Alberta", and "Jasper, Alberta" into latitude/longitude coordinates.
- Calculate distances between locations for itinerary planning.

#### Step 2: Flight Discovery ✈️
- Use the **Flight Server** to search for flights from the nearest airport to Reston, VA (e.g., IAD) to Calgary, AB (nearest to Banff/Jasper) for the specified dates.
- Filter by price, duration, and preferred airlines.
- Retrieve detailed flight information, including layovers, baggage policies, and total cost

#### Step 3: Accommodation Search 🏨
- Use the **Hotel Server** to find hotels or vacation rentals in Banff and Jasper for the trip dates.
- Filter by price, amenities (e.g., free WiFi, breakfast), and guest ratings.
- Retrieve detailed property information, compare top options, and analyze total accommodation cost.

#### Step 4: Weather Analysis 🌤️
- Use the **Weather Server** to get daily/hourly forecasts for Banff and Jasper.
- Assess weather suitability for outdoor activities and suggest optimal days for hiking or sightseeing.

#### Step 5: Event & Activity Discovery 🎭
- Use the **Event Server** to find local events, festivals, and activities in Banff and Jasper during the trip.
- Filter by interests (hiking, sightseeing, dining, museums).

#### Step 6: Financial Analysis 💰
- Use the **Finance Server** to convert all costs (hotels, events, etc.) from CAD to USD.
- Ensure the total plan fits within the $5000 USD budget.

#### Step 7: Intelligent Synthesis 🧠
Claude synthesizes all data to create:
- **Optimized flight options** with price comparisons
- **Curated hotel recommendations** matching preferences and budget
- **Weather-appropriate activity scheduling** 
- **Day-by-day itinerary** with backup options for weather
- **Complete budget breakdown** in USD with currency conversion
- **Distance and travel time calculations** between locations
- Presents a day-by-day itinerary, recommends activities based on weather and interests, and provides a budget breakdown in USD.

## 🎯 Why MCP Makes This Possible

### Cross-Server Integration
- **Unified Protocol**: All servers use the same MCP specification, enabling seamless communication
- **Standardized Data Formats**: Consistent JSON structures across different domains
- **Shared Context**: Claude maintains conversation state across multiple server interactions

### Intelligent Sequencing  
- **Dependency Management**: Claude understands that geocoding must happen before weather forecasts
- **Conditional Logic**: Flight searches trigger hotel searches in destination cities
- **Error Handling**: If one server fails, Claude can adapt the sequence dynamically

### Real-Time Processing
- **Parallel Execution**: Multiple servers can be queried simultaneously when dependencies allow
- **Live Data**: All servers provide real-time information (flights, weather, events, exchange rates)
- **Dynamic Filtering**: Results from one server inform the parameters for another

### Data Synthesis
- **Multi-Domain Analysis**: Combines weather data with event scheduling and activity recommendations
- **Budget Optimization**: Currency conversion enables accurate budget tracking across international trips
- **Preference Matching**: Filters activities based on stated interests (hiking, museums, dining)

## Server Capabilities at a Glance

| Server         | Key Tools/Resources/Prompts                                      | Example Use Cases                                  |
|----------------|------------------------------------------------------------------|----------------------------------------------------|
| **Flight**     | `search_flights`, `get_flight_details`, `filter_flights_by_price`| Find and compare flights, analyze options          |
| **Hotel**      | `search_hotels`, `get_hotel_details`, `filter_hotels_by_price`   | Find hotels/rentals, filter by amenities, compare  |
| **Event**      | `search_events`, `get_event_details`, `filter_events_by_date`    | Discover local events, filter by type/date         |
| **Weather**    | `get_weather_forecast`, `get_current_conditions`, `filter_forecast_by_conditions` | Plan activities based on weather, get alerts       |
| **Geocoder**   | `geocode_location`, `reverse_geocode`, `calculate_distance`      | Convert addresses, plan routes, calculate distances|
| **Finance**    | `convert_currency`, `lookup_stock`, `get_market_overview`        | Convert costs, analyze budget, get market data     |

---

## 🛠️ Complete Installation Guide

### Prerequisites
- Python 3.8 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- Claude Desktop application
- API keys for required services

### Required API Keys
- **SerpAPI Key** (for flights, hotels, events) - [Get free key](https://serpapi.com/)
- **OpenWeatherMap** or use National Weather Service (free)
- **OpenStreetMap Nominatim** (free, no key required)

### Step-by-Step Setup

1. **Create project directory:**
```bash
mkdir travel-assistant-mcp
cd travel-assistant-mcp
```

2. **Clone all server repositories:**
```bash
# Create subdirectories for each server
mkdir flight-search hotel-search event-search geocoder weather-search finance-search
```

3. **Install dependencies for each server:**
```bash
# In each server directory
uv sync
```

4. **Configure Claude Desktop:**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "flight-search": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/flight-search",
        "run", "python", "flight_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key"
      }
    },
    "hotel-search": {
      "command": "uv", 
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/hotel-search",
        "run", "python", "hotel_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key"
      }
    },
    "event-search": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/event-search", 
        "run", "python", "event_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key"
      }
    },
    "geocoder": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/geocoder",
        "run", "python", "geocoder_server.py" 
      ]
    },
    "weather-search": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/weather-search",
        "run", "python", "weather_search_server.py"
      ]
    },
    "finance-search": {
      "command": "uv", 
      "args": [
        "--directory", "/path/to/travel-assistant-mcp/finance-search",
        "run", "python", "finance_search_server.py"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key"
      }
    }
  }
}
```

5. **Restart Claude Desktop** to load all servers.

## 💡 Advanced Usage Examples

### Weekend Getaway Planning
```
Plan a weekend trip from San Francisco to Portland, Oregon for next weekend. 
We want to visit breweries, food trucks, and outdoor markets. Budget is $1500 
for 2 people. Find flights leaving Friday evening and returning Sunday night.
```

### International Business Travel
```
I need to travel from New York to Tokyo for a conference June 20-25, 2025. 
Find business class flights, luxury hotels near Tokyo Station, check weather 
for appropriate clothing, and convert all costs to USD. Also find networking 
events for tech professionals during that week.
```

### Family Vacation Planning  
```
Plan a family vacation to Orlando, Florida for July 15-22, 2025 for 2 adults 
and 2 children (ages 8 and 12). We want to visit theme parks, but also need 
backup indoor activities in case of rain. Budget is $8000 USD total.
```

### Multi-City European Tour
```
Plan a 2-week European tour visiting London, Paris, Rome, and Barcelona 
from August 5-19, 2025. Find the most efficient flight routing, centrally 
located hotels, cultural events and museums, check weather patterns, 
and provide a day-by-day itinerary with budget breakdown.
```

## 🏗️ Architecture Benefits

### Modularity
- Each server handles a specific domain expertly
- Servers can be updated independently
- Easy to add new capabilities (car rentals, restaurant reservations, etc.)

### Scalability  
- Servers can be distributed across different systems
- Load balancing possible for high-traffic scenarios
- Individual server failures don't bring down the entire system

### Data Privacy
- No central data storage requirement
- Each server handles its own data retention policies
- Users control which servers to enable

### Extensibility
- New travel-related servers can be added easily
- Custom business logic can be implemented per server
- Integration with enterprise travel management systems possible

## 🔧 Troubleshooting Guide

### Common Integration Issues

**Servers not communicating:**
- Check all servers are running: `ps aux | grep python`
- Verify Claude Desktop configuration paths
- Ensure all API keys are valid and have sufficient quota

**Inconsistent results:**
- Some APIs have rate limits - space out requests
- Exchange rates and flight prices change frequently  
- Weather forecasts become less accurate beyond 7 days

**Budget calculations incorrect:**
- Always use latest exchange rates from finance server
- Account for booking fees and taxes in hotel/flight prices
- Consider seasonal price variations

### Performance Optimization

- **Caching**: Most servers cache results locally to reduce API calls
- **Parallel Processing**: Claude can query multiple servers simultaneously
- **Smart Filtering**: Use broad searches first, then narrow with filters

## 🤝 Contributing

This ecosystem thrives on community contributions:

1. **New Server Types**: Restaurant reservations, car rentals, travel insurance
2. **Enhanced Filtering**: More sophisticated preference matching
3. **Better Integration**: Cross-server data sharing and caching
4. **Mobile Support**: Extend MCP support to mobile travel apps

## 📄 License

This travel assistant ecosystem is open source under the MIT License. Individual servers may have different licenses - check each server's documentation.

## 🆘 Support

For issues related to:
- **Individual Servers**: Check the specific server's README and repository
- **Integration Problems**: Create an issue in the main travel-assistant-mcp repository  
- **Claude Desktop**: Visit Anthropic's support documentation
- **API Issues**: Contact the respective API providers (SerpAPI, weather services, etc.)

---

**The power of MCP lies in its ability to orchestrate complex, multi-step workflows that would traditionally require multiple apps and manual coordination. With this travel assistant ecosystem, Claude becomes your intelligent travel agent, capable of handling sophisticated requests that span multiple domains and data sources.**