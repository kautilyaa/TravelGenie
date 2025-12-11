"""
Report Generator
Generates performance reports in various formats
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

class ReportGenerator:
    """Generates performance reports"""
    
    def __init__(self, results_dir: Optional[str] = None):
        if results_dir is None:
            results_dir = Path(__file__).parent.parent / "results"
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def generate_json_report(self, metrics: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Generate JSON report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(filepath)
    
    def generate_csv_report(self, metrics: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Generate CSV report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.csv"
        
        filepath = self.results_dir / filename
        
        if not metrics:
            return str(filepath)
        
        fieldnames = metrics[0].keys()
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics)
        
        return str(filepath)
    
    def generate_html_report(self, metrics: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Generate HTML report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.html"
        
        filepath = self.results_dir / filename
        
        html = self._generate_html_content(metrics)
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return str(filepath)
    
    def _generate_html_content(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML content"""
        latency_stats = metrics.get("latency_stats", {})
        network_stats = metrics.get("network_stats", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Test Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="metric">
        <h2>Latency Statistics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Mean</td><td>{latency_stats.get('mean', 0):.2f} ms</td></tr>
            <tr><td>Median</td><td>{latency_stats.get('median', 0):.2f} ms</td></tr>
            <tr><td>P95</td><td>{latency_stats.get('p95', 0):.2f} ms</td></tr>
            <tr><td>P99</td><td>{latency_stats.get('p99', 0):.2f} ms</td></tr>
            <tr><td>Min</td><td>{latency_stats.get('min', 0):.2f} ms</td></tr>
            <tr><td>Max</td><td>{latency_stats.get('max', 0):.2f} ms</td></tr>
        </table>
    </div>
    
    <div class="metric">
        <h2>Network Statistics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Mean RTT</td><td>{network_stats.get('mean_rtt', 0):.2f} ms</td></tr>
            <tr><td>Total Requests</td><td>{network_stats.get('total_requests', 0)}</td></tr>
            <tr><td>Success Rate</td><td>{network_stats.get('success_rate', 0):.2f}%</td></tr>
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics"""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "p50": sorted_values[int(n * 0.50)] if n > 0 else 0,
            "p90": sorted_values[int(n * 0.90)] if n > 0 else 0,
            "p95": sorted_values[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_values[int(n * 0.99)] if n > 0 else 0,
            "stddev": statistics.stdev(values) if len(values) > 1 else 0
        }
