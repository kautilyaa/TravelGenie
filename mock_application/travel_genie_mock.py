"""
Mock Travel Genie - Main Application Entry Point
Fully mocked Travel Genie application that works without API keys
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector

# Page configuration
st.set_page_config(
    page_title="Mock Travel Genie",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    config_path = Path(__file__).parent / "config" / "app_config.yaml"
    st.session_state.orchestrator = MockOrchestrator(config_path=str(config_path))
    st.session_state.metrics_collector = get_metrics_collector(
        platform=st.session_state.orchestrator.platform,
        config_path=str(config_path)
    )
    st.session_state.query_history = []
    st.session_state.metrics_history = []

# Title
st.title("Mock Travel Genie")
st.markdown("**Fully mocked travel planning assistant - No API keys required!**")
st.info("This is a demonstration version using mock data. All responses are simulated.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Platform info
    st.subheader("Platform Information")
    st.text(f"Platform: {st.session_state.orchestrator.platform}")
    st.text(f"Tag: {st.session_state.orchestrator.platform_tag}")
    st.text(f"Mock LLM: Enabled")
    
    st.divider()
    
    # Metrics
    st.subheader("Metrics")
    metrics = st.session_state.orchestrator.get_metrics()
    
    if metrics.get("request_metrics"):
        st.metric("Total Requests", metrics["request_metrics"].get("total_requests", 0))
        st.metric("Success Rate", f"{metrics['request_metrics'].get('success_rate', 0) * 100:.1f}%")
        if metrics["request_metrics"].get("requests_per_second"):
            st.metric("Throughput", f"{metrics['request_metrics']['requests_per_second']:.2f} RPS")
    
    st.divider()
    
    # Export metrics
    if st.button("Export Metrics"):
        metrics_data = st.session_state.metrics_collector.get_metrics()
        st.download_button(
            label="Download Metrics JSON",
            data=json.dumps(metrics_data, indent=2),
            file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Main interface
tab1, tab2, tab3 = st.tabs(["Chat", "Metrics", "History"])

with tab1:
    st.header("Plan Your Trip")
    st.markdown("Ask me anything about travel planning. I'll use mock data to help you!")
    
    # Example queries
    st.subheader("Example Queries")
    example_queries = [
        "Find flights from IAD to JFK on 2025-12-17",
        "Search for hotels in Banff, Alberta from 2025-06-07 to 2025-06-14",
        "Plan a trip to Banff, Alberta from Reston, Virginia for June 7-14, 2025. Find flights, hotels, and events.",
        "What's the weather forecast for New York City?",
        "Convert $5000 USD to CAD"
    ]
    
    cols = st.columns(len(example_queries))
    for i, query in enumerate(example_queries):
        with cols[i]:
            if st.button(f"Example {i+1}", key=f"example_{i}"):
                st.session_state.example_query = query
    
    # Query input
    user_query = st.text_area(
        "Enter your travel query:",
        value=st.session_state.get("example_query", ""),
        height=100,
        key="user_query_input"
    )
    
    if st.button("Submit Query", type="primary"):
        if user_query:
            with st.spinner("Processing your query..."):
                # Process query
                result = st.session_state.orchestrator.process_query(user_query)
                
                # Record metrics
                st.session_state.metrics_collector.record_request_metrics(
                    request_id=result.get("request_id", ""),
                    latency_ms=result.get("latency_ms", 0),
                    success=result.get("success", False),
                    tool_calls=result.get("tool_calls", [])
                )
                
                # Store in history
                st.session_state.query_history.append({
                    "query": user_query,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Display result
                if result.get("success"):
                    st.success("Query processed successfully!")
                    
                    # Display response
                    st.subheader("Response")
                    st.write(result.get("response", "No response generated"))
                    
                    # Display tool calls
                    if result.get("tool_calls"):
                        st.subheader("Tools Used")
                        for tool_call in result["tool_calls"]:
                            with st.expander(f"{tool_call.get('tool', 'Unknown')} - {tool_call.get('latency_ms', 0):.2f}ms"):
                                st.json(tool_call.get("input", {}))
                    
                    # Display metrics
                    st.subheader("Performance Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Latency", f"{result.get('latency_ms', 0):.2f} ms")
                    with col2:
                        st.metric("Total Turns", result.get("total_turns", 0))
                    with col3:
                        st.metric("Tool Calls", len(result.get("tool_calls", [])))
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")

with tab2:
    st.header("Performance Metrics")
    
    # Overall metrics
    metrics = st.session_state.orchestrator.get_metrics()
    
    if metrics.get("request_metrics"):
        st.subheader("Request Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Requests", metrics["request_metrics"].get("total_requests", 0))
        with col2:
            st.metric("Successful", metrics["request_metrics"].get("successful_requests", 0))
        with col3:
            st.metric("Failed", metrics["request_metrics"].get("failed_requests", 0))
        with col4:
            st.metric("Success Rate", f"{metrics['request_metrics'].get('success_rate', 0) * 100:.1f}%")
        
        if metrics["request_metrics"].get("requests_per_second"):
            st.metric("Throughput", f"{metrics['request_metrics']['requests_per_second']:.2f} requests/second")
    
    # Latency statistics
    if metrics.get("latency_stats"):
        st.subheader("Latency Statistics")
        latency_stats = metrics["latency_stats"]
        
        if "llama_api_call" in latency_stats:
            llama_stats = latency_stats["llama_api_call"]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{llama_stats.get('mean', 0):.2f} ms")
            with col2:
                st.metric("P50", f"{llama_stats.get('p50', 0):.2f} ms")
            with col3:
                st.metric("P95", f"{llama_stats.get('p95', 0):.2f} ms")
            with col4:
                st.metric("P99", f"{llama_stats.get('p99', 0):.2f} ms")
    
    # Tool usage
    if metrics.get("tool_usage"):
        st.subheader("Tool Usage")
        tool_usage = metrics["tool_usage"]
        if tool_usage:
            st.bar_chart(tool_usage)
    
    # Platform metrics
    st.subheader("Platform Metrics")
    platform_metrics = st.session_state.metrics_collector.get_metrics()
    if platform_metrics.get("summary"):
        summary = platform_metrics["summary"]
        st.json(summary)

with tab3:
    st.header("Query History")
    
    if st.session_state.query_history:
        for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Show last 10
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {entry['query'][:50]}..."):
                st.text(f"Timestamp: {entry['timestamp']}")
                st.text(f"Query: {entry['query']}")
                if entry['result'].get("success"):
                    st.success(f"Success - Latency: {entry['result'].get('latency_ms', 0):.2f} ms")
                    st.text("Response:")
                    st.write(entry['result'].get("response", ""))
                else:
                    st.error(f"Error: {entry['result'].get('error', 'Unknown')}")
    else:
        st.info("No queries yet. Start chatting in the Chat tab!")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Mock Travel Genie - Fully mocked travel planning assistant</p>
        <p>Platform: {} | Tag: {}</p>
    </div>
    """.format(
        st.session_state.orchestrator.platform,
        st.session_state.orchestrator.platform_tag
    ),
    unsafe_allow_html=True
)
