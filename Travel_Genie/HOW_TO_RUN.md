# 🚀 How to Run and Test Travel Genie

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### 3. Verify Setup
```bash
python test_setup.py
```

### 4. Run the App
```bash
streamlit run ui/app.py
```

**That's it!** The app opens at `http://localhost:8501`

---

## 🧪 Testing Individual Components

### Test MCP Orchestrator
```bash
python mcp_servers/orchestrator.py
```
**Expected**: All servers start, process request, show results

### Test FastMCP Client
```bash
python examples/fastmcp_client_example.py
```
**Expected**: Connects to servers, calls tools, shows results

### Test Complete Integration
```bash
python examples/integration_example.py
```
**Expected**: All components work together

---

## 🎯 Testing the UI

### 1. Start the App
```bash
streamlit run ui/app.py
```

### 2. Test Each Feature

#### 💬 Chat Tab
- Type: "Plan a trip to Paris"
- **Expected**: Claude responds with travel suggestions

#### 📹 Video Analysis Tab
- Paste YouTube URL
- Click "Analyze"
- **Expected**: Object detection results appear

#### 🗺️ Itinerary Tab
- Enter destination, dates, travelers
- Click "Create Itinerary"
- **Expected**: Itinerary created successfully

#### 🎫 Bookings Tab
- Search for flights/hotels
- **Expected**: Results displayed

---

## 📋 Complete Testing Checklist

Run `python test_setup.py` to verify:

- [x] Python version (3.11+)
- [x] All dependencies installed
- [x] Project structure correct
- [x] .env file configured
- [x] All modules importable

---

## 🔧 Troubleshooting

**Missing packages?**
```bash
pip install -r requirements.txt
```

**API key error?**
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY
```

**Port in use?**
```bash
streamlit run ui/app.py --server.port 8502
```

---

## 📚 More Help

- **Quick Start**: `QUICK_START.md`
- **Detailed Guide**: `SETUP_AND_TESTING.md`
- **Examples**: `examples/README.md`

---

**Ready to go! 🎉**

