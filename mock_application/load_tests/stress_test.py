"""
Stress Test
Gradually increase load until failure
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector

def main():
    """Run stress test"""
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "app_config.yaml"
    with open(config_path, 'r') as f:
        app_config = yaml.safe_load(f)
    
    platform = app_config.get("platform", "local")
    
    # Initialize
    orchestrator = MockOrchestrator(config_path=str(config_path))
    orchestrator.platform = platform
    scenarios = PlatformComparisonScenarios(orchestrator)
    tester = LoadTester()
    metrics_collector = get_metrics_collector(platform=platform, config_path=str(config_path))
    
    # Get configuration
    config = tester.config.get("stress_test", {})
    start_rps = config.get("start_rps", 1)
    max_rps = config.get("max_rps", 100)
    ramp_up = config.get("ramp_up_seconds", 60)
    hold = config.get("hold_seconds", 120)
    
    print("=" * 60)
    print(f"Stress Test - Platform: {platform.upper()}")
    print("=" * 60)
    print(f"Start RPS: {start_rps}")
    print(f"Max RPS: {max_rps}")
    print(f"Ramp-up: {ramp_up} seconds")
    print(f"Hold: {hold} seconds")
    
    # Run test
    result = tester.run_stress_test(
        start_rps=start_rps,
        max_rps=max_rps,
        scenario_func=scenarios.scenario_7_full_workflow,
        ramp_up_seconds=ramp_up,
        hold_seconds=hold
    )
    
    print("\nResults by RPS level:")
    for rps in result.get("rps_levels", [])[:10]:  # Show first 10
        analysis = result["rps_analysis"].get(rps, {})
        print(f"\n  RPS {rps}:")
        print(f"    Success rate: {analysis.get('success_rate', 0)*100:.1f}%")
        print(f"    Mean latency: {analysis.get('mean_latency_ms', 0):.2f} ms")
        print(f"    P95 latency: {analysis.get('p95_latency_ms', 0):.2f} ms")
        print(f"    Error rate: {analysis.get('error_rate', 0)*100:.1f}%")
    
    # Find failure point
    failure_rps = None
    for rps in sorted(result.get("rps_levels", []), reverse=True):
        analysis = result["rps_analysis"].get(rps, {})
        if analysis.get("error_rate", 0) > 0.05:  # 5% error rate threshold
            failure_rps = rps
            break
    
    if failure_rps:
        print(f"\nFailure point detected at: {failure_rps} RPS")
    else:
        print("\nNo failure point detected within tested range")
    
    # Record metrics
    if result.get("overall"):
        overall = result["overall"]
        metrics_collector.record_request_metrics(
            request_id=f"stress_test_{datetime.now().timestamp()}",
            latency_ms=overall.get("mean_latency_ms", 0),
            success=overall.get("success_rate", 0) > 0.95,
            tool_calls=[]
        )
    
    # Save metrics
    metrics_file = f"metrics_{platform}_stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    metrics_collector.save_metrics(metrics_file)
    print(f"\nMetrics saved to: {metrics_file}")
    
    # Save results
    results_file = f"stress_test_results_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()
