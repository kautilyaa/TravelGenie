"""
Performance Monitor
Collects comprehensive performance metrics
"""

import time
from typing import Dict, List, Any, Optional
from collections import defaultdict

from metrics.latency_tracker import LatencyTracker
from metrics.network_monitor import NetworkMonitor
from metrics.results_analyzer import ResultsAnalyzer

class PerformanceMonitor:
    """Monitors and collects performance metrics"""
    
    def __init__(self):
        self.latency_tracker = LatencyTracker()
        self.network_monitor = NetworkMonitor()
        self.results_analyzer = ResultsAnalyzer()
        
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tool_calls": defaultdict(int),
            "llama_calls": 0,
            "total_tokens": 0,
            "start_time": time.time()
        }
    
    def start_request(self, request_id: str):
        """Start tracking a request"""
        self.latency_tracker.start_trace(request_id)
        self.metrics["total_requests"] += 1
    
    def record_llama_call(
        self,
        latency_ms: float,
        tokens: Optional[int] = None,
        success: bool = True
    ):
        """Record a Llama API call"""
        self.latency_tracker.record_event("llama_api_call", latency_ms)
        self.metrics["llama_calls"] += 1
        
        if tokens:
            self.metrics["total_tokens"] += tokens
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
    
    def record_tool_call(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool = True
    ):
        """Record a tool call"""
        self.latency_tracker.record_event(f"tool_{tool_name}", duration_ms)
        self.metrics["tool_calls"][tool_name] += 1
    
    def record_network_request(
        self,
        url: str,
        method: str,
        status_code: int,
        latency_ms: float,
        dns_time_ms: float = 0.0,
        error: Optional[str] = None
    ):
        """Record a network request"""
        self.network_monitor.record_request(
            url, method, status_code, latency_ms, dns_time_ms, error
        )
    
    def end_request(self) -> Dict[str, Any]:
        """End tracking current request and return summary"""
        trace_summary = self.latency_tracker.end_trace()
        return trace_summary
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        latency_stats = self.latency_tracker.get_statistics()
        network_stats = self.network_monitor.get_statistics()
        trace_summary = self.latency_tracker.get_trace_summary()
        
        elapsed_time = time.time() - self.metrics["start_time"]
        
        return {
            "request_metrics": {
                "total_requests": self.metrics["total_requests"],
                "successful_requests": self.metrics["successful_requests"],
                "failed_requests": self.metrics["failed_requests"],
                "success_rate": (
                    self.metrics["successful_requests"] / self.metrics["total_requests"]
                    if self.metrics["total_requests"] > 0 else 0.0
                ),
                "requests_per_second": (
                    self.metrics["total_requests"] / elapsed_time
                    if elapsed_time > 0 else 0.0
                )
            },
            "latency_stats": latency_stats,
            "network_stats": network_stats,
            "trace_summary": trace_summary,
            "tool_usage": dict(self.metrics["tool_calls"]),
            "llama_metrics": {
                "total_calls": self.metrics["llama_calls"],
                "total_tokens": self.metrics["total_tokens"]
            },
            "elapsed_time_seconds": elapsed_time
        }
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis of performance"""
        traces = self.latency_tracker.traces
        latency_breakdown = self.results_analyzer.analyze_latency_breakdown(traces)
        
        metrics = self.get_metrics()
        
        recommendations = self.results_analyzer.generate_recommendations({
            "bottlenecks": latency_breakdown.get("bottlenecks", []),
            "p95_latency_ms": metrics.get("trace_summary", {}).get("p95_duration_ms", 0),
            "success_rate": metrics.get("request_metrics", {}).get("success_rate", 1.0)
        })
        
        return {
            **metrics,
            "latency_breakdown": latency_breakdown,
            "recommendations": recommendations
        }
    
    def clear(self):
        """Clear all metrics"""
        self.latency_tracker.clear()
        self.network_monitor.clear()
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tool_calls": defaultdict(int),
            "llama_calls": 0,
            "total_tokens": 0,
            "start_time": time.time()
        }
