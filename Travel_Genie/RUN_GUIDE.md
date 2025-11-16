# 🚀 How to Run Travel Genie

Complete guide to running Travel Genie with port configuration.

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd Travel_Genie
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your_key_here
```

### Step 3: Run the Application
```bash
streamlit run ui/app.py
```

The app opens at `http://localhost:8501` 🎉

---

## MCP Server Port Configuration

### Default Configuration (No Setup Needed)

By default, MCP servers use **stdio transport** and are configured with ports (but ports aren't actively used with stdio):

- **Itinerary Server**: Port 8000
- **Maps Server**: Port 8001  
- **Booking Server**: Port 8002

**Just run the app - no port configuration needed!**

```bash
streamlit run ui/app.py
```

### Custom Port Configuration

If you want to customize ports, edit `.env`:

```env
# MCP Server Ports
MCP_ITINERARY_PORT=9000
MCP_MAPS_PORT=9001
MCP_BOOKING_PORT=9002

# Or use different hosts
MCP_ITINERARY_HOST=localhost
MCP_MAPS_HOST=0.0.0.0  # Listen on all interfaces
```

### Using HTTP/SSE Transport (Advanced)

To use HTTP transport instead of stdio:

```env
# Enable HTTP/SSE transport
MCP_TRANSPORT=sse

# Configure ports
MCP_ITINERARY_PORT=8000
MCP_MAPS_PORT=8001
MCP_BOOKING_PORT=8002
```

**Note**: HTTP transport requires `httpx` package:
```bash
pip install httpx
```

---

## Running Individual Components

### Run MCP Orchestrator (Test All Servers)

```bash
python mcp_servers/orchestrator.py
```

This will:
- Start all MCP servers
- Process a sample travel request
- Show server status
- Perform health checks

### Run Individual MCP Servers

```bash
# Itinerary Server
python mcp_servers/itinerary_server.py

# Maps Server  
python mcp_servers/maps_server.py

# Booking Server
python mcp_servers/booking_server.py
```

**With custom port:**
```bash
MCP_PORT=9000 MCP_HOST=localhost python mcp_servers/itinerary_server.py
```

### Test FastMCP Client

```bash
python examples/fastmcp_client_example.py
```

### Test Complete Integration

```bash
python examples/integration_example.py
```

---

## Running the Streamlit UI

### Basic Run
```bash
streamlit run ui/app.py
```

### Custom Port
```bash
streamlit run ui/app.py --server.port 8502
```

### Custom Host
```bash
streamlit run ui/app.py --server.address 0.0.0.0
```

### With Configuration
```bash
# Set environment variables first
export ANTHROPIC_API_KEY=your_key
export MCP_ITINERARY_PORT=9000

# Then run
streamlit run ui/app.py
```

---

## Complete Run Example

### Full Setup and Run

```bash
# 1. Navigate to project
cd Travel_Genie

# 2. Create virtual environment (optional but recommended)
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 5. (Optional) Configure MCP ports in .env
# MCP_ITINERARY_PORT=8000
# MCP_MAPS_PORT=8001
# MCP_BOOKING_PORT=8002

# 6. Verify setup
python test_setup.py

# 7. Run the application
streamlit run ui/app.py
```

---

## What Happens When You Run

1. **Streamlit starts** on port 8501 (default)
2. **MCP Orchestrator initializes** and reads port configuration
3. **MCP Servers start** with configured ports (stdio transport by default)
4. **Application loads** with all features available

### Server Startup Logs

You'll see logs like:
```
INFO - Started itinerary server with stdio transport on port 8000 (PID: 12345)
INFO - Started maps server with stdio transport on port 8001 (PID: 12346)
INFO - Started booking server with stdio transport on port 8002 (PID: 12347)
```

---

## Testing After Running

### 1. Test Chat
- Go to **💬 Chat** tab
- Type: "Plan a trip to Paris"
- Should get Claude's response

### 2. Test Video Analysis
- Go to **📹 Video Analysis** tab
- Paste YouTube URL
- Click **🔍 Analyze**
- Video should display in webview
- Analysis results should appear

### 3. Test Itinerary
- Go to **🗺️ Itinerary** tab
- Enter destination, dates, travelers
- Click **📝 Create Itinerary**
- Itinerary should be created
- Map should display (if configured)

### 4. Test Bookings
- Go to **🎫 Bookings** tab
- Search for flights
- Results should appear

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port in .env
MCP_ITINERARY_PORT=9000
```

### MCP Servers Not Starting

```bash
# Check logs in terminal
# Verify Python version (3.11+)
python --version

# Check if FastMCP is installed
pip show fastmcp
```

### API Key Error

```bash
# Verify .env file exists
ls -la .env

# Check API key is set
cat .env | grep ANTHROPIC_API_KEY
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify you're in correct directory
pwd  # Should be in Travel_Genie/
```

---

## Environment Variables Summary

### Required
```env
ANTHROPIC_API_KEY=your_key_here
```

### Optional (MCP Configuration)
```env
# Transport type
MCP_TRANSPORT=stdio  # or "sse"

# Server hosts
MCP_ITINERARY_HOST=localhost
MCP_MAPS_HOST=localhost
MCP_BOOKING_HOST=localhost

# Server ports
MCP_ITINERARY_PORT=8000
MCP_MAPS_PORT=8001
MCP_BOOKING_PORT=8002
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `streamlit run ui/app.py` | Run main application |
| `python mcp_servers/orchestrator.py` | Test MCP servers |
| `python test_setup.py` | Verify setup |
| `python examples/integration_example.py` | Test integration |

---

## Next Steps

1. ✅ Run the app: `streamlit run ui/app.py`
2. ✅ Test chat functionality
3. ✅ Test video analysis
4. ✅ Create an itinerary
5. ✅ Explore all features!

For detailed documentation:
- **Port Configuration**: `MCP_PORT_CONFIGURATION.md`
- **Setup Guide**: `SETUP_AND_TESTING.md`
- **Quick Start**: `QUICK_START.md`

---

**Happy Travel Planning! ✈️**




