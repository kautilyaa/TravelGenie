"""
Simple Trip Scenario
Basic flight + hotel search scenario
"""

def simple_trip_scenario(orchestrator):
    """Simple trip planning scenario"""
    query = "I want to plan a trip from IAD to JFK on December 17, 2025. Find flights and hotels in New York."
    
    result = orchestrator.process_query(query)
    return result
