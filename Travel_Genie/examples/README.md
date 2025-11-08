# Travel Genie - Example Usage Files

This directory contains example scripts demonstrating how to use various components of Travel Genie.

## 📁 Files

### 1. `fastmcp_client_example.py`
Demonstrates how to connect to MCP servers using the FastMCP client library.

**Usage:**
```bash
python examples/fastmcp_client_example.py
```

**What it shows:**
- How to connect to MCP servers via stdio
- How to call tools on MCP servers
- How to list available tools and resources
- Examples for itinerary, booking, and maps servers

### 2. `integration_example.py`
Complete integration example showing all components working together.

**Usage:**
```bash
python examples/integration_example.py
```

**What it shows:**
- Complete travel planning workflow
- Claude chat integration with MCP servers
- Video analysis workflow
- How components interact with each other

## 🚀 Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run examples:**
   ```bash
   # FastMCP client example
   python examples/fastmcp_client_example.py
   
   # Integration example
   python examples/integration_example.py
   ```

## 📝 Example Scenarios

### Scenario 1: Create an Itinerary

```python
from mcp_servers.orchestrator import MCPOrchestrator

async def create_itinerary():
    orchestrator = MCPOrchestrator()
    async with orchestrator.session():
        result = await orchestrator.manager.send_request(
            "itinerary",
            "create_itinerary",
            {
                "destination": "Paris, France",
                "start_date": "2025-12-15",
                "end_date": "2025-12-22",
                "travelers": 2
            }
        )
        print(result)
```

### Scenario 2: Chat with Claude

```python
from agents.claude_agent import ClaudeAgent

async def chat_example():
    agent = ClaudeAgent(api_key="your_key")
    session_id = agent.create_session("my_session")
    response = await agent.chat("Plan a trip to Paris", session_id)
    print(response)
```

### Scenario 3: Analyze Video

```python
from agents.video_analyzer import YOLO11Analyzer

async def analyze_video():
    analyzer = YOLO11Analyzer()
    result = await analyzer.analyze_youtube_video(
        url="https://www.youtube.com/watch?v=...",
        duration_seconds=30
    )
    print(result.summary)
```

## 🔧 Troubleshooting

### FastMCP Client Not Available
If you see "FastMCP client not available", install it:
```bash
pip install fastmcp
```

### API Key Errors
Make sure your API keys are set in the `.env` file or as environment variables.

### Import Errors
Ensure you're running from the project root directory:
```bash
cd Travel_Genie
python examples/integration_example.py
```

## 📚 More Information

For detailed documentation, see:
- Main README: `../README.md`
- Integration Status: `../INTEGRATION_STATUS.md`
- API Documentation: Check individual module docstrings

