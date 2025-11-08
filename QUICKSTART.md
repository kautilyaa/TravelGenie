# 🚀 Quick Start Guide - Run TravelGenie Locally

## Step 1: Activate Virtual Environment

```bash
cd /Users/arunbhyashaswi/Drive/Code/UMD/DATA650/TravelGenie
source venv/bin/activate
```

## Step 2: Configure Environment Variables

The `.env` file has been created from `env.example`. You need to add your API keys:

### Required:
- **ANTHROPIC_API_KEY** - Get from https://console.anthropic.com/
  - This is REQUIRED for the app to work with AI features

### Optional (for full functionality):
- OPENTRIPMAP_KEY - For places/attractions
- OPENROUTESERVICE_KEY - For routing
- UNSPLASH_ACCESS_KEY - For location images
- EVENTBRITE_TOKEN - For local events

**Note:** Weather and Currency APIs work without keys!

Edit the `.env` file:
```bash
nano .env
# or
open .env
```

At minimum, add:
```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
```

## Step 3: Check/Fix Port Issue

If port 8000 is in use, either:

**Option A:** Kill the existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

**Option B:** Use a different port:
```bash
PORT=8001 uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Step 4: Run the Application

### Method 1: Using uvicorn directly (Recommended)
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Method 2: Using Python directly
```bash
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 5: Test the API

### Open in Browser:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

### Test with curl:
```bash
# Health check
curl http://localhost:8000/health

# Test query (requires ANTHROPIC_API_KEY)
curl "http://localhost:8000/query?q=weather in Paris&lat=48.8566&lon=2.3522"
```

## Troubleshooting

### 1. Missing ANTHROPIC_API_KEY Error
- Make sure `.env` file exists and has `ANTHROPIC_API_KEY` set
- Get your key from: https://console.anthropic.com/

### 2. Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### 3. Module Not Found Errors
```bash
source venv/bin/activate
pip install aiosqlite sqlalchemy mcp
```

### 4. Database Errors
- The database is auto-created at `data/travelgenie.db`
- Make sure the `data/` directory exists and is writable

## Quick Test Script

Save this as `test_server.sh`:
```bash
#!/bin/bash
cd /Users/arunbhyashaswi/Drive/Code/UMD/DATA650/TravelGenie
source venv/bin/activate

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start server
echo "Starting TravelGenie server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Make it executable:
```bash
chmod +x test_server.sh
./test_server.sh
```

## What's Working?

Once running, you can:
- ✅ View API documentation at `/docs`
- ✅ Check health status at `/health`
- ✅ Test basic endpoints
- ⚠️ Full AI features require ANTHROPIC_API_KEY
- ⚠️ Some features need additional API keys (see `env.example`)

---

**Next Steps:**
1. Add your ANTHROPIC_API_KEY to `.env`
2. Add other API keys for full functionality (optional)
3. Start the server and test!


