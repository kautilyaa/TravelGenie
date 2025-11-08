"""
Test suite for TravelGenie API modules
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from modules.weather import WeatherAPI
from modules.places import PlacesAPI
from modules.routing import RoutingAPI
from modules.images import ImagesAPI
from modules.events import EventsAPI
from modules.currency import CurrencyAPI
from modules.intent_detector import IntentDetector
from modules.response_composer import ResponseComposer
from modules.mcp_client import MCPClient, MCPResponse


class TestWeatherAPI:
    """Test Weather API functionality."""
    
    @pytest.mark.asyncio
    async def test_get_weather_mock(self):
        """Test weather API with mock data."""
        weather_api = WeatherAPI()
        result = await weather_api.get_weather(48.8566, 2.3522)
        
        assert "current" in result
        assert "daily" in result
        assert result["current"]["temperature"] is not None


class TestPlacesAPI:
    """Test Places API functionality."""
    
    @pytest.mark.asyncio
    async def test_get_places_mock(self):
        """Test places API with mock data."""
        places_api = PlacesAPI()
        result = await places_api.get_places(48.8566, 2.3522)
        
        assert "features" in result
        assert len(result["features"]) > 0


class TestIntentDetector:
    """Test Intent Detection functionality."""
    
    def test_weather_intent(self):
        """Test weather intent detection."""
        detector = IntentDetector()
        intent = asyncio.run(detector.detect("What's the weather like?"))
        assert intent == "weather"
    
    def test_places_intent(self):
        """Test places intent detection."""
        detector = IntentDetector()
        intent = asyncio.run(detector.detect("Find restaurants near me"))
        assert intent == "places"


class TestResponseComposer:
    """Test Response Composition functionality."""
    
    def test_weather_response(self):
        """Test weather response composition."""
        composer = ResponseComposer()
        weather_data = {
            "current": {
                "temperature": 20,
                "weather_description": "Sunny",
                "windspeed": 10
            },
            "daily": []
        }
        
        response = composer._compose_weather_response(weather_data, "weather test")
        assert "Current Weather" in response
        assert "20°C" in response


class TestMCPClient:
    """Test MCP Client functionality."""
    
    @pytest.fixture
    def mcp_client(self):
        """Create MCP client instance for testing."""
        return MCPClient()
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self, mcp_client):
        """Test MCP client initialization."""
        # Test initial state
        assert not mcp_client.is_initialized
        assert mcp_client.client is None
        
        # Test initialization (with mock)
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            await mcp_client.initialize()
            
            assert mcp_client.is_initialized
            assert mcp_client.client is not None
    
    @pytest.mark.asyncio
    async def test_mcp_client_connection_status(self, mcp_client):
        """Test MCP client connection status."""
        # Test when not initialized
        is_connected = await mcp_client.is_connected()
        assert not is_connected
        
        # Test when initialized
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            await mcp_client.initialize()
            is_connected = await mcp_client.is_connected()
            assert is_connected
    
    @pytest.mark.asyncio
    async def test_mcp_client_close(self, mcp_client):
        """Test MCP client close functionality."""
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            await mcp_client.initialize()
            assert mcp_client.is_initialized
            
            await mcp_client.close()
            assert not mcp_client.is_initialized
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, mcp_client):
        """Test successful query processing."""
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = "Test response from Claude"
        mock_response.usage = AsyncMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            result = await mcp_client.process_query(
                "What's the weather like?", 
                48.8566, 
                2.3522
            )
            
            assert "response" in result
            assert result["response"] == "Test response from Claude"
            assert "model" in result
            assert "usage" in result
            assert result["usage"]["input_tokens"] == 100
    
    @pytest.mark.asyncio
    async def test_process_query_error(self, mcp_client):
        """Test query processing with error."""
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))
            mock_anthropic.return_value = mock_client
            
            result = await mcp_client.process_query(
                "Test query", 
                48.8566, 
                2.3522
            )
            
            assert "error" in result
            assert "I'm having trouble processing" in result["response"]
    
    @pytest.mark.asyncio
    async def test_plan_itinerary(self, mcp_client):
        """Test itinerary planning functionality."""
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = """9:00 AM - Visit Eiffel Tower
• Take photos
• Enjoy the view

10:30 AM - Walk to Louvre Museum
• See famous artworks
• Take guided tour"""
        
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            context = {
                "location": (48.8566, 2.3522),
                "query": "Plan a day in Paris",
                "user_profile": {"interests": ["museums", "landmarks"]}
            }
            
            result = await mcp_client.plan_itinerary(context)
            
            assert "itinerary" in result
            assert "raw_response" in result
            assert "location" in result
            assert len(result["itinerary"]) > 0
            assert result["itinerary"][0]["time"] == "9:00 AM"
    
    @pytest.mark.asyncio
    async def test_enhance_response(self, mcp_client):
        """Test response enhancement functionality."""
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = "Here's a helpful response about the weather!"
        
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            data = {"temperature": 20, "weather": "sunny"}
            result = await mcp_client.enhance_response(
                "weather", 
                data, 
                "What's the weather like?"
            )
            
            assert result == "Here's a helpful response about the weather!"
    
    @pytest.mark.asyncio
    async def test_analyze_intent(self, mcp_client):
        """Test intent analysis functionality."""
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock()]
        mock_response.content[0].text = '{"intent": "weather", "confidence": 0.9, "entities": ["weather"], "sub_intent": null}'
        
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            result = await mcp_client.analyze_intent("What's the weather like?")
            
            assert result["intent"] == "weather"
            assert result["confidence"] == 0.9
            assert "weather" in result["entities"]
    
    def test_build_prompt(self, mcp_client):
        """Test prompt building functionality."""
        prompt = mcp_client._build_prompt(
            "Test query", 
            48.8566, 
            2.3522, 
            {"test": "context"}
        )
        
        assert "TravelGenie" in prompt
        assert "Test query" in prompt
        assert "48.8566" in prompt
        assert "2.3522" in prompt
        assert "test" in prompt
    
    def test_parse_itinerary(self, mcp_client):
        """Test itinerary parsing functionality."""
        content = """9:00 AM - Visit Eiffel Tower
• Take photos
• Enjoy the view

10:30 AM - Walk to Louvre Museum
• See famous artworks"""
        
        result = mcp_client._parse_itinerary(content)
        
        assert len(result) == 2
        assert result[0]["time"] == "9:00 AM"
        assert "Eiffel Tower" in result[0]["activity"]
        assert len(result[0]["details"]) == 2
        assert result[1]["time"] == "10:30 AM"
    
    def test_parse_itinerary_fallback(self, mcp_client):
        """Test itinerary parsing fallback."""
        content = "Just some random text without time patterns"
        
        result = mcp_client._parse_itinerary(content)
        
        assert len(result) == 1
        assert result[0]["time"] == "Full Day"
        assert result[0]["activity"] == "Explore the area"


class TestMCPIntegration:
    """Test MCP integration with other modules."""
    
    @pytest.mark.asyncio
    async def test_mcp_with_weather_api(self):
        """Test MCP integration with weather API."""
        weather_api = WeatherAPI()
        mcp_client = MCPClient()
        
        # Mock the weather API response
        weather_data = {
            "current": {"temperature": 20, "weather_description": "Sunny"},
            "daily": []
        }
        
        # Mock MCP client
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = [AsyncMock()]
            mock_response.content[0].text = "The weather is sunny and pleasant!"
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            # Test enhanced weather response
            enhanced = await mcp_client.enhance_response(
                "weather", 
                weather_data, 
                "What's the weather like?"
            )
            
            assert "sunny" in enhanced.lower()
    
    @pytest.mark.asyncio
    async def test_mcp_with_places_api(self):
        """Test MCP integration with places API."""
        places_api = PlacesAPI()
        mcp_client = MCPClient()
        
        # Mock places data
        places_data = {
            "features": [
                {"properties": {"name": "Eiffel Tower", "category": "landmark"}}
            ]
        }
        
        # Mock MCP client
        with patch('modules.mcp_client.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = [AsyncMock()]
            mock_response.content[0].text = "Here are some great places to visit!"
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            # Test enhanced places response
            enhanced = await mcp_client.enhance_response(
                "places", 
                places_data, 
                "Find attractions near me"
            )
            
            assert "places" in enhanced.lower()


if __name__ == "__main__":
    pytest.main([__file__])