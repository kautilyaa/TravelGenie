# How to Run Load Tests

## Quick Answer

**Run all load tests:**
```bash
cd mock_application
python run_load_tests.py
```

**Run specific test type:**
```bash
python load_tests/concurrent_users.py    # Concurrent users
python load_tests/sustained_load.py      # Sustained load
python load_tests/stress_test.py         # Stress test
```

## Detailed Guide

### 1. Basic Load Test (Single Platform)

```bash
# Set platform in config/app_config.yaml
# platform: aws  (or colab, zaratan)

# Run all tests
python run_load_tests.py

# Or run specific test
python load_tests/concurrent_users.py
```

### 2. Load Test for Platform Comparison

**Step 1:** Configure for AWS
```yaml
# config/app_config.yaml
platform: aws
platform_tag: aws-us-east-1
```

**Step 2:** Run tests on AWS
```bash
python run_load_tests.py --platform aws
# Saves: metrics_aws_YYYYMMDD_HHMMSS.json
```

**Step 3:** Configure for Colab
```yaml
platform: colab
platform_tag: colab-free-tier
```

**Step 4:** Run tests on Colab
```bash
python run_load_tests.py --platform colab
# Saves: metrics_colab_YYYYMMDD_HHMMSS.json
```

**Step 5:** Configure for Zaratan
```yaml
platform: zaratan
platform_tag: zaratan-gpu
```

**Step 6:** Run tests on Zaratan
```bash
python run_load_tests.py --platform zaratan
# Saves: metrics_zaratan_YYYYMMDD_HHMMSS.json
```

**Step 7:** Generate comparison report
```python
from reporting.report_generator import ReportGenerator

generator = ReportGenerator([
    "metrics_aws_20250115_120000.json",
    "metrics_colab_20250115_130000.json",
    "metrics_zaratan_20250115_140000.json"
])
generator.save_reports()  # Creates Markdown and HTML reports
```

## Test Types Explained

### Concurrent Users Test
- **What it does**: Simulates N users making requests simultaneously
- **Default**: 50 users for 60 seconds
- **Use case**: Test how system handles concurrent load
- **Command**: `python load_tests/concurrent_users.py`

### Sustained Load Test
- **What it does**: Maintains constant RPS over time
- **Default**: 10 RPS for 5 minutes (300 seconds)
- **Use case**: Test system stability under constant load
- **Command**: `python load_tests/sustained_load.py`

### Stress Test
- **What it does**: Gradually increases load until failure
- **Default**: 1-100 RPS ramp-up over 60 seconds, hold for 120 seconds
- **Use case**: Find system limits and failure points
- **Command**: `python load_tests/stress_test.py`

## Customizing Tests

### Edit Configuration

Edit `config/load_test_config.yaml`:

```yaml
concurrent_users:
  users: [10, 25, 50, 100]  # User counts to test
  duration_seconds: 120      # Test duration
  ramp_up_seconds: 20        # Ramp-up time

sustained_load:
  rps: 20                    # Target RPS
  duration_seconds: 600      # 10 minutes
  ramp_up_seconds: 60

stress_test:
  start_rps: 5
  max_rps: 200
  ramp_up_seconds: 120
  hold_seconds: 180
```

### Use Command Line Options

```bash
# Test specific platform
python run_load_tests.py --platform aws

# Run only concurrent and sustained tests
python run_load_tests.py --test-types concurrent sustained

# Test specific scenarios
python run_load_tests.py --scenarios simple_trip complex_trip full_workflow
```

## Understanding Results

### Key Metrics

- **Throughput (RPS)**: Requests per second - higher is better
- **Mean Latency**: Average response time - lower is better
- **P95 Latency**: 95th percentile - most requests complete faster
- **P99 Latency**: 99th percentile - worst-case performance
- **Success Rate**: Percentage of successful requests - should be >99%
- **Error Rate**: Percentage of failed requests - should be <1%

### Good Performance Indicators

- **P95 Latency < 1000ms**: Fast responses
- **Success Rate > 99%**: High reliability  
- **Throughput matches target**: System handles load
- **Error Rate < 1%**: Stable operation

### Warning Signs

- **P95 Latency > 5000ms**: System overloaded
- **Success Rate < 95%**: High failure rate
- **Throughput below target**: Capacity issues
- **Error Rate > 5%**: System instability

## Example Workflow

```bash
# 1. Configure for AWS
# Edit config/app_config.yaml: platform: aws

# 2. Run load tests
python run_load_tests.py --platform aws

# 3. Check results
cat metrics_aws_*.json | jq '.summary'

# 4. Repeat for other platforms
# Edit config: platform: colab
python run_load_tests.py --platform colab

# Edit config: platform: zaratan  
python run_load_tests.py --platform zaratan

# 5. Generate comparison report
python -c "
from reporting.report_generator import ReportGenerator
import glob
files = glob.glob('metrics_*.json')
generator = ReportGenerator(files)
generator.save_reports()
print('Reports saved to reports/ directory')
"
```

## Files Generated

After running load tests, you'll get:

- `metrics_<platform>_<timestamp>.json` - Platform metrics
- `load_test_results_<platform>_<timestamp>.json` - Test results
- `reports/comparison_report_<timestamp>.md` - Markdown report
- `reports/comparison_report_<timestamp>.html` - HTML report

## Need Help?

- See `LOAD_TESTING_GUIDE.md` for detailed documentation
- See `QUICK_START_LOAD_TESTING.md` for quick reference
- Check `config/load_test_config.yaml` for configuration options
