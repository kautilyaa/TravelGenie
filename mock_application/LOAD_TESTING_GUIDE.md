# Load Testing Guide for Mock Travel Genie

This guide explains how to run load tests on the Mock Travel Genie application across different platforms (AWS, Colab, Zaratan).

## Quick Start

### Option 1: Run All Load Tests (Recommended)

```bash
cd mock_application
python run_load_tests.py
```

This will run all load test types and generate comprehensive reports.

### Option 2: Run Individual Load Tests

```bash
# Concurrent users test
python load_tests/concurrent_users.py

# Sustained load test
python load_tests/sustained_load.py

# Stress test
python load_tests/stress_test.py
```

## Load Test Types

### 1. Concurrent Users Test

Simulates multiple users making requests simultaneously.

```python
from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator

orchestrator = MockOrchestrator()
scenarios = PlatformComparisonScenarios(orchestrator)

tester = LoadTester()
result = tester.run_concurrent_users(
    num_users=50,
    scenario_func=scenarios.scenario_5_simple_trip,
    duration_seconds=60,
    ramp_up_seconds=10
)

print(f"Throughput: {result['throughput_rps']:.2f} RPS")
print(f"Mean Latency: {result['mean_latency_ms']:.2f} ms")
print(f"P95 Latency: {result['p95_latency_ms']:.2f} ms")
```

### 2. Sustained Load Test

Maintains a constant requests-per-second (RPS) rate over time.

```python
tester = LoadTester()
result = tester.run_sustained_load(
    rps=10,  # 10 requests per second
    scenario_func=scenarios.scenario_6_complex_trip,
    duration_seconds=300,  # 5 minutes
    ramp_up_seconds=30
)
```

### 3. Stress Test

Gradually increases load until failure point.

```python
tester = LoadTester()
result = tester.run_stress_test(
    start_rps=1,
    max_rps=100,
    scenario_func=scenarios.scenario_7_full_workflow,
    ramp_up_seconds=60,
    hold_seconds=120
)
```

## Load Testing with Platform Comparison

### Step 1: Configure Platform

Edit `config/app_config.yaml`:

```yaml
platform: aws  # or "colab" or "zaratan"
platform_tag: aws-us-east-1
use_mock_llm: true
```

### Step 2: Run Load Tests

```python
from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector

# Initialize
orchestrator = MockOrchestrator()
scenarios = PlatformComparisonScenarios(orchestrator)
tester = LoadTester()
metrics_collector = get_metrics_collector(
    platform=orchestrator.platform,
    config_path="config/app_config.yaml"
)

# Run load test
result = tester.run_sustained_load(
    rps=10,
    scenario_func=scenarios.scenario_5_simple_trip,
    duration_seconds=300
)

# Save metrics
metrics_collector.save_metrics(f"metrics_{orchestrator.platform}.json")
```

### Step 3: Collect Metrics from All Platforms

1. **Run on AWS**: Set `platform: aws`, run tests, save `metrics_aws.json`
2. **Run on Colab**: Set `platform: colab`, run tests, save `metrics_colab.json`
3. **Run on Zaratan**: Set `platform: zaratan`, run tests, save `metrics_zaratan.json`

### Step 4: Generate Comparison Report

```python
from reporting.report_generator import ReportGenerator

metrics_files = [
    "metrics_aws.json",
    "metrics_colab.json",
    "metrics_zaratan.json"
]

generator = ReportGenerator(metrics_files)
generator.save_reports()  # Generates Markdown and HTML reports
```

## Configuration

Edit `config/load_test_config.yaml` to customize:

```yaml
concurrent_users:
  users: [1, 5, 10, 20, 50, 100]  # User counts to test
  duration_seconds: 60
  ramp_up_seconds: 10

sustained_load:
  rps: 10  # Target requests per second
  duration_seconds: 300  # 5 minutes
  ramp_up_seconds: 30

stress_test:
  start_rps: 1
  max_rps: 100
  ramp_up_seconds: 60
  hold_seconds: 120
```

## Test Scenarios

Use standardized scenarios from `scenarios/platform_comparison_scenarios.py`:

- `scenario_1_simple_flight_search()` - 1 tool call
- `scenario_2_hotel_search()` - 1 tool call
- `scenario_5_simple_trip()` - 2-3 tool calls
- `scenario_6_complex_trip()` - 4-5 tool calls
- `scenario_7_full_workflow()` - 5+ tool calls

## Metrics Collected

- **Latency**: Mean, P50, P95, P99 percentiles
- **Throughput**: Requests per second (RPS)
- **Reliability**: Success rate, error rate
- **Resource Usage**: CPU, memory (platform-specific)
- **Platform-Specific**: CloudWatch (AWS), SLURM (Zaratan), Colab metrics

## Example: Complete Load Test Workflow

```python
#!/usr/bin/env python3
"""Complete load testing workflow"""

from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector
import json

def run_platform_load_tests(platform: str):
    """Run load tests for a specific platform"""
    print(f"\n{'='*60}")
    print(f"Running load tests on {platform.upper()}")
    print(f"{'='*60}")
    
    # Initialize
    orchestrator = MockOrchestrator()
    orchestrator.platform = platform
    scenarios = PlatformComparisonScenarios(orchestrator)
    tester = LoadTester()
    metrics_collector = get_metrics_collector(platform=platform)
    
    # Test 1: Concurrent users
    print("\n1. Concurrent Users Test (50 users, 60s)")
    result1 = tester.run_concurrent_users(
        num_users=50,
        scenario_func=scenarios.scenario_5_simple_trip,
        duration_seconds=60
    )
    print(f"   Throughput: {result1['throughput_rps']:.2f} RPS")
    print(f"   P95 Latency: {result1['p95_latency_ms']:.2f} ms")
    
    # Test 2: Sustained load
    print("\n2. Sustained Load Test (10 RPS, 300s)")
    result2 = tester.run_sustained_load(
        rps=10,
        scenario_func=scenarios.scenario_6_complex_trip,
        duration_seconds=300
    )
    print(f"   Throughput: {result2['throughput_rps']:.2f} RPS")
    print(f"   P95 Latency: {result2['p95_latency_ms']:.2f} ms")
    
    # Save metrics
    metrics_file = f"metrics_{platform}.json"
    metrics_collector.save_metrics(metrics_file)
    print(f"\nMetrics saved to: {metrics_file}")
    
    return metrics_file

# Run on all platforms
if __name__ == "__main__":
    platforms = ["aws", "colab", "zaratan"]
    metrics_files = []
    
    for platform in platforms:
        try:
            metrics_file = run_platform_load_tests(platform)
            metrics_files.append(metrics_file)
        except Exception as e:
            print(f"Error testing {platform}: {e}")
    
    # Generate comparison report
    if metrics_files:
        from reporting.report_generator import ReportGenerator
        generator = ReportGenerator(metrics_files)
        generator.save_reports()
        print("\nComparison report generated!")
```

## Running Load Tests on Each Platform

### AWS EC2

```bash
# SSH into EC2 instance
ssh ec2-user@<EC2_IP>

# Run load tests
cd ~/mock_application
python run_load_tests.py

# Metrics will be saved to metrics_aws.json
```

### Google Colab

1. Upload `mock_application` to Colab
2. Set `platform: colab` in config
3. Run load test cells in notebook
4. Download `metrics_colab.json`

### Zaratan HPC

```bash
# SSH to Zaratan
ssh zaratan.umd.edu

# Submit load test job
cd ~/mock_application
sbatch load_test_job.sh

# Check results
cat metrics_zaratan.json
```

## Interpreting Results

### Good Performance Indicators

- **Latency P95 < 1000ms**: Fast response times
- **Success Rate > 99%**: High reliability
- **Throughput matches target**: System handles load
- **Low error rate < 1%**: Stable operation

### Warning Signs

- **Latency P95 > 5000ms**: System overloaded
- **Success Rate < 95%**: High failure rate
- **Throughput below target**: Capacity issues
- **High error rate > 5%**: System instability

## Troubleshooting

### High Latency

- Check resource usage (CPU, memory)
- Reduce concurrent users or RPS
- Check network latency
- Verify mock delays in config

### High Error Rate

- Check application logs
- Verify configuration
- Reduce load
- Check platform limits

### Low Throughput

- Increase concurrent workers
- Check platform resource limits
- Optimize scenario complexity
- Verify no bottlenecks

## Best Practices

1. **Start Small**: Begin with low load and gradually increase
2. **Use Standardized Scenarios**: Use `platform_comparison_scenarios.py`
3. **Collect Metrics**: Always save metrics for comparison
4. **Run Multiple Times**: Average results for accuracy
5. **Monitor Resources**: Watch CPU/memory during tests
6. **Document Results**: Save reports with timestamps

## Next Steps

After running load tests:

1. Collect metrics from all platforms
2. Generate comparison report: `python -m reporting.report_generator`
3. Analyze results and identify bottlenecks
4. Document findings in comparison report
5. Use insights to optimize deployment
