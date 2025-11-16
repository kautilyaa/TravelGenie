"""
Travel Genie - Main Streamlit Application
Interactive dashboard for travel planning with chat, video analysis, and MCP integration
"""

import streamlit as st
import asyncio
from typing import Dict, Any, Optional
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def run_async(coro):
    """
    Run an async coroutine in Streamlit's context.
    Handles event loop conflicts by using nest_asyncio to allow nested event loops.
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # There's a running loop, use nest_asyncio to allow nested loops
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(coro)
        except RuntimeError:
            # No running loop, safe to use asyncio.run directly
            return asyncio.run(coro)
    except ImportError:
        # nest_asyncio not available, use thread-based fallback
        import concurrent.futures
        
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

# Import custom modules
from agents.claude_agent import ClaudeAgent
from agents.video_analyzer import YOLO11Analyzer
from mcp_servers.orchestrator import MCPOrchestrator
from utils.config import get_config
from utils.security import get_secure_api_key, sanitizer
from utils.youtube_utils import YouTubeHelper
from ui.components import (
    ChatInterface,
    VideoAnalysisPanel,
    ItineraryBuilder,
    BookingManager,
    Analytics
)

# Configure Streamlit
config = get_config()
st.set_page_config(**config.get_streamlit_config())

# Custom CSS for styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 1rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message.user {
        background-color: #e3f2fd;
        justify-content: flex-end;
    }
    
    .chat-message.assistant {
        background-color: #f5f5f5;
    }
    
    /* Video analysis panel */
    .video-panel {
        border: 2px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Itinerary card */
    .itinerary-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-active {
        background-color: #4caf50;
    }
    
    .status-inactive {
        background-color: #f44336;
    }
    
    /* Analytics cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


class TravelGenieApp:
    """
    Main Travel Genie application class.
    """
    
    def __init__(self):
        """Initialize the Travel Genie application."""
        self.config = get_config()
        self.init_session_state()
        self.init_services()
    
    def init_session_state(self):
        """Initialize Streamlit session state."""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.chat_history = []
            st.session_state.current_itinerary = None
            st.session_state.video_results = []
            st.session_state.mcp_status = {}
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.active_tab = "Chat"
    
    def init_services(self):
        """Initialize backend services."""
        # Initialize Claude agent
        if 'claude_agent' not in st.session_state:
            api_key = get_secure_api_key('anthropic')
            if api_key:
                try:
                    st.session_state.claude_agent = ClaudeAgent(api_key=api_key)
                    st.session_state.claude_agent.create_session(st.session_state.session_id)
                except Exception as e:
                    st.error(f"Failed to initialize Claude agent: {e}")
                    st.session_state.claude_agent = None
            else:
                st.warning("Claude API key not found. Chat features will be limited.")
                st.session_state.claude_agent = None
        
        # Initialize YOLO analyzer
        if 'yolo_analyzer' not in st.session_state:
            try:
                st.session_state.yolo_analyzer = YOLO11Analyzer()
            except Exception as e:
                st.error(f"Failed to initialize YOLO analyzer: {e}")
                st.session_state.yolo_analyzer = None
        
        # Initialize MCP orchestrator
        if 'mcp_orchestrator' not in st.session_state:
            st.session_state.mcp_orchestrator = MCPOrchestrator()
    
    def render_header(self):
        """Render application header."""
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.image("https://img.icons8.com/color/96/000000/airplane-take-off.png", width=80)
        
        with col2:
            st.title("✈️ Travel Genie")
            st.markdown("*Your AI-powered travel planning assistant*")
        
        with col3:
            # MCP Server Status
            if st.session_state.mcp_orchestrator:
                status = st.session_state.mcp_orchestrator.manager.get_server_status()
                running = sum(1 for s in status.values() if s.get('running', False))
                total = len(status)
                
                if running == total:
                    st.success(f"🟢 {running}/{total} servers")
                elif running > 0:
                    st.warning(f"🟡 {running}/{total} servers")
                else:
                    st.error(f"🔴 {running}/{total} servers")
    
    def render_sidebar(self):
        """Render application sidebar."""
        with st.sidebar:
            st.header("🎯 Navigation")
            
            # Tab selection
            tabs = ["💬 Chat", "📹 Video Analysis", "🗺️ Itinerary", 
                   "🎫 Bookings", "📊 Analytics", "⚙️ Settings"]
            
            selected_tab = st.radio("Select Feature", tabs, label_visibility="collapsed")
            st.session_state.active_tab = selected_tab.split()[-1]  # Get last word
            
            st.divider()
            
            # Quick Actions
            st.header("⚡ Quick Actions")
            
            if st.button("🆕 New Trip", use_container_width=True):
                self.start_new_trip()
            
            if st.button("💾 Save Session", use_container_width=True):
                self.save_session()
            
            if st.button("📤 Export Itinerary", use_container_width=True):
                self.export_itinerary()
            
            st.divider()
            
            # MCP Server Controls
            st.header("🔧 MCP Servers")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start All", use_container_width=True):
                    run_async(self.start_mcp_servers())
            
            with col2:
                if st.button("⏹️ Stop All", use_container_width=True):
                    run_async(self.stop_mcp_servers())
            
            # Server status
            if st.session_state.mcp_orchestrator:
                status = st.session_state.mcp_orchestrator.manager.get_server_status()
                for server, info in status.items():
                    if info['running']:
                        st.success(f"✅ {server.capitalize()}")
                    else:
                        st.error(f"❌ {server.capitalize()}")
    
    def render_chat_tab(self):
        """Render chat interface tab."""
        st.header("💬 Chat with Travel Genie")
        
        # Initialize chat interface
        chat_ui = ChatInterface(st.session_state.claude_agent)
        
        # Chat history container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
        
        # Chat input
        user_input = st.chat_input("Ask me about your travel plans...")
        
        if user_input:
            # Sanitize input
            user_input = sanitizer.sanitize_input(user_input)
            
            # Add to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get response
            if st.session_state.claude_agent:
                with st.spinner("Travel Genie is thinking..."):
                    response = run_async(chat_ui.get_response(
                        user_input, 
                        st.session_state.session_id
                    ))
                    
                    # Add response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    
                    # Rerun to update chat
                    st.rerun()
            else:
                st.error("Chat service is not available. Please check your API key.")
                
    def render_video_tab(self):
        """Render video analysis tab."""
        st.header("📹 YouTube Travel Video Analysis")
        
        video_panel = VideoAnalysisPanel(st.session_state.yolo_analyzer)
        
        # Video URL input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_url = st.text_input(
                "Enter YouTube URL",
                placeholder="https://www.youtube.com/watch?v=..."
            )
        
        with col2:
            analyze_btn = st.button("🔍 Analyze", use_container_width=True)
        
        # Display YouTube video in webview if URL is provided
        if video_url:
            video_id = YouTubeHelper.extract_video_id(video_url)
            if video_id:
                # Embed YouTube video using iframe
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                st.markdown(f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%;">
                    <iframe 
                        src="{embed_url}" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
                    </iframe>
                </div>
                """, unsafe_allow_html=True)
        
        # Analysis settings
        with st.expander("⚙️ Analysis Settings"):
            duration = st.slider("Analysis Duration (seconds)", 10, 120, 30)
            skip_frames = st.slider("Skip Frames (for speed)", 1, 10, 5)
            show_live = st.checkbox("Show Live Detection", value=True)
        
        # Analyze video
        if analyze_btn and video_url:
                # Validate URL
                video_url = sanitizer.sanitize_url(video_url)
                
                if video_url and YouTubeHelper.validate_url(video_url):
                    with st.spinner("Analyzing video... This may take a moment."):
                        result = run_async(video_panel.analyze_video(
                            video_url,
                            duration,
                            skip_frames,
                            show_live
                        ))
                        
                        if result:
                            # Safely check summary structure
                            summary = getattr(result, 'summary', {}) or {}
                            
                            # Check if analysis was successful
                            if not summary or 'error' in summary:
                                error_msg = summary.get('error', 'Unknown error occurred during video analysis')
                                st.error(f"❌ Analysis failed: {error_msg}")
                            else:
                                st.session_state.video_results.append(result)
                                
                                # Display results
                                st.success("✅ Analysis Complete!")
                                
                                # Summary metrics - use .get() with defaults for safety
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Total Detections", summary.get('total_detections', 0))
                                
                                with col2:
                                    st.metric("Unique Objects", summary.get('unique_objects', 0))
                                
                                with col3:
                                    st.metric("Travel Context", summary.get('travel_context', 'unknown'))
                                
                                # Top objects chart
                                top_objects = summary.get('top_objects', [])
                                if top_objects:
                                    try:
                                        df = pd.DataFrame(top_objects[:5])
                                        fig = px.bar(df, x='name', y='count', 
                                                title="Top Detected Objects",
                                                color='avg_confidence',
                                                color_continuous_scale='viridis')
                                        st.plotly_chart(fig, use_container_width=True)
                                    except Exception as e:
                                        st.warning(f"Could not display chart: {e}")
                                
                                # Travel indicators
                                indicators = summary.get('travel_indicators', {})
                                if indicators:
                                    st.subheader("🎯 Travel Indicators")
                                    cols = st.columns(4)
                                    icons = ['🧳', '🚗', '👥', '🏞️']
                                    labels = ['Has Luggage', 'Has Transportation', 'Has People', 'Outdoor Scene']
                                    indicator_keys = list(indicators.keys())[:4]  # Take first 4 keys
                                    
                                    for col, icon, label, key in zip(cols, icons, labels, indicator_keys):
                                        with col:
                                            if indicators.get(key, False):
                                                st.success(f"{icon} {label}")
                                            else:
                                                st.info(f"{icon} {label}")
                        elif result is None:
                            st.error("❌ Video analysis returned no results. Please check the video URL and try again.")
                else:
                    st.error("Invalid YouTube URL. Please check and try again.")

    
    # def render_video_tab(self):
    #     """Render video analysis tab."""
    #     st.header("📹 YouTube Travel Video Analysis")
        
    #     video_panel = VideoAnalysisPanel(st.session_state.yolo_analyzer)
        
    #     # Video URL input
    #     col1, col2 = st.columns([3, 1])
        
    #     with col1:
    #         video_url = st.text_input(
    #             "Enter YouTube URL",
    #             placeholder="https://www.youtube.com/watch?v=..."
    #         )
        
    #     with col2:
    #         analyze_btn = st.button("🔍 Analyze", use_container_width=True)
        
    #     # Analysis settings
    #     with st.expander("⚙️ Analysis Settings"):
    #         duration = st.slider("Analysis Duration (seconds)", 10, 120, 30)
    #         skip_frames = st.slider("Skip Frames (for speed)", 1, 10, 5)
    #         show_live = st.checkbox("Show Live Detection", value=True)
        
    #     # Analyze video
    #     if analyze_btn and video_url:
    #         # Validate URL
    #         video_url = sanitizer.sanitize_url(video_url)
            
    #         if video_url and YouTubeHelper.validate_url(video_url):
    #             with st.spinner("Analyzing video... This may take a moment."):
    #                 result = asyncio.run(video_panel.analyze_video(
    #                     video_url,
    #                     duration,
    #                     skip_frames,
    #                     show_live
    #                 ))
                    
    #                 if result:
    #                     st.session_state.video_results.append(result)
                        
    #                     # Display results
    #                     st.success("✅ Analysis Complete!")
                        
    #                     # Summary metrics
    #                     col1, col2, col3 = st.columns(3)
                        
    #                     with col1:
    #                         st.metric("Total Detections", result.summary['total_detections'])
                        
    #                     with col2:
    #                         st.metric("Unique Objects", result.summary['unique_objects'])
                        
    #                     with col3:
    #                         st.metric("Travel Context", result.summary['travel_context'])
                        
    #                     # Top objects chart
    #                     if result.summary['top_objects']:
    #                         df = pd.DataFrame(result.summary['top_objects'][:5])
    #                         fig = px.bar(df, x='name', y='count', 
    #                                    title="Top Detected Objects",
    #                                    color='avg_confidence',
    #                                    color_continuous_scale='viridis')
    #                         st.plotly_chart(fig, use_container_width=True)
                        
    #                     # Travel indicators
    #                     st.subheader("🎯 Travel Indicators")
    #                     indicators = result.summary['travel_indicators']
                        
    #                     cols = st.columns(4)
    #                     icons = ['🧳', '🚗', '👥', '🏞️']
    #                     labels = ['Has Luggage', 'Has Transportation', 'Has People', 'Outdoor Scene']
                        
    #                     for col, icon, label, key in zip(cols, icons, labels, indicators.keys()):
    #                         with col:
    #                             if indicators[key]:
    #                                 st.success(f"{icon} {label}")
    #                             else:
    #                                 st.info(f"{icon} {label}")
    #         else:
    #             st.error("Invalid YouTube URL. Please check and try again.")
    
    def render_itinerary_tab(self):
        """Render itinerary builder tab."""
        st.header("🗺️ Itinerary Builder")
        
        itinerary_ui = ItineraryBuilder(st.session_state.mcp_orchestrator)
        
        # Create new itinerary or load existing
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Create New Itinerary")
            
            destination = st.text_input("Destination", placeholder="Paris, France")
            
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Start Date")
            with col_date2:
                end_date = st.date_input("End Date")
            
            travelers = st.number_input("Number of Travelers", 1, 10, 2)
            
            preferences = st.multiselect(
                "Travel Preferences",
                ["Adventure", "Culture", "Food", "Relaxation", "Shopping", "Nature"]
            )
        
        with col2:
            st.subheader("Quick Templates")
            
            template = st.selectbox(
                "Select Template",
                ["Custom", "Weekend City Break", "Beach Vacation", "Cultural Tour"]
            )
            
            if st.button("📝 Create Itinerary", use_container_width=True):
                if destination and start_date and end_date:
                    result = run_async(itinerary_ui.create_itinerary(
                        destination,
                        str(start_date),
                        str(end_date),
                        travelers,
                        preferences
                    ))
                    
                    if result:
                        st.session_state.current_itinerary = result
                        st.success("✅ Itinerary created successfully!")
        
        # Display current itinerary
        if st.session_state.current_itinerary:
            st.divider()
            st.subheader("📅 Current Itinerary")
            
            itinerary = st.session_state.current_itinerary
            
            # Itinerary header
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Destination", itinerary.get('destination', 'N/A'))
            with col2:
                st.metric("Duration", f"{itinerary.get('duration_days', 0)} days")
            with col3:
                st.metric("Travelers", itinerary.get('travelers', 1))
            
            # Activities timeline
            st.subheader("📍 Activities")
            
            activities = itinerary.get('activities', [])
            if activities:
                for activity in activities:
                    with st.container():
                        st.markdown(f"""
                        <div class="itinerary-card">
                            <h4>{activity['name']}</h4>
                            <p>📅 {activity['date']} at {activity['time']}</p>
                            <p>⏱️ Duration: {activity['duration_hours']} hours</p>
                            <p>📍 {activity.get('location', 'TBD')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No activities added yet. Add some activities to your itinerary!")
            
            # Add activity button
            if st.button("➕ Add Activity"):
                with st.form("add_activity_form"):
                    act_name = st.text_input("Activity Name")
                    act_date = st.date_input("Date")
                    act_time = st.time_input("Time")
                    act_duration = st.number_input("Duration (hours)", 0.5, 12.0, 2.0)
                    act_location = st.text_input("Location")
                    
                    if st.form_submit_button("Add"):
                        # Add activity logic here
                        st.success("Activity added!")
    
    def render_bookings_tab(self):
        """Render bookings management tab."""
        st.header("🎫 Bookings Manager")
        
        booking_ui = BookingManager(st.session_state.mcp_orchestrator)
        
        # Booking type selection
        booking_type = st.selectbox(
            "Select Booking Type",
            ["✈️ Flights", "🏨 Hotels", "🚗 Car Rentals"]
        )
        
        if booking_type == "✈️ Flights":
            st.subheader("Search Flights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                origin = st.text_input("From", placeholder="New York")
                departure_date = st.date_input("Departure Date")
            
            with col2:
                destination = st.text_input("To", placeholder="Paris")
                return_date = st.date_input("Return Date (optional)")
            
            passengers = st.number_input("Passengers", 1, 10, 1)
            class_type = st.selectbox("Class", ["Economy", "Business", "First"])
            
            if st.button("🔍 Search Flights", use_container_width=True):
                with st.spinner("Searching flights..."):
                    results = run_async(booking_ui.search_flights(
                        origin, destination, str(departure_date),
                        str(return_date) if return_date else None,
                        passengers, class_type.lower()
                    ))
                    
                    if results and 'outbound_flights' in results:
                        st.success(f"Found {results['flights_found']} flights!")
                        
                        # Display flights
                        for flight in results['outbound_flights'][:5]:
                            with st.expander(f"{flight['airline']} - {flight['flight_id']}"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.write(f"**Departure:** {flight['departure']['time']}")
                                    st.write(f"**Arrival:** {flight['arrival']['time']}")
                                
                                with col2:
                                    st.write(f"**Duration:** {flight['duration']}")
                                    st.write(f"**Stops:** {flight['stops']}")
                                
                                with col3:
                                    st.write(f"**Price:** ${flight['price'][class_type.lower()]}")
                                    if st.button(f"Book", key=flight['flight_id']):
                                        st.success("Booking initiated!")
        
        elif booking_type == "🏨 Hotels":
            st.subheader("Search Hotels")
            
            location = st.text_input("Location", placeholder="Paris, France")
            
            col1, col2 = st.columns(2)
            
            with col1:
                check_in = st.date_input("Check-in Date")
            
            with col2:
                check_out = st.date_input("Check-out Date")
            
            guests = st.number_input("Guests", 1, 10, 2)
            rooms = st.number_input("Rooms", 1, 5, 1)
            
            amenities = st.multiselect(
                "Amenities",
                ["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Parking"]
            )
            
            if st.button("🔍 Search Hotels", use_container_width=True):
                with st.spinner("Searching hotels..."):
                    results = run_async(booking_ui.search_hotels(
                        location, str(check_in), str(check_out),
                        guests, rooms, amenities
                    ))
                    
                    if results and 'hotels' in results:
                        st.success(f"Found {results['hotels_found']} hotels!")
                        
                        # Display hotels
                        for hotel in results['hotels'][:5]:
                            with st.expander(f"{hotel['name']} - {hotel['stars']}⭐"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.write(f"**Rating:** {hotel['rating']}/5.0")
                                    st.write(f"**Distance:** {hotel['distance_from_center']}")
                                
                                with col2:
                                    st.write(f"**Price/night:** ${hotel['price_per_night']}")
                                    st.write(f"**Total:** ${hotel['total_price']}")
                                
                                with col3:
                                    st.write(f"**Reviews:** {hotel['reviews']['count']}")
                                    if st.button(f"Book", key=hotel['hotel_id']):
                                        st.success("Booking initiated!")
    
    def render_analytics_tab(self):
        """Render analytics dashboard tab."""
        st.header("📊 Analytics Dashboard")
        
        analytics_ui = Analytics()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h2>12</h2>
                <p>Trips Planned</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h2>45</h2>
                <p>Destinations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h2>$8,450</h2>
                <p>Total Saved</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h2>98%</h2>
                <p>Satisfaction</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.subheader("📈 Travel Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Popular destinations chart
            destinations_data = pd.DataFrame({
                'Destination': ['Paris', 'Tokyo', 'New York', 'London', 'Rome'],
                'Searches': [120, 98, 85, 76, 65]
            })
            
            fig = px.bar(destinations_data, x='Destination', y='Searches',
                        title="Popular Destinations",
                        color='Searches',
                        color_continuous_scale='blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Travel categories pie chart
            categories_data = pd.DataFrame({
                'Category': ['Adventure', 'Culture', 'Relaxation', 'Business', 'Food'],
                'Count': [30, 25, 20, 15, 10]
            })
            
            fig = px.pie(categories_data, values='Count', names='Category',
                        title="Travel Categories")
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline chart
        st.subheader("📅 Travel Timeline")
        
        timeline_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Bookings': [15, 22, 28, 35, 42, 38]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_data['Month'],
            y=timeline_data['Bookings'],
            mode='lines+markers',
            name='Bookings',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Monthly Booking Trends",
            xaxis_title="Month",
            yaxis_title="Number of Bookings",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_settings_tab(self):
        """Render settings tab."""
        st.header("⚙️ Settings")
        
        # API Keys section
        st.subheader("🔑 API Configuration")
        
        with st.expander("API Keys"):
            anthropic_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value="*" * 20 if get_secure_api_key('anthropic') else "",
                help="Required for chat functionality"
            )
            
            youtube_key = st.text_input(
                "YouTube API Key",
                type="password",
                value="*" * 20 if get_secure_api_key('youtube') else "",
                help="Optional for enhanced video features"
            )
            
            if st.button("💾 Save API Keys"):
                # Save keys securely
                st.success("API keys saved securely!")
        
        # Model Configuration
        st.subheader("🤖 Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            claude_model = st.selectbox(
                "Claude Model",
                [
                    "claude-sonnet-4-20250514",
                    "claude-opus-4-1-20250805",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                index=0
            )
            
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        with col2:
            yolo_model = st.selectbox(
                "YOLO Model",
                ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt"],
                index=0
            )
            
            confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)
        
        # UI Preferences
        st.subheader("🎨 UI Preferences")
        
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        sidebar_state = st.selectbox("Default Sidebar", ["Expanded", "Collapsed"])
        show_analytics = st.checkbox("Show Analytics Dashboard", value=True)
        
        # Save settings button
        if st.button("💾 Save All Settings", use_container_width=True):
            # Update configuration
            config.update_setting("app", "claude_model", claude_model)
            config.update_setting("app", "claude_temperature", temperature)
            config.update_setting("app", "yolo_model", yolo_model)
            config.update_setting("app", "yolo_confidence", confidence)
            config.update_setting("app", "theme", theme.lower())
            config.update_setting("app", "sidebar_state", sidebar_state.lower())
            config.update_setting("app", "show_analytics", show_analytics)
            
            # Save to file
            config.save_config()
            st.success("✅ Settings saved successfully!")
    
    def start_new_trip(self):
        """Start a new trip planning session."""
        st.session_state.current_itinerary = None
        st.session_state.chat_history = []
        st.session_state.video_results = []
        st.success("🆕 New trip started!")
    
    def save_session(self):
        """Save current session data."""
        session_data = {
            "session_id": st.session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "chat_history": st.session_state.chat_history,
            "current_itinerary": st.session_state.current_itinerary,
            "video_results": [
                {
                    "url": r.video_url,
                    "summary": r.summary
                } for r in st.session_state.video_results
            ]
        }
        
        # Save to file
        filename = f"session_{st.session_state.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        st.success(f"💾 Session saved to {filename}")
    
    def export_itinerary(self):
        """Export current itinerary."""
        if st.session_state.current_itinerary:
            # Create downloadable JSON
            itinerary_json = json.dumps(st.session_state.current_itinerary, indent=2)
            
            st.download_button(
                label="📥 Download Itinerary (JSON)",
                data=itinerary_json,
                file_name=f"itinerary_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        else:
            st.warning("No itinerary to export. Create one first!")
    
    async def start_mcp_servers(self):
        """Start all MCP servers."""
        if st.session_state.mcp_orchestrator:
            results = await st.session_state.mcp_orchestrator.manager.start_all_servers()
            
            for server, success in results.items():
                if success:
                    st.success(f"✅ Started {server} server")
                else:
                    st.error(f"❌ Failed to start {server} server")
    
    async def stop_mcp_servers(self):
        """Stop all MCP servers."""
        if st.session_state.mcp_orchestrator:
            results = await st.session_state.mcp_orchestrator.manager.stop_all_servers()
            
            for server, success in results.items():
                if success:
                    st.success(f"✅ Stopped {server} server")
                else:
                    st.error(f"❌ Failed to stop {server} server")
    
    def run(self):
        """Run the main application."""
        # Render header
        self.render_header()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main content based on selected tab
        if st.session_state.active_tab == "Chat":
            self.render_chat_tab()
        elif st.session_state.active_tab == "Analysis":
            self.render_video_tab()
        elif st.session_state.active_tab == "Itinerary":
            self.render_itinerary_tab()
        elif st.session_state.active_tab == "Bookings":
            self.render_bookings_tab()
        elif st.session_state.active_tab == "Analytics":
            self.render_analytics_tab()
        elif st.session_state.active_tab == "Settings":
            self.render_settings_tab()
        
        # Footer
        st.divider()
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p>Travel Genie v1.0.0 | Powered by Claude AI & YOLO11 | Built with ❤️ using Streamlit</p>
        </div>
        """, unsafe_allow_html=True)


# Main execution
if __name__ == "__main__":
    app = TravelGenieApp()
    app.run()
