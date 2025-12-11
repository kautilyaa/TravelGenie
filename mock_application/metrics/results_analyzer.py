"""
Results Analyzer
Analyzes test results and provides insights
"""

import statistics
from typing import Dict, List, Any
from pathlib import Path
import json

class ResultsAnalyzer:
    """Analyzes performance test results"""
    
    def __init__(self):
        pass
    
    def analyze_latency_breakdown(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze latency breakdown from traces"""
        if not traces:
            return {}
        
        # Group events by name
        event_times = {}
        total_times = []
        
        for trace in traces:
            total_times.append(trace.get("total_duration_ms", 0))
            
            for event in trace.get("events", []):
                event_name = event.get("event_name")
                duration = event.get("duration_ms", 0)
                
                if event_name not in event_times:
                    event_times[event_name] = []
                event_times[event_name].append(duration)
        
        # Calculate statistics for each event type
        event_stats = {}
        for event_name, times in event_times.items():
            if times:
                event_stats[event_name] = {
                    "count": len(times),
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "p95": sorted(times)[int(len(times) * 0.95)] if times else 0,
                    "p99": sorted(times)[int(len(times) * 0.99)] if times else 0,
                    "total": sum(times),
                    "percentage_of_total": (sum(times) / sum(total_times) * 100) if total_times else 0
                }
        
        return {
            "total_traces": len(traces),
            "mean_total_latency_ms": statistics.mean(total_times) if total_times else 0,
            "event_breakdown": event_stats,
            "bottlenecks": self._identify_bottlenecks(event_stats)
        }
    
    def _identify_bottlenecks(self, event_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Sort by mean latency
        sorted_events = sorted(
            event_stats.items(),
            key=lambda x: x[1].get("mean", 0),
            reverse=True
        )
        
        # Top 3 bottlenecks
        for event_name, stats in sorted_events[:3]:
            if stats.get("mean", 0) > 100:  # More than 100ms
                bottlenecks.append({
                    "event": event_name,
                    "mean_latency_ms": stats.get("mean", 0),
                    "percentage_of_total": stats.get("percentage_of_total", 0)
                })
        
        return bottlenecks
    
    def analyze_load_test_results(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze load test results"""
        if not results:
            return {}
        
        # Extract metrics
        latencies = [r.get("latency_ms", 0) for r in results]
        errors = [r for r in results if not r.get("success", True)]
        success_rate = (len(results) - len(errors)) / len(results) if results else 0
        
        return {
            "total_requests": len(results),
            "successful_requests": len(results) - len(errors),
            "failed_requests": len(errors),
            "success_rate": success_rate,
            "mean_latency_ms": statistics.mean(latencies) if latencies else 0,
            "median_latency_ms": statistics.median(latencies) if latencies else 0,
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
            "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0
        }
    
    def compare_results(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare current results with baseline"""
        comparison = {}
        
        for metric in ["mean_latency_ms", "p95_latency_ms", "p99_latency_ms", "success_rate"]:
            baseline_val = baseline.get(metric, 0)
            current_val = current.get(metric, 0)
            
            if baseline_val > 0:
                change_percent = ((current_val - baseline_val) / baseline_val) * 100
                comparison[metric] = {
                    "baseline": baseline_val,
                    "current": current_val,
                    "change_percent": change_percent,
                    "improved": change_percent < 0 if "latency" in metric else change_percent > 0
                }
        
        return comparison
    
    def generate_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            recommendations.append(
                f"Optimize {top_bottleneck['event']} - accounts for "
                f"{top_bottleneck['percentage_of_total']:.1f}% of total latency"
            )
        
        p95_latency = analysis.get("p95_latency_ms", 0)
        if p95_latency > 5000:
            recommendations.append(
                f"P95 latency ({p95_latency:.0f}ms) exceeds 5s threshold - consider optimization"
            )
        
        success_rate = analysis.get("success_rate", 1.0)
        if success_rate < 0.95:
            recommendations.append(
                f"Success rate ({success_rate*100:.1f}%) is below 95% - investigate errors"
            )
        
        return recommendations
