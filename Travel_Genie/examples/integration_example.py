"""
Integration Example - Complete workflow demonstrating all components working together
Shows how to integrate Claude chat, video analysis, and MCP servers
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.claude_agent import ClaudeAgent
from agents.video_analyzer import YOLO11Analyzer
from mcp_servers.orchestrator import MCPOrchestrator
from utils.config import get_config
from utils.security import get_secure_api_key


async def example_complete_travel_planning():
    """
    Complete example: Plan a trip using Claude chat, MCP servers, and video analysis.
    """
    print("=" * 60)
    print("Complete Travel Planning Integration Example")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing components...")
    
    # Initialize Claude agent
    api_key = get_secure_api_key('anthropic')
    if not api_key:
        print("⚠️  Claude API key not found. Chat features will be limited.")
        claude_agent = None
    else:
        claude_agent = ClaudeAgent(api_key=api_key)
        session_id = claude_agent.create_session("example_session")
        print(f"✅ Claude agent initialized (session: {session_id})")
    
    # Initialize MCP orchestrator
    orchestrator = MCPOrchestrator()
    print("✅ MCP orchestrator initialized")
    
    # Initialize YOLO analyzer
    try:
        yolo_analyzer = YOLO11Analyzer()
        print("✅ YOLO11 analyzer initialized")
    except Exception as e:
        print(f"⚠️  YOLO analyzer initialization failed: {e}")
        yolo_analyzer = None
    
    # Step 2: Start MCP servers
    print("\n2. Starting MCP servers...")
    async with orchestrator.session():
        status = orchestrator.manager.get_server_status()
        for server, info in status.items():
            if info['running']:
                print(f"✅ {server.capitalize()} server running")
            else:
                print(f"❌ {server.capitalize()} server not running")
        
        # Step 3: Plan a trip using MCP servers
        print("\n3. Planning trip using MCP servers...")
        travel_request = {
            "id": "example_001",
            "type": "plan_trip",
            "params": {
                "destination": "Paris, France",
                "origin": "New York, USA",
                "dates": {
                    "start": "2025-12-15",
                    "end": "2025-12-22"
                }
            }
        }
        
        result = await orchestrator.process_travel_request(travel_request)
        print(f"Trip planning result: {json.dumps(result, indent=2)}")
        
        # Step 4: Chat with Claude about the trip
        if claude_agent:
            print("\n4. Chatting with Claude about the trip...")
            user_query = "I want to plan a 7-day trip to Paris. What are the must-see attractions?"
            
            response = await claude_agent.chat(
                user_query,
                session_id,
                stream=False
            )
            print(f"\nUser: {user_query}")
            print(f"Claude: {response[:200]}...")  # First 200 chars
        
        # Step 5: Analyze a travel video (if analyzer available)
        if yolo_analyzer:
            print("\n5. Analyzing travel video...")
            print("(Note: This requires a valid YouTube URL)")
            # Uncomment to test with actual video:
            # youtube_url = "https://www.youtube.com/watch?v=..."
            # result = await yolo_analyzer.analyze_youtube_video(
            #     url=youtube_url,
            #     duration_seconds=30,
            #     skip_frames=5
            # )
            # print(f"Video analysis: {result.summary}")
            print("⚠️  Video analysis skipped (no URL provided)")
    
    print("\n" + "=" * 60)
    print("Integration example completed!")
    print("=" * 60)


async def example_claude_with_mcp():
    """Example: Using Claude chat with MCP server data."""
    print("\n" + "=" * 60)
    print("Claude + MCP Integration Example")
    print("=" * 60)
    
    api_key = get_secure_api_key('anthropic')
    if not api_key:
        print("⚠️  Claude API key not found. Skipping this example.")
        return
    
    claude_agent = ClaudeAgent(api_key=api_key)
    session_id = claude_agent.create_session("mcp_session")
    
    orchestrator = MCPOrchestrator()
    
    async with orchestrator.session():
        # Get data from MCP servers
        itinerary_data = await orchestrator.manager.send_request(
            "itinerary",
            "create_itinerary",
            {
                "destination": "Tokyo, Japan",
                "start_date": "2025-06-01",
                "end_date": "2025-06-07",
                "travelers": 2
            }
        )
        
        # Use Claude to enhance the response
        mcp_context = {
            "itinerary": itinerary_data,
            "timestamp": datetime.now().isoformat()
        }
        
        response = await claude_agent.chat_with_mcp(
            "Based on this itinerary, suggest some activities and restaurants",
            session_id,
            mcp_context
        )
        
        print(f"\nClaude Response with MCP Context:")
        print(f"{json.dumps(response, indent=2)}")


async def example_video_analysis_workflow():
    """Example: Complete video analysis workflow."""
    print("\n" + "=" * 60)
    print("Video Analysis Workflow Example")
    print("=" * 60)
    
    try:
        analyzer = YOLO11Analyzer()
        print("✅ YOLO11 analyzer initialized")
        
        # Example YouTube URL (replace with actual travel video)
        youtube_url = "https://www.youtube.com/watch?v=EXAMPLE"
        
        print(f"\nAnalyzing video: {youtube_url}")
        print("(Note: Replace with actual YouTube URL to test)")
        
        # Uncomment to run actual analysis:
        # result = await analyzer.analyze_youtube_video(
        #     url=youtube_url,
        #     duration_seconds=30,
        #     skip_frames=5,
        #     real_time=False
        # )
        # 
        # print(f"\nAnalysis Results:")
        # print(f"Total detections: {result.summary['total_detections']}")
        # print(f"Travel context: {result.summary['travel_context']}")
        # print(f"Top objects: {[obj['name'] for obj in result.summary['top_objects'][:5]]}")
        
        print("\n⚠️  Video analysis skipped (example URL provided)")
        
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all integration examples."""
    print("\n" + "🚀 Travel Genie Integration Examples" + "\n")
    
    # Run examples
    await example_complete_travel_planning()
    await example_claude_with_mcp()
    await example_video_analysis_workflow()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

