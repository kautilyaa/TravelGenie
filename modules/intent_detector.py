"""
Intent Detection Module
Classifies user queries into travel-related intents
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class Intent:
    """Intent classification result."""
    name: str
    confidence: float
    keywords: List[str]
    entities: Dict[str, any]


class IntentDetector:
    """Detect user intent from natural language queries."""
    
    def __init__(self):
        """Initialize intent detector with patterns."""
        self.intent_patterns = {
            "weather": {
                "keywords": ["weather", "temperature", "rain", "sunny", "cloudy", 
                           "forecast", "climate", "hot", "cold", "humid", "snow"],
                "patterns": [
                    r"what.{0,10}weather",
                    r"how.{0,10}weather",
                    r"is it.{0,10}(rain|sun|cloud|snow)",
                    r"temperature",
                    r"forecast"
                ]
            },
            "places": {
                "keywords": ["restaurant", "museum", "hotel", "attraction", "cafe",
                           "bar", "park", "beach", "monument", "church", "temple",
                           "shopping", "market", "things to do", "visit", "see"],
                "patterns": [
                    r"(find|show|where|recommend).{0,20}(restaurant|museum|hotel|cafe|bar)",
                    r"places to (visit|see|go)",
                    r"attractions",
                    r"things to do",
                    r"what to (see|visit)"
                ]
            },
            "route": {
                "keywords": ["direction", "route", "how to get", "navigate", "distance",
                           "travel time", "get to", "from", "to", "transportation"],
                "patterns": [
                    r"how.{0,10}get.{0,10}(to|from)",
                    r"direction.{0,10}(to|from)",
                    r"route.{0,10}(to|from)",
                    r"distance.{0,10}between",
                    r"travel.{0,10}time"
                ]
            },
            "events": {
                "keywords": ["event", "festival", "concert", "show", "exhibition",
                           "performance", "happening", "activities", "tonight", "today"],
                "patterns": [
                    r"(events?|festivals?|concerts?|shows?)",
                    r"what.{0,10}happening",
                    r"things.{0,10}(tonight|today|tomorrow)",
                    r"local.{0,10}events?"
                ]
            },
            "currency": {
                "keywords": ["currency", "exchange", "rate", "convert", "money",
                           "dollar", "euro", "pound", "yen"],
                "patterns": [
                    r"exchange.{0,10}rate",
                    r"currency",
                    r"convert.{0,20}(dollar|euro|pound|yen)",
                    r"how much.{0,10}in"
                ]
            },
            "image": {
                "keywords": ["photo", "image", "picture", "view", "look like"],
                "patterns": [
                    r"(photo|image|picture).{0,10}of",
                    r"show.{0,10}(photo|image|picture)",
                    r"what.{0,10}look.{0,10}like"
                ]
            },
            "plan_day": {
                "keywords": ["plan", "itinerary", "day trip", "schedule", "suggest",
                           "recommend", "day", "morning", "afternoon", "evening"],
                "patterns": [
                    r"plan.{0,20}(day|trip|itinerary)",
                    r"(suggest|recommend).{0,20}itinerary",
                    r"what.{0,10}do.{0,10}(today|tomorrow)",
                    r"day.{0,10}trip"
                ]
            }
        }
    
    async def detect(self, query: str) -> str:
        """
        Detect intent from user query.
        
        Args:
            query: User's natural language query
            
        Returns:
            Detected intent name
        """
        query_lower = query.lower()
        scores = {}
        
        # Check each intent
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in intent_data["keywords"]:
                if keyword in query_lower:
                    score += 1.0
            
            # Check patterns
            for pattern in intent_data["patterns"]:
                if re.search(pattern, query_lower):
                    score += 2.0  # Patterns are more specific, so higher weight
            
            scores[intent_name] = score
        
        # Get the intent with highest score
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            if best_intent[1] > 0:  # If we have any match
                logger.debug(f"Intent scores: {scores}")
                logger.info(f"Detected intent: {best_intent[0]} (score: {best_intent[1]})")
                return best_intent[0]
        
        # Default intent
        return "places"  # Default to places search
    
    def extract_entities(self, query: str, intent: str) -> Dict[str, any]:
        """
        Extract entities from query based on intent.
        
        Args:
            query: User query
            intent: Detected intent
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract location mentions
        location_pattern = r"in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        location_match = re.search(location_pattern, query)
        if location_match:
            entities["location"] = location_match.group(1)
        
        # Extract time mentions
        time_keywords = {
            "today": "today",
            "tomorrow": "tomorrow",
            "tonight": "tonight",
            "this week": "week",
            "this weekend": "weekend"
        }
        for keyword, value in time_keywords.items():
            if keyword in query_lower:
                entities["time"] = value
                break
        
        # Extract distance/radius
        distance_pattern = r"(\d+)\s*(km|kilometer|mile|m|meter)"
        distance_match = re.search(distance_pattern, query_lower)
        if distance_match:
            entities["radius"] = {
                "value": int(distance_match.group(1)),
                "unit": distance_match.group(2)
            }
        
        # Intent-specific entity extraction
        if intent == "route":
            # Extract from/to locations
            from_pattern = r"from\s+([^to]+?)(?:\s+to|$)"
            to_pattern = r"to\s+([^from]+?)(?:\s+from|$)"
            
            from_match = re.search(from_pattern, query_lower)
            to_match = re.search(to_pattern, query_lower)
            
            if from_match:
                entities["from"] = from_match.group(1).strip()
            if to_match:
                entities["to"] = to_match.group(1).strip()
        
        elif intent == "currency":
            # Extract currency codes
            currency_pattern = r"\b([A-Z]{3})\b"
            currencies = re.findall(currency_pattern, query.upper())
            if currencies:
                entities["currencies"] = currencies
            
            # Extract amount
            amount_pattern = r"(\d+(?:\.\d+)?)"
            amount_match = re.search(amount_pattern, query)
            if amount_match:
                entities["amount"] = float(amount_match.group(1))
        
        elif intent == "places":
            # Extract place types
            place_types = ["restaurant", "museum", "hotel", "cafe", "bar", 
                          "park", "beach", "monument"]
            for place_type in place_types:
                if place_type in query_lower:
                    entities["place_type"] = place_type
                    break
        
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def get_intent_info(self, intent_name: str) -> Dict[str, any]:
        """
        Get detailed information about an intent.
        
        Args:
            intent_name: Name of the intent
            
        Returns:
            Intent information dictionary
        """
        if intent_name in self.intent_patterns:
            return {
                "name": intent_name,
                "keywords": self.intent_patterns[intent_name]["keywords"],
                "description": self._get_intent_description(intent_name)
            }
        return {
            "name": intent_name,
            "keywords": [],
            "description": "Unknown intent"
        }
    
    def _get_intent_description(self, intent: str) -> str:
        """Get human-readable description of intent."""
        descriptions = {
            "weather": "Get weather information and forecasts",
            "places": "Find attractions, restaurants, and points of interest",
            "route": "Get directions and navigation assistance",
            "events": "Discover local events and activities",
            "currency": "Check exchange rates and convert currencies",
            "image": "View photos and images of locations",
            "plan_day": "Create travel itineraries and day plans"
        }
        return descriptions.get(intent, "General travel assistance")
    
    async def detect_with_confidence(self, query: str) -> Intent:
        """
        Detect intent with confidence score.
        
        Args:
            query: User query
            
        Returns:
            Intent object with confidence score
        """
        query_lower = query.lower()
        scores = {}
        matched_keywords = {}
        
        # Calculate scores for each intent
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0.0
            keywords_found = []
            
            # Check keywords
            for keyword in intent_data["keywords"]:
                if keyword in query_lower:
                    score += 1.0
                    keywords_found.append(keyword)
            
            # Check patterns
            for pattern in intent_data["patterns"]:
                if re.search(pattern, query_lower):
                    score += 2.0
            
            scores[intent_name] = score
            matched_keywords[intent_name] = keywords_found
        
        # Get best intent
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            max_score = best_intent[1]
            
            # Calculate confidence (normalize to 0-1)
            confidence = min(max_score / 5.0, 1.0) if max_score > 0 else 0.0
            
            # Extract entities
            entities = self.extract_entities(query, best_intent[0])
            
            return Intent(
                name=best_intent[0] if max_score > 0 else "general",
                confidence=confidence,
                keywords=matched_keywords.get(best_intent[0], []),
                entities=entities
            )
        
        return Intent(
            name="general",
            confidence=0.0,
            keywords=[],
            entities={}
        )


# Export the detector class
__all__ = ["IntentDetector", "Intent"]