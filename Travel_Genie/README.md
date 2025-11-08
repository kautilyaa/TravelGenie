# ✈️ Travel Genie

A streamlined multi-agent travel planning assistant with AI-powered chat, video analysis, and intelligent itinerary management.

## 🚀 Features

- **🤖 AI Chat**: Integrated Claude API for conversational travel planning
- **📹 Video Analysis**: YOLO11-powered real-time object detection on YouTube travel videos
- **🗺️ Itinerary Management**: Smart trip planning with MCP server integration
- **🎫 Booking Services**: Flight, hotel, and car rental search capabilities
- **📊 Analytics Dashboard**: Visual insights into travel patterns and preferences
- **🔒 Secure**: Environment-based API key management and data sanitization

## 🏗️ Architecture

### Modular MCP Servers
- **Itinerary Server**: Manages travel itineraries and trip planning
- **Booking Server**: Handles reservations and bookings
- **Maps Server**: Location services and geographical data

All servers use **FastMCP** with **stdio transport** for efficient process management.

### Core Components
- **Claude Agent**: Conversational AI integration
- **YOLO11 Analyzer**: Real-time video object detection
- **Streamlit UI**: Interactive dashboard
- **MCP Orchestrator**: Multi-server coordination

## 📋 Prerequisites

- Python 3.12+
- Anthropic API key (for Claude chat)
- (Optional) YouTube API key (for enhanced video features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Travel_Genie.git
   cd Travel_Genie
   ```

2. **Create virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # If available
   # Or create .env file with:
   # ANTHROPIC_API_KEY=your_key_here
   # YOUTUBE_API_KEY=your_key_here (optional)
   ```

## 🚀 Usage

### Run the Streamlit Application

```bash
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

### Features Overview

1. **💬 Chat Tab**: Ask Travel Genie about your travel plans
2. **📹 Video Analysis**: Input a YouTube URL to analyze travel videos
3. **🗺️ Itinerary**: Create and manage travel itineraries
4. **🎫 Bookings**: Search for flights, hotels, and car rentals
5. **📊 Analytics**: View travel insights and trends
6. **⚙️ Settings**: Configure API keys and preferences

## 📁 Project Structure

```
Travel_Genie/
├── agents/
│   ├── claude_agent.py      # Claude API integration
│   └── video_analyzer.py     # YOLO11 video analysis
├── mcp_servers/
│   ├── booking_server.py     # Booking MCP server
│   ├── itinerary_server.py   # Itinerary MCP server
│   ├── maps_server.py        # Maps MCP server
│   └── orchestrator.py       # MCP server orchestrator
├── ui/
│   ├── app.py                # Main Streamlit application
│   └── components.py        # Reusable UI components
├── utils/
│   ├── config.py             # Configuration management
│   ├── security.py           # Security utilities
│   └── youtube_utils.py      # YouTube helper functions
├── requirements.txt           # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 Configuration

### API Keys

Store your API keys securely using one of these methods:

1. **Environment Variables** (Recommended)
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   export YOUTUBE_API_KEY=your_key_here
   ```

2. **Streamlit Secrets**
   Create `.streamlit/secrets.toml`:
   ```toml
   anthropic = "your_key_here"
   youtube = "your_key_here"
   ```

3. **.env File**
   Create `.env` in the project root:
   ```
   ANTHROPIC_API_KEY=your_key_here
   YOUTUBE_API_KEY=your_key_here
   ```

## 🎯 MCP Server Usage

### Start MCP Servers

The orchestrator automatically manages MCP servers. You can also run them individually:

```bash
# Itinerary Server
python mcp_servers/itinerary_server.py

# Booking Server
python mcp_servers/booking_server.py

# Maps Server
python mcp_servers/maps_server.py
```

### Example: Using MCP Orchestrator

```python
from mcp_servers.orchestrator import MCPOrchestrator

async def main():
    orchestrator = MCPOrchestrator()
    async with orchestrator.session():
        # Your code here
        result = await orchestrator.process_travel_request({
            "type": "plan_trip",
            "params": {
                "destination": "Paris, France",
                "dates": {"start": "2025-12-15", "end": "2025-12-22"}
            }
        })
        print(result)
```

## 📹 Video Analysis

### Analyze YouTube Videos

```python
from agents.video_analyzer import YOLO11Analyzer

async def main():
    analyzer = YOLO11Analyzer()
    result = await analyzer.analyze_youtube_video(
        url="https://www.youtube.com/watch?v=...",
        duration_seconds=30,
        skip_frames=5
    )
    print(f"Detected {result.summary['total_detections']} objects")
```

## 💬 Chat Integration

### Use Claude Agent

```python
from agents.claude_agent import ClaudeAgent

async def main():
    agent = ClaudeAgent(api_key="your_key")
    agent.create_session("my_session")
    response = await agent.chat("Plan a trip to Paris", "my_session")
    print(response)
```

## 🔒 Security

- API keys are stored securely using encryption
- User input is sanitized to prevent injection attacks
- Rate limiting is implemented for API calls
- Session management for user authentication

## 📝 Development

### Running Tests

```bash
# Add tests as needed
pytest tests/
```

### Code Style

Follow PEP 8 guidelines. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for MCP server framework
- [Anthropic](https://www.anthropic.com/) for Claude API
- [Ultralytics](https://ultralytics.com/) for YOLO11
- [Streamlit](https://streamlit.io/) for the UI framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Python 3.12, FastMCP, Claude AI, and YOLO11**

