"""
Claude API Agent - Handles conversational AI using Anthropic's Claude
Integrates with the application workflow for chat functionality
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import anthropic
from anthropic import AsyncAnthropic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Maintains conversation context and history."""
    messages: List[Message] = field(default_factory=list)
    system_prompt: str = ""
    max_history: int = 50
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history."""
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        
        # Trim history if exceeds max
        if len(self.messages) > self.max_history:
            # Keep system message if present
            if self.messages[0].role == "system":
                self.messages = [self.messages[0]] + self.messages[-(self.max_history-1):]
            else:
                self.messages = self.messages[-self.max_history:]
    
    def get_claude_format(self) -> List[Dict[str, str]]:
        """Convert messages to Claude API format."""
        claude_messages = []
        for msg in self.messages:
            if msg.role != "system":  # System messages handled separately
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return claude_messages
    
    def clear_history(self):
        """Clear conversation history except system prompt."""
        self.messages = [m for m in self.messages if m.role == "system"]


class ClaudeAgent:
    """
    Claude API agent for handling conversational AI in the travel assistant.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize the Claude agent.
        
        Args:
            api_key: Anthropic API key (uses env var if not provided)
            model: Claude model to use
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Claude API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize client
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.sync_client = anthropic.Anthropic(api_key=self.api_key)
        
        # Model settings
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Conversation contexts for multiple sessions
        self.contexts: Dict[str, ConversationContext] = {}
        
        # Default system prompt for travel assistant
        self.default_system_prompt = """You are Travel Genie, an intelligent travel planning assistant. 
        You help users plan their trips, find flights and hotels, create itineraries, and provide 
        travel recommendations. You have access to real-time information about destinations, weather, 
        and travel options. Be helpful, informative, and enthusiastic about travel while maintaining 
        accuracy in your responses. When users ask about specific bookings or itineraries, coordinate 
        with the available MCP servers to provide accurate information."""
    
    def create_session(self, session_id: str, system_prompt: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique identifier for the session
            system_prompt: Optional custom system prompt
        
        Returns:
            Session ID
        """
        context = ConversationContext(
            system_prompt=system_prompt or self.default_system_prompt
        )
        
        # Add system message
        context.add_message("system", context.system_prompt)
        
        self.contexts[session_id] = context
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    async def chat(
        self,
        message: str,
        session_id: str = "default",
        stream: bool = False,
        tools: Optional[List[Dict]] = None
    ) -> Any:
        """
        Send a chat message to Claude and get response.
        
        Args:
            message: User message
            session_id: Session identifier
            stream: Whether to stream the response
            tools: Optional tool definitions for function calling
        
        Returns:
            Claude's response (string or async generator if streaming)
        """
        # Get or create context
        if session_id not in self.contexts:
            self.create_session(session_id)
        
        context = self.contexts[session_id]
        
        # Add user message to history
        context.add_message("user", message)
        
        try:
            # Prepare messages for Claude
            claude_messages = context.get_claude_format()
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": claude_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": context.system_prompt
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = {"type": "auto"}
            
            if stream:
                # Stream response
                return self._stream_response(request_params, context)
            else:
                # Get complete response
                response = await self.client.messages.create(**request_params)
                
                # Extract response text
                response_text = response.content[0].text if response.content else ""
                
                # Add assistant message to history
                context.add_message("assistant", response_text)
                
                # Check for tool use
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    return {
                        "content": response_text,
                        "tool_calls": response.tool_calls
                    }
                
                return response_text
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_msg = f"I encountered an error: {str(e)}"
            context.add_message("assistant", error_msg)
            return error_msg
    
    async def _stream_response(
        self, 
        request_params: Dict,
        context: ConversationContext
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Claude.
        
        Args:
            request_params: Parameters for the API request
            context: Conversation context
        
        Yields:
            Response chunks
        """
        try:
            full_response = ""
            
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield text
            
            # Add complete response to history
            context.add_message("assistant", full_response)
            
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"Error: {str(e)}"
    
    async def chat_with_mcp(
        self,
        message: str,
        session_id: str = "default",
        mcp_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chat with Claude while providing MCP server data as context.
        
        Args:
            message: User message
            session_id: Session identifier
            mcp_data: Data from MCP servers to include as context
        
        Returns:
            Response with integrated MCP data
        """
        # Enhance message with MCP data if available
        enhanced_message = message
        if mcp_data:
            context_info = "\n\nAvailable travel data:\n"
            context_info += json.dumps(mcp_data, indent=2)
            enhanced_message = f"{message}\n{context_info}"
        
        # Define tools for MCP interaction
        mcp_tools = [
            {
                "name": "search_flights",
                "description": "Search for available flights",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string"},
                        "destination": {"type": "string"},
                        "date": {"type": "string"}
                    }
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for hotels",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"}
                    }
                }
            },
            {
                "name": "create_itinerary",
                "description": "Create a travel itinerary",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"}
                    }
                }
            }
        ]
        
        response = await self.chat(enhanced_message, session_id, tools=mcp_tools)
        
        return {
            "response": response,
            "mcp_context": mcp_data,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of messages in the session
        """
        if session_id not in self.contexts:
            return []
        
        context = self.contexts[session_id]
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in context.messages
        ]
    
    def clear_session(self, session_id: str):
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.contexts:
            self.contexts[session_id].clear_history()
            logger.info(f"Cleared session: {session_id}")
    
    def delete_session(self, session_id: str):
        """
        Delete a conversation session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    async def analyze_travel_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a travel query to extract intent and entities.
        
        Args:
            query: User's travel query
        
        Returns:
            Analysis results with intent and entities
        """
        analysis_prompt = f"""Analyze this travel query and extract:
        1. Intent (search_flights, book_hotel, create_itinerary, get_recommendations, etc.)
        2. Entities (destination, dates, travelers, preferences, etc.)
        3. Urgency (immediate, planning, exploring)
        
        Query: {query}
        
        Return as JSON format."""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.3,
                system="You are a travel query analyzer. Extract intent and entities from travel queries."
            )
            
            # Parse response
            result_text = response.content[0].text if response.content else "{}"
            
            # Try to parse as JSON
            try:
                analysis = json.loads(result_text)
            except:
                # Fallback to basic structure
                analysis = {
                    "intent": "general_query",
                    "entities": {},
                    "urgency": "exploring",
                    "raw_analysis": result_text
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "error": str(e)
            }


# Example usage and testing
async def main():
    """Example usage of the Claude Agent."""
    # Initialize agent
    agent = ClaudeAgent()
    
    # Create a session
    session_id = "test_session"
    agent.create_session(session_id)
    
    # Example queries
    queries = [
        "I want to plan a trip to Paris for next month",
        "What are the best attractions in Paris?",
        "Find me flights from New York to Paris in December"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        
        # Get response
        response = await agent.chat(query, session_id)
        print(f"Assistant: {response}")
        
        # Analyze query
        analysis = await agent.analyze_travel_query(query)
        print(f"Analysis: {json.dumps(analysis, indent=2)}")
    
    # Get session history
    history = agent.get_session_history(session_id)
    print(f"\nSession history: {len(history)} messages")


if __name__ == "__main__":
    # Run example if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        asyncio.run(main())
    else:
        print("Please set ANTHROPIC_API_KEY environment variable to test")
