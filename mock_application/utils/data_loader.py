"""
Data Loader
Loads cached JSON data from existing data directories
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Optional, Any

class DataLoader:
    """Loads cached JSON data for mock responses"""
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            # Default to project root
            self.base_path = Path(__file__).parent.parent.parent
        else:
            self.base_path = Path(base_path)
        
        self._cache = {}
    
    def load_flight_data(self, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all flight JSON files"""
        if data_dir is None:
            data_dir = self.base_path / "flights"
        else:
            data_dir = Path(data_dir)
        
        if not data_dir.exists():
            return []
        
        files = glob.glob(str(data_dir / "*.json"))
        data = []
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return data
    
    def load_hotel_data(self, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all hotel JSON files"""
        if data_dir is None:
            data_dir = self.base_path / "hotels"
        else:
            data_dir = Path(data_dir)
        
        if not data_dir.exists():
            return []
        
        files = glob.glob(str(data_dir / "*.json"))
        data = []
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return data
    
    def load_event_data(self, data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all event JSON files"""
        if data_dir is None:
            data_dir = self.base_path / "events"
        else:
            data_dir = Path(data_dir)
        
        if not data_dir.exists():
            return []
        
        files = glob.glob(str(data_dir / "*.json"))
        data = []
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return data
    
    def find_matching_flight(
        self,
        departure: Optional[str] = None,
        arrival: Optional[str] = None,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find flight data matching criteria"""
        flights = self.load_flight_data()
        
        for flight in flights:
            metadata = flight.get("search_metadata", {})
            if departure and metadata.get("departure") != departure:
                continue
            if arrival and metadata.get("arrival") != arrival:
                continue
            if date and metadata.get("outbound_date") != date:
                continue
            return flight
        
        # Return first available if no match
        return flights[0] if flights else None
    
    def find_matching_hotel(
        self,
        location: Optional[str] = None,
        check_in: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find hotel data matching criteria"""
        hotels = self.load_hotel_data()
        
        location_lower = location.lower() if location else None
        
        for hotel in hotels:
            metadata = hotel.get("search_metadata", {})
            search_location = metadata.get("location", "").lower()
            
            if location and location_lower not in search_location and search_location not in location_lower:
                continue
            if check_in and metadata.get("check_in_date") != check_in:
                continue
            return hotel
        
        # Return first available if no match
        return hotels[0] if hotels else None
    
    def find_matching_event(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find event data matching criteria"""
        events = self.load_event_data()
        
        query_lower = query.lower() if query else None
        location_lower = location.lower() if location else None
        
        for event in events:
            metadata = event.get("search_metadata", {})
            search_query = metadata.get("query", "").lower()
            search_location = metadata.get("location", "").lower()
            
            if query and query_lower not in search_query and search_query not in query_lower:
                continue
            if location and location_lower and location_lower not in search_location:
                continue
            return event
        
        # Return first available if no match
        return events[0] if events else None
