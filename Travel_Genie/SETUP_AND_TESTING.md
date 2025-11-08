# Travel Genie - Setup and Testing Guide

This guide will help you set up, run, and test the Travel Genie application.

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## 🚀 Quick Start

### 1. Clone and Navigate to Repository

```bash
git clone https://github.com/kautilyaa/TravelGenie.git
cd TravelGenie/Travel_Genie
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# At minimum, you need:
# ANTHROPIC_API_KEY=your_key_here
```

**Get API Keys:**
- **Anthropic Claude**: https://console.anthropic.com/
- **YouTube** (optional): https://console.cloud.google.com/
- **Google Maps** (optional): https://console.cloud.google.com/

### 5. Run the Application

```bash
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

## 🧪 Testing Individual Components

### Test 1: MCP Servers

#### Test Itinerary Server

```bash
# Run the itinerary server directly
python mcp_servers/itinerary_server.py
```

The server will start and wait for stdio input. Press Ctrl+C to stop.

#### Test Booking Server

```bash
python mcp_servers/booking_server.py
```

#### Test Maps Server

```bash
python mcp_servers/maps_server.py
```

### Test 2: MCP Orchestrator

```bash
# Test the orchestrator with example usage
python mcp_servers/orchestrator.py
```

This will:
- Start all MCP servers
- Process a sample travel request
- Perform health checks
- Clean up resources

**Expected Output:**
```
Server Status:
{
  "itinerary": {
    "name": "travel-itinerary",
    "running": true,
    ...
  },
  ...
}
```

### Test 3: Claude Agent

```bash
# Test Claude agent (requires API key)
python agents/claude_agent.py
```

**Note**: Make sure `ANTHROPIC_API_KEY` is set in your `.env` file.

### Test 4: Video Analyzer

```bash
# Test YOLO11 video analyzer
python agents/video_analyzer.py
```

**Note**: This will download the YOLO11 model on first run (may take a few minutes).

### Test 5: FastMCP Client Example

```bash
# Test FastMCP client integration
python examples/fastmcp_client_example.py
```

This demonstrates:
- Connecting to MCP servers
- Calling tools
- Listing resources

### Test 6: Complete Integration

```bash
# Test complete integration workflow
python examples/integration_example.py
```

This tests:
- MCP orchestrator
- Claude chat integration
- Video analysis (if configured)

## 🎯 Testing the Streamlit UI

### 1. Start the Application

```bash
streamlit run ui/app.py
```

### 2. Test Each Tab

#### Chat Tab
1. Enter a travel-related question
2. Example: "Plan a 7-day trip to Paris"
3. Verify Claude responds with travel suggestions

#### Video Analysis Tab
1. Enter a YouTube URL (travel video)
2. Click "Analyze"
3. Verify object detection results appear
4. Check summary metrics

#### Itinerary Tab
1. Enter destination, dates, travelers
2. Click "Create Itinerary"
3. Verify itinerary is created
4. Try adding activities

#### Bookings Tab
1. Search for flights (origin, destination, dates)
2. Verify flight results appear
3. Search for hotels
4. Verify hotel results appear

#### Analytics Tab
1. View dashboard metrics
2. Check charts and visualizations

#### Settings Tab
1. Configure API keys
2. Adjust model settings
3. Save preferences

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Make sure you're in the project root directory
cd Travel_Genie

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Claude API Key Error

**Solution:**
```bash
# Check if .env file exists
ls -la .env

# Verify API key is set
cat .env | grep ANTHROPIC_API_KEY

# Or set as environment variable
export ANTHROPIC_API_KEY=your_key_here
```

### Issue: YOLO Model Download Fails

**Solution:**
```bash
# The model will auto-download, but if it fails:
# Manually download from: https://github.com/ultralytics/ultralytics
# Or check your internet connection
```

### Issue: MCP Servers Not Starting

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.12+

# Check if FastMCP is installed
pip show fastmcp

# Reinstall if needed
pip install --upgrade fastmcp
```

### Issue: Port Already in Use

**Solution:**
```bash
# Use a different port
streamlit run ui/app.py --server.port 8502

# Or kill the process using port 8501
# On macOS/Linux:
lsof -ti:8501 | xargs kill -9
```

## 📊 Testing Checklist

### Basic Functionality
- [ ] Application starts without errors
- [ ] All tabs load correctly
- [ ] MCP servers can be started/stopped
- [ ] Claude chat responds to queries
- [ ] Video analysis processes YouTube URLs
- [ ] Itinerary creation works
- [ ] Booking searches return results

### Integration Tests
- [ ] MCP orchestrator coordinates multiple servers
- [ ] Claude chat integrates with MCP data
- [ ] Video analysis results display in UI
- [ ] Settings are saved and loaded
- [ ] Session management works

### Error Handling
- [ ] Graceful handling of missing API keys
- [ ] Error messages display correctly
- [ ] Invalid inputs are rejected
- [ ] Server failures are handled gracefully

## 🧪 Running Automated Tests (Future)

When unit tests are added:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_claude_agent.py
```

## 📝 Example Test Scenarios

### Scenario 1: Complete Trip Planning

1. **Start Application**: `streamlit run ui/app.py`
2. **Navigate to Chat Tab**
3. **Ask**: "I want to plan a 7-day trip to Tokyo in June"
4. **Verify**: Claude provides suggestions
5. **Navigate to Itinerary Tab**
6. **Create Itinerary**: Tokyo, June 1-7, 2 travelers
7. **Verify**: Itinerary is created
8. **Navigate to Bookings Tab**
9. **Search Flights**: New York to Tokyo, June 1
10. **Verify**: Flight options appear

### Scenario 2: Video Analysis

1. **Start Application**
2. **Navigate to Video Analysis Tab**
3. **Enter YouTube URL**: Any travel video
4. **Set Duration**: 30 seconds
5. **Click Analyze**
6. **Verify**: 
   - Analysis completes
   - Detection results appear
   - Summary metrics display
   - Top objects chart shows

### Scenario 3: MCP Server Coordination

1. **Run Orchestrator Test**: `python mcp_servers/orchestrator.py`
2. **Verify**:
   - All servers start
   - Travel request is processed
   - Results from multiple servers are combined
   - Health checks pass
   - Cleanup works correctly

## 🎓 Learning Resources

- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **Streamlit Docs**: https://docs.streamlit.io/
- **Anthropic Claude API**: https://docs.anthropic.com/
- **YOLO11 Docs**: https://docs.ultralytics.com/

## 💡 Tips

1. **Start Small**: Test individual components before full integration
2. **Check Logs**: Look at terminal output for error messages
3. **Use Examples**: The example files show proper usage patterns
4. **API Keys**: Keep your API keys secure and never commit them
5. **Virtual Environment**: Always use a virtual environment
6. **Python Version**: Ensure you're using Python 3.12+

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages in the terminal
3. Check the GitHub issues: https://github.com/kautilyaa/TravelGenie/issues
4. Review the integration status: `INTEGRATION_STATUS.md`
5. Check example files for usage patterns

---

**Happy Testing! 🚀**

