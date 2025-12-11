"""
Network Monitor
Monitors network-level metrics for Llama endpoint communication
"""

import time
import socket
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import statistics

class NetworkMonitor:
    """Monitors network metrics"""
    
    def __init__(self):
        self.requests = []
        self.dns_cache = {}
    
    def measure_dns_lookup(self, hostname: str) -> float:
        """Measure DNS lookup time"""
        if hostname in self.dns_cache:
            return 0.0  # Cached
        
        start_time = time.time()
        try:
            socket.gethostbyname(hostname)
            dns_time = (time.time() - start_time) * 1000
            self.dns_cache[hostname] = dns_time
            return dns_time
        except Exception:
            return -1.0  # Error
    
    def record_request(
        self,
        url: str,
        method: str,
        status_code: int,
        latency_ms: float,
        dns_time_ms: float = 0.0,
        error: Optional[str] = None
    ):
        """Record a network request"""
        parsed = urlparse(url)
        
        request_record = {
            "url": url,
            "host": parsed.hostname,
            "method": method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "dns_time_ms": dns_time_ms,
            "error": error,
            "timestamp": time.time()
        }
        
        self.requests.append(request_record)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics"""
        if not self.requests:
            return {}
        
        latencies = [r["latency_ms"] for r in self.requests if r["latency_ms"] > 0]
        dns_times = [r["dns_time_ms"] for r in self.requests if r["dns_time_ms"] > 0]
        errors = [r for r in self.requests if r.get("error")]
        success_codes = [r for r in self.requests if 200 <= r["status_code"] < 300]
        
        return {
            "total_requests": len(self.requests),
            "successful_requests": len(success_codes),
            "failed_requests": len(errors),
            "success_rate": len(success_codes) / len(self.requests) if self.requests else 0.0,
            "mean_latency_ms": statistics.mean(latencies) if latencies else 0.0,
            "median_latency_ms": statistics.median(latencies) if latencies else 0.0,
            "min_latency_ms": min(latencies) if latencies else 0.0,
            "max_latency_ms": max(latencies) if latencies else 0.0,
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0,
            "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0.0,
            "mean_dns_time_ms": statistics.mean(dns_times) if dns_times else 0.0,
            "error_rate": len(errors) / len(self.requests) if self.requests else 0.0
        }
    
    def get_host_statistics(self, hostname: str) -> Dict[str, Any]:
        """Get statistics for a specific hostname"""
        host_requests = [r for r in self.requests if r["host"] == hostname]
        
        if not host_requests:
            return {}
        
        latencies = [r["latency_ms"] for r in host_requests if r["latency_ms"] > 0]
        
        return {
            "hostname": hostname,
            "request_count": len(host_requests),
            "mean_latency_ms": statistics.mean(latencies) if latencies else 0.0,
            "min_latency_ms": min(latencies) if latencies else 0.0,
            "max_latency_ms": max(latencies) if latencies else 0.0
        }
    
    def clear(self):
        """Clear all records"""
        self.requests.clear()
        self.dns_cache.clear()
