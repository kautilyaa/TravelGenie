"""
Platform Comparison Scenarios
Standardized test scenarios for fair comparison across platforms (AWS, Colab, Zaratan)
"""

from typing import List, Dict, Any, Callable, Optional
from mock_orchestrator import MockOrchestrator


class PlatformComparisonScenarios:
    """Standardized scenarios for platform comparison"""
    
    def __init__(self, orchestrator: MockOrchestrator):
        self.orchestrator = orchestrator
    
    def scenario_1_simple_flight_search(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 1: Simple flight search (1 tool call)"""
        query = "Find flights from IAD to JFK on 2025-12-17"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_2_hotel_search(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 2: Hotel search (1 tool call)"""
        query = "Search for hotels in Banff, Alberta from 2025-06-07 to 2025-06-14"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_3_weather_check(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 3: Weather forecast (1 tool call)"""
        query = "What's the weather forecast for New York City?"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_4_currency_conversion(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 4: Currency conversion (1 tool call)"""
        query = "Convert $5000 USD to CAD"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_5_simple_trip(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 5: Simple trip planning (2-3 tool calls)"""
        query = "I want to plan a trip from IAD to JFK on December 17, 2025. Find flights and hotels in New York."
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_6_complex_trip(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 6: Complex trip planning (4-5 tool calls)"""
        query = "Plan a trip to Banff, Alberta from Reston, Virginia for June 7-14, 2025. Find flights, hotels, events, and weather forecast."
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_7_full_workflow(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 7: Full workflow with currency (5+ tool calls)"""
        query = "I'm planning a trip to Banff, Alberta from Reston, Virginia during June 7th 2025 to June 14th 2025. Find flights, hotels and events. My budget is $5000 USD. Convert costs from Canadian dollars to USD."
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_8_event_search(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 8: Event search (1-2 tool calls)"""
        query = "Find events and things to do in Banff, Alberta. I like hiking, sight-seeing, and dining."
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_9_geocoding(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 9: Geocoding (1 tool call)"""
        query = "Get coordinates for Banff, Alberta"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def scenario_10_multi_location(self, orchestrator: Optional[MockOrchestrator] = None) -> Dict[str, Any]:
        """Scenario 10: Multi-location query (3+ tool calls)"""
        query = "Compare flights from IAD to JFK and from LAX to SFO on 2025-12-17"
        orch = orchestrator if orchestrator is not None else self.orchestrator
        return orch.process_query(query)
    
    def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """Run all scenarios and return results"""
        scenarios = [
            ("Simple Flight Search", self.scenario_1_simple_flight_search),
            ("Hotel Search", self.scenario_2_hotel_search),
            ("Weather Check", self.scenario_3_weather_check),
            ("Currency Conversion", self.scenario_4_currency_conversion),
            ("Simple Trip", self.scenario_5_simple_trip),
            ("Complex Trip", self.scenario_6_complex_trip),
            ("Full Workflow", self.scenario_7_full_workflow),
            ("Event Search", self.scenario_8_event_search),
            ("Geocoding", self.scenario_9_geocoding),
            ("Multi-Location", self.scenario_10_multi_location),
        ]
        
        results = []
        for name, scenario_func in scenarios:
            try:
                result = scenario_func()
                result["scenario_name"] = name
                results.append(result)
            except Exception as e:
                results.append({
                    "scenario_name": name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def run_scenario_suite(self, scenario_names: List[str] = None) -> List[Dict[str, Any]]:
        """Run a specific set of scenarios"""
        if scenario_names is None:
            return self.run_all_scenarios()
        
        scenario_map = {
            "simple_flight": self.scenario_1_simple_flight_search,
            "hotel": self.scenario_2_hotel_search,
            "weather": self.scenario_3_weather_check,
            "currency": self.scenario_4_currency_conversion,
            "simple_trip": self.scenario_5_simple_trip,
            "complex_trip": self.scenario_6_complex_trip,
            "full_workflow": self.scenario_7_full_workflow,
            "events": self.scenario_8_event_search,
            "geocoding": self.scenario_9_geocoding,
            "multi_location": self.scenario_10_multi_location,
        }
        
        results = []
        for name in scenario_names:
            if name in scenario_map:
                try:
                    result = scenario_map[name]()
                    result["scenario_name"] = name
                    results.append(result)
                except Exception as e:
                    results.append({
                        "scenario_name": name,
                        "success": False,
                        "error": str(e)
                    })
        
        return results


def get_standard_scenarios() -> List[Dict[str, Any]]:
    """Get list of standard scenarios with metadata"""
    return [
        {
            "id": "simple_flight",
            "name": "Simple Flight Search",
            "description": "Single flight search query",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "hotel",
            "name": "Hotel Search",
            "description": "Single hotel search query",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "weather",
            "name": "Weather Check",
            "description": "Single weather forecast query",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "currency",
            "name": "Currency Conversion",
            "description": "Single currency conversion query",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "simple_trip",
            "name": "Simple Trip Planning",
            "description": "Flight + hotel search",
            "expected_tools": 2,
            "complexity": "medium"
        },
        {
            "id": "complex_trip",
            "name": "Complex Trip Planning",
            "description": "Multiple tool calls (flights, hotels, events, weather)",
            "expected_tools": 4,
            "complexity": "high"
        },
        {
            "id": "full_workflow",
            "name": "Full Workflow",
            "description": "Complete trip planning with currency conversion",
            "expected_tools": 5,
            "complexity": "high"
        },
        {
            "id": "events",
            "name": "Event Search",
            "description": "Event and activity search",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "geocoding",
            "name": "Geocoding",
            "description": "Location to coordinates conversion",
            "expected_tools": 1,
            "complexity": "low"
        },
        {
            "id": "multi_location",
            "name": "Multi-Location Query",
            "description": "Multiple location comparisons",
            "expected_tools": 3,
            "complexity": "medium"
        }
    ]
