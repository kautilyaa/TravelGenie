"""
User Profile Management Module
Handles user preferences and profile data
"""

import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
import asyncio
import aiosqlite

from config.settings import settings
from urllib.parse import urlparse


class UserProfileManager:
    """User profile and preferences management."""
    
    def __init__(self):
        """Initialize profile manager."""
        # self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        parsed = urlparse(settings.DATABASE_URL)
        self.db_path = parsed.path.lstrip('/')
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database and tables exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences TEXT DEFAULT '{}',
                    travel_history TEXT DEFAULT '[]',
                    favorite_places TEXT DEFAULT '[]'
                )
            """)
            
            # Create query_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    intent TEXT,
                    location_lat REAL,
                    location_lon REAL,
                    response_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {str(e)}")
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary or None
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "created_at": row[1],
                        "last_active": row[2],
                        "preferences": json.loads(row[3]) if row[3] else {},
                        "travel_history": json.loads(row[4]) if row[4] else [],
                        "favorite_places": json.loads(row[5]) if row[5] else []
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return None
    
    async def create_profile(
        self,
        user_id: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user profile.
        
        Args:
            user_id: User identifier
            preferences: Initial preferences
            
        Returns:
            Created profile dictionary
        """
        try:
            profile_data = {
                "id": user_id,
                "preferences": preferences or {},
                "travel_history": [],
                "favorite_places": []
            }
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT OR REPLACE INTO users 
                       (id, preferences, travel_history, favorite_places) 
                       VALUES (?, ?, ?, ?)""",
                    (
                        user_id,
                        json.dumps(profile_data["preferences"]),
                        json.dumps(profile_data["travel_history"]),
                        json.dumps(profile_data["favorite_places"])
                    )
                )
                await db.commit()
            
            logger.info(f"Profile created for user: {user_id}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            return {"error": str(e)}
    
    async def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: New preferences
            
        Returns:
            Success status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET preferences = ?, last_active = CURRENT_TIMESTAMP WHERE id = ?",
                    (json.dumps(preferences), user_id)
                )
                await db.commit()
            
            logger.info(f"Preferences updated for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return False
    
    async def add_to_history(
        self,
        user_id: str,
        query: str,
        intent: str,
        lat: float,
        lon: float,
        response_time: float
    ) -> bool:
        """
        Add query to user history.
        
        Args:
            user_id: User identifier
            query: User query
            intent: Detected intent
            lat: Latitude
            lon: Longitude
            response_time: Response time in seconds
            
        Returns:
            Success status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO query_history 
                       (user_id, query, intent, location_lat, location_lon, response_time)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, query, intent, lat, lon, response_time)
                )
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to history: {str(e)}")
            return False
    
    async def get_query_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user query history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of queries to return
            
        Returns:
            List of query history entries
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """SELECT query, intent, location_lat, location_lon, 
                              response_time, timestamp
                       FROM query_history 
                       WHERE user_id = ? 
                       ORDER BY timestamp DESC 
                       LIMIT ?""",
                    (user_id, limit)
                )
                rows = await cursor.fetchall()
                
                history = []
                for row in rows:
                    history.append({
                        "query": row[0],
                        "intent": row[1],
                        "location": {"lat": row[2], "lon": row[3]},
                        "response_time": row[4],
                        "timestamp": row[5]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    async def add_favorite_place(
        self,
        user_id: str,
        place_data: Dict[str, Any]
    ) -> bool:
        """
        Add a place to user's favorites.
        
        Args:
            user_id: User identifier
            place_data: Place information
            
        Returns:
            Success status
        """
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                await self.create_profile(user_id)
                profile = await self.get_profile(user_id)
            
            favorites = profile.get("favorite_places", [])
            favorites.append(place_data)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET favorite_places = ? WHERE id = ?",
                    (json.dumps(favorites), user_id)
                )
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding favorite place: {str(e)}")
            return False
    
    async def get_favorite_places(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's favorite places.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of favorite places
        """
        try:
            profile = await self.get_profile(user_id)
            if profile:
                return profile.get("favorite_places", [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting favorite places: {str(e)}")
            return []
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            User statistics dictionary
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get total queries
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM query_history WHERE user_id = ?",
                    (user_id,)
                )
                total_queries = (await cursor.fetchone())[0]
                
                # Get most common intents
                cursor = await db.execute(
                    """SELECT intent, COUNT(*) as count 
                       FROM query_history 
                       WHERE user_id = ? 
                       GROUP BY intent 
                       ORDER BY count DESC 
                       LIMIT 5""",
                    (user_id,)
                )
                intent_stats = await cursor.fetchall()
                
                # Get average response time
                cursor = await db.execute(
                    "SELECT AVG(response_time) FROM query_history WHERE user_id = ?",
                    (user_id,)
                )
                avg_response_time = (await cursor.fetchone())[0] or 0
                
                return {
                    "total_queries": total_queries,
                    "average_response_time": round(avg_response_time, 2),
                    "most_common_intents": [
                        {"intent": intent, "count": count} 
                        for intent, count in intent_stats
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {"error": str(e)}


# Export the manager class
__all__ = ["UserProfileManager"]