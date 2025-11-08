# 🚀 Quick Start Guide

Get Travel Genie up and running in 5 minutes!

## Step 1: Setup (2 minutes)

```bash
# 1. Navigate to project directory
cd Travel_Genie

# 2. Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and add your Anthropic API key
# Get your key from: https://console.anthropic.com/
```

Edit `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Step 3: Run the App (1 minute)

```bash
streamlit run ui/app.py
```

The app will open at `http://localhost:8501` 🎉

## Step 4: Test It! (1 minute)

### Test Chat:
1. Go to **💬 Chat** tab
2. Type: "Plan a trip to Paris"
3. See Claude's response!

### Test Video Analysis:
1. Go to **📹 Video Analysis** tab
2. Paste a YouTube travel video URL
3. Click **🔍 Analyze**
4. View detection results!

### Test Itinerary:
1. Go to **🗺️ Itinerary** tab
2. Enter destination, dates, travelers
3. Click **📝 Create Itinerary**
4. View your itinerary!

## 🧪 Quick Component Tests

### Test MCP Orchestrator:
```bash
python mcp_servers/orchestrator.py
```

### Test FastMCP Client:
```bash
python examples/fastmcp_client_example.py
```

### Test Integration:
```bash
python examples/integration_example.py
```

## ❓ Troubleshooting

**Problem**: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

**Problem**: `ANTHROPIC_API_KEY not found`
```bash
# Make sure .env file exists and has your key
cat .env | grep ANTHROPIC_API_KEY
```

**Problem**: Port 8501 already in use
```bash
streamlit run ui/app.py --server.port 8502
```

## 📚 More Help

- Full setup guide: `SETUP_AND_TESTING.md`
- Integration status: `INTEGRATION_STATUS.md`
- Examples: `examples/README.md`

---

**That's it! You're ready to use Travel Genie! ✈️**

