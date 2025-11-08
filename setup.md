# 🛠️ TravelGenie Setup Guide

Complete setup instructions for TravelGenie Travel Assistant with Python 3.12 and MCP (Model Context Protocol).

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Python 3.12 Installation](#python-312-installation)
3. [Project Setup](#project-setup)
4. [API Key Registration](#api-key-registration)
5. [MCP Configuration](#mcp-configuration)
6. [Database Setup](#database-setup)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Python**: 3.12.0 or higher
- **RAM**: Minimum 4GB
- **Disk Space**: 500MB free space
- **Internet**: Required for API calls

## 🐍 Python 3.12 Installation

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

### macOS (using Homebrew)
```bash
brew update
brew install python@3.12
```

### Windows
Download and install from [python.org](https://www.python.org/downloads/release/python-3120/)

### Verify Installation
```bash
python3.12 --version
# Should output: Python 3.12.x
```

## 📦 Project Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/travelgenie.git
cd travelgenie
```

### 2. Create Virtual Environment
```bash
python3.12 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔑 API Key Registration

### 1. Claude API (via Anthropic)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key starting with `sk-ant-...`

**Free Tier Limits:**
- Rate limit: 1000 requests/month
- Token limit: 100K tokens/month

### 2. OpenTripMap API

1. Visit [OpenTripMap API](https://opentripmap.io/product)
2. Register for a free account
3. Confirm your email
4. Get your API key from the dashboard

**Free Tier:**
- 500 requests/day
- No commercial use

### 3. OpenRouteService

1. Go to [OpenRouteService](https://openrouteservice.org/dev/#/signup)
2. Sign up for free account
3. Navigate to dashboard → Tokens
4. Create new token (name: "TravelGenie")
5. Copy the API key

**Free Tier:**
- 2,500 requests/day
- 40 requests/minute

### 4. Unsplash API

1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Register/Login
3. Create new application
4. Accept API Guidelines
5. Copy Access Key (not Secret Key)

**Free Tier:**
- 50 requests/hour
- Demo rate limit

### 5. Eventbrite API

1. Go to [Eventbrite Platform](https://www.eventbrite.com/platform)
2. Create account
3. Navigate to Account Settings → App Management
4. Create new app
5. Get your Personal OAuth Token

**Free Tier:**
- 1000 requests/hour
- Public events only

### 6. Open-Meteo (Weather)

**No API Key Required!** 🎉
- Free for non-commercial use
- No rate limits for reasonable use

### 7. ExchangeRate.host

**No API Key Required!** 🎉
- Completely free
- No registration needed

## 🔧 MCP Configuration

### 1. Install MCP Python SDK
```bash
pip install mcp-python
```

### 2. Configure MCP Settings

Create `config/mcp_config.json`:
```json
{
  "client": {
    "name": "TravelGenie",
    "version": "1.0.0"
  },
  "server": {
    "command": "python",
    "args": ["-m", "mcp_server"]
  },
  "transport": "stdio",
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": true
  }
}
```

### 3. Environment Variables

Create `.env` file in project root:
```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Travel APIs
OPENTRIPMAP_KEY=your_opentripmap_key
OPENROUTESERVICE_KEY=your_openrouteservice_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
EVENTBRITE_TOKEN=your_eventbrite_token

# Database
DATABASE_URL=sqlite:///./data/travelgenie.db

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# MCP Settings
MCP_SERVER_URL=http://localhost:8001
MCP_TIMEOUT=30
```

## 💾 Database Setup

### SQLite (Default - No setup required)

The SQLite database will be automatically created at first run.

### PostgreSQL (Optional for production)

1. Install PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```

2. Create database:
```bash
sudo -u postgres psql
CREATE DATABASE travelgenie;
CREATE USER traveluser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE travelgenie TO traveluser;
\q
```

3. Update `.env`:
```bash
DATABASE_URL=postgresql://traveluser:yourpassword@localhost/travelgenie
```

## 🧪 Testing

### 1. Run Unit Tests
```bash
pytest tests/
```

### 2. Test API Endpoints

Start the server:
```bash
uvicorn main:app --reload
```

Test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Weather query
curl "http://localhost:8000/query?q=weather in Paris&lat=48.8566&lon=2.3522"

# Places query
curl "http://localhost:8000/query?q=museums near me&lat=48.8566&lon=2.3522"
```

### 3. Test MCP Integration
```python
python -m modules.test_mcp
```

## 🚀 Deployment

### Option 1: Render (Recommended)

1. Create account at [render.com](https://render.com)

2. Create `render.yaml`:
```yaml
services:
  - type: web
    name: travelgenie
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
```

3. Connect GitHub repo and deploy

### Option 2: Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy:
```bash
railway login
railway init
railway up
```

### Option 3: Docker

1. Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t travelgenie .
docker run -p 8000:8000 --env-file .env travelgenie
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Version Error
```bash
# Error: Python 3.12 not found
# Solution: Use pyenv to manage Python versions
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv local 3.12.0
```

#### 2. MCP Connection Error
```bash
# Error: Cannot connect to MCP server
# Solution: Check MCP server is running
python -m modules.mcp_server --debug
```

#### 3. API Rate Limits
```python
# Add rate limiting to avoid hitting API limits
from time import sleep
import functools

def rate_limit(calls_per_second=1):
    def decorator(func):
        last_called = [0.0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

#### 4. SSL Certificate Error
```bash
# For development only
export PYTHONHTTPSVERIFY=0
# Or install certificates
pip install certifi
```

### Debug Mode

Enable detailed logging:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support Resources

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/travelgenie/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/travelgenie/issues)
- **Discord**: [Join Community](https://discord.gg/travelgenie)

---

## 📊 API Limits Summary

| API | Free Tier Limits | Rate Limit |
|-----|-----------------|------------|
| Claude (Anthropic) | 1000 req/month | 100K tokens/month |
| OpenTripMap | 500 req/day | No per-minute limit |
| OpenRouteService | 2,500 req/day | 40 req/minute |
| Unsplash | Demo mode | 50 req/hour |
| Eventbrite | Public events | 1000 req/hour |
| Open-Meteo | Unlimited* | Reasonable use |
| ExchangeRate | Unlimited | No limits |

*Within reasonable use

---

## ✅ Setup Checklist

- [ ] Python 3.12 installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Claude API key obtained
- [ ] OpenTripMap API key obtained
- [ ] OpenRouteService API key obtained
- [ ] Unsplash API key obtained
- [ ] Eventbrite token obtained
- [ ] .env file configured
- [ ] Database initialized
- [ ] Server running successfully
- [ ] Test queries working

---

**Need Help?** Open an issue on GitHub or check the troubleshooting section above.