"""
Complex Trip Scenario
Multi-step scenario with events, weather, and currency conversion
"""

def complex_trip_scenario(orchestrator):
    """Complex multi-step trip planning scenario"""
    query = """I am planning a trip to Banff and Jasper in Alberta from Reston, Virginia 
    during June 7th 2025 to June 14th 2025. Find flights, hotels and events that are 
    happening in Banff, Alberta. We like to hike, go sight-seeing, dining, and going to museums. 
    My budget is $5000 USD. Make sure to convert cost from Canadian dollars to USD before presenting."""
    
    result = orchestrator.process_query(query)
    return result
