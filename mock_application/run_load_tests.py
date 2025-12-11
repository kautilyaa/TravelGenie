#!/usr/bin/env python3
"""
Unified Load Testing Script
Runs comprehensive load tests with platform comparison and metrics collection
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector


def run_load_test_suite(
    platform: str = None,
    test_types: List[str] = None,
    scenarios: List[str] = None
) -> Dict[str, Any]:
    """
    Run comprehensive load test suite
    
    Args:
        platform: Platform to test (aws, colab, zaratan, or None for auto-detect)
        test_types: List of test types to run (concurrent, sustained, stress)
        scenarios: List of scenario IDs to test
    """
    # Load config
    config_path = Path(__file__).parent / "config" / "app_config.yaml"
    with open(config_path, 'r') as f:
        app_config = yaml.safe_load(f)
    
    # Determine platform
    if platform is None:
        platform = app_config.get("platform", "local")
    
    print(f"\n{'='*70}")
    print(f"Load Testing Suite - Platform: {platform.upper()}")
    print(f"{'='*70}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize components
    orchestrator = MockOrchestrator(config_path=str(config_path))
    orchestrator.platform = platform
    orchestrator.platform_tag = app_config.get("platform_tag", f"{platform}-default")
    
    scenarios_obj = PlatformComparisonScenarios(orchestrator)
    tester = LoadTester()
    metrics_collector = get_metrics_collector(platform=platform, config_path=str(config_path))
    
    # Default test types
    if test_types is None:
        test_types = ["concurrent", "sustained", "stress"]
    
    # Default scenarios
    if scenarios is None:
        scenarios = ["simple_trip", "complex_trip", "full_workflow"]
    
    # Map scenario IDs to functions
    scenario_map = {
        "simple_flight": scenarios_obj.scenario_1_simple_flight_search,
        "hotel": scenarios_obj.scenario_2_hotel_search,
        "weather": scenarios_obj.scenario_3_weather_check,
        "currency": scenarios_obj.scenario_4_currency_conversion,
        "simple_trip": scenarios_obj.scenario_5_simple_trip,
        "complex_trip": scenarios_obj.scenario_6_complex_trip,
        "full_workflow": scenarios_obj.scenario_7_full_workflow,
        "events": scenarios_obj.scenario_8_event_search,
        "geocoding": scenarios_obj.scenario_9_geocoding,
        "multi_location": scenarios_obj.scenario_10_multi_location,
    }
    
    all_results = {}
    
    # Run tests
    for test_type in test_types:
        print(f"\n{'='*70}")
        print(f"Test Type: {test_type.upper()}")
        print(f"{'='*70}")
        
        test_results = {}
        
        for scenario_id in scenarios:
            if scenario_id not in scenario_map:
                print(f"  Warning: Unknown scenario '{scenario_id}', skipping...")
                continue
            
            scenario_func = scenario_map[scenario_id]
            print(f"\n  Scenario: {scenario_id}")
            print(f"  {'-'*60}")
            
            try:
                if test_type == "concurrent":
                    # Concurrent users test
                    result = tester.run_concurrent_users(
                        num_users=50,
                        scenario_func=scenario_func,
                        duration_seconds=60,
                        ramp_up_seconds=10
                    )
                    
                elif test_type == "sustained":
                    # Sustained load test
                    result = tester.run_sustained_load(
                        rps=10,
                        scenario_func=scenario_func,
                        duration_seconds=300,
                        ramp_up_seconds=30
                    )
                    
                elif test_type == "stress":
                    # Stress test
                    result = tester.run_stress_test(
                        start_rps=1,
                        max_rps=50,
                        scenario_func=scenario_func,
                        ramp_up_seconds=60,
                        hold_seconds=120
                    )
                    
                else:
                    print(f"    Unknown test type: {test_type}")
                    continue
                
                # Record metrics
                if isinstance(result, dict) and result.get("total_requests"):
                    metrics_collector.record_request_metrics(
                        request_id=f"{test_type}_{scenario_id}_{datetime.now().timestamp()}",
                        latency_ms=result.get("mean_latency_ms", 0),
                        success=result.get("success_rate", 0) > 0.95,
                        tool_calls=[]  # Load test results don't include individual tool calls
                    )
                
                # Display results
                print(f"    Total Requests: {result.get('total_requests', 0)}")
                print(f"    Success Rate: {result.get('success_rate', 0)*100:.1f}%")
                print(f"    Throughput: {result.get('throughput_rps', 0):.2f} RPS")
                print(f"    Mean Latency: {result.get('mean_latency_ms', 0):.2f} ms")
                print(f"    P95 Latency: {result.get('p95_latency_ms', 0):.2f} ms")
                print(f"    P99 Latency: {result.get('p99_latency_ms', 0):.2f} ms")
                
                test_results[scenario_id] = result
                
            except Exception as e:
                print(f"    Error: {e}")
                test_results[scenario_id] = {"error": str(e)}
        
        all_results[test_type] = test_results
    
    # Save metrics
    metrics_file = f"metrics_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    metrics_collector.save_metrics(metrics_file)
    print(f"\n{'='*70}")
    print(f"Metrics saved to: {metrics_file}")
    print(f"{'='*70}")
    
    # Save test results
    results_file = f"load_test_results_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "test_types": test_types,
            "scenarios": scenarios,
            "results": all_results
        }, f, indent=2)
    print(f"Test results saved to: {results_file}")
    
    return {
        "platform": platform,
        "metrics_file": metrics_file,
        "results_file": results_file,
        "results": all_results
    }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run load tests for Mock Travel Genie")
    parser.add_argument(
        "--platform",
        choices=["aws", "colab", "zaratan", "local"],
        default=None,
        help="Platform to test (default: auto-detect from config)"
    )
    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["concurrent", "sustained", "stress"],
        default=None,
        help="Test types to run (default: all)"
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=["simple_flight", "hotel", "weather", "currency", "simple_trip",
                 "complex_trip", "full_workflow", "events", "geocoding", "multi_location"],
        default=None,
        help="Scenarios to test (default: simple_trip, complex_trip, full_workflow)"
    )
    
    args = parser.parse_args()
    
    try:
        results = run_load_test_suite(
            platform=args.platform,
            test_types=args.test_types,
            scenarios=args.scenarios
        )
        
        print(f"\n{'='*70}")
        print("Load Testing Complete!")
        print(f"{'='*70}")
        print(f"Platform: {results['platform']}")
        print(f"Metrics: {results['metrics_file']}")
        print(f"Results: {results['results_file']}")
        print()
        print("Next steps:")
        print("1. Run tests on other platforms (AWS, Colab, Zaratan)")
        print("2. Collect all metrics files")
        print("3. Generate comparison report:")
        print("   python -c \"from reporting.report_generator import ReportGenerator; "
              "ReportGenerator(['metrics_aws.json', 'metrics_colab.json', 'metrics_zaratan.json']).save_reports()\"")
        
    except KeyboardInterrupt:
        print("\n\nLoad testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running load tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
