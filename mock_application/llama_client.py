"""
Llama Client
HTTP client for communicating with external Llama endpoints with latency tracking
"""

import time
import requests
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LlamaClient:
    """Client for external Llama API endpoint"""
    
    def __init__(self, endpoint: Optional[str] = None, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "app_config.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.endpoint = endpoint or config.get("llama_endpoint", "http://localhost:8000")
        self.timeout = config.get("llama_timeout", 120)
        self.max_retries = config.get("llama_max_retries", 3)
        self.retry_delay = config.get("llama_retry_delay", 1)
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        # Metrics tracking
        self.latency_history = []
        self.error_count = 0
        self.total_requests = 0
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Llama endpoint
        Returns response and timing information
        """
        url = f"{self.endpoint}/v1/chat/completions"
        
        payload = {
            "model": kwargs.get("model", "llama-3.2"),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "top_p": kwargs.get("top_p", 0.9)
        }
        
        # Track timing
        start_time = time.time()
        dns_start = time.time()
        
        try:
            # Measure DNS lookup and connection time
            dns_time = time.time() - dns_start
            
            # Make request with retries
            response = None
            for attempt in range(self.max_retries):
                try:
                    request_start = time.time()
                    response = self.session.post(
                        url,
                        json=payload,
                        timeout=self.timeout
                    )
                    request_time = time.time() - request_start
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise
            
            total_time = time.time() - start_time
            
            response.raise_for_status()
            data = response.json()
            
            # Track metrics
            self.total_requests += 1
            self.latency_history.append({
                "total_time": total_time * 1000,  # Convert to ms
                "dns_time": dns_time * 1000,
                "request_time": request_time * 1000,
                "status_code": response.status_code,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "response": data,
                "latency_ms": total_time * 1000,
                "dns_time_ms": dns_time * 1000,
                "request_time_ms": request_time * 1000
            }
            
        except Exception as e:
            total_time = time.time() - start_time
            self.error_count += 1
            self.total_requests += 1
            
            logger.error(f"Error calling Llama API: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "latency_ms": total_time * 1000
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Llama endpoint is healthy"""
        try:
            url = f"{self.endpoint}/health"
            start_time = time.time()
            response = self.session.get(url, timeout=5)
            latency = (time.time() - start_time) * 1000
            
            return {
                "healthy": response.status_code == 200,
                "latency_ms": latency,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.latency_history:
            return {
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "error_rate": 0.0
            }
        
        latencies = [h["total_time"] for h in self.latency_history]
        
        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.total_requests if self.total_requests > 0 else 0.0,
            "mean_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "recent_latencies": latencies[-10:]  # Last 10 requests
        }
