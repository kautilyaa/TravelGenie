"""
Colab-specific metrics collection
Collects resource usage metrics available in Google Colab environment
"""

import psutil
import os
from typing import Dict, Any
from datetime import datetime


class ColabMetrics:
    """Collect metrics specific to Colab environment"""
    
    def __init__(self):
        self.is_colab = self._check_colab()
    
    def _check_colab(self) -> bool:
        """Check if running in Colab"""
        try:
            import google.colab
            return True
        except ImportError:
            return False
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / (1024**3),
                "disk_used_gb": disk.used / (1024**3),
                "disk_percent": disk.percent,
                "is_colab": self.is_colab
            }
            
            # Colab-specific info
            if self.is_colab:
                try:
                    import google.colab
                    metrics["colab_runtime"] = os.environ.get("COLAB_GPU", "CPU")
                except:
                    pass
            
            return metrics
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information if available"""
        if not self.is_colab:
            return {"gpu_available": False}
        
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    gpu_info = lines[1].split(', ')
                    return {
                        "gpu_available": True,
                        "gpu_name": gpu_info[0] if len(gpu_info) > 0 else "Unknown",
                        "gpu_memory_total": gpu_info[1] if len(gpu_info) > 1 else "Unknown",
                        "gpu_memory_used": gpu_info[2] if len(gpu_info) > 2 else "Unknown"
                    }
        except Exception as e:
            pass
        
        return {"gpu_available": False}
