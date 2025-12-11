"""
Report Generator
Generates comparison reports in Markdown and HTML formats
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from comparison_analyzer import ComparisonAnalyzer
from aws_advantages import get_aws_advantages


class ReportGenerator:
    """Generates comparison reports"""
    
    def __init__(self, metrics_files: List[str], output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            metrics_files: List of paths to metrics JSON files
            output_dir: Directory to save reports
        """
        self.analyzer = ComparisonAnalyzer(metrics_files)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        summary = self.analyzer.generate_summary()
        aws_advantages = get_aws_advantages()
        
        report = []
        report.append("# Platform Comparison Report: Mock Travel Genie")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("## Executive Summary")
        report.append("")
        report.append("This report compares the performance of Mock Travel Genie across three platforms:")
        report.append("- **AWS EC2**: Production-grade cloud infrastructure")
        report.append("- **Google Colab**: Free cloud notebook environment")
        report.append("- **Zaratan HPC**: University HPC cluster")
        report.append("")
        
        # Latency Comparison
        report.append("## Latency Comparison")
        report.append("")
        latency = summary["latency_comparison"]
        report.append("| Platform | Mean (ms) | P50 (ms) | P95 (ms) | P99 (ms) |")
        report.append("|----------|-----------|----------|----------|----------|")
        for platform, metrics in latency.items():
            if platform != "_analysis":
                report.append(
                    f"| {platform.upper()} | {metrics.get('mean', 0):.2f} | "
                    f"{metrics.get('p50', 0):.2f} | {metrics.get('p95', 0):.2f} | "
                    f"{metrics.get('p99', 0):.2f} |"
                )
        report.append("")
        
        # Throughput Comparison
        report.append("## Throughput Comparison")
        report.append("")
        throughput = summary["throughput_comparison"]
        report.append("| Platform | Throughput (RPS) | Total Requests |")
        report.append("|----------|------------------|----------------|")
        for platform, metrics in throughput.items():
            if platform != "_analysis":
                report.append(
                    f"| {platform.upper()} | {metrics.get('throughput_rps', 0):.2f} | "
                    f"{metrics.get('total_requests', 0)} |"
                )
        report.append("")
        
        # Reliability Comparison
        report.append("## Reliability Comparison")
        report.append("")
        reliability = summary["reliability_comparison"]
        report.append("| Platform | Success Rate | Failed Requests |")
        report.append("|----------|--------------|-----------------|")
        for platform, metrics in reliability.items():
            if platform != "_analysis":
                success_rate = metrics.get("success_rate", 0) * 100
                report.append(
                    f"| {platform.upper()} | {success_rate:.2f}% | "
                    f"{metrics.get('failed_requests', 0)} |"
                )
        report.append("")
        
        # Resource Usage
        report.append("## Resource Usage Comparison")
        report.append("")
        resources = summary["resource_comparison"]
        report.append("| Platform | Avg CPU % | Avg Memory % |")
        report.append("|----------|-----------|--------------|")
        for platform, metrics in resources.items():
            if platform != "_analysis":
                report.append(
                    f"| {platform.upper()} | {metrics.get('avg_cpu_percent', 0):.1f}% | "
                    f"{metrics.get('avg_memory_percent', 0):.1f}% |"
                )
        report.append("")
        
        # Key Insights
        report.append("## Key Insights")
        report.append("")
        for insight in summary["insights"]:
            report.append(f"- {insight}")
        report.append("")
        
        # AWS Advantages
        report.append("## Why AWS is Better for Production")
        report.append("")
        for advantage in aws_advantages:
            report.append(f"### {advantage['title']}")
            report.append("")
            report.append(advantage["description"])
            report.append("")
            if advantage.get("details"):
                for detail in advantage["details"]:
                    report.append(f"- {detail}")
                report.append("")
        
        # Conclusion
        report.append("## Conclusion")
        report.append("")
        report.append(
            "While all three platforms can run the Mock Travel Genie application, AWS EC2 provides "
            "superior capabilities for production deployments. AWS offers enterprise-grade infrastructure, "
            "comprehensive monitoring, auto-scaling, high availability, and robust security features that "
            "are essential for production workloads."
        )
        report.append("")
        report.append("**Recommendation:** Use AWS EC2 for production deployments.")
        report.append("")
        
        return "\n".join(report)
    
    def generate_html_report(self) -> str:
        """Generate HTML report with visualizations"""
        summary = self.analyzer.generate_summary()
        aws_advantages = get_aws_advantages()
        
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append('<meta charset="UTF-8">')
        html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append("<title>Platform Comparison Report: Mock Travel Genie</title>")
        html.append('<style>')
        html.append('body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }')
        html.append('.container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
        html.append('h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }')
        html.append('h2 { color: #34495e; margin-top: 30px; }')
        html.append('h3 { color: #7f8c8d; }')
        html.append('table { width: 100%; border-collapse: collapse; margin: 20px 0; }')
        html.append('th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }')
        html.append('th { background-color: #3498db; color: white; }')
        html.append('tr:hover { background-color: #f5f5f5; }')
        html.append('.insight { background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4caf50; }')
        html.append('.advantage { background: #fff3e0; padding: 15px; margin: 10px 0; border-left: 4px solid #ff9800; }')
        html.append('.conclusion { background: #e3f2fd; padding: 20px; margin: 20px 0; border-left: 4px solid #2196f3; }')
        html.append('</style>')
        html.append("</head>")
        html.append("<body>")
        html.append('<div class="container">')
        
        html.append("<h1>Platform Comparison Report: Mock Travel Genie</h1>")
        html.append(f'<p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        
        html.append("<h2>Executive Summary</h2>")
        html.append("<p>This report compares the performance of Mock Travel Genie across three platforms:</p>")
        html.append("<ul>")
        html.append("<li><strong>AWS EC2:</strong> Production-grade cloud infrastructure</li>")
        html.append("<li><strong>Google Colab:</strong> Free cloud notebook environment</li>")
        html.append("<li><strong>Zaratan HPC:</strong> University HPC cluster</li>")
        html.append("</ul>")
        
        # Latency Comparison
        html.append("<h2>Latency Comparison</h2>")
        latency = summary["latency_comparison"]
        html.append("<table>")
        html.append("<tr><th>Platform</th><th>Mean (ms)</th><th>P50 (ms)</th><th>P95 (ms)</th><th>P99 (ms)</th></tr>")
        for platform, metrics in latency.items():
            if platform != "_analysis":
                html.append(
                    f"<tr><td>{platform.upper()}</td>"
                    f"<td>{metrics.get('mean', 0):.2f}</td>"
                    f"<td>{metrics.get('p50', 0):.2f}</td>"
                    f"<td>{metrics.get('p95', 0):.2f}</td>"
                    f"<td>{metrics.get('p99', 0):.2f}</td></tr>"
                )
        html.append("</table>")
        
        # Throughput Comparison
        html.append("<h2>Throughput Comparison</h2>")
        throughput = summary["throughput_comparison"]
        html.append("<table>")
        html.append("<tr><th>Platform</th><th>Throughput (RPS)</th><th>Total Requests</th></tr>")
        for platform, metrics in throughput.items():
            if platform != "_analysis":
                html.append(
                    f"<tr><td>{platform.upper()}</td>"
                    f"<td>{metrics.get('throughput_rps', 0):.2f}</td>"
                    f"<td>{metrics.get('total_requests', 0)}</td></tr>"
                )
        html.append("</table>")
        
        # Reliability Comparison
        html.append("<h2>Reliability Comparison</h2>")
        reliability = summary["reliability_comparison"]
        html.append("<table>")
        html.append("<tr><th>Platform</th><th>Success Rate</th><th>Failed Requests</th></tr>")
        for platform, metrics in reliability.items():
            if platform != "_analysis":
                success_rate = metrics.get("success_rate", 0) * 100
                html.append(
                    f"<tr><td>{platform.upper()}</td>"
                    f"<td>{success_rate:.2f}%</td>"
                    f"<td>{metrics.get('failed_requests', 0)}</td></tr>"
                )
        html.append("</table>")
        
        # Key Insights
        html.append("<h2>Key Insights</h2>")
        for insight in summary["insights"]:
            html.append(f'<div class="insight">{insight}</div>')
        
        # AWS Advantages
        html.append("<h2>Why AWS is Better for Production</h2>")
        for advantage in aws_advantages:
            html.append(f'<div class="advantage">')
            html.append(f"<h3>{advantage['title']}</h3>")
            html.append(f"<p>{advantage['description']}</p>")
            if advantage.get("details"):
                html.append("<ul>")
                for detail in advantage["details"]:
                    html.append(f"<li>{detail}</li>")
                html.append("</ul>")
            html.append("</div>")
        
        # Conclusion
        html.append('<div class="conclusion">')
        html.append("<h2>Conclusion</h2>")
        html.append(
            "<p>While all three platforms can run the Mock Travel Genie application, AWS EC2 provides "
            "superior capabilities for production deployments. AWS offers enterprise-grade infrastructure, "
            "comprehensive monitoring, auto-scaling, high availability, and robust security features that "
            "are essential for production workloads.</p>"
        )
        html.append("<p><strong>Recommendation:</strong> Use AWS EC2 for production deployments.</p>")
        html.append("</div>")
        
        html.append("</div>")
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def save_reports(self):
        """Save both Markdown and HTML reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save Markdown
        md_content = self.generate_markdown_report()
        md_path = self.output_dir / f"comparison_report_{timestamp}.md"
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"Markdown report saved to: {md_path}")
        
        # Save HTML
        html_content = self.generate_html_report()
        html_path = self.output_dir / f"comparison_report_{timestamp}.html"
        with open(html_path, 'w') as f:
            f.write(html_content)
        print(f"HTML report saved to: {html_path}")
        
        return str(md_path), str(html_path)


if __name__ == "__main__":
    # Example usage
    metrics_files = [
        "metrics_aws.json",
        "metrics_colab.json",
        "metrics_zaratan.json"
    ]
    
    generator = ReportGenerator(metrics_files)
    generator.save_reports()
