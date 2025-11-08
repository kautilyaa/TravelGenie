# 🌍 TravelGenie - AI Travel Assistant

An intelligent conversational travel assistant powered by Claude API through MCP (Model Context Protocol) and free travel APIs. Built with Python 3.12 and FastAPI.

## ✨ Features

- 🗺️ **Places Discovery** - Find attractions, restaurants, and points of interest using OpenTripMap
- 🌤️ **Weather Information** - Real-time weather data from Open-Meteo
- 🧭 **Route Planning** - Get directions and routes via OpenRouteService
- 📸 **Location Images** - Beautiful location photos from Unsplash
- 🎫 **Event Discovery** - Find local events through Eventbrite
- 💱 **Currency Exchange** - Real-time exchange rates from ExchangeRate.host
- 🤖 **AI-Powered Responses** - Natural language understanding using Claude API via MCP

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip package manager
- API keys for required services (see SETUP.md)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travelgenie.git
cd travelgenie
```

2. Create virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. Test the API:
```bash
curl "http://localhost:8000/query?q=weather in Paris&lat=48.8566&lon=2.3522"
```

## 📁 Project Structure

```
travelgenie/
│
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
├── SETUP.md                    # Detailed setup instructions
│
├── config/
│   └── settings.py             # Configuration and environment management
│
├── modules/
│   ├── __init__.py
│   ├── mcp_client.py          # MCP Claude integration
│   ├── intent_detector.py     # Query intent classification
│   ├── places.py              # OpenTripMap integration
│   ├── weather.py             # Open-Meteo integration
│   ├── routing.py             # OpenRouteService integration
│   ├── events.py              # Eventbrite integration
│   ├── currency.py            # ExchangeRate.host integration
│   ├── images.py              # Unsplash integration
│   ├── profile.py             # User preference management
│   └── response_composer.py   # Response generation and formatting
│
├── data/
│   └── travelgenie.db         # SQLite database (auto-created)
│
├── static/                    # Static files (optional)
└── tests/                     # Test files
    └── test_apis.py
```

## 🔌 API Endpoints

### Main Query Endpoint
```
GET /query
```
Parameters:
- `q` (string): User query in natural language
- `lat` (float): Latitude (optional, default: Paris)
- `lon` (float): Longitude (optional, default: Paris)

### Health Check
```
GET /health
```

### API Documentation
```
GET /docs
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **AI Integration**: Claude API via MCP
- **Database**: SQLite
- **APIs Used**:
  - OpenTripMap (Places)
  - Open-Meteo (Weather)
  - OpenRouteService (Routing)
  - Unsplash (Images)
  - Eventbrite (Events)
  - ExchangeRate.host (Currency)

## 🚀 Deployment Options

### Free Hosting Platforms

1. **Render** - 750 free hours/month
2. **Railway** - $5 free credit
3. **Vercel** - For static/serverless
4. **Fly.io** - Free tier available

See SETUP.md for detailed deployment instructions.

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ for travelers by the TravelGenie team