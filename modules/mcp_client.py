"""
MCP (Model Context Protocol) Client for Claude Integration
Handles communication with Claude API via MCP
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import anthropic
from anthropic import AsyncAnthropic
from loguru import logger

from config.settings import settings


@dataclass
class MCPResponse:
    """MCP response structure."""
    content: str
    intent: Optional[str] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class MCPClient:
    """MCP Client for Claude API integration."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.client: Optional[AsyncAnthropic] = None
        self.is_initialized = False
        self.model = "claude-3-sonnet-20240229"  # Using Sonnet for cost efficiency
        
    async def initialize(self):
        """Initialize the MCP client connection."""
        try:
            self.client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                timeout=settings.API_TIMEOUT_CLAUDE
            )
            self.is_initialized = True
            logger.info("✅ MCP Client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP Client: {str(e)}")
            raise
    
    async def close(self):
        """Close the MCP client connection."""
        if self.client:
            # Anthropic client doesn't need explicit closing
            self.is_initialized = False
            logger.info("MCP Client closed")
    
    async def is_connected(self) -> bool:
        """Check if MCP client is connected."""
        return self.is_initialized and self.client is not None
    
    async def process_query(
        self,
        query: str,
        lat: float,
        lon: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a general query using Claude.
        
        Args:
            query: User's natural language query
            lat: Latitude
            lon: Longitude
            context: Additional context
            
        Returns:
            Processed response from Claude
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Build the prompt
            prompt = self._build_prompt(query, lat, lon, context)
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and parse response
            content = response.content[0].text if response.content else ""
            
            return {
                "response": content,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens if hasattr(response, 'usage') else 0,
                    "output_tokens": response.usage.output_tokens if hasattr(response, 'usage') else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query with Claude: {str(e)}")
            return {
                "response": "I'm having trouble processing your request right now. Please try again.",
                "error": str(e)
            }
    
    async def plan_itinerary(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan a travel itinerary using Claude.
        
        Args:
            context: Context including location, preferences, etc.
            
        Returns:
            Itinerary plan
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            lat, lon = context.get("location", (48.8566, 2.3522))
            query = context.get("query", "Plan a day trip")
            user_profile = context.get("user_profile", {})
            
            prompt = f"""You are a travel planning assistant. Create a detailed day itinerary based on:
            
            Location: Latitude {lat}, Longitude {lon}
            Request: {query}
            User Preferences: {json.dumps(user_profile, indent=2) if user_profile else "None specified"}
            
            Please provide:
            1. A structured itinerary with times
            2. Specific places to visit
            3. Estimated time at each location
            4. Travel time between locations
            5. Tips and recommendations
            
            Format the response as a clear, actionable plan."""
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.8,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Parse the itinerary into structured format
            itinerary = self._parse_itinerary(content)
            
            return {
                "itinerary": itinerary,
                "raw_response": content,
                "location": {"lat": lat, "lon": lon}
            }
            
        except Exception as e:
            logger.error(f"Error planning itinerary: {str(e)}")
            return {
                "error": str(e),
                "itinerary": []
            }
    
    async def enhance_response(
        self,
        intent: str,
        data: Dict[str, Any],
        original_query: str
    ) -> str:
        """
        Enhance a response with Claude's natural language capabilities.
        
        Args:
            intent: Detected intent
            data: Raw data from APIs
            original_query: Original user query
            
        Returns:
            Enhanced natural language response
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            prompt = f"""Convert this travel data into a helpful, conversational response:
            
            User Query: {original_query}
            Intent: {intent}
            Data: {json.dumps(data, indent=2)[:2000]}  # Limit data size
            
            Guidelines:
            - Be conversational and helpful
            - Highlight the most relevant information
            - Add practical tips if appropriate
            - Keep it concise but informative
            - Use emojis sparingly for friendliness
            """
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text if response.content else "Here's what I found for you."
            
        except Exception as e:
            logger.error(f"Error enhancing response: {str(e)}")
            return "Here's what I found for you."
    
    def _build_prompt(
        self,
        query: str,
        lat: float,
        lon: float,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a prompt for Claude."""
        prompt_parts = [
            f"You are TravelGenie, a helpful travel assistant.",
            f"User Query: {query}",
            f"Current Location: Latitude {lat}, Longitude {lon}",
        ]
        
        if context:
            prompt_parts.append(f"Additional Context: {json.dumps(context, indent=2)}")
        
        prompt_parts.append("\nPlease provide a helpful, informative response.")
        
        return "\n".join(prompt_parts)
    
    def _parse_itinerary(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Claude's itinerary response into structured format.
        
        Args:
            content: Raw itinerary text from Claude
            
        Returns:
            Structured itinerary list
        """
        # Simple parsing - in production, use more sophisticated parsing
        lines = content.strip().split('\n')
        itinerary = []
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for time patterns (e.g., "9:00 AM", "14:30")
            import re
            time_match = re.match(r'^(\d{1,2}:\d{2}\s*(?:AM|PM)?)', line)
            
            if time_match:
                if current_item:
                    itinerary.append(current_item)
                
                current_item = {
                    "time": time_match.group(1),
                    "activity": line[len(time_match.group(1)):].strip(' -:'),
                    "details": []
                }
            elif current_item and line.startswith(('•', '-', '*')):
                current_item["details"].append(line.strip('•-* '))
        
        if current_item:
            itinerary.append(current_item)
        
        return itinerary if itinerary else [
            {
                "time": "Full Day",
                "activity": "Explore the area",
                "details": content.split('\n')[:5]  # First 5 lines as details
            }
        ]
    
    async def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Use Claude to analyze query intent with more nuance.
        
        Args:
            query: User query
            
        Returns:
            Intent analysis including confidence scores
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            prompt = f"""Analyze this travel query and identify the primary intent:
            
            Query: "{query}"
            
            Possible intents:
            - weather: Weather information
            - places: Finding attractions, restaurants, etc.
            - route: Directions and navigation
            - events: Local events and activities
            - currency: Exchange rates
            - image: Photos of locations
            - plan_day: Itinerary planning
            - general: General travel information
            
            Respond with JSON containing:
            {{
                "intent": "primary_intent",
                "confidence": 0.0-1.0,
                "entities": ["extracted", "entities"],
                "sub_intent": "optional_sub_intent"
            }}
            """
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text if response.content else "{}"
            
            # Try to parse JSON from response
            try:
                # Extract JSON from the response (Claude might add explanation)
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            # Fallback
            return {
                "intent": "general",
                "confidence": 0.5,
                "entities": [],
                "sub_intent": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing intent with Claude: {str(e)}")
            return {
                "intent": "general",
                "confidence": 0.0,
                "error": str(e)
            }


# Export the client class
__all__ = ["MCPClient", "MCPResponse"]