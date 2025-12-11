# Quick Start: Load Testing

## Run All Load Tests (Easiest)

```bash
cd mock_application
python run_load_tests.py
```

This runs all test types (concurrent, sustained, stress) with default scenarios.

## Run Specific Test Types

```bash
# Concurrent users test (50 users, 60 seconds)
python load_tests/concurrent_users.py

# Sustained load test (10 RPS, 5 minutes)
python load_tests/sustained_load.py

# Stress test (1-100 RPS ramp-up)
python load_tests/stress_test.py
```

## Run with Custom Options

```bash
# Test specific platform
python run_load_tests.py --platform aws

# Run only concurrent and sustained tests
python run_load_tests.py --test-types concurrent sustained

# Test specific scenarios
python run_load_tests.py --scenarios simple_trip complex_trip
```

## Load Testing Workflow for Platform Comparison

### Step 1: Configure Platform

Edit `config/app_config.yaml`:
```yaml
platform: aws  # Change to "colab" or "zaratan" for other platforms
platform_tag: aws-us-east-1
use_mock_llm: true
```

### Step 2: Run Load Tests

```bash
python run_load_tests.py --platform aws
```

This will:
- Run concurrent users test (50 users, 60s)
- Run sustained load test (10 RPS, 300s)
- Run stress test (1-50 RPS)
- Save metrics to `metrics_aws_YYYYMMDD_HHMMSS.json`
- Save results to `load_test_results_aws_YYYYMMDD_HHMMSS.json`

### Step 3: Repeat for Other Platforms

1. Change `platform: colab` in config
2. Run: `python run_load_tests.py --platform colab`
3. Change `platform: zaratan` in config
4. Run: `python run_load_tests.py --platform zaratan`

### Step 4: Generate Comparison Report

```python
from reporting.report_generator import ReportGenerator

metrics_files = [
    "metrics_aws_20250101_120000.json",
    "metrics_colab_20250101_130000.json",
    "metrics_zaratan_20250101_140000.json"
]

generator = ReportGenerator(metrics_files)
generator.save_reports()
```

Reports will be saved to `reports/` directory.

## Test Scenarios Available

- `simple_flight` - Single flight search
- `hotel` - Single hotel search
- `weather` - Weather forecast
- `currency` - Currency conversion
- `simple_trip` - Flight + hotel (2-3 tools)
- `complex_trip` - Full trip planning (4-5 tools)
- `full_workflow` - Complete workflow with currency (5+ tools)

## Configuration

Edit `config/load_test_config.yaml` to customize:

```yaml
concurrent_users:
  users: [1, 5, 10, 20, 50, 100]  # User counts
  duration_seconds: 60

sustained_load:
  rps: 10  # Requests per second
  duration_seconds: 300  # 5 minutes

stress_test:
  start_rps: 1
  max_rps: 100
  ramp_up_seconds: 60
  hold_seconds: 120
```

## What Gets Measured

- **Latency**: Mean, P50, P95, P99 percentiles (ms)
- **Throughput**: Requests per second (RPS)
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Percentage of failed requests
- **Resource Usage**: CPU, memory (platform-specific)

## Example Output

```
======================================================================
Load Testing Suite - Platform: AWS
======================================================================
Timestamp: 2025-01-15 14:30:00

======================================================================
Test Type: CONCURRENT
======================================================================

  Scenario: simple_trip
  ------------------------------------------------------------
    Total Requests: 1250
    Success Rate: 99.2%
    Throughput: 20.83 RPS
    Mean Latency: 245.32 ms
    P95 Latency: 512.45 ms
    P99 Latency: 789.12 ms

Metrics saved to: metrics_aws_20250115_143000.json
Results saved to: load_test_results_aws_20250115_143000.json
```

## Tips

1. **Start small**: Begin with low load and increase gradually
2. **Run multiple times**: Average results for better accuracy
3. **Monitor resources**: Watch CPU/memory during tests
4. **Save metrics**: Always save metrics files for comparison
5. **Use same scenarios**: Use standardized scenarios for fair comparison

## Troubleshooting

**High latency?**
- Reduce concurrent users or RPS
- Check resource usage
- Verify mock delays in config

**High error rate?**
- Check application logs
- Reduce load
- Verify configuration

**Low throughput?**
- Increase concurrent workers
- Check platform limits
- Optimize scenario complexity
