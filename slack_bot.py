#!/usr/bin/env python3
"""
Slack-integrated Travel Assistant Bot
Connects Slack to the Travel Assistant MCP orchestrator using Claude AI
"""

import asyncio
import json
import os
import sys
import logging
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import hashlib
from functools import wraps

from dotenv import load_dotenv
from anthropic import Anthropic
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "flight_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "hotel_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "event_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "geocoder_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "weather_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "finance_server"))
sys.path.insert(0, str(PROJECT_ROOT / "servers" / "traffic_crowd_server"))

try:
    from claude_orchestrator import get_tool_definitions, execute_tool, get_system_prompt
except ImportError as e:
    print(f"Error importing orchestrator: {e}")
    sys.exit(1)

load_dotenv()

IS_AWS_ENV = os.getenv('AWS_EXECUTION_ENV') is not None or os.getenv('ECS_CONTAINER_METADATA_URI') is not None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("slack_travel_bot.log")
    ]
)
logger = logging.getLogger("Slack-Travel-Bot")


class SlackConnectionErrorFilter(logging.Filter):
    """Filter to downgrade expected Slack SDK connection errors to warnings."""
    def filter(self, record):
        if record.levelno == logging.ERROR:
            error_msg = str(record.getMessage()).lower()
            if any(keyword in error_msg for keyword in [
                'enqueue', 'connection', 'transport', 'closing', 
                'reset', 'stale', 'disconnected', 'clientconnection'
            ]):
                record.levelno = logging.WARNING
                record.levelname = 'WARNING'
        return True


slack_logger = logging.getLogger("slack_sdk")
slack_logger.addFilter(SlackConnectionErrorFilter())


def retry_slack_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry Slack API operations on connection errors."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in [
                        'connection', 'transport', 'closed', 'reset', 
                        'stale', 'disconnected', 'enqueue'
                    ]):
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)
                            logger.warning(
                                f"Slack connection error (attempt {attempt + 1}/{max_retries}): {e}. "
                                f"Retrying in {wait_time}s..."
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"Slack operation failed after {max_retries} attempts: {e}")
                    else:
                        raise
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


def get_slack_system_prompt() -> str:
    """Get the base system prompt for the Slack Travel Assistant Bot."""
    base_prompt = get_system_prompt()
    
    slack_instructions = """

You are operating in Slack, a team communication platform. Follow these guidelines for Slack-compatible formatting:

**Slack mrkdwn Formatting Rules:**
- Use *bold* for emphasis and important information (e.g., prices, dates, locations)
- Use _italic_ for subtle emphasis or secondary information
- Use `backticks` for inline code, technical terms, or specific values (e.g., flight numbers, hotel codes)
- Use ```code blocks``` for multi-line code or structured data
- Use • (bullet) or - (dash) for bullet points - both work in Slack
- Use > for quotes or callouts
- Use <url|link text> format for clickable links
- Use blank lines to separate sections for better readability
- Avoid using # for headers as they don't render well in Slack - use *bold* text on its own line instead

**Structured Response Format:**
When presenting travel information, use this format:
```
*Section Title*
• First item with details
• Second item with details

*Next Section*
• More information here
```

**Travel Plan Formatting Examples:**
- *Flight Options* (use bold for section headers)
  • *Option 1:* Details here with price `$XXX`
  • *Option 2:* Details here with price `$XXX`

- *Hotel Recommendations*
  • *Hotel Name* - Rating: `X/5` | Price: `$XXX/night`
  • Location and key features

- *Daily Itinerary*
  • *Day 1:* Activities and times
  • *Day 2:* Activities and times

- *Weather Forecast*
  • Use clear, concise weather information
  • Include temperatures and conditions

- *Budget Breakdown*
  • Use `$` for currency formatting
  • List items clearly with amounts

**Response Style:**
- Keep responses concise but informative - Slack users prefer scannable information
- Break up long responses into readable sections with clear headers
- Use blank lines between major sections
- When presenting multiple options, highlight the top 2-3 recommendations prominently
- Always include prices, dates, locations, and ratings in a clear, scannable format
- For complex travel plans, structure information hierarchically with proper spacing

**Conversation Style:**
- Be conversational but professional
- Acknowledge the user's request before diving into details
- If a query is unclear, ask clarifying questions in a friendly way
- Remember conversation history within the thread
- Reference previous messages when relevant
- Build on previous context for follow-up questions
- Maintain consistency in currency, date formats, and location names

**Error Handling:**
- If something goes wrong, provide a clear, helpful error message
- Suggest alternatives when a specific request cannot be fulfilled
- Always be helpful and solution-oriented

**Important:**
- NEVER use markdown that doesn't work in Slack (like # headers, complex tables, or HTML)
- ALWAYS use Slack's native mrkdwn syntax
- Keep formatting simple and readable on mobile devices
- Test your formatting mentally - if it looks cluttered, simplify it
"""
    
    return base_prompt + slack_instructions


def get_secret_from_aws(secret_name: str) -> Optional[str]:
    """Get secret from AWS Secrets Manager"""
    if not AWS_AVAILABLE or not IS_AWS_ENV:
        return None
    
    try:
        client = boto3.client('secretsmanager', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get('SecretString', '')
        
        try:
            secret_dict = json.loads(secret_string)
            key = secret_name.split('/')[-1].upper().replace('-', '_')
            return secret_dict.get(key) or secret_dict.get(key.replace('_KEY', '')) or secret_string
        except:
            return secret_string
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        return None


def get_env_or_secret(env_var: str, secret_name: str) -> Optional[str]:
    """Get value from environment variable or AWS Secrets Manager"""
    value = os.getenv(env_var)
    if value:
        return value
    
    if IS_AWS_ENV and secret_name:
        value = get_secret_from_aws(secret_name)
        if value:
            return value
    
    return None


class ChatDatabase:
    """Database for tracking chat history - supports both SQLite (local) and DynamoDB (AWS)"""

    def __init__(self, db_path: str = "slack_chat_history.db"):
        self.db_path = db_path
        self.use_dynamodb = IS_AWS_ENV
        
        if self.use_dynamodb:
            try:
                from dynamodb_database import ChatDatabase as DynamoDBChatDatabase
                self.db = DynamoDBChatDatabase()
                logger.info("Using DynamoDB for chat history")
            except Exception as e:
                logger.warning(f"Failed to initialize DynamoDB, falling back to SQLite: {e}")
                self.use_dynamodb = False
                self.init_database()
        else:
            self.init_database()

    def init_database(self):
        """Initialize SQLite database schema"""
        if self.use_dynamodb:
            return
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    thread_ts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    input_params TEXT,
                    output TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
            ''')

            conn.commit()

    def create_session_id(self, channel_id: str, user_id: str, thread_ts: Optional[str] = None) -> str:
        """Generate unique session ID"""
        components = f"{channel_id}:{user_id}:{thread_ts or 'main'}"
        return hashlib.md5(components.encode()).hexdigest()

    def save_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Save a message to the database"""
        if self.use_dynamodb:
            self.db.save_message(session_id, role, content, metadata)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (session_id, role, content, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, role, content, json.dumps(metadata) if metadata else None))
                conn.commit()

    def save_tool_call(self, session_id: str, tool_name: str, input_params: Dict,
                      output: str, status: str = "success"):
        """Save tool call information"""
        if self.use_dynamodb:
            self.db.save_tool_call(session_id, tool_name, input_params, output, status)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tool_calls (session_id, tool_name, input_params, output, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, tool_name, json.dumps(input_params), str(output)[:10000], status))
                conn.commit()

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversation history"""
        if self.use_dynamodb:
            return self.db.get_session_history(session_id, limit)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role, content, created_at 
                    FROM messages 
                    WHERE session_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (session_id, limit))

                rows = cursor.fetchall()
                return [
                    {"role": row[0], "content": row[1], "timestamp": row[2]}
                    for row in reversed(rows)
                ]

    def upsert_session(self, session_id: str, channel_id: str, user_id: str,
                      thread_ts: Optional[str] = None):
        """Create or update a chat session"""
        if self.use_dynamodb:
            self.db.upsert_session(session_id, channel_id, user_id, thread_ts)
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO chat_sessions 
                    (session_id, channel_id, user_id, thread_ts, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (session_id, channel_id, user_id, thread_ts))
                conn.commit()


class SlackTravelBot:
    """
    Slack-integrated Travel Assistant Bot with Claude AI
    """

    def __init__(self, model: str = "claude-3-7-sonnet-20250219"):
        self.model = model
        self.db = ChatDatabase()

        project_name = os.getenv("PROJECT_NAME", "travel-assistant-slack-bot")
        environment = os.getenv("ENVIRONMENT", "production")
        
        api_key = get_env_or_secret(
            "ANTHROPIC_API_KEY",
            f"{project_name}/{environment}/anthropic-api-key"
        )
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or AWS Secrets Manager")
        self.claude = Anthropic(api_key=api_key)

        self.slack_token = get_env_or_secret(
            "SLACK_BOT_TOKEN",
            f"{project_name}/{environment}/slack-bot-token"
        )
        self.slack_app_token = get_env_or_secret(
            "SLACK_APP_TOKEN",
            f"{project_name}/{environment}/slack-app-token"
        )

        if not self.slack_token or not self.slack_app_token:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required (check environment or AWS Secrets Manager)")

        self.slack_client = AsyncWebClient(token=self.slack_token)
        self.socket_client = SocketModeClient(
            app_token=self.slack_app_token,
            web_client=self.slack_client
        )

        self.tools = get_tool_definitions()
        self.system_prompt = get_slack_system_prompt()

        logger.info(f"Initialized Travel Assistant Bot with {len(self.tools)} tools")

    @retry_slack_operation(max_retries=3, delay=1.0)
    async def safe_slack_call(self, method_name: str, *args, **kwargs):
        """
        Safely call Slack API methods with retry logic for connection errors.
        """
        method = getattr(self.slack_client, method_name)
        return await method(*args, **kwargs)

    async def safe_post_message(self, channel: str, text: str, **kwargs):
        """
        Safely post a message to Slack with retry logic.
        """
        try:
            return await self.safe_slack_call('chat_postMessage', channel=channel, text=text, **kwargs)
        except Exception as e:
            logger.error(f"Failed to post message to Slack after retries: {e}")
            raise

    async def safe_add_reaction(self, channel: str, timestamp: str, name: str):
        """Safely add a reaction to a Slack message with retry logic."""
        try:
            return await self.safe_slack_call('reactions_add', channel=channel, timestamp=timestamp, name=name)
        except Exception as e:
            logger.debug(f"Could not add reaction (non-critical): {e}")
            return None

    async def safe_remove_reaction(self, channel: str, timestamp: str, name: str):
        """Safely remove a reaction from a Slack message with retry logic."""
        try:
            return await self.safe_slack_call('reactions_remove', channel=channel, timestamp=timestamp, name=name)
        except Exception as e:
            logger.debug(f"Could not remove reaction (non-critical): {e}")
            return None

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, "socket_client") and self.socket_client:
                await self.socket_client.disconnect()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def _anthropic_tools_from_definitions(self) -> List[Dict[str, Any]]:
        """Convert orchestrator tool definitions to Anthropic format"""
        tools = []
        for tool_def in self.tools:
            tools.append({
                "name": tool_def["name"],
                "description": tool_def["description"],
                "input_schema": tool_def["input_schema"]
            })
        return tools

    async def process_with_context(self, query: str, session_id: str,
                                  channel_id: str, user_id: str) -> str:
        """Process query with conversation context"""
        self.db.save_message(session_id, "user", query)
        history = self.db.get_session_history(session_id, limit=5)

        messages: List[Dict[str, Any]] = []

        for msg in history[:-1]:
            content = [{"type": "text", "text": msg["content"]}]
            messages.append({"role": msg["role"], "content": content})

        messages.append({"role": "user", "content": [{"type": "text", "text": query}]})
        tools = self._anthropic_tools_from_definitions()

        MAX_TURNS = 10
        for turn in range(MAX_TURNS):
            try:
                response = self.claude.messages.create(
                    model=self.model,
                    system=self.system_prompt,
                    tools=tools,
                    tool_choice={"type": "auto"},
                    max_tokens=4096,
                    temperature=0.1,
                    messages=messages,
                )

                assistant_content = response.content
                tool_uses = [b for b in assistant_content if hasattr(b, 'type') and b.type == "tool_use"]

                MAX_TOOLS_PER_TURN = 5
                tools_to_execute = tool_uses[:MAX_TOOLS_PER_TURN]
                remaining_tools = tool_uses[MAX_TOOLS_PER_TURN:]

                assistant_content_dicts = []
                for block in assistant_content:
                    if hasattr(block, 'type'):
                        if block.type == "text":
                            assistant_content_dicts.append({
                                "type": "text",
                                "text": block.text
                            })
                        elif block.type == "tool_use":
                            if block in tools_to_execute:
                                assistant_content_dicts.append({
                                    "type": "tool_use",
                                    "id": block.id,
                                    "name": block.name,
                                    "input": block.input
                                })

                messages.append({"role": "assistant", "content": assistant_content_dicts})

                if tools_to_execute:
                    tool_results_blocks: List[Dict[str, Any]] = []

                    if len(tool_uses) > MAX_TOOLS_PER_TURN:
                        logger.info(f"Limiting tool execution to {MAX_TOOLS_PER_TURN} tools (requested {len(tool_uses)} tools). {len(remaining_tools)} tools will be handled in next turn.")

                    for tu in tools_to_execute:
                        tool_name = tu.name
                        tool_use_id = tu.id
                        tool_input = tu.input if hasattr(tu, 'input') else {}

                        logger.info(f"Executing tool '{tool_name}' with params: {tool_input}")

                        try:
                            result = execute_tool(tool_name, **tool_input)

                            if isinstance(result, dict):
                                result_text = json.dumps(result, default=str, indent=2)[:10000]
                            else:
                                result_text = str(result)[:10000]

                            self.db.save_tool_call(session_id, tool_name, tool_input, result_text)

                        except Exception as e:
                            result_text = f"Error executing tool '{tool_name}': {str(e)}"
                            logger.error(result_text, exc_info=True)
                            self.db.save_tool_call(session_id, tool_name, tool_input, str(e), "error")

                        tool_results_blocks.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": [{"type": "text", "text": result_text}]
                        })

                    messages.append({"role": "user", "content": tool_results_blocks})
                    continue

                text_blocks = [b for b in assistant_content if hasattr(b, 'type') and b.type == "text"]
                final_text = "\n".join([b.text for b in text_blocks]).strip() if text_blocks else "(No response)"

                self.db.save_message(session_id, "assistant", final_text)

                return final_text

            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                return f"Error: {str(e)}"

        return "Conversation exceeded maximum turns. Please try a simpler query."

    async def handle_slack_event(self, client: SocketModeClient, req: SocketModeRequest):
        """Handle incoming Slack events"""
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            await client.send_socket_mode_response(response)

            event = req.payload.get("event", {})
            event_type = event.get("type")

            if event_type == "app_mention":
                await self.handle_mention(event)
            elif event_type == "message":
                if event.get("channel_type") == "im" or event.get("thread_ts"):
                    await self.handle_message(event)

    async def handle_mention(self, event: Dict):
        """Handle @mentions of the bot"""
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event.get("ts")

        bot_id = await self.get_bot_id()
        text = text.replace(f"<@{bot_id}>", "").strip()

        if not text:
            await self.safe_post_message(
                channel=channel_id,
                thread_ts=thread_ts,
                text="Hi! I'm your Travel Assistant. I can help you:\n"
                     "• Find flights and hotels\n"
                     "• Discover events and activities\n"
                     "• Check weather forecasts\n"
                     "• Convert currencies\n"
                     "• Analyze traffic and crowd conditions\n"
                     "• Plan comprehensive trips\n\n"
                     "Try asking: *\"Plan a trip to Banff, Alberta from Reston, Virginia for June 7-14, 2025\"*"
            )
            return

        await self.safe_add_reaction(channel_id, thread_ts, "thinking_face")

        session_id = self.db.create_session_id(channel_id, user_id, thread_ts)
        self.db.upsert_session(session_id, channel_id, user_id, thread_ts)

        try:
            response = await self.process_with_context(text, session_id, channel_id, user_id)

            await self.safe_remove_reaction(channel_id, thread_ts, "thinking_face")

            await self.safe_post_message(
                channel=channel_id,
                thread_ts=thread_ts,
                text=response,
                mrkdwn=True
            )

        except Exception as e:
            logger.error(f"Error handling mention: {e}", exc_info=True)
            await self.safe_remove_reaction(channel_id, thread_ts, "thinking_face")
            await self.safe_post_message(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"Sorry, I encountered an error: {str(e)}"
            )

    async def handle_message(self, event: Dict):
        """Handle direct messages"""
        if event.get("bot_id"):
            return

        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")
        thread_ts = event.get("thread_ts")
        ts = event.get("ts")

        if not text:
            return

        await self.safe_add_reaction(channel_id, ts, "thinking_face")

        session_id = self.db.create_session_id(channel_id, user_id, thread_ts)
        self.db.upsert_session(session_id, channel_id, user_id, thread_ts)

        try:
            response = await self.process_with_context(text, session_id, channel_id, user_id)

            await self.safe_remove_reaction(channel_id, ts, "thinking_face")

            await self.safe_post_message(
                channel=channel_id,
                thread_ts=thread_ts or ts,
                text=response,
                mrkdwn=True
            )

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self.safe_remove_reaction(channel_id, ts, "thinking_face")
            await self.safe_post_message(
                channel=channel_id,
                thread_ts=thread_ts or ts,
                text=f"Sorry, I encountered an error: {str(e)}"
            )

    async def get_bot_id(self) -> str:
        """Get the bot's user ID"""
        response = await self.slack_client.auth_test()
        return response["user_id"]

    async def start(self):
        """Start the Slack bot"""
        self.socket_client.socket_mode_request_listeners.append(self.handle_slack_event)
        await self.socket_client.connect()

        logger.info("=" * 60)
        logger.info("Travel Assistant Slack Bot Started!")
        logger.info("=" * 60)
        logger.info("The bot will respond to:")
        logger.info("  • Direct messages")
        logger.info("  • @mentions in channels")
        logger.info("  • Thread replies")
        logger.info("=" * 60)

        await asyncio.Event().wait()


async def main():
    """Main entry point"""
    test_mode = "--test" in sys.argv
    model = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")

    try:
        client = SlackTravelBot(model=model)

        if test_mode:
            logger.info("Running in test mode...")

            try:
                test_response = client.claude.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
                logger.info("Successfully connected to Anthropic API!")
            except Exception as e:
                logger.error(f"Anthropic connection failed: {e}")
                return

            try:
                bot_info = await client.slack_client.auth_test()
                logger.info(f"Successfully connected to Slack as {bot_info['user']}")
            except Exception as e:
                logger.error(f"Slack connection failed: {e}")
                return

            try:
                test_session = client.db.create_session_id("test", "test", "test")
                client.db.save_message(test_session, "user", "Test message")
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Database test failed: {e}")
                return

            try:
                tools = get_tool_definitions()
                logger.info(f"Loaded {len(tools)} tool definitions")
            except Exception as e:
                logger.error(f"Tool definitions failed: {e}")
                return

            logger.info("\n" + "=" * 60)
            logger.info("All systems operational!")
            logger.info("Run without --test to start the bot.")
            logger.info("=" * 60)

        else:
            await client.start()

    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        if 'client' in locals():
            await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

