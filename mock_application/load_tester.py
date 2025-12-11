"""
Load Tester
Framework for concurrent and sustained load testing
"""

import time
import threading
import yaml
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import statistics

from mock_orchestrator import MockOrchestrator
from performance_monitor import PerformanceMonitor

class LoadTester:
    """Load testing framework"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "load_test_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.results = []
        self.lock = threading.Lock()
    
    def run_concurrent_users(
        self,
        num_users: int,
        scenario_func: Callable,
        duration_seconds: int,
        ramp_up_seconds: int = 10
    ) -> Dict[str, Any]:
        """Run concurrent users test"""
        print(f"Starting concurrent users test: {num_users} users for {duration_seconds}s")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        results = []
        
        def user_simulation(user_id: int):
            """Simulate a single user"""
            user_results = []
            orchestrator = MockOrchestrator()
            
            while time.time() < end_time:
                # Execute scenario
                result = scenario_func(orchestrator)
                user_results.append(result)
                
                # Think time between requests
                think_time = self.config.get("concurrent_users", {}).get("think_time_min", 1.0)
                time.sleep(think_time)
            
            return user_results
        
        # Ramp up users gradually
        if ramp_up_seconds > 0:
            users_per_second = num_users / ramp_up_seconds
            current_users = 0
            ramp_start = time.time()
            
            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = []
                
                while time.time() < end_time:
                    # Add new users during ramp-up
                    if time.time() < ramp_start + ramp_up_seconds:
                        if current_users < num_users:
                            new_users = min(
                                int((time.time() - ramp_start) * users_per_second) - current_users,
                                num_users - current_users
                            )
                            for i in range(new_users):
                                future = executor.submit(user_simulation, current_users + i)
                                futures.append(future)
                                current_users += 1
                    
                    # Collect completed results (with longer timeout)
                    completed_futures = []
                    for future in list(futures):
                        if future.done():
                            completed_futures.append(future)
                    
                    for future in completed_futures:
                        try:
                            user_results = future.result(timeout=30)  # Increased timeout
                            results.extend(user_results)
                            futures.remove(future)
                        except Exception as e:
                            print(f"Error in user simulation: {e}")
                            futures.remove(future)
                    
                    time.sleep(0.1)
                
                # Wait for remaining futures with longer timeout
                for future in as_completed(futures, timeout=300):  # 5 minute timeout
                    try:
                        user_results = future.result(timeout=30)
                        results.extend(user_results)
                    except Exception as e:
                        print(f"Error in user simulation: {e}")
        else:
            # Start all users immediately
            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(user_simulation, i) for i in range(num_users)]
                
                for future in as_completed(futures, timeout=300):  # 5 minute timeout
                    try:
                        user_results = future.result(timeout=30)
                        results.extend(user_results)
                    except Exception as e:
                        print(f"Error in user simulation: {e}")
        
        return self._analyze_results(results, duration_seconds)
    
    def run_sustained_load(
        self,
        rps: float,
        scenario_func: Callable,
        duration_seconds: int,
        ramp_up_seconds: int = 30
    ) -> Dict[str, Any]:
        """Run sustained load test"""
        print(f"Starting sustained load test: {rps} RPS for {duration_seconds}s")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        results = []
        request_times = []
        
        interval = 1.0 / rps  # Time between requests
        current_rps = 0
        
        # Ramp up
        ramp_end = start_time + ramp_up_seconds
        ramp_slope = rps / ramp_up_seconds
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            
            while time.time() < end_time:
                # Calculate current target RPS
                if time.time() < ramp_end:
                    current_rps = (time.time() - start_time) * ramp_slope
                else:
                    current_rps = rps
                
                # Submit requests at current rate
                requests_this_second = int(current_rps)
                for _ in range(requests_this_second):
                    if len(futures) < 100:  # Limit concurrent futures
                        orchestrator = MockOrchestrator()
                        future = executor.submit(scenario_func, orchestrator)
                        futures.append(future)
                        request_times.append(time.time())
                
                # Collect completed results (check done() instead of as_completed with timeout)
                completed_futures = []
                for future in list(futures):
                    if future.done():
                        completed_futures.append(future)
                
                for future in completed_futures:
                    try:
                        result = future.result(timeout=30)  # Increased timeout
                        results.append(result)
                        futures.remove(future)
                    except Exception as e:
                        results.append({
                            "success": False,
                            "error": str(e),
                            "latency_ms": 0
                        })
                        futures.remove(future)
                
                # Sleep to maintain rate
                time.sleep(interval)
            
            # Collect remaining results
            for future in as_completed(futures, timeout=300):  # 5 minute timeout
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "latency_ms": 0
                    })
        
        return self._analyze_results(results, duration_seconds)
    
    def run_stress_test(
        self,
        start_rps: float,
        max_rps: float,
        scenario_func: Callable,
        ramp_up_seconds: int = 60,
        hold_seconds: int = 120
    ) -> Dict[str, Any]:
        """Run stress test with gradual load increase"""
        print(f"Starting stress test: {start_rps} to {max_rps} RPS")
        
        start_time = time.time()
        results = []
        current_rps = start_rps
        
        ramp_end = start_time + ramp_up_seconds
        hold_end = ramp_end + hold_seconds
        
        rps_increase_per_second = (max_rps - start_rps) / ramp_up_seconds
        
        # Track request submission timing
        last_submit_time = start_time
        requests_submitted_this_second = 0
        second_start_time = start_time
        
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = []
            
            while time.time() < hold_end:
                current_time = time.time()
                
                # Calculate current RPS
                if current_time < ramp_end:
                    current_rps = start_rps + (current_time - start_time) * rps_increase_per_second
                    current_rps = min(current_rps, max_rps)
                else:
                    current_rps = max_rps
                
                # Reset counter every second
                if current_time - second_start_time >= 1.0:
                    requests_submitted_this_second = 0
                    second_start_time = current_time
                
                # Submit requests at the target rate (requests per second)
                target_requests_this_second = int(current_rps)
                while requests_submitted_this_second < target_requests_this_second:
                    if len(futures) < 200:  # Limit concurrent futures
                        orchestrator = MockOrchestrator()
                        future = executor.submit(scenario_func, orchestrator)
                        futures.append(future)
                        requests_submitted_this_second += 1
                    else:
                        # If we've hit the limit, break and wait for some to complete
                        break
                
                # Collect completed results
                completed_futures = []
                for future in list(futures):
                    if future.done():
                        completed_futures.append(future)
                
                for future in completed_futures:
                    try:
                        result = future.result(timeout=30)
                        results.append({
                            **result,
                            "current_rps": current_rps,
                            "timestamp": time.time()
                        })
                        futures.remove(future)
                    except Exception as e:
                        results.append({
                            "success": False,
                            "error": str(e),
                            "latency_ms": 0,
                            "current_rps": current_rps,
                            "timestamp": time.time()
                        })
                        futures.remove(future)
                
                # Small sleep to prevent tight loop
                time.sleep(0.01)  # 10ms sleep instead of 100ms
            
            # Collect remaining futures
            print(f"Waiting for {len(futures)} remaining requests to complete...")
            for future in as_completed(futures, timeout=300):  # 5 minute timeout
                try:
                    result = future.result(timeout=30)
                    results.append({
                        **result,
                        "current_rps": current_rps,
                        "timestamp": time.time()
                    })
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "latency_ms": 0,
                        "current_rps": current_rps,
                        "timestamp": time.time()
                    })
        
        total_duration = hold_end - start_time
        return self._analyze_stress_results(results, total_duration)
    
    def _analyze_results(self, results: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        """Analyze test results"""
        if not results:
            return {}
        
        latencies = [r.get("latency_ms", 0) for r in results if r.get("success", True)]
        errors = [r for r in results if not r.get("success", True)]
        
        return {
            "total_requests": len(results),
            "successful_requests": len(results) - len(errors),
            "failed_requests": len(errors),
            "success_rate": (len(results) - len(errors)) / len(results) if results else 0,
            "throughput_rps": len(results) / duration if duration > 0 else 0,
            "mean_latency_ms": statistics.mean(latencies) if latencies else 0,
            "median_latency_ms": statistics.median(latencies) if latencies else 0,
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
            "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "error_rate": len(errors) / len(results) if results else 0
        }
    
    def _analyze_stress_results(self, results: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        """Analyze stress test results"""
        if not results:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "throughput_rps": 0.0,
                "mean_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "rps_levels": [],
                "rps_analysis": {},
                "overall": {}
            }
        
        # Group by RPS level
        rps_groups = {}
        for result in results:
            rps = result.get("current_rps", 0)
            # Round to nearest integer for grouping
            rps_key = int(round(rps))
            if rps_key not in rps_groups:
                rps_groups[rps_key] = []
            rps_groups[rps_key].append(result)
        
        # Analyze each RPS level
        rps_analysis = {}
        for rps, group_results in rps_groups.items():
            # Calculate duration for this RPS level (approximate)
            rps_duration = len(group_results) / max(rps, 1) if rps > 0 else 1.0
            rps_analysis[rps] = self._analyze_results(group_results, rps_duration)
        
        return {
            "total_requests": len(results),
            "successful_requests": len([r for r in results if r.get("success", True)]),
            "failed_requests": len([r for r in results if not r.get("success", True)]),
            "success_rate": len([r for r in results if r.get("success", True)]) / len(results) if results else 0,
            "throughput_rps": len(results) / duration if duration > 0 else 0,
            "rps_levels": sorted(rps_groups.keys()),
            "rps_analysis": rps_analysis,
            "overall": self._analyze_results(results, duration)
        }
