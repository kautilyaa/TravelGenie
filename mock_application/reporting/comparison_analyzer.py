"""
Comparison Analyzer
Analyzes metrics from different platforms and generates insights
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class ComparisonAnalyzer:
    """Analyzes metrics from multiple platforms"""
    
    def __init__(self, metrics_files: List[str]):
        """
        Initialize with metrics files from different platforms
        
        Args:
            metrics_files: List of paths to metrics JSON files
        """
        self.metrics_files = metrics_files
        self.platform_metrics = {}
        self.load_metrics()
    
    def load_metrics(self):
        """Load metrics from all files"""
        for file_path in self.metrics_files:
            try:
                with open(file_path, 'r') as f:
                    metrics = json.load(f)
                    platform = metrics.get("platform", "unknown")
                    self.platform_metrics[platform] = metrics
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def compare_latency(self) -> Dict[str, Any]:
        """Compare latency metrics across platforms"""
        comparison = {}
        
        for platform, metrics in self.platform_metrics.items():
            summary = metrics.get("summary", {})
            percentiles = summary.get("latency_percentiles_ms", {})
            
            comparison[platform] = {
                "mean": percentiles.get("mean", 0),
                "p50": percentiles.get("p50", 0),
                "p95": percentiles.get("p95", 0),
                "p99": percentiles.get("p99", 0),
                "min": percentiles.get("min", 0),
                "max": percentiles.get("max", 0)
            }
        
        # Find best platform for each metric
        if len(comparison) > 1:
            best_mean = min(comparison.items(), key=lambda x: x[1]["mean"])
            best_p95 = min(comparison.items(), key=lambda x: x[1]["p95"])
            best_p99 = min(comparison.items(), key=lambda x: x[1]["p99"])
            
            comparison["_analysis"] = {
                "best_mean_latency": best_mean[0],
                "best_p95_latency": best_p95[0],
                "best_p99_latency": best_p99[0]
            }
        
        return comparison
    
    def compare_throughput(self) -> Dict[str, Any]:
        """Compare throughput metrics across platforms"""
        comparison = {}
        
        for platform, metrics in self.platform_metrics.items():
            summary = metrics.get("summary", {})
            comparison[platform] = {
                "throughput_rps": summary.get("throughput_rps", 0),
                "total_requests": summary.get("total_requests", 0)
            }
        
        # Find best platform
        if len(comparison) > 1:
            best_throughput = max(comparison.items(), key=lambda x: x[1]["throughput_rps"])
            comparison["_analysis"] = {
                "best_throughput": best_throughput[0]
            }
        
        return comparison
    
    def compare_reliability(self) -> Dict[str, Any]:
        """Compare reliability metrics across platforms"""
        comparison = {}
        
        for platform, metrics in self.platform_metrics.items():
            summary = metrics.get("summary", {})
            comparison[platform] = {
                "success_rate": summary.get("success_rate", 0),
                "failed_requests": summary.get("failed_requests", 0),
                "total_requests": summary.get("total_requests", 0)
            }
        
        # Find best platform
        if len(comparison) > 1:
            best_success_rate = max(comparison.items(), key=lambda x: x[1]["success_rate"])
            comparison["_analysis"] = {
                "best_success_rate": best_success_rate[0]
            }
        
        return comparison
    
    def compare_resource_usage(self) -> Dict[str, Any]:
        """Compare resource usage across platforms"""
        comparison = {}
        
        for platform, metrics in self.platform_metrics.items():
            summary = metrics.get("summary", {})
            comparison[platform] = {
                "avg_cpu_percent": summary.get("average_cpu_percent", 0),
                "avg_memory_percent": summary.get("average_memory_percent", 0)
            }
        
        return comparison
    
    def generate_insights(self) -> List[str]:
        """Generate insights from comparison"""
        insights = []
        
        latency_comparison = self.compare_latency()
        throughput_comparison = self.compare_throughput()
        reliability_comparison = self.compare_reliability()
        resource_comparison = self.compare_resource_usage()
        
        # Latency insights
        if "_analysis" in latency_comparison:
            analysis = latency_comparison["_analysis"]
            insights.append(
                f"Best mean latency: {analysis.get('best_mean_latency', 'N/A')} "
                f"({latency_comparison.get(analysis.get('best_mean_latency', ''), {}).get('mean', 0):.2f} ms)"
            )
            insights.append(
                f"Best P95 latency: {analysis.get('best_p95_latency', 'N/A')} "
                f"({latency_comparison.get(analysis.get('best_p95_latency', ''), {}).get('p95', 0):.2f} ms)"
            )
        
        # Throughput insights
        if "_analysis" in throughput_comparison:
            analysis = throughput_comparison["_analysis"]
            best_platform = analysis.get("best_throughput", "N/A")
            insights.append(
                f"Best throughput: {best_platform} "
                f"({throughput_comparison.get(best_platform, {}).get('throughput_rps', 0):.2f} RPS)"
            )
        
        # Reliability insights
        if "_analysis" in reliability_comparison:
            analysis = reliability_comparison["_analysis"]
            best_platform = analysis.get("best_success_rate", "N/A")
            success_rate = reliability_comparison.get(best_platform, {}).get("success_rate", 0)
            insights.append(
                f"Best reliability: {best_platform} "
                f"({success_rate * 100:.2f}% success rate)"
            )
        
        # Resource usage insights
        for platform, resources in resource_comparison.items():
            if platform != "_analysis":
                insights.append(
                    f"{platform}: CPU {resources.get('avg_cpu_percent', 0):.1f}%, "
                    f"Memory {resources.get('avg_memory_percent', 0):.1f}%"
                )
        
        return insights
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive comparison summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "platforms_compared": list(self.platform_metrics.keys()),
            "latency_comparison": self.compare_latency(),
            "throughput_comparison": self.compare_throughput(),
            "reliability_comparison": self.compare_reliability(),
            "resource_comparison": self.compare_resource_usage(),
            "insights": self.generate_insights()
        }
