"""
Platform Comparison Metrics
Collects and stores performance metrics for platform comparison (AWS, Colab, Zaratan)
"""

import time
import json
import psutil
import platform as platform_module
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import yaml


class PlatformMetricsCollector:
    """Collects platform-specific metrics for comparison"""
    
    def __init__(self, config_path: Optional[str] = None, platform: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "app_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.platform = platform or self.config.get("platform", "local")
        self.platform_tag = self.config.get("platform_tag", "")
        
        self.metrics = {
            "platform": self.platform,
            "platform_tag": self.platform_tag,
            "start_time": datetime.now().isoformat(),
            "requests": [],
            "resource_usage": [],
            "summary": {}
        }
        
        self.metrics_config = self.config.get("metrics", {})
        self.save_to_file = self.metrics_config.get("save_to_file", True)
        self.metrics_file = self.metrics_config.get("metrics_file", "metrics.json")
        
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / (1024**3),
                "disk_used_gb": disk.used / (1024**3),
                "disk_percent": disk.percent,
                "platform": platform_module.system(),
                "platform_release": platform_module.release(),
                "platform_machine": platform_module.machine(),
                "processor": platform_module.processor()
            }
        except Exception as e:
            return {
                "error": str(e),
                "platform": platform_module.system()
            }
    
    def record_request_metrics(
        self,
        request_id: str,
        latency_ms: float,
        success: bool,
        tool_calls: List[Dict[str, Any]],
        platform_info: Optional[Dict[str, Any]] = None
    ):
        """Record metrics for a single request"""
        if platform_info is None:
            platform_info = self.collect_system_info()
        
        request_metric = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency_ms,
            "success": success,
            "tool_calls_count": len(tool_calls),
            "tool_calls": [tc.get("tool") for tc in tool_calls],
            "resource_usage": platform_info
        }
        
        self.metrics["requests"].append(request_metric)
        
        # Periodically save to file
        if self.save_to_file and len(self.metrics["requests"]) % 10 == 0:
            self.save_metrics()
    
    def calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentile statistics"""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < n:
                return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
            return sorted_values[f]
        
        return {
            "p50": percentile(0.50),
            "p75": percentile(0.75),
            "p90": percentile(0.90),
            "p95": percentile(0.95),
            "p99": percentile(0.99),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / n
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.metrics["requests"]:
            return {}
        
        latencies = [r["latency_ms"] for r in self.metrics["requests"]]
        success_count = sum(1 for r in self.metrics["requests"] if r["success"])
        total_count = len(self.metrics["requests"])
        
        # Calculate throughput
        if len(self.metrics["requests"]) > 1:
            first_time = datetime.fromisoformat(self.metrics["requests"][0]["timestamp"])
            last_time = datetime.fromisoformat(self.metrics["requests"][-1]["timestamp"])
            duration_seconds = (last_time - first_time).total_seconds()
            if duration_seconds > 0:
                throughput_rps = total_count / duration_seconds
            else:
                throughput_rps = 0
        else:
            throughput_rps = 0
        
        # Resource usage averages
        resource_samples = [r["resource_usage"] for r in self.metrics["requests"]]
        avg_cpu = sum(r.get("cpu_percent", 0) for r in resource_samples) / len(resource_samples) if resource_samples else 0
        avg_memory = sum(r.get("memory_percent", 0) for r in resource_samples) / len(resource_samples) if resource_samples else 0
        
        summary = {
            "total_requests": total_count,
            "successful_requests": success_count,
            "failed_requests": total_count - success_count,
            "success_rate": success_count / total_count if total_count > 0 else 0.0,
            "throughput_rps": throughput_rps,
            "latency_percentiles_ms": self.calculate_percentiles(latencies),
            "average_cpu_percent": avg_cpu,
            "average_memory_percent": avg_memory,
            "end_time": datetime.now().isoformat()
        }
        
        self.metrics["summary"] = summary
        return summary
    
    def save_metrics(self, file_path: Optional[str] = None):
        """Save metrics to JSON file"""
        if file_path is None:
            file_path = Path(__file__).parent.parent / self.metrics_file
        
        # Generate summary before saving
        self.generate_summary()
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def load_metrics(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load metrics from JSON file"""
        if file_path is None:
            file_path = Path(__file__).parent.parent / self.metrics_file
        
        file_path = Path(file_path)
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics with summary"""
        self.generate_summary()
        return self.metrics
    
    def clear(self):
        """Clear all metrics"""
        self.metrics = {
            "platform": self.platform,
            "platform_tag": self.platform_tag,
            "start_time": datetime.now().isoformat(),
            "requests": [],
            "resource_usage": [],
            "summary": {}
        }


class AWSMetricsCollector(PlatformMetricsCollector):
    """AWS-specific metrics collector with CloudWatch integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path, platform="aws")
        self.aws_config = self.config.get("aws", {})
        self.enable_cloudwatch = self.aws_config.get("enable_cloudwatch", False)
        
        if self.enable_cloudwatch:
            try:
                import boto3
                self.cloudwatch = boto3.client('cloudwatch', region_name=self.aws_config.get("region", "us-east-1"))
                self.log_group = self.aws_config.get("cloudwatch_log_group", "travel-genie-mock")
            except ImportError:
                self.enable_cloudwatch = False
    
    def send_to_cloudwatch(self, metric_name: str, value: float, unit: str = "None"):
        """Send metric to CloudWatch"""
        if not self.enable_cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace='TravelGenie/Mock',
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Dimensions': [
                        {'Name': 'Platform', 'Value': 'AWS'},
                        {'Name': 'PlatformTag', 'Value': self.platform_tag or 'default'}
                    ]
                }]
            )
        except Exception as e:
            print(f"Failed to send metric to CloudWatch: {e}")


class ColabMetricsCollector(PlatformMetricsCollector):
    """Colab-specific metrics collector"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path, platform="colab")
        self.colab_config = self.config.get("colab", {})
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect Colab-specific system info"""
        info = super().collect_system_info()
        
        # Check if running in Colab
        try:
            import google.colab
            info["is_colab"] = True
            info["colab_port"] = self.colab_config.get("port", 7860)
        except ImportError:
            info["is_colab"] = False
        
        return info


class ZaratanMetricsCollector(PlatformMetricsCollector):
    """Zaratan HPC-specific metrics collector with SLURM integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path, platform="zaratan")
        self.zaratan_config = self.config.get("zaratan", {})
        self.enable_slurm_metrics = self.zaratan_config.get("enable_slurm_metrics", True)
    
    def collect_slurm_info(self) -> Dict[str, Any]:
        """Collect SLURM job information"""
        info = {}
        
        if not self.enable_slurm_metrics:
            return info
        
        # Try to get SLURM environment variables
        import os
        
        slurm_vars = {
            "SLURM_JOB_ID": os.environ.get("SLURM_JOB_ID"),
            "SLURM_JOB_NODELIST": os.environ.get("SLURM_JOB_NODELIST"),
            "SLURM_CPUS_ON_NODE": os.environ.get("SLURM_CPUS_ON_NODE"),
            "SLURM_GPUS_ON_NODE": os.environ.get("SLURM_GPUS_ON_NODE"),
            "SLURM_MEM_PER_NODE": os.environ.get("SLURM_MEM_PER_NODE"),
            "SLURM_PARTITION": os.environ.get("SLURM_PARTITION"),
        }
        
        info["slurm"] = {k: v for k, v in slurm_vars.items() if v}
        return info
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect Zaratan-specific system info"""
        info = super().collect_system_info()
        slurm_info = self.collect_slurm_info()
        info.update(slurm_info)
        return info


def get_metrics_collector(platform: str, config_path: Optional[str] = None) -> PlatformMetricsCollector:
    """Factory function to get appropriate metrics collector"""
    if platform == "aws":
        return AWSMetricsCollector(config_path)
    elif platform == "colab":
        return ColabMetricsCollector(config_path)
    elif platform == "zaratan":
        return ZaratanMetricsCollector(config_path)
    else:
        return PlatformMetricsCollector(config_path, platform=platform)
