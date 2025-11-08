#!/usr/bin/env python3
"""
MCP Testing Script for TravelGenie
Run this script to test MCP functionality manually
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from modules.mcp_client import MCPClient
from config.settings import settings


async def test_mcp_basic():
    """Test basic MCP functionality."""
    print("🧪 Testing MCP Client Basic Functionality")
    print("=" * 50)
    
    mcp_client = MCPClient()
    
    try:
        # Test initialization
        print("1. Testing MCP Client initialization...")
        await mcp_client.initialize()
        print("✅ MCP Client initialized successfully")
        
        # Test connection status
        print("\n2. Testing connection status...")
        is_connected = await mcp_client.is_connected()
        print(f"✅ Connection status: {is_connected}")
        
        # Test basic query processing
        print("\n3. Testing basic query processing...")
        result = await mcp_client.process_query(
            "What's the weather like in Paris?", 
            48.8566, 
            2.3522
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Query processed successfully")
            print(f"Response: {result['response'][:100]}...")
            print(f"Model: {result['model']}")
            print(f"Usage: {result['usage']}")
        
        # Test intent analysis
        print("\n4. Testing intent analysis...")
        intent_result = await mcp_client.analyze_intent("What's the weather like?")
        print(f"✅ Intent analysis: {intent_result}")
        
        # Test response enhancement
        print("\n5. Testing response enhancement...")
        weather_data = {
            "current": {"temperature": 20, "weather_description": "Sunny"},
            "daily": []
        }
        enhanced = await mcp_client.enhance_response(
            "weather", 
            weather_data, 
            "What's the weather like?"
        )
        print(f"✅ Enhanced response: {enhanced[:100]}...")
        
        # Test itinerary planning
        print("\n6. Testing itinerary planning...")
        context = {
            "location": (48.8566, 2.3522),
            "query": "Plan a day trip in Paris",
            "user_profile": {"interests": ["museums", "landmarks"]}
        }
        itinerary = await mcp_client.plan_itinerary(context)
        
        if "error" in itinerary:
            print(f"❌ Itinerary error: {itinerary['error']}")
        else:
            print("✅ Itinerary planned successfully")
            print(f"Number of activities: {len(itinerary['itinerary'])}")
            for i, activity in enumerate(itinerary['itinerary'][:3]):  # Show first 3
                print(f"  {i+1}. {activity['time']} - {activity['activity']}")
        
        # Test close
        print("\n7. Testing MCP Client close...")
        await mcp_client.close()
        print("✅ MCP Client closed successfully")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 MCP Testing Complete")


async def test_mcp_with_api_keys():
    """Test MCP with actual API keys."""
    print("🔑 Testing MCP with API Keys")
    print("=" * 50)
    
    # Check if API key is available
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    print(f"✅ API Key found: {settings.ANTHROPIC_API_KEY[:10]}...")
    
    mcp_client = MCPClient()
    
    try:
        await mcp_client.initialize()
        
        # Test a real query
        print("\n🌍 Testing real query...")
        result = await mcp_client.process_query(
            "Tell me about Paris and suggest 3 must-visit places", 
            48.8566, 
            2.3522
        )
        
        if "error" in result:
            print(f"❌ API Error: {result['error']}")
        else:
            print("✅ Real query successful!")
            print(f"Response: {result['response']}")
            print(f"Token usage: {result['usage']}")
        
        await mcp_client.close()
        
    except Exception as e:
        print(f"❌ Error with real API: {str(e)}")


def check_environment():
    """Check environment setup."""
    print("🔍 Checking Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        'anthropic', 'fastapi', 'uvicorn', 'pydantic', 
        'httpx', 'aiohttp', 'loguru', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check environment variables
    print(f"\nEnvironment variables:")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if settings.ANTHROPIC_API_KEY else '❌ Not set'}")
    print(f"OPENTRIPMAP_KEY: {'✅ Set' if settings.OPENTRIPMAP_KEY else '❌ Not set'}")
    print(f"OPENROUTESERVICE_KEY: {'✅ Set' if settings.OPENROUTESERVICE_KEY else '❌ Not set'}")
    print(f"UNSPLASH_ACCESS_KEY: {'✅ Set' if settings.UNSPLASH_ACCESS_KEY else '❌ Not set'}")
    
    return True


async def main():
    """Main testing function."""
    print("🚀 TravelGenie MCP Testing Suite")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues above.")
        return
    
    print("\n" + "=" * 60)
    
    # Test basic functionality (with mocks)
    await test_mcp_basic()
    
    # Test with real API keys if available
    if settings.ANTHROPIC_API_KEY:
        print("\n" + "=" * 60)
        await test_mcp_with_api_keys()
    else:
        print("\n⚠️  Skipping real API tests - ANTHROPIC_API_KEY not set")
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
