"""
Budget Planning Scenario
Full workflow with budget constraints and currency conversion
"""

def budget_planning_scenario(orchestrator):
    """Budget planning scenario with currency conversion"""
    query = """Plan a trip from Washington DC to Paris, France from March 15-22, 2025 
    for 2 people. Find flights and hotels. My budget is $3000 USD. Convert all prices to USD."""
    
    result = orchestrator.process_query(query)
    return result
