"""
Latency Tracker
Tracks detailed latency metrics for each component
"""

import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics

class LatencyTracker:
    """Tracks latency for different components"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.current_trace = {}
        self.traces = []
    
    def start_trace(self, trace_id: str):
        """Start a new trace"""
        self.current_trace = {
            "trace_id": trace_id,
            "start_time": time.time(),
            "events": []
        }
    
    def record_event(
        self,
        event_name: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record an event with duration"""
        event = {
            "event_name": event_name,
            "duration_ms": duration_ms,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.current_trace["events"].append(event)
        self.metrics[event_name].append(duration_ms)
    
    def end_trace(self) -> Dict[str, Any]:
        """End current trace and return summary"""
        if not self.current_trace:
            return {}
        
        total_time = (time.time() - self.current_trace["start_time"]) * 1000
        
        trace_summary = {
            **self.current_trace,
            "total_duration_ms": total_time,
            "event_count": len(self.current_trace["events"])
        }
        
        self.traces.append(trace_summary)
        self.current_trace = {}
        
        return trace_summary
    
    def get_statistics(self, event_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific event or all events"""
        if event_name:
            values = self.metrics.get(event_name, [])
            if not values:
                return {}
            
            return {
                "event_name": event_name,
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "p95": sorted(values)[int(len(values) * 0.95)] if values else 0,
                "p99": sorted(values)[int(len(values) * 0.99)] if values else 0,
                "stddev": statistics.stdev(values) if len(values) > 1 else 0
            }
        else:
            # Return statistics for all events
            result = {}
            for event_name, values in self.metrics.items():
                result[event_name] = self.get_statistics(event_name)
            return result
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of all traces"""
        if not self.traces:
            return {}
        
        total_durations = [t["total_duration_ms"] for t in self.traces]
        
        return {
            "total_traces": len(self.traces),
            "mean_duration_ms": statistics.mean(total_durations),
            "median_duration_ms": statistics.median(total_durations),
            "min_duration_ms": min(total_durations),
            "max_duration_ms": max(total_durations),
            "p95_duration_ms": sorted(total_durations)[int(len(total_durations) * 0.95)] if total_durations else 0,
            "p99_duration_ms": sorted(total_durations)[int(len(total_durations) * 0.99)] if total_durations else 0
        }
    
    def clear(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.traces.clear()
        self.current_trace = {}
