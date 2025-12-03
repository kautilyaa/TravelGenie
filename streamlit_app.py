import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

# Claude API imports
try:
    from anthropic import Anthropic  # type: ignore
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    # Note: Warning will be shown in the chat tab if needed

# Add server directories to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "flight_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "hotel_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "event_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "geocoder_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "weather_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "finance_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "traffic_crowd_server"))

# Verify critical modules are available before starting Streamlit
try:
    import mcp.server.fastmcp
    import geopy
    import requests
except ImportError as e:
    print(f"❌ ERROR: Missing required module: {e}")
    print("Please ensure you're running Streamlit with the virtual environment activated:")
    print("  source .venv/bin/activate")
    print("  streamlit run streamlit_app.py")
    print("\nOr use the provided script:")
    print("  ./run_streamlit.sh")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.set_page_config(
    page_title="Travel Assistant - MCP Orchestration",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'api_keys_set' not in st.session_state:
    st.session_state.api_keys_set = False

# Title
st.title("🌍 Travel Assistant - MCP Server Orchestration")
st.markdown("**Orchestrate 7 MCP servers** to create comprehensive travel plans")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ API Configuration")
    
    serpapi_key = st.text_input(
        "SerpAPI Key",
        value=os.getenv("SERPAPI_KEY", ""),
        type="password",
        help="Required for flights, hotels, events, and finance servers"
    )
    
    st.info("ℹ️ Weather Server uses Open-Meteo API (free, no API key required)")
    
    if serpapi_key:
        os.environ["SERPAPI_KEY"] = serpapi_key
        st.session_state.api_keys_set = True
        st.success("✅ SerpAPI key set")
    else:
        st.warning("⚠️ SerpAPI key required")
        st.session_state.api_keys_set = False
    
    st.divider()
    
    st.header("📊 Server Status")
    server_status = {}
    
    # Check if servers can be imported
    servers_to_check = {
        "Flight Server": "servers.flight_server.flight_server",
        "Hotel Server": "servers.hotel_server.hotel_server",
        "Event Server": "servers.event_server.event_server",
        "Geocoder Server": "servers.geocoder_server.geocoder_server",
        "Weather Server": "servers.weather_server.weather_server",
        "Finance Server": "servers.finance_server.finance_server",
        "Traffic & Crowd Server": "servers.traffic_crowd_server.traffic_crowd_server"
    }
    
    for server_name, module_path in servers_to_check.items():
        try:
            __import__(module_path)
            server_status[server_name] = "✅ Available"
        except Exception as e:
            server_status[server_name] = f"❌ Error: {str(e)[:30]}"
    
    for server, status in server_status.items():
        st.text(f"{server}: {status}")

# Main Interface
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Plan Trip", "💬 Chat with Claude", "🔍 Individual Searches", "📋 View Results"])

with tab1:
    st.header("Complete Travel Planning")
    st.markdown("Fill out the form below to get a comprehensive travel plan")
    
    with st.form("travel_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            origin = st.text_input("📍 Origin", placeholder="e.g., Reston, Virginia", key="origin")
            destination = st.text_input("📍 Destination", placeholder="e.g., Banff, Alberta", key="dest")
            start_date = st.date_input("📅 Start Date", value=datetime.now().date() + timedelta(days=7), key="start")
            end_date = st.date_input("📅 End Date", value=datetime.now().date() + timedelta(days=14), key="end")
        
        with col2:
            adults = st.number_input("👥 Adults", min_value=1, max_value=10, value=2, key="adults")
            children = st.number_input("👶 Children", min_value=0, max_value=10, value=0, key="children")
            budget = st.number_input("💰 Budget (USD)", min_value=0, value=5000, key="budget")
            currency = st.selectbox("💵 Currency", ["USD", "CAD", "EUR", "GBP", "JPY"], key="currency")
        
        interests = st.multiselect(
            "🎯 Interests",
            ["Hiking", "Sight-seeing", "Dining", "Museums", "Nightlife", "Shopping", "Beaches", "Adventure Sports"],
            default=["Hiking", "Sight-seeing", "Dining", "Museums"],
            key="interests"
        )
        
        # Server selection
        st.subheader("Select Servers to Use")
        col_flight, col_hotel, col_event, col_weather, col_finance = st.columns(5)
        
        with col_flight:
            use_flights = st.checkbox("✈️ Flights", value=True)
        with col_hotel:
            use_hotels = st.checkbox("🏨 Hotels", value=True)
        with col_event:
            use_events = st.checkbox("🎭 Events", value=True)
        with col_weather:
            use_weather = st.checkbox("🌤️ Weather", value=True)
        with col_finance:
            use_finance = st.checkbox("💰 Finance", value=True)
        
        submitted = st.form_submit_button("🚀 Plan My Trip", type="primary", use_container_width=True)
    
    if submitted:
        if not st.session_state.api_keys_set:
            st.error("⚠️ Please enter your SerpAPI key in the sidebar")
            st.stop()
        
        if not origin or not destination:
            st.error("⚠️ Please fill in origin and destination")
            st.stop()
        
        if end_date <= start_date:
            st.error("⚠️ End date must be after start date")
            st.stop()
        
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        total_steps = sum([
            use_flights, use_hotels, use_events, use_weather, use_finance, True  # +1 for geocoding
        ])
        current_step = 0
        
        results = {}
        
        # Step 1: Geocoding (always needed)
        status_text.text("🗺️ Step 1: Getting location coordinates...")
        progress_bar.progress(current_step / total_steps)
        try:
            from servers.geocoder_server.geocoder_server import geocode_location
            
            origin_result = geocode_location(origin)
            dest_result = geocode_location(destination)
            
            results["geocoding"] = {
                "origin": origin_result,
                "destination": dest_result
            }
            
            # Extract coordinates from nested location_data structure
            origin_location_data = origin_result.get("location_data", {})
            dest_location_data = dest_result.get("location_data", {})
            
            origin_lat = origin_location_data.get("latitude", "N/A")
            origin_lon = origin_location_data.get("longitude", "N/A")
            dest_lat = dest_location_data.get("latitude", "N/A")
            dest_lon = dest_location_data.get("longitude", "N/A")
            
            # Display route format: Origin -> Destination with coordinates
            if origin_lat != "N/A" and dest_lat != "N/A":
                st.success(f"✅ Geocoded: {origin} → {destination} | ({origin_lat}, {origin_lon}) → ({dest_lat}, {dest_lon})")
            else:
                st.warning(f"⚠️ Geocoding incomplete: {origin} → {destination} | Check coordinates")
            current_step += 1
        except Exception as e:
            st.error(f"❌ Geocoding error: {e}")
            results["geocoding"] = None
        
        # Step 2: Flight Search
        if use_flights:
            status_text.text(f"✈️ Step {current_step + 1}/{total_steps}: Searching for flights...")
            progress_bar.progress(current_step / total_steps)
            try:
                from servers.flight_server.flight_server import search_flights
                
                flight_results = search_flights(
                    departure_id=origin,
                    arrival_id=destination,
                    outbound_date=start_date.strftime("%Y-%m-%d"),
                    return_date=end_date.strftime("%Y-%m-%d"),
                    adults=adults,
                    children=children,
                    currency=currency,
                    max_results=10
                )
                
                # Load full flight data from saved file
                search_id = flight_results.get("search_id", "")
                if search_id:
                    try:
                        flight_file_path = os.path.join("flights", f"{search_id}.json")
                        if os.path.exists(flight_file_path):
                            with open(flight_file_path, 'r') as f:
                                full_flight_data = json.load(f)
                                # Add flights to results for display
                                flight_results["best_flights"] = full_flight_data.get("best_flights", [])
                                flight_results["other_flights"] = full_flight_data.get("other_flights", [])
                    except Exception as e:
                        st.warning(f"Could not load full flight data: {e}")
                
                results["flights"] = flight_results
                # Flight results structure: best_flights and other_flights
                best_flights = flight_results.get("best_flights", [])
                other_flights = flight_results.get("other_flights", [])
                flight_count = len(best_flights) + len(other_flights)
                if flight_count > 0:
                    st.success(f"✅ Found {flight_count} flight options ({len(best_flights)} best, {len(other_flights)} other)")
                else:
                    total_best = flight_results.get("total_best_flights", 0)
                    total_other = flight_results.get("total_other_flights", 0)
                    if total_best > 0 or total_other > 0:
                        st.success(f"✅ Found {total_best + total_other} flight options ({total_best} best, {total_other} other)")
                    else:
                        st.warning(f"⚠️ No flights found. Try using airport codes (e.g., 'IAD' for Reston area, 'YYC' for Calgary/Banff area)")
                current_step += 1
            except Exception as e:
                st.error(f"❌ Flight search error: {e}")
                results["flights"] = None
        
        # Step 3: Hotel Search
        if use_hotels:
            status_text.text(f"🏨 Step {current_step + 1}/{total_steps}: Searching for hotels...")
            progress_bar.progress(current_step / total_steps)
            try:
                from servers.hotel_server.hotel_server import search_hotels
                
                hotel_results = search_hotels(
                    location=destination,
                    check_in_date=start_date.strftime("%Y-%m-%d"),
                    check_out_date=end_date.strftime("%Y-%m-%d"),
                    adults=adults,
                    children=children,
                    currency=currency,
                    max_results=10
                )
                
                # Load full hotel data from saved file
                search_id = hotel_results.get("search_id", "")
                if search_id:
                    try:
                        hotel_file_path = os.path.join("hotels", f"{search_id}.json")
                        if os.path.exists(hotel_file_path):
                            with open(hotel_file_path, 'r') as f:
                                full_hotel_data = json.load(f)
                                # Add properties to results for display
                                hotel_results["properties"] = full_hotel_data.get("properties", [])
                    except Exception as e:
                        st.warning(f"Could not load full hotel data: {e}")
                
                results["hotels"] = hotel_results
                # Hotel results structure: properties
                hotel_count = hotel_results.get("total_properties", 0)
                if hotel_count > 0:
                    st.success(f"✅ Found {hotel_count} hotel options")
                else:
                    st.warning(f"⚠️ No hotels found for {destination}")
                current_step += 1
            except Exception as e:
                st.error(f"❌ Hotel search error: {e}")
                results["hotels"] = None
        
        # Step 4: Weather Forecast
        if use_weather:
            status_text.text(f"🌤️ Step {current_step + 1}/{total_steps}: Getting weather forecast...")
            progress_bar.progress(current_step / total_steps)
            try:
                from servers.weather_server.weather_server import get_weather_forecast
                
                # Use destination name for weather (Open-Meteo supports location names)
                # This ensures the location name appears correctly in results
                weather_results = get_weather_forecast(
                    location=destination,
                    forecast_days=5,
                    hourly=False
                )
                
                # Update location name in weather results if geocoding was successful
                if results.get("geocoding") and results["geocoding"].get("destination"):
                    dest_result = results["geocoding"]["destination"]
                    dest_location_data = dest_result.get("location_data", {})
                    display_name = dest_location_data.get("display_name", destination)
                    
                    # Update the location name in weather results
                    if "location" in weather_results:
                        weather_results["location"]["name"] = display_name
                        # Update coordinates if available
                        lat = dest_location_data.get("latitude")
                        lon = dest_location_data.get("longitude")
                        if lat and lon:
                            weather_results["location"]["coordinates"] = f"{lat}, {lon}"
                
                results["weather"] = weather_results
                st.success("✅ Weather forecast retrieved")
                current_step += 1
            except Exception as e:
                st.error(f"❌ Weather error: {e}")
                results["weather"] = None
        
        # Step 5: Event Search
        if use_events:
            status_text.text(f"🎭 Step {current_step + 1}/{total_steps}: Finding local events...")
            progress_bar.progress(current_step / total_steps)
            try:
                from servers.event_server.event_server import search_events
                
                event_query = ", ".join(interests) if interests else "events"
                event_results = search_events(
                    query=event_query,
                    location=destination,
                    date_filter="month",
                    max_results=20
                )
                
                results["events"] = event_results
                event_count = len(event_results.get("events", []))
                st.success(f"✅ Found {event_count} events")
                current_step += 1
            except Exception as e:
                st.error(f"❌ Event search error: {e}")
                results["events"] = None
        
        # Step 6: Currency Conversion & Budget Analysis
        if use_finance:
            status_text.text(f"💰 Step {current_step + 1}/{total_steps}: Analyzing budget...")
            progress_bar.progress(current_step / total_steps)
            try:
                from servers.finance_server.finance_server import convert_currency
                
                # Convert currency if needed
                conversion_rate = 1.0
                if currency != "USD":
                    conversion_result = convert_currency(
                        amount=1,
                        from_currency=currency,
                        to_currency="USD"
                    )
                    if conversion_result and "converted_amount" in conversion_result:
                        conversion_rate = conversion_result["converted_amount"]
                
                results["currency_conversion"] = {
                    "rate": conversion_rate,
                    "from": currency,
                    "to": "USD"
                }
                
                # Calculate total costs
                total_cost = 0
                cost_breakdown = {}
                
                if results.get("flights"):
                    # Flight results structure: best_flights and other_flights
                    best_flights = results["flights"].get("best_flights", [])
                    other_flights = results["flights"].get("other_flights", [])
                    flights = best_flights + other_flights
                    if flights:
                        price_info = flights[0].get("price", {})
                        flight_price = price_info.get("total") or price_info.get("extracted_value") or 0
                        if flight_price:
                            total_cost += flight_price
                            cost_breakdown["flights"] = flight_price
                
                if results.get("hotels"):
                    # Hotel results structure: properties
                    hotels = results["hotels"].get("properties", [])
                    if hotels:
                        # Get price per night and calculate total for stay duration
                        rate_info = hotels[0].get("rate_per_night", {})
                        price_per_night = rate_info.get("extracted_lowest") or rate_info.get("low") or 0
                        if price_per_night:
                            # Calculate nights
                            nights = (end_date - start_date).days
                            hotel_total = price_per_night * nights * adults
                            total_cost += hotel_total
                            cost_breakdown["hotels"] = hotel_total
                            cost_breakdown["hotels_per_night"] = price_per_night
                
                results["budget_analysis"] = {
                    "total_budget_usd": budget,
                    "estimated_cost_usd": total_cost * conversion_rate,
                    "remaining_budget": budget - (total_cost * conversion_rate),
                    "cost_breakdown": cost_breakdown,
                    "currency": currency
                }
                
                st.success("✅ Budget analysis complete")
                current_step += 1
            except Exception as e:
                st.error(f"❌ Finance error: {e}")
                results["currency_conversion"] = None
        
        progress_bar.progress(1.0)
        status_text.text("✅ Complete!")
        
        # Store results in session state
        st.session_state.results = results
        
        # Display results
        with results_container:
            st.header("📊 Travel Plan Results")
            
            # Summary Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if results.get("flights"):
                    # Flight results structure: best_flights and other_flights
                    best_flights = results["flights"].get("best_flights", [])
                    other_flights = results["flights"].get("other_flights", [])
                    flight_count = len(best_flights) + len(other_flights)
                    st.metric("Flight Options", flight_count)
            
            with col2:
                if results.get("hotels"):
                    # Hotel results structure: properties
                    hotel_count = results["hotels"].get("total_properties", 0)
                    st.metric("Hotel Options", hotel_count)
            
            with col3:
                if results.get("events"):
                    event_count = len(results["events"].get("events", []))
                    st.metric("Events Found", event_count)
            
            with col4:
                if results.get("budget_analysis"):
                    remaining = results["budget_analysis"].get("remaining_budget", 0)
                    st.metric("Remaining Budget", f"${remaining:,.2f}")
            
            # Detailed Results
            if results.get("flights"):
                st.subheader("✈️ Flight Options")
                # Flight results structure: best_flights and other_flights
                best_flights = results["flights"].get("best_flights", [])
                other_flights = results["flights"].get("other_flights", [])
                
                if best_flights:
                    st.markdown("**Best Flights:**")
                    for i, flight in enumerate(best_flights[:5], 1):
                        price_info = flight.get("price", {})
                        price = price_info.get("total") or price_info.get("extracted_value") or "N/A"
                        with st.expander(f"Best Flight {i}: ${price}"):
                            st.json(flight)
                
                if other_flights:
                    st.markdown("**Other Flights:**")
                    for i, flight in enumerate(other_flights[:5], 1):
                        price_info = flight.get("price", {})
                        price = price_info.get("total") or price_info.get("extracted_value") or "N/A"
                        with st.expander(f"Flight {i}: ${price}"):
                            st.json(flight)
                
                if not best_flights and not other_flights:
                    st.info("No flight results available. Try using airport codes (e.g., 'IAD' for Reston area, 'YYC' for Calgary/Banff area)")
            
            if results.get("hotels"):
                st.subheader("🏨 Hotel Options")
                # Hotel results structure: properties
                hotels = results["hotels"].get("properties", [])
                if hotels:
                    for i, hotel in enumerate(hotels[:5], 1):
                        title = hotel.get("title", "N/A")
                        price_info = hotel.get("rate_per_night", {})
                        price = price_info.get("extracted_lowest") or price_info.get("low") or "N/A"
                        with st.expander(f"Hotel {i}: {title} - ${price}/night"):
                            st.json(hotel)
                else:
                    st.info(f"No hotel results available for {destination}")
            
            if results.get("weather"):
                st.subheader("🌤️ Weather Forecast")
                st.json(results["weather"])
            
            if results.get("events"):
                st.subheader("🎭 Local Events")
                events = results["events"].get("events", [])[:10]
                for i, event in enumerate(events, 1):
                    with st.expander(f"Event {i}: {event.get('title', 'N/A')}"):
                        st.json(event)
            
            if results.get("budget_analysis"):
                st.subheader("💰 Budget Analysis")
                st.json(results["budget_analysis"])
            
            # Download button
            st.download_button(
                label="📥 Download Full Results (JSON)",
                data=json.dumps(results, indent=2, default=str),
                file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

with tab2:
    st.header("💬 Chat with Claude - Travel Planning Assistant")
    st.markdown("**Have a conversation with Claude to plan your trip!** Claude will use all available travel services to help you.")
    
    if not CLAUDE_AVAILABLE:
        st.error("❌ Anthropic SDK not installed. Please install it: `pip install anthropic`")
        st.stop()
    
    # Initialize Claude client
    anthropic_api_key = st.sidebar.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Get your API key from https://console.anthropic.com/"
    )
    
    if not anthropic_api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to use Claude chat.")
        st.info("💡 You can also set it as an environment variable: `ANTHROPIC_API_KEY`")
        st.stop()
    
    # Initialize session state for chat
    if 'claude_messages' not in st.session_state:
        st.session_state.claude_messages = []
    
    if 'claude_client' not in st.session_state or st.session_state.get('claude_api_key') != anthropic_api_key:
        try:
            st.session_state.claude_client = Anthropic(api_key=anthropic_api_key)
            st.session_state.claude_api_key = anthropic_api_key
        except Exception as e:
            st.error(f"❌ Error initializing Claude client: {e}")
            st.stop()
    
    # Import orchestrator
    try:
        from claude_orchestrator import get_tool_definitions, execute_tool, get_system_prompt
    except ImportError as e:
        st.error(f"❌ Could not import orchestrator: {e}")
        st.stop()
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.claude_messages:
            with st.chat_message(message["role"]):
                # Display content
                if message.get("content"):
                    st.markdown(message["content"])
                
                # Display tool calls with better formatting
                if "tool_calls" in message and message["tool_calls"]:
                    st.markdown("---")
                    st.markdown("**🔧 Tools Used:**")
                    for i, tool_call in enumerate(message["tool_calls"], 1):
                        tool_name = tool_call.get("name", "Unknown")
                        tool_input = tool_call.get("input", {})
                        
                        # Display tool call in a cleaner format
                        with st.expander(f"**{i}. {tool_name}**", expanded=False):
                            st.json(tool_input)
                
                # Display status messages if any
                if "status_messages" in message:
                    for status in message["status_messages"]:
                        st.info(f"ℹ️ {status}")
    
    # Chat input
    user_input = st.chat_input("Ask me about travel planning... (e.g., 'Plan a trip to Banff from Reston, Virginia for June 7-14, 2025')")
    
    if user_input:
        # Add user message to chat
        st.session_state.claude_messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get Claude's response
        with st.chat_message("assistant"):
            # Create placeholders for different parts of the response
            status_placeholder = st.empty()
            thinking_placeholder = st.empty()
            tool_execution_container = st.container()
            tool_calls_placeholder = st.empty()
            response_placeholder = st.empty()
            
            try:
                # Prepare messages for Claude (convert to API format)
                api_messages = []
                for msg in st.session_state.claude_messages[:-1]:  # Exclude the just-added user message
                    if msg["role"] == "user":
                        api_messages.append({
                            "role": "user",
                            "content": msg["content"]
                        })
                    elif msg["role"] == "assistant":
                        # Reconstruct assistant message with tool calls if any
                        content = []
                        if msg.get("content"):
                            content.append({"type": "text", "text": msg["content"]})
                        if "tool_calls" in msg:
                            # Note: We'll need to store tool use blocks differently
                            # For now, just include text content
                            pass
                        if content:
                            api_messages.append({
                                "role": "assistant",
                                "content": content
                            })
                
                # Add current user message
                api_messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Call Claude with tools
                # Try claude-3-5-sonnet first, fallback to claude-3-haiku if not available
                model_name = "claude-3-5-sonnet-20241022"
                thinking_placeholder.info("🤔 **Thinking...** Analyzing your request and planning the best approach.")
                
                try:
                    response = st.session_state.claude_client.messages.create(
                        model=model_name,
                        max_tokens=4096,
                        system=get_system_prompt(),
                        messages=api_messages,
                        tools=get_tool_definitions()
                    )
                except Exception as model_error:
                    # If model not found, try fallback model
                    if "404" in str(model_error) or "not_found" in str(model_error).lower():
                        status_placeholder.warning(f"⚠️ Model {model_name} not available. Using fallback model...")
                        model_name = "claude-3-haiku-20240307"
                        thinking_placeholder.info("🤔 **Thinking...** Analyzing your request with fallback model.")
                        response = st.session_state.claude_client.messages.create(
                            model=model_name,
                            max_tokens=4096,
                            system=get_system_prompt(),
                            messages=api_messages,
                            tools=get_tool_definitions()
                        )
                    else:
                        raise
                
                # Clear thinking placeholder
                thinking_placeholder.empty()
                
                # Process response
                assistant_message = {"role": "assistant", "content": "", "tool_calls": [], "status_messages": []}
                full_response = ""
                tool_calls_info = []
                
                # Handle tool calls
                if response.stop_reason == "tool_use":
                    tool_results = []
                    tool_status_messages = []
                    
                    # First round of tool calls
                    with tool_execution_container:
                        for idx, content_block in enumerate(response.content):
                            if content_block.type == "tool_use":
                                tool_name = content_block.name
                                tool_input = content_block.input
                                tool_id = content_block.id
                                
                                tool_call_info = {
                                    "name": tool_name,
                                    "input": tool_input
                                }
                                tool_calls_info.append(tool_call_info)
                                
                                # Show tool call in real-time
                                tool_status = st.empty()
                                tool_status.info(f"🔧 **Executing:** `{tool_name}`")
                                
                                # Execute tool
                                tool_result = execute_tool(tool_name, **tool_input)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": json.dumps(tool_result, indent=2, default=str)
                                })
                                
                                # Update status to show completion
                                tool_status.success(f"✅ **Completed:** `{tool_name}`")
                    
                    # Show all tool calls summary after execution
                    if tool_calls_info:
                        tool_calls_placeholder.markdown("---")
                        tool_calls_placeholder.markdown("**🔧 Tools Executed:**")
                        for i, tool_call in enumerate(tool_calls_info, 1):
                            tool_name = tool_call.get("name", "Unknown")
                            tool_input = tool_call.get("input", {})
                            with tool_calls_placeholder.expander(f"**{i}. {tool_name}**", expanded=False):
                                st.json(tool_input)
                    
                    # Call Claude again with tool results
                    api_messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    api_messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Get final response (may need multiple rounds)
                    max_iterations = 5
                    iteration = 0
                    current_response = response
                    
                    while current_response.stop_reason == "tool_use" and iteration < max_iterations:
                        iteration += 1
                        tool_results = []
                        round_tool_calls = []
                        
                        # Show status for additional rounds
                        if iteration > 1:
                            thinking_placeholder.info(f"🤔 **Analyzing results...** (Round {iteration})")
                        
                        with tool_execution_container:
                            for content_block in current_response.content:
                                if content_block.type == "tool_use":
                                    tool_name = content_block.name
                                    tool_input = content_block.input
                                    tool_id = content_block.id
                                    
                                    tool_call_info = {
                                        "name": tool_name,
                                        "input": tool_input
                                    }
                                    tool_calls_info.append(tool_call_info)
                                    round_tool_calls.append(tool_call_info)
                                    
                                    # Show tool execution in real-time
                                    tool_status = st.empty()
                                    tool_status.info(f"🔧 **Executing:** `{tool_name}`")
                                    
                                    # Execute tool
                                    tool_result = execute_tool(tool_name, **tool_input)
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_id,
                                        "content": json.dumps(tool_result, indent=2, default=str)
                                    })
                                    
                                    # Update status
                                    tool_status.success(f"✅ **Completed:** `{tool_name}`")
                        
                        # Update tool calls display summary after execution
                        if round_tool_calls:
                            tool_calls_placeholder.markdown("---")
                            tool_calls_placeholder.markdown(f"**🔧 Additional Tools Executed (Round {iteration}):**")
                            start_idx = len(tool_calls_info) - len(round_tool_calls) + 1
                            for i, tool_call in enumerate(round_tool_calls, start_idx):
                                tool_name = tool_call.get("name", "Unknown")
                                tool_input = tool_call.get("input", {})
                                with tool_calls_placeholder.expander(f"**{i}. {tool_name}**", expanded=False):
                                    st.json(tool_input)
                        
                        api_messages.append({
                            "role": "assistant",
                            "content": current_response.content
                        })
                        api_messages.append({
                            "role": "user",
                            "content": tool_results
                        })
                        
                        thinking_placeholder.info("🤔 **Analyzing results...** Synthesizing information.")
                        current_response = st.session_state.claude_client.messages.create(
                            model=model_name,
                            max_tokens=4096,
                            system=get_system_prompt(),
                            messages=api_messages,
                            tools=get_tool_definitions()
                        )
                        thinking_placeholder.empty()
                    
                    # Extract text content from final response
                    for content_block in current_response.content:
                        if content_block.type == "text":
                            full_response += content_block.text
                    
                    assistant_message["tool_calls"] = tool_calls_info
                
                else:
                    # Extract text content from response
                    for content_block in response.content:
                        if content_block.type == "text":
                            full_response += content_block.text
                
                # Display response progressively
                if full_response:
                    # Clear any status messages
                    thinking_placeholder.empty()
                    status_placeholder.empty()
                    
                    # Display the response
                    response_placeholder.markdown(full_response)
                    assistant_message["content"] = full_response
                else:
                    # If no text response but we have tool calls, show a message
                    if tool_calls_info:
                        response_placeholder.info("✅ Tools executed successfully. Processing results...")
                
                # Add to chat history
                st.session_state.claude_messages.append(assistant_message)
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                response_placeholder.error(error_msg)
                import traceback
                st.code(traceback.format_exc())
                # Add error to chat history
                st.session_state.claude_messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "tool_calls": [],
                    "status_messages": []
                })
        
        # Rerun to show new messages
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.claude_messages = []
        st.rerun()

with tab3:
    st.header("Individual Server Searches")
    st.markdown("Test individual MCP servers")
    
    server_choice = st.selectbox(
        "Select Server",
        ["Flight", "Hotel", "Event", "Geocoder", "Weather", "Finance"]
    )
    
    if server_choice == "Flight":
        st.subheader("✈️ Flight Search")
        with st.form("flight_form"):
            col1, col2 = st.columns(2)
            with col1:
                dep = st.text_input("Departure", "LAX")
                arr = st.text_input("Arrival", "JFK")
                out_date = st.date_input("Outbound Date", datetime.now().date() + timedelta(days=7))
            with col2:
                ret_date = st.date_input("Return Date", datetime.now().date() + timedelta(days=14))
                adults_count = st.number_input("Adults", 1, 10, 1)
            
            if st.form_submit_button("Search Flights"):
                try:
                    from servers.flight_server.flight_server import search_flights
                    flight_result = search_flights(
                        departure_id=dep,
                        arrival_id=arr,
                        outbound_date=out_date.strftime("%Y-%m-%d"),
                        return_date=ret_date.strftime("%Y-%m-%d"),
                        adults=adults_count
                    )
                    st.json(flight_result)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif server_choice == "Hotel":
        st.subheader("🏨 Hotel Search")
        with st.form("hotel_form"):
            location = st.text_input("Location", "New York")
            check_in = st.date_input("Check-in", datetime.now().date() + timedelta(days=7))
            check_out = st.date_input("Check-out", datetime.now().date() + timedelta(days=14))
            adults_count = st.number_input("Adults", 1, 10, 2)
            
            if st.form_submit_button("Search Hotels"):
                try:
                    from servers.hotel_server.hotel_server import search_hotels
                    hotel_result = search_hotels(
                        location=location,
                        check_in_date=check_in.strftime("%Y-%m-%d"),
                        check_out_date=check_out.strftime("%Y-%m-%d"),
                        adults=adults_count
                    )
                    st.json(hotel_result)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif server_choice == "Event":
        st.subheader("🎭 Event Search")
        with st.form("event_form"):
            query = st.text_input("Query", "concerts")
            location = st.text_input("Location", "San Francisco")
            date_filter = st.selectbox("Date Filter", ["today", "tomorrow", "week", "weekend", "month"])
            
            if st.form_submit_button("Search Events"):
                try:
                    from servers.event_server.event_server import search_events
                    event_result = search_events(
                        query=query,
                        location=location,
                        date_filter=date_filter
                    )
                    st.json(event_result)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif server_choice == "Geocoder":
        st.subheader("🗺️ Geocoder")
        with st.form("geocoder_form"):
            location = st.text_input("Location", "New York, NY")
            
            if st.form_submit_button("Geocode"):
                try:
                    from servers.geocoder_server.geocoder_server import geocode_location
                    geo_result = geocode_location(location)
                    st.json(geo_result)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif server_choice == "Weather":
        st.subheader("🌤️ Weather")
        st.info("ℹ️ Using Open-Meteo API (free, no API key required)")
        
        with st.form("weather_form"):
            input_type = st.radio(
                "Input Type",
                ["Location Name", "Coordinates"],
                horizontal=True
            )
            
            if input_type == "Location Name":
                location = st.text_input("Location", "New York, NY", help="City name, address, or location")
                forecast_days = st.slider("Forecast Days", 1, 16, 5)
                hourly = st.checkbox("Include Hourly Data", False)
            else:
                col1, col2 = st.columns(2)
                with col1:
                    lat = st.number_input("Latitude", value=40.7128, format="%.4f")
                with col2:
                    lon = st.number_input("Longitude", value=-74.0060, format="%.4f")
                forecast_days = st.slider("Forecast Days", 1, 16, 5)
                hourly = st.checkbox("Include Hourly Data", False)
                location = f"{lat},{lon}"
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Get Current Weather"):
                    try:
                        from servers.weather_server.weather_server import get_current_weather
                        weather_result = get_current_weather(location=location)
                        st.success("✅ Current weather retrieved!")
                        st.json(weather_result)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())
            
            with col2:
                if st.form_submit_button("Get Forecast"):
                    try:
                        from servers.weather_server.weather_server import get_weather_forecast
                        weather_result = get_weather_forecast(
                            location=location,
                            forecast_days=forecast_days,
                            hourly=hourly
                        )
                        st.success("✅ Weather forecast retrieved!")
                        st.json(weather_result)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())
    
    elif server_choice == "Finance":
        st.subheader("💰 Finance")
        with st.form("finance_form"):
            amount = st.number_input("Amount", value=100.0)
            from_curr = st.selectbox("From Currency", ["USD", "CAD", "EUR", "GBP", "JPY"])
            to_curr = st.selectbox("To Currency", ["USD", "CAD", "EUR", "GBP", "JPY"])
            
            if st.form_submit_button("Convert Currency"):
                try:
                    from servers.finance_server.finance_server import convert_currency
                    finance_result = convert_currency(
                        amount=amount,
                        from_currency=from_curr,
                        to_currency=to_curr
                    )
                    st.json(finance_result)
                except Exception as e:
                    st.error(f"Error: {e}")

with tab4:
    st.header("📋 Saved Results")
    
    if st.session_state.results:
        st.json(st.session_state.results)
        
        st.download_button(
            label="📥 Download Results (JSON)",
            data=json.dumps(st.session_state.results, indent=2, default=str),
            file_name=f"travel_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.info("No results yet. Plan a trip in the 'Plan Trip' tab!")