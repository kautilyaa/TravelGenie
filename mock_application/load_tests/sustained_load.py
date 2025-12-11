"""
Sustained Load Test
Constant RPS over time period
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
    """Run sustained load test"""
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
    config = tester.config.get("sustained_load", {})
    rps = config.get("rps", 10)
    duration = config.get("duration_seconds", 300)
    ramp_up = config.get("ramp_up_seconds", 30)
    
    print("=" * 60)
    print(f"Sustained Load Test - Platform: {platform.upper()}")
    print("=" * 60)
    print(f"Target RPS: {rps}")
    print(f"Duration: {duration} seconds")
    print(f"Ramp-up: {ramp_up} seconds")
    
    # Run test
    result = tester.run_sustained_load(
        rps=rps,
        scenario_func=scenarios.scenario_6_complex_trip,
        duration_seconds=duration,
        ramp_up_seconds=ramp_up
    )
    
    print("\nResults:")
    print(f"  Total requests: {result['total_requests']}")
    print(f"  Success rate: {result['success_rate']*100:.1f}%")
    print(f"  Mean latency: {result['mean_latency_ms']:.2f} ms")
    print(f"  P95 latency: {result['p95_latency_ms']:.2f} ms")
    print(f"  P99 latency: {result['p99_latency_ms']:.2f} ms")
    print(f"  Throughput: {result['throughput_rps']:.2f} RPS")
    print(f"  Error rate: {result['error_rate']*100:.1f}%")
    
    # Record metrics
    if result.get("total_requests"):
        metrics_collector.record_request_metrics(
            request_id=f"sustained_{rps}rps_{datetime.now().timestamp()}",
            latency_ms=result.get("mean_latency_ms", 0),
            success=result.get("success_rate", 0) > 0.95,
            tool_calls=[]
        )
    
    # Save metrics
    metrics_file = f"metrics_{platform}_sustained_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    metrics_collector.save_metrics(metrics_file)
    print(f"\nMetrics saved to: {metrics_file}")
    
    # Save results
    results_file = f"sustained_load_results_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()
