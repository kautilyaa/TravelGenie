"""
UI Components - Reusable Streamlit components for Travel Genie
Modular components for chat, video analysis, itinerary, bookings, and analytics
"""

import streamlit as st
import asyncio
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px
from datetime import datetime
import json


class ChatInterface:
    """
    Chat interface component for Claude integration.
    """
    
    def __init__(self, claude_agent):
        """
        Initialize chat interface.
        
        Args:
            claude_agent: Claude agent instance
        """
        self.claude_agent = claude_agent
    
    async def get_response(
        self, 
        message: str, 
        session_id: str,
        with_mcp: bool = True
    ) -> str:
        """
        Get response from Claude.
        
        Args:
            message: User message
            session_id: Session ID
            with_mcp: Whether to include MCP context
        
        Returns:
            Assistant response
        """
        if not self.claude_agent:
            return "Chat service is not available. Please configure your API key."
        
        try:
            if with_mcp:
                # Analyze query for travel context
                analysis = await self.claude_agent.analyze_travel_query(message)
                
                # Get MCP data if relevant
                mcp_data = None
                if analysis.get('is_travel_related'):
                    # Here you would fetch relevant MCP data based on intent
                    mcp_data = {
                        "intent": analysis.get('intent'),
                        "entities": analysis.get('entities')
                    }
                
                # Get response with MCP context
                result = await self.claude_agent.chat_with_mcp(
                    message, session_id, mcp_data
                )
                return result.get('response', 'I apologize, but I encountered an error.')
            else:
                # Simple chat without MCP
                return await self.claude_agent.chat(message, session_id)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def render_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """
        Render a chat message.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            timestamp: Optional timestamp
        """
        css_class = "user" if role == "user" else "assistant"
        icon = "👤" if role == "user" else "🤖"
        
        message_html = f"""
        <div class="chat-message {css_class}">
            <div class="message-icon">{icon}</div>
            <div class="message-content">
                <p>{content}</p>
                {f'<small>{timestamp}</small>' if timestamp else ''}
            </div>
        </div>
        """
        
        st.markdown(message_html, unsafe_allow_html=True)


class VideoAnalysisPanel:
    """
    Video analysis panel component for YOLO11 integration.
    """
    
    def __init__(self, yolo_analyzer):
        """
        Initialize video analysis panel.
        
        Args:
            yolo_analyzer: YOLO11 analyzer instance
        """
        self.yolo_analyzer = yolo_analyzer
    
    async def analyze_video(
        self,
        url: str,
        duration: int = 30,
        skip_frames: int = 5,
        show_live: bool = False
    ) -> Any:
        """
        Analyze a YouTube video.
        
        Args:
            url: YouTube video URL
            duration: Analysis duration in seconds
            skip_frames: Frame skip rate
            show_live: Show live detection
        
        Returns:
            Analysis results
        """
        if not self.yolo_analyzer:
            st.error("Video analyzer is not available.")
            return None
        
        try:
            # Run analysis
            result = await self.yolo_analyzer.analyze_youtube_video(
                url=url,
                duration_seconds=duration,
                skip_frames=skip_frames,
                real_time=show_live
            )
            
            return result
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None
    
    def render_results(self, results: Any):
        """
        Render video analysis results.
        
        Args:
            results: Analysis results
        """
        if not results:
            return
        
        # Create results display
        st.markdown("""
        <div class="video-panel">
            <h3>📊 Analysis Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Frames Analyzed", results.total_frames)
        
        with col2:
            st.metric("Objects Detected", results.summary['total_detections'])
        
        with col3:
            st.metric("Unique Objects", results.summary['unique_objects'])
        
        with col4:
            st.metric("Context", results.summary['travel_context'])
        
        # Top objects
        if results.summary['top_objects']:
            st.subheader("Top Detected Objects")
            df = pd.DataFrame(results.summary['top_objects'][:10])
            st.dataframe(df, use_container_width=True)


class ItineraryBuilder:
    """
    Itinerary builder component for trip planning.
    """
    
    def __init__(self, mcp_orchestrator):
        """
        Initialize itinerary builder.
        
        Args:
            mcp_orchestrator: MCP orchestrator instance
        """
        self.mcp_orchestrator = mcp_orchestrator
    
    async def create_itinerary(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        travelers: int,
        preferences: List[str]
    ) -> Dict[str, Any]:
        """
        Create a new itinerary.
        
        Args:
            destination: Travel destination
            start_date: Trip start date
            end_date: Trip end date
            travelers: Number of travelers
            preferences: Travel preferences
        
        Returns:
            Created itinerary
        """
        if not self.mcp_orchestrator:
            st.error("MCP servers are not available.")
            return None
        
        try:
            # Initialize MCP servers if needed
            if not self.mcp_orchestrator.initialized:
                await self.mcp_orchestrator.initialize()
            
            # Send request to itinerary server
            response = await self.mcp_orchestrator.manager.send_request(
                "itinerary",
                "create_itinerary",
                {
                    "destination": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "travelers": travelers,
                    "preferences": preferences
                }
            )
            
            if response.get('result'):
                return response['result'].get('itinerary')
            
            return None
            
        except Exception as e:
            st.error(f"Error creating itinerary: {str(e)}")
            return None
    
    def render_itinerary_card(self, itinerary: Dict[str, Any]):
        """
        Render an itinerary card.
        
        Args:
            itinerary: Itinerary data
        """
        st.markdown(f"""
        <div class="itinerary-card">
            <h3>📍 {itinerary.get('destination', 'Unknown')}</h3>
            <p>📅 {itinerary.get('start_date')} to {itinerary.get('end_date')}</p>
            <p>👥 {itinerary.get('travelers', 1)} travelers</p>
            <p>⏱️ {itinerary.get('duration_days', 0)} days</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_activity_timeline(self, activities: List[Dict[str, Any]]):
        """
        Render activity timeline.
        
        Args:
            activities: List of activities
        """
        for activity in activities:
            with st.expander(f"📍 {activity['name']} - {activity['date']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"⏰ Time: {activity['time']}")
                    st.write(f"⏱️ Duration: {activity['duration_hours']} hours")
                
                with col2:
                    st.write(f"📍 Location: {activity.get('location', 'TBD')}")
                    if activity.get('notes'):
                        st.write(f"📝 Notes: {activity['notes']}")


class BookingManager:
    """
    Booking manager component for travel reservations.
    """
    
    def __init__(self, mcp_orchestrator):
        """
        Initialize booking manager.
        
        Args:
            mcp_orchestrator: MCP orchestrator instance
        """
        self.mcp_orchestrator = mcp_orchestrator
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str],
        passengers: int,
        class_type: str
    ) -> Dict[str, Any]:
        """
        Search for flights.
        
        Args:
            origin: Origin city/airport
            destination: Destination city/airport
            departure_date: Departure date
            return_date: Optional return date
            passengers: Number of passengers
            class_type: Flight class
        
        Returns:
            Flight search results
        """
        if not self.mcp_orchestrator:
            return None
        
        try:
            # Initialize MCP servers if needed
            if not self.mcp_orchestrator.initialized:
                await self.mcp_orchestrator.initialize()
            
            # Send request to booking server
            response = await self.mcp_orchestrator.manager.send_request(
                "booking",
                "search_flights",
                {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "passengers": passengers,
                    "class_type": class_type
                }
            )
            
            return response.get('result')
            
        except Exception as e:
            st.error(f"Error searching flights: {str(e)}")
            return None
    
    async def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        guests: int,
        rooms: int,
        amenities: List[str]
    ) -> Dict[str, Any]:
        """
        Search for hotels.
        
        Args:
            location: Hotel location
            check_in: Check-in date
            check_out: Check-out date
            guests: Number of guests
            rooms: Number of rooms
            amenities: Required amenities
        
        Returns:
            Hotel search results
        """
        if not self.mcp_orchestrator:
            return None
        
        try:
            # Initialize MCP servers if needed
            if not self.mcp_orchestrator.initialized:
                await self.mcp_orchestrator.initialize()
            
            # Send request to booking server
            response = await self.mcp_orchestrator.manager.send_request(
                "booking",
                "search_hotels",
                {
                    "location": location,
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                    "rooms": rooms,
                    "amenities": amenities
                }
            )
            
            return response.get('result')
            
        except Exception as e:
            st.error(f"Error searching hotels: {str(e)}")
            return None
    
    def render_flight_card(self, flight: Dict[str, Any]):
        """
        Render a flight card.
        
        Args:
            flight: Flight data
        """
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <h4>✈️ {flight['airline']} - {flight['flight_id']}</h4>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p>🛫 Departure: {flight['departure']['time']}</p>
                    <p>🛬 Arrival: {flight['arrival']['time']}</p>
                </div>
                <div>
                    <p>⏱️ Duration: {flight['duration']}</p>
                    <p>🔄 Stops: {flight['stops']}</p>
                </div>
                <div>
                    <h3>${flight['price']['economy']}</h3>
                    <p>Economy</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_hotel_card(self, hotel: Dict[str, Any]):
        """
        Render a hotel card.
        
        Args:
            hotel: Hotel data
        """
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <h4>🏨 {hotel['name']} - {"⭐" * hotel['stars']}</h4>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p>📍 {hotel['distance_from_center']}</p>
                    <p>⭐ Rating: {hotel['rating']}/5.0</p>
                </div>
                <div>
                    <p>💬 {hotel['reviews']['count']} reviews</p>
                    <p>📊 Score: {hotel['reviews']['score']}</p>
                </div>
                <div>
                    <h3>${hotel['price_per_night']}</h3>
                    <p>per night</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


class Analytics:
    """
    Analytics dashboard component for travel insights.
    """
    
    def __init__(self):
        """Initialize analytics component."""
        pass
    
    def render_metrics(self, metrics: Dict[str, Any]):
        """
        Render metric cards.
        
        Args:
            metrics: Dictionary of metrics
        """
        cols = st.columns(len(metrics))
        
        for col, (label, value) in zip(cols, metrics.items()):
            with col:
                st.metric(label, value)
    
    def render_destination_chart(self, data: pd.DataFrame):
        """
        Render destination popularity chart.
        
        Args:
            data: Destination data
        """
        fig = px.bar(
            data,
            x='destination',
            y='searches',
            title="Popular Destinations",
            color='searches',
            color_continuous_scale='viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_timeline_chart(self, data: pd.DataFrame):
        """
        Render booking timeline chart.
        
        Args:
            data: Timeline data
        """
        fig = px.line(
            data,
            x='date',
            y='bookings',
            title="Booking Trends",
            markers=True
        )
        
        fig.update_traces(
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_category_distribution(self, data: pd.DataFrame):
        """
        Render travel category distribution.
        
        Args:
            data: Category data
        """
        fig = px.pie(
            data,
            values='count',
            names='category',
            title="Travel Categories",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def get_sample_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get sample analytics data.
        
        Returns:
            Dictionary of sample dataframes
        """
        # Sample destination data
        destinations = pd.DataFrame({
            'destination': ['Paris', 'Tokyo', 'New York', 'London', 'Rome'],
            'searches': [120, 98, 85, 76, 65]
        })
        
        # Sample timeline data
        timeline = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'bookings': [15, 22, 28, 35, 42, 48, 52, 58, 61, 65, 68, 72]
        })
        
        # Sample category data
        categories = pd.DataFrame({
            'category': ['Adventure', 'Culture', 'Relaxation', 'Business', 'Food'],
            'count': [30, 25, 20, 15, 10]
        })
        
        return {
            'destinations': destinations,
            'timeline': timeline,
            'categories': categories
        }
# Add to ui/components.py or create new file ui/map_component.py

import folium
from streamlit_folium import st_folium
import streamlit as st

def display_map(latitude: float, longitude: float, location_name: str = ""):
    """
    Display an interactive map using Folium and OpenStreetMap.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        location_name: Name of the location
    """
    # Create map centered on location
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=13,
        tiles='OpenStreetMap'  # Free OpenStreetMap tiles
    )
    
    # Add marker
    folium.Marker(
        [latitude, longitude],
        popup=location_name or f"{latitude}, {longitude}",
        tooltip=location_name,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
    
    # Display in Streamlit
    st_folium(m, width=700, height=500, returned_objects=[])