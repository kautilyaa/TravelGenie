"""
DynamoDB database adapter for Slack Travel Bot
Replaces SQLite with DynamoDB for AWS deployment
"""

import os
import json
import hashlib
import boto3
from datetime import datetime
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
import uuid

# Get table names from environment
PROJECT_NAME = os.getenv('PROJECT_NAME', 'travel-assistant-slack-bot')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

CHAT_SESSIONS_TABLE = os.getenv(
    'DYNAMODB_CHAT_SESSIONS_TABLE',
    f'{PROJECT_NAME}-{ENVIRONMENT}-chat-sessions'
)
MESSAGES_TABLE = os.getenv(
    'DYNAMODB_MESSAGES_TABLE',
    f'{PROJECT_NAME}-{ENVIRONMENT}-messages'
)
TOOL_CALLS_TABLE = os.getenv(
    'DYNAMODB_TOOL_CALLS_TABLE',
    f'{PROJECT_NAME}-{ENVIRONMENT}-tool-calls'
)

# Initialize DynamoDB
try:
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    chat_sessions_table = dynamodb.Table(CHAT_SESSIONS_TABLE)
    messages_table = dynamodb.Table(MESSAGES_TABLE)
    tool_calls_table = dynamodb.Table(TOOL_CALLS_TABLE)
except Exception as e:
    print(f"Warning: Could not initialize DynamoDB. Falling back to SQLite. Error: {e}")
    dynamodb = None


def get_timestamp() -> int:
    """Get current timestamp as epoch seconds"""
    return int(datetime.now().timestamp())


class ChatDatabase:
    """DynamoDB database for tracking chat history"""

    def __init__(self):
        """Initialize database connection"""
        if dynamodb is None:
            raise RuntimeError("DynamoDB not available. Check AWS credentials and region.")
        self.chat_sessions_table = chat_sessions_table
        self.messages_table = messages_table
        self.tool_calls_table = tool_calls_table

    def create_session_id(self, channel_id: str, user_id: str, thread_ts: Optional[str] = None) -> str:
        """Generate unique session ID"""
        components = f"{channel_id}:{user_id}:{thread_ts or 'main'}"
        return hashlib.md5(components.encode()).hexdigest()

    def save_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Save a message to the database"""
        try:
            item = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': json.dumps(metadata) if metadata else '',
                'created_at': get_timestamp()
            }
            self.messages_table.put_item(Item=item)
        except ClientError as e:
            print(f"Error saving message to DynamoDB: {e}")

    def save_tool_call(self, session_id: str, tool_name: str, input_params: Dict,
                      output: str, status: str = "success"):
        """Save tool call information"""
        try:
            item = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'tool_name': tool_name,
                'input_params': json.dumps(input_params),
                'output': str(output)[:10000],  # Limit output size
                'status': status,
                'created_at': get_timestamp()
            }
            self.tool_calls_table.put_item(Item=item)
        except ClientError as e:
            print(f"Error saving tool call to DynamoDB: {e}")

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversation history"""
        try:
            response = self.messages_table.query(
                IndexName='SessionIdIndex',
                KeyConditionExpression='session_id = :session_id',
                ExpressionAttributeValues={
                    ':session_id': session_id
                },
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )
            
            items = response.get('Items', [])
            # Sort by created_at and reverse to get chronological order
            items.sort(key=lambda x: x.get('created_at', 0))
            
            result = []
            for item in items:
                try:
                    timestamp = item.get('created_at', 0)
                    if isinstance(timestamp, (int, float)):
                        timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        timestamp_str = str(timestamp)
                    result.append({
                        "role": item.get('role', ''),
                        "content": item.get('content', ''),
                        "timestamp": timestamp_str
                    })
                except Exception as e:
                    # Fallback if timestamp conversion fails
                    result.append({
                        "role": item.get('role', ''),
                        "content": item.get('content', ''),
                        "timestamp": str(item.get('created_at', ''))
                    })
            return result
        except ClientError as e:
            print(f"Error retrieving session history from DynamoDB: {e}")
            return []

    def upsert_session(self, session_id: str, channel_id: str, user_id: str,
                      thread_ts: Optional[str] = None):
        """Create or update a chat session"""
        try:
            item = {
                'session_id': session_id,
                'channel_id': channel_id,
                'user_id': user_id,
                'thread_ts': thread_ts or '',
                'created_at': get_timestamp(),
                'updated_at': get_timestamp()
            }
            self.chat_sessions_table.put_item(Item=item)
        except ClientError as e:
            print(f"Error upserting session to DynamoDB: {e}")

