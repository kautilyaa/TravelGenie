# Mock Travel Genie - Fully Mocked Application

A fully mocked Travel Genie application that works **without any API keys**. The application can be deployed on AWS EC2, Google Colab, and Zaratan HPC for platform comparison and performance testing.

## Overview

This mock application provides:

- **Mock LLM Client**: Intelligent query parsing and tool call generation (no API keys needed!)
- **Mock Orchestrator**: Simulates the application's decision-making flow
- **Mock MCP Servers**: Returns cached JSON responses with configurable delays
- **Platform Comparison**: Deploy on AWS, Colab, or Zaratan and compare performance
- **Performance Monitoring**: Comprehensive metrics collection with platform-specific adapters
- **Report Generation**: Automatic Markdown and HTML comparison reports
- **Load Testing**: Concurrent users, sustained load, and stress testing

## Quick Start

### Option 1: Run with Mock LLM (No API Keys Required!)

```python
from mock_orchestrator import MockOrchestrator

orchestrator = MockOrchestrator()  # Uses mock LLM by default
result = orchestrator.process_query("Find flights from IAD to JFK on Dec 17, 2025")

print(f"Response: {result['response']}")
print(f"Latency: {result['latency_ms']} ms")
print(f"Tool calls: {result['tool_calls']}")
```

### Option 2: Run Streamlit App

```bash
streamlit run travel_genie_mock.py
```

### Option 3: Use Real Llama Endpoint

Edit `config/app_config.yaml`:

```yaml
use_mock_llm: false
llama_endpoint: "http://your-ec2-instance:8000"  # or Colab URL
```

### 3. Run Load Tests

```bash
# Concurrent users test
python load_tests/concurrent_users.py

# Sustained load test
python load_tests/sustained_load.py

# Stress test
python load_tests/stress_test.py
```

## Architecture

### Components

1. **MockOrchestrator** (`mock_orchestrator.py`)
   - Simulates the orchestrator's decision-making flow
   - Makes tool calls to mock MCP servers
   - Communicates with external Llama endpoint
   - Tracks timing for each step

2. **MockMCPServers** (`mock_mcp_servers.py`)
   - Returns cached JSON responses from existing data files
   - Simulates realistic response times
   - Supports all MCP tools

3. **LlamaClient** (`llama_client.py`)
   - HTTP client for external Llama endpoint
   - Network latency measurement
   - Retry logic and error handling

4. **PerformanceMonitor** (`performance_monitor.py`)
   - Collects comprehensive metrics
   - Tracks latency breakdowns
   - Provides detailed analysis

5. **LoadTester** (`load_tester.py`)
   - Concurrent user simulation
   - Sustained load testing
   - Stress testing with gradual load increase

## Performance Metrics

The system tracks:

- **End-to-end latency**: Query → Response time
- **Network latency**: Round-trip time to Llama endpoint
- **MCP call latency**: Per-tool execution time
- **Orchestration overhead**: Decision-making time
- **Token usage**: Estimated costs
- **Error rates**: Success/failure rates
- **Throughput**: Requests per second

## Load Testing

### Concurrent Users Test

Simulates N users making requests simultaneously:

```python
from load_tester import LoadTester
from scenarios.simple_trip import simple_trip_scenario

tester = LoadTester()
result = tester.run_concurrent_users(
    num_users=50,
    scenario_func=simple_trip_scenario,
    duration_seconds=60
)
```

### Sustained Load Test

Maintains constant RPS over time:

```python
result = tester.run_sustained_load(
    rps=10,
    scenario_func=simple_trip_scenario,
    duration_seconds=300
)
```

### Stress Test

Gradually increases load until failure:

```python
result = tester.run_stress_test(
    start_rps=1,
    max_rps=100,
    scenario_func=simple_trip_scenario,
    ramp_up_seconds=60,
    hold_seconds=120
)
```

## Test Scenarios

Predefined scenarios in `scenarios/`:

- **simple_trip.py**: Basic flight + hotel search
- **complex_trip.py**: Multi-step with events, weather, currency
- **budget_planning.py**: Full workflow with budget constraints

## Configuration

### Application Config (`config/app_config.yaml`)

- `llama_endpoint`: External Llama endpoint URL
- `mcp_response_delay_ms`: Simulated MCP response delay
- `enable_network_monitoring`: Enable detailed network metrics
- `max_turns`: Maximum conversation turns
- `max_tools_per_turn`: Maximum tools per turn

### Load Test Config (`config/load_test_config.yaml`)

- `concurrent_users`: User counts and duration
- `sustained_load`: RPS and duration
- `stress_test`: Ramp-up parameters

## Results and Reports

Results are saved to `results/` directory:

- **JSON reports**: Machine-readable metrics
- **HTML reports**: Visual performance dashboards
- **CSV exports**: For analysis in spreadsheet tools

## Network Latency Measurement

The system measures:

- DNS lookup time
- Connection establishment time
- Request/response time
- Total round-trip time
- Geographic latency (if testing from different regions)

## Usage Examples

### Basic Performance Test

```python
from mock_orchestrator import MockOrchestrator

orchestrator = MockOrchestrator()

# Process a query
result = orchestrator.process_query("Find hotels in New York")

# Get metrics
metrics = orchestrator.get_metrics()
print(f"Total requests: {metrics['request_metrics']['total_requests']}")
print(f"Mean latency: {metrics['latency_stats']['llama_api_call']['mean']} ms")

# Get detailed analysis
analysis = orchestrator.get_detailed_analysis()
print(f"Bottlenecks: {analysis['latency_breakdown']['bottlenecks']}")
print(f"Recommendations: {analysis['recommendations']}")
```

### Custom Load Test

```python
from load_tester import LoadTester

def custom_scenario(orchestrator):
    return orchestrator.process_query("Your custom query here")

tester = LoadTester()
result = tester.run_concurrent_users(
    num_users=20,
    scenario_func=custom_scenario,
    duration_seconds=120
)
```

## Requirements

- Python 3.12+
- requests
- pyyaml
- See `requirements.txt` for full list

## Integration

- Uses cached JSON data from `../flights/`, `../hotels/`, `../events/`
- Communicates with external Llama endpoint (configured via config)
- Can integrate with `baseline_tests/tracking` for metrics storage
- Results can be compared with baseline_tests results

## Troubleshooting

### Llama Endpoint Not Accessible

- Verify endpoint URL in `config/app_config.yaml`
- Check network connectivity: `curl http://your-endpoint/health`
- Verify firewall rules allow connections

### High Latency

- Check network latency to Llama endpoint
- Verify Llama endpoint is not overloaded
- Reduce `mcp_response_delay_ms` in config for faster MCP responses

### Load Test Failures

- Reduce concurrent users or RPS
- Increase timeout values
- Check Llama endpoint capacity

## Platform Deployment

### AWS EC2

```bash
cd deployments/aws
./deploy_aws.sh
```

See [deployments/aws/README.md](deployments/aws/README.md) for detailed instructions.

### Google Colab

1. Open `deployments/colab/colab_setup.ipynb` in Google Colab
2. Upload the `mock_application` directory
3. Run all cells

See [deployments/colab/README.md](deployments/colab/README.md) for detailed instructions.

### Zaratan HPC

```bash
cd deployments/zaratan
bash zaratan_setup.sh
sbatch slurm_job.sh
```

See [deployments/zaratan/README.md](deployments/zaratan/README.md) for detailed instructions.

## Platform Comparison and Reporting

### Running Comparison Tests

```python
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator

orchestrator = MockOrchestrator()
scenarios = PlatformComparisonScenarios(orchestrator)

# Run all scenarios
results = scenarios.run_all_scenarios()

# Or run specific scenarios
results = scenarios.run_scenario_suite(["simple_flight", "complex_trip"])
```

### Generating Comparison Reports

```python
from reporting.report_generator import ReportGenerator

# Collect metrics from all platforms
metrics_files = [
    "metrics_aws.json",
    "metrics_colab.json",
    "metrics_zaratan.json"
]

generator = ReportGenerator(metrics_files)
generator.save_reports()  # Generates both Markdown and HTML reports
```

Reports will be saved to the `reports/` directory with timestamps.

## Why AWS is Better for Production

See [reporting/aws_advantages.py](reporting/aws_advantages.py) for detailed documentation on why AWS EC2 is superior for production deployments:

- Production-grade infrastructure with SLAs
- Auto-scaling capabilities
- Comprehensive monitoring (CloudWatch)
- High availability and reliability
- Enterprise security features
- Persistent storage and databases
- Load balancing and CDN integration
- 24/7 enterprise support

## License

Same as parent project.
