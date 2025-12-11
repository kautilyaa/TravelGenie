"""
Zaratan-specific metrics collection
Collects SLURM job metrics and resource usage
"""

import os
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime


class ZaratanMetrics:
    """Collect metrics specific to Zaratan HPC environment"""
    
    def __init__(self):
        self.slurm_job_id = os.environ.get("SLURM_JOB_ID")
        self.slurm_node = os.environ.get("SLURM_NODELIST")
    
    def get_slurm_job_info(self) -> Dict[str, Any]:
        """Get SLURM job information"""
        info = {
            "job_id": self.slurm_job_id,
            "node": self.slurm_node,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get SLURM environment variables
        slurm_vars = {
            "SLURM_JOB_ID": os.environ.get("SLURM_JOB_ID"),
            "SLURM_JOB_NAME": os.environ.get("SLURM_JOB_NAME"),
            "SLURM_JOB_NODELIST": os.environ.get("SLURM_JOB_NODELIST"),
            "SLURM_CPUS_ON_NODE": os.environ.get("SLURM_CPUS_ON_NODE"),
            "SLURM_GPUS_ON_NODE": os.environ.get("SLURM_GPUS_ON_NODE"),
            "SLURM_MEM_PER_NODE": os.environ.get("SLURM_MEM_PER_NODE"),
            "SLURM_PARTITION": os.environ.get("SLURM_PARTITION"),
            "SLURM_ACCOUNT": os.environ.get("SLURM_ACCOUNT"),
        }
        
        info["slurm_env"] = {k: v for k, v in slurm_vars.items() if v}
        
        # Try to get job details from squeue
        if self.slurm_job_id:
            try:
                result = subprocess.run(
                    ['squeue', '-j', self.slurm_job_id, '--format=%A,%P,%T,%M,%l,%m,%D', '--noheader'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split(',')
                    if len(parts) >= 7:
                        info["squeue_info"] = {
                            "job_id": parts[0],
                            "partition": parts[1],
                            "state": parts[2],
                            "time": parts[3],
                            "time_limit": parts[4],
                            "min_memory": parts[5],
                            "nodes": parts[6]
                        }
            except Exception as e:
                info["squeue_error"] = str(e)
        
        return info
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            info = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "memory_percent": memory.percent
            }
            
            # Get GPU info if available
            gpu_info = self.get_gpu_info()
            if gpu_info:
                info["gpu"] = gpu_info
            
            return info
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Get GPU information if available"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,utilization.gpu', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                gpus = []
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(', ')
                    if len(parts) >= 5:
                        gpus.append({
                            "index": parts[0],
                            "name": parts[1],
                            "memory_total": parts[2],
                            "memory_used": parts[3],
                            "utilization": parts[4]
                        })
                return {"gpus": gpus, "count": len(gpus)}
        except Exception as e:
            pass
        
        return None
    
    def get_job_efficiency(self) -> Dict[str, Any]:
        """Calculate job efficiency metrics"""
        if not self.slurm_job_id:
            return {}
        
        try:
            # Get job statistics
            result = subprocess.run(
                ['sacct', '-j', self.slurm_job_id, '--format=JobID,Elapsed,TotalCPU,MaxRSS,MaxVMSize', '--parsable2', '--noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                if len(parts) >= 5:
                    return {
                        "elapsed_time": parts[1],
                        "total_cpu": parts[2],
                        "max_rss": parts[3],
                        "max_vm_size": parts[4]
                    }
        except Exception as e:
            return {"error": str(e)}
        
        return {}
