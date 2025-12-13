#!/usr/bin/env python3
"""
EC2 vs ECS Comparison Script
Runs load tests on both EC2 and ECS deployments and generates comparison reports
"""

import sys
import json
import yaml
import time
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from urllib.parse import urlparse

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from load_tester import LoadTester
from scenarios.platform_comparison_scenarios import PlatformComparisonScenarios
from mock_orchestrator import MockOrchestrator
from metrics.platform_comparison import get_metrics_collector
from metrics.network_monitor import NetworkMonitor


class EC2ECSComparison:
    """Compare EC2 and ECS deployments"""
    
    @staticmethod
    def _clean_endpoint(endpoint: Optional[str]) -> Optional[str]:
        """Clean and validate endpoint URL, removing any trailing argument fragments"""
        if not endpoint:
            return None
        
        # Remove any trailing whitespace
        endpoint = endpoint.strip()
        
        # Check if endpoint contains argument-like fragments (starting with --)
        # This can happen if shell parsing incorrectly concatenated arguments
        if '--' in endpoint:
            # Split on '--' and take only the first part (the actual URL)
            endpoint = endpoint.split('--')[0].strip()
        
        # Validate it's a proper URL format
        try:
            parsed = urlparse(endpoint)
            if not parsed.scheme or not parsed.netloc:
                # If it doesn't have scheme/netloc, it might be malformed
                # But we'll still return it cleaned up
                pass
        except Exception:
            # If parsing fails, return the cleaned endpoint anyway
            pass
        
        return endpoint.rstrip('/') if endpoint else None
    
    def __init__(
        self, 
        config_path: Optional[str] = None, 
        aws_profile: Optional[str] = None,
        ec2_endpoint: Optional[str] = None,
        ecs_endpoint: Optional[str] = None
    ):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "app_config.yaml"
        
        # Set AWS profile if provided
        if aws_profile:
            os.environ['AWS_PROFILE'] = aws_profile
            print(f"Using AWS profile: {aws_profile}")
        
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Clean and store endpoints (remove any trailing argument fragments)
        # #region agent log
        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:52","message":"__init__ storing endpoints","data":{"ec2_endpoint":ec2_endpoint,"ecs_endpoint":ecs_endpoint,"ec2_endpoint_repr":repr(ec2_endpoint) if ec2_endpoint else None,"ecs_endpoint_repr":repr(ecs_endpoint) if ecs_endpoint else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
        except: pass
        # #endregion
        self.ec2_endpoint = self._clean_endpoint(ec2_endpoint)
        self.ecs_endpoint = self._clean_endpoint(ecs_endpoint)
        
        self.results = {
            "ec2": {},
            "ecs": {},
            "comparison": {},
            "timestamp": datetime.now().isoformat(),
            "aws_profile": aws_profile,
            "ec2_endpoint": ec2_endpoint,
            "ecs_endpoint": ecs_endpoint
        }
    
    def _make_http_request(
        self,
        endpoint: str,
        query: str,
        network_monitor: NetworkMonitor
    ) -> Dict[str, Any]:
        """Make HTTP request to deployed endpoint"""
        # #region agent log
        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B,C,D,E","location":"ec2_ecs_comparison.py:72","message":"_make_http_request called","data":{"endpoint":endpoint,"query":query[:50] if query else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
        except Exception as log_err: pass
        # #endregion
        start_time = time.time()
        parsed_url = urlparse(endpoint)
        hostname = parsed_url.hostname or parsed_url.path.split(':')[0]
        # #region agent log
        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"ec2_ecs_comparison.py:77","message":"URL parsed","data":{"endpoint":endpoint,"parsed_hostname":parsed_url.hostname,"parsed_path":parsed_url.path,"extracted_hostname":hostname,"parsed_scheme":parsed_url.scheme,"parsed_netloc":parsed_url.netloc},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
        except: pass
        # #endregion
        
        # Measure DNS lookup
        dns_time_ms = network_monitor.measure_dns_lookup(hostname)
        
        try:
            # Try multiple endpoint patterns for Streamlit apps
            # Pattern 1: Direct base endpoint (health check)
            # Pattern 2: /api/query (if API wrapper exists)
            # Pattern 3: /_stcore/health (Streamlit health endpoint)
            
            base_endpoint = endpoint.rstrip('/')
            endpoints_to_try = [
                base_endpoint + '/_stcore/health',  # Streamlit health check
                base_endpoint + '/api/query',       # API wrapper (if exists)
                base_endpoint                       # Base endpoint
            ]
            # #region agent log
            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"ec2_ecs_comparison.py:93","message":"Endpoints to try","data":{"endpoints":endpoints_to_try},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
            except: pass
            # #endregion
            last_error = None
            for api_endpoint in endpoints_to_try:
                try:
                    # Try GET first (for health/status endpoints)
                    response = requests.get(
                        api_endpoint,
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    latency_ms = (time.time() - start_time) * 1000
                    # #region agent log
                    try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:102","message":"GET response received","data":{"endpoint":api_endpoint,"status_code":response.status_code,"latency_ms":latency_ms},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                    except: pass
                    # #endregion
                    
                    # Record network request
                    network_monitor.record_request(
                        url=api_endpoint,
                        method="GET",
                        status_code=response.status_code,
                        latency_ms=latency_ms,
                        dns_time_ms=dns_time_ms,
                        error=None if response.status_code == 200 else f"HTTP {response.status_code}"
                    )
                    
                    # If successful, return
                    if response.status_code == 200:
                        # #region agent log
                        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"ec2_ecs_comparison.py:116","message":"Returning success","data":{"endpoint":api_endpoint,"status_code":200},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                        except: pass
                        # #endregion
                        return {
                            "success": True,
                            "latency_ms": latency_ms,
                            "status_code": response.status_code,
                            "error": None
                        }
                    else:
                        last_error = f"HTTP {response.status_code}"
                        # #region agent log
                        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:123","message":"Non-200 status, trying next endpoint","data":{"endpoint":api_endpoint,"status_code":response.status_code,"last_error":last_error},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                        except: pass
                        # #endregion
                        continue
                        
                except requests.exceptions.RequestException as get_exc:
                    # #region agent log
                    try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"ec2_ecs_comparison.py:145","message":"GET request exception, trying POST","data":{"endpoint":api_endpoint,"error":str(get_exc),"error_type":type(get_exc).__name__,"error_args":str(get_exc.args) if hasattr(get_exc, 'args') else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                    except: pass
                    # #endregion
                    # Try POST if GET fails (for API endpoints)
                    try:
                        response = requests.post(
                            api_endpoint,
                            json={"query": query},
                            timeout=120,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        latency_ms = (time.time() - start_time) * 1000
                        # #region agent log
                        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:136","message":"POST response received","data":{"endpoint":api_endpoint,"status_code":response.status_code,"latency_ms":latency_ms},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                        except: pass
                        # #endregion
                        
                        network_monitor.record_request(
                            url=api_endpoint,
                            method="POST",
                            status_code=response.status_code,
                            latency_ms=latency_ms,
                            dns_time_ms=dns_time_ms,
                            error=None if response.status_code == 200 else f"HTTP {response.status_code}"
                        )
                        
                        if response.status_code == 200:
                            # #region agent log
                            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"ec2_ecs_comparison.py:148","message":"Returning success from POST","data":{"endpoint":api_endpoint,"status_code":200},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                            except: pass
                            # #endregion
                            return {
                                "success": True,
                                "latency_ms": latency_ms,
                                "status_code": response.status_code,
                                "error": None
                            }
                        else:
                            last_error = f"HTTP {response.status_code}"
                            # #region agent log
                            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:155","message":"POST non-200 status, trying next endpoint","data":{"endpoint":api_endpoint,"status_code":response.status_code,"last_error":last_error},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                            except: pass
                            # #endregion
                            continue
                    except requests.exceptions.RequestException as e:
                        last_error = str(e)
                        # #region agent log
                        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"ec2_ecs_comparison.py:192","message":"POST request exception","data":{"endpoint":api_endpoint,"error":str(e),"error_type":type(e).__name__,"error_args":str(e.args) if hasattr(e, 'args') else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                        except: pass
                        # #endregion
                        continue
            
            # If all endpoints failed, return error
            latency_ms = (time.time() - start_time) * 1000
            # #region agent log
            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"ec2_ecs_comparison.py:163","message":"All endpoints failed","data":{"endpoint":endpoint,"last_error":last_error,"endpoints_tried":endpoints_to_try},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
            except: pass
            # #endregion
            return {
                "success": False,
                "latency_ms": latency_ms,
                "status_code": 0,
                "error": last_error or "All endpoint patterns failed"
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            # #region agent log
            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"ec2_ecs_comparison.py:170","message":"Outer exception caught","data":{"endpoint":endpoint,"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
            except: pass
            # #endregion
            network_monitor.record_request(
                url=endpoint,
                method="GET",
                status_code=0,
                latency_ms=latency_ms,
                dns_time_ms=dns_time_ms,
                error=str(e)
            )
            return {
                "success": False,
                "latency_ms": latency_ms,
                "status_code": 0,
                "error": str(e)
            }
    
    def run_test_on_platform(
        self,
        platform: str,
        num_requests: int,
        scenario_id: str = "simple_trip",
        max_concurrent: int = 50,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run load test on a specific platform"""
        # #region agent log
        try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"ec2_ecs_comparison.py:229","message":"run_test_on_platform entry","data":{"platform":platform,"num_requests":num_requests,"scenario_id":scenario_id,"endpoint":endpoint,"has_endpoint":endpoint is not None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
        except: pass
        # #endregion
        print(f"\n{'='*70}")
        print(f"Testing {platform.upper()} - {num_requests} requests")
        if endpoint:
            print(f"Endpoint: {endpoint}")
        print(f"{'='*70}")
        
        # Initialize network monitor for detailed network latency tracking
        network_monitor = NetworkMonitor()
        
        # If endpoint is provided, test against deployed instance
        if endpoint:
            # Get scenario queries
            scenario_queries = {
                "simple_flight": "Find flights from IAD to JFK on 2025-12-17",
                "hotel": "Search for hotels in Banff, Alberta from 2025-06-07 to 2025-06-14",
                "weather": "What's the weather forecast for New York City?",
                "currency": "Convert $5000 USD to CAD",
                "simple_trip": "I want to plan a trip from IAD to JFK on December 17, 2025. Find flights and hotels in New York.",
                "complex_trip": "Plan a trip to Banff, Alberta from Reston, Virginia for June 7-14, 2025. Find flights, hotels, events, and weather forecast.",
                "full_workflow": "Plan a complete trip to Tokyo, Japan from Washington DC for March 15-22, 2025. Include flights, hotels, events, weather, and currency conversion.",
                "events": "Find events in New York City on December 17, 2025",
                "geocoding": "Get coordinates for Banff, Alberta",
                "multi_location": "Find flights from IAD to JFK, hotels in New York, and events in both cities"
            }
            
            if scenario_id not in scenario_queries:
                raise ValueError(f"Unknown scenario: {scenario_id}")
            
            query = scenario_queries[scenario_id]
            
            # Run HTTP load test
            print(f"Running {num_requests} HTTP requests to {endpoint} with scenario: {scenario_id}")
            start_time = time.time()
            
            # Use LoadTester's fixed request count but with HTTP requests
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            results = []
            completed_count = 0
            
            def make_request():
                return self._make_http_request(endpoint, query, network_monitor)
            
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                futures = []
                
                # Submit all requests
                for _ in range(num_requests):
                    future = executor.submit(make_request)
                    futures.append(future)
                
                # Track processed futures
                processed_futures = set()
                
                # Collect results
                try:
                    for future in as_completed(futures, timeout=600):
                        processed_futures.add(future)
                        try:
                            result = future.result(timeout=120)
                            # #region agent log
                            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"ec2_ecs_comparison.py:280","message":"Future result received","data":{"success":result.get("success"),"status_code":result.get("status_code"),"error":result.get("error"),"completed_count":completed_count+1},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                            except: pass
                            # #endregion
                            results.append(result)
                            completed_count += 1
                            
                            if completed_count % 100 == 0:
                                elapsed = time.time() - start_time
                                rps = completed_count / elapsed if elapsed > 0 else 0
                                print(f"  Progress: {completed_count}/{num_requests} ({rps:.1f} RPS)")
                        except Exception as e:
                            # #region agent log
                            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"ec2_ecs_comparison.py:290","message":"Future result exception","data":{"error":str(e),"completed_count":completed_count+1},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
                            except: pass
                            # #endregion
                            results.append({
                                "success": False,
                                "latency_ms": 0,
                                "status_code": 0,
                                "error": str(e)
                            })
                            completed_count += 1
                except Exception as timeout_error:
                    # Handle timeout or other errors from as_completed
                    print(f"  Warning: Timeout or error collecting results: {timeout_error}")
                    print(f"  Completed: {completed_count}/{num_requests}")
                
                # Process any remaining incomplete futures
                incomplete_futures = [f for f in futures if f not in processed_futures]
                for future in incomplete_futures:
                    # Try to get result if it completed but wasn't processed
                    if future.done():
                        try:
                            result = future.result(timeout=1)
                            results.append(result)
                            completed_count += 1
                        except Exception as e:
                            results.append({
                                "success": False,
                                "latency_ms": 0,
                                "status_code": 0,
                                "error": f"Error retrieving result: {str(e)}"
                            })
                            completed_count += 1
                    else:
                        # Future is still running - mark as timeout
                        results.append({
                            "success": False,
                            "latency_ms": 0,
                            "status_code": 0,
                            "error": "Request timeout - not completed within 600 seconds"
                        })
                        completed_count += 1
                
                # Ensure all requests are accounted for
                if completed_count < num_requests:
                    missing_count = num_requests - completed_count
                    print(f"  Warning: {missing_count} requests were not accounted for. Marking as failed.")
                    for _ in range(missing_count):
                        results.append({
                            "success": False,
                            "latency_ms": 0,
                            "status_code": 0,
                            "error": "Request not accounted for - missing from results"
                        })
                        completed_count += 1
                
                # Final verification
                if completed_count != num_requests:
                    print(f"  Error: Request count mismatch! Expected {num_requests}, got {completed_count}")
            
            # Analyze results
            elapsed_time = time.time() - start_time
            successful = [r for r in results if r.get("success", False)]
            failed = [r for r in results if not r.get("success", False)]
            latencies = [r.get("latency_ms", 0) for r in results if r.get("latency_ms", 0) > 0]
            # #region agent log
            try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"ec2_ecs_comparison.py:320","message":"Results analysis","data":{"total_results":len(results),"successful_count":len(successful),"failed_count":len(failed),"expected_requests":num_requests,"sample_successful":successful[:2] if successful else None,"sample_failed":failed[:2] if failed else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
            except: pass
            # #endregion
            
            # Debug: Show error breakdown if all requests failed
            if len(successful) == 0 and len(failed) > 0:
                print(f"\n  Debug: All {len(failed)} requests failed. Error breakdown:")
                error_counts = {}
                for r in failed:
                    error_msg = r.get("error", "Unknown error")
                    error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
                for error_msg, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {error_msg}: {count} requests")
            
            # Verify we have results for all requests
            if len(results) != num_requests:
                print(f"\n  Warning: Result count mismatch! Expected {num_requests}, got {len(results)}")
                print(f"    Successful: {len(successful)}, Failed: {len(failed)}, Total: {len(results)}")
            
            if latencies:
                sorted_latencies = sorted(latencies)
                p95_idx = int(len(sorted_latencies) * 0.95)
                p99_idx = int(len(sorted_latencies) * 0.99)
                p95_latency = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else sorted_latencies[-1]
                p99_latency = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else sorted_latencies[-1]
            else:
                p95_latency = 0
                p99_latency = 0
            
            result = {
                "total_requests": len(results),
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "success_rate": len(successful) / len(results) if results else 0.0,
                "throughput_rps": len(results) / elapsed_time if elapsed_time > 0 else 0.0,
                "mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
                "p95_latency_ms": p95_latency,
                "p99_latency_ms": p99_latency
            }
            
            # Collect system metrics (local machine)
            metrics_collector = get_metrics_collector(platform=platform, config_path=self.config_path)
            metrics_collector.generate_summary()
            metrics = metrics_collector.get_metrics()
            
        else:
            # Use mock/local testing
            # Update config for platform
            config = self.config.copy()
            config["platform"] = platform
            config["platform_tag"] = f"{platform}-comparison"
            
            # Save temporary config
            temp_config_path = Path(__file__).parent / f"config_temp_{platform}.yaml"
            with open(temp_config_path, 'w') as f:
                yaml.dump(config, f)
            
            try:
                # Initialize components
                orchestrator = MockOrchestrator(config_path=str(temp_config_path))
                orchestrator.platform = platform
                orchestrator.platform_tag = config["platform_tag"]
                
                scenarios_obj = PlatformComparisonScenarios(orchestrator)
                tester = LoadTester(config_path=str(temp_config_path))
                metrics_collector = get_metrics_collector(platform=platform, config_path=str(temp_config_path))
                
                # Get scenario function
                scenario_map = {
                    "simple_flight": scenarios_obj.scenario_1_simple_flight_search,
                    "hotel": scenarios_obj.scenario_2_hotel_search,
                    "weather": scenarios_obj.scenario_3_weather_check,
                    "currency": scenarios_obj.scenario_4_currency_conversion,
                    "simple_trip": scenarios_obj.scenario_5_simple_trip,
                    "complex_trip": scenarios_obj.scenario_6_complex_trip,
                    "full_workflow": scenarios_obj.scenario_7_full_workflow,
                    "events": scenarios_obj.scenario_8_event_search,
                    "geocoding": scenarios_obj.scenario_9_geocoding,
                    "multi_location": scenarios_obj.scenario_10_multi_location,
                }
                
                if scenario_id not in scenario_map:
                    raise ValueError(f"Unknown scenario: {scenario_id}")
                
                scenario_func = scenario_map[scenario_id]
                
                # Run fixed request count test
                print(f"Running {num_requests} requests with scenario: {scenario_id}")
                start_time = time.time()
                
                result = tester.run_fixed_request_count(
                    num_requests=num_requests,
                    scenario_func=scenario_func,
                    max_concurrent=max_concurrent
                )
                
                elapsed_time = time.time() - start_time
                
                # Collect final metrics
                metrics_collector.generate_summary()
                metrics = metrics_collector.get_metrics()
                
                # Clean up temp config
                if temp_config_path.exists():
                    temp_config_path.unlink()
            
            except Exception as e:
                # Clean up temp config on error
                if temp_config_path.exists():
                    temp_config_path.unlink()
                raise
        
        elapsed_time = time.time() - start_time if 'elapsed_time' not in locals() else elapsed_time
        
        # Collect network metrics
        network_metrics = network_monitor.get_statistics()
        
        # Save metrics
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        metrics_file = results_dir / f"metrics_{platform}_{num_requests}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if 'metrics_collector' in locals():
            metrics_collector.save_metrics(str(metrics_file))
        
        # Combine results
        platform_result = {
            "platform": platform,
            "num_requests": num_requests,
            "scenario": scenario_id,
            "test_duration_seconds": elapsed_time,
            "endpoint": endpoint,
            "metrics_file": str(metrics_file) if 'metrics_file' in locals() else None,
            "load_test_results": result,
            "system_metrics": metrics.get("summary", {}) if 'metrics' in locals() else {},
            "network_metrics": network_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Display summary
        print(f"\n{platform.upper()} Test Results:")
        print(f"  Total Requests: {result.get('total_requests', 0)}")
        print(f"  Successful: {result.get('successful_requests', 0)}")
        print(f"  Failed: {result.get('failed_requests', 0)}")
        print(f"  Success Rate: {result.get('success_rate', 0)*100:.1f}%")
        print(f"  Throughput: {result.get('throughput_rps', 0):.2f} RPS")
        print(f"  Mean Latency: {result.get('mean_latency_ms', 0):.2f} ms")
        print(f"  P95 Latency: {result.get('p95_latency_ms', 0):.2f} ms")
        print(f"  P99 Latency: {result.get('p99_latency_ms', 0):.2f} ms")
        print(f"  Test Duration: {elapsed_time:.2f} seconds")
        
        # Display network metrics if available
        if network_metrics:
            print(f"\n  Network Metrics:")
            print(f"    Mean Network Latency: {network_metrics.get('mean_latency_ms', 0):.2f} ms")
            print(f"    Median Network Latency: {network_metrics.get('median_latency_ms', 0):.2f} ms")
            print(f"    P95 Network Latency: {network_metrics.get('p95_latency_ms', 0):.2f} ms")
            print(f"    P99 Network Latency: {network_metrics.get('p99_latency_ms', 0):.2f} ms")
            print(f"    Mean DNS Lookup Time: {network_metrics.get('mean_dns_time_ms', 0):.2f} ms")
            print(f"    Network Success Rate: {network_metrics.get('success_rate', 0)*100:.1f}%")
            print(f"    Network Error Rate: {network_metrics.get('error_rate', 0)*100:.1f}%")
        
        # Display system metrics
        if 'metrics' in locals():
            system_summary = metrics.get("summary", {})
            if system_summary:
                print(f"\n  System Metrics:")
                print(f"    Average CPU: {system_summary.get('average_cpu_percent', 0):.1f}%")
                print(f"    Average Memory: {system_summary.get('average_memory_percent', 0):.1f}%")
        
        return platform_result
    
    def compare_results(self, ec2_results: Dict[str, Any], ecs_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare EC2 and ECS results"""
        comparison = {
            "ec2_results": ec2_results,
            "ecs_results": ecs_results,
            "differences": {}
        }
        
        ec2_load = ec2_results.get("load_test_results", {})
        ecs_load = ecs_results.get("load_test_results", {})
        
        # Calculate differences
        metrics_to_compare = [
            "throughput_rps",
            "mean_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "success_rate",
            "test_duration_seconds"
        ]
        
        # Network metrics comparison
        ec2_network = ec2_results.get("network_metrics", {})
        ecs_network = ecs_results.get("network_metrics", {})
        
        network_metrics_to_compare = [
            "mean_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "mean_dns_time_ms",
            "success_rate"
        ]
        
        differences = {}
        for metric in metrics_to_compare:
            ec2_val = ec2_load.get(metric, 0) if metric != "test_duration_seconds" else ec2_results.get(metric, 0)
            ecs_val = ecs_load.get(metric, 0) if metric != "test_duration_seconds" else ecs_results.get(metric, 0)
            
            if ec2_val == 0 or ecs_val == 0:
                continue
            
            if metric in ["throughput_rps", "success_rate"]:
                # Higher is better
                diff_pct = ((ecs_val - ec2_val) / ec2_val) * 100
                winner = "ECS" if ecs_val > ec2_val else "EC2"
            else:
                # Lower is better (latency, duration)
                diff_pct = ((ec2_val - ecs_val) / ec2_val) * 100
                winner = "ECS" if ecs_val < ec2_val else "EC2"
            
            differences[metric] = {
                "ec2": ec2_val,
                "ecs": ecs_val,
                "difference_pct": diff_pct,
                "winner": winner
            }
        
        # Compare network metrics
        network_differences = {}
        for metric in network_metrics_to_compare:
            ec2_val = ec2_network.get(metric, 0)
            ecs_val = ecs_network.get(metric, 0)
            
            if ec2_val == 0 or ecs_val == 0:
                continue
            
            if metric == "success_rate":
                # Higher is better
                diff_pct = ((ecs_val - ec2_val) / ec2_val) * 100
                winner = "ECS" if ecs_val > ec2_val else "EC2"
            else:
                # Lower is better (latency, DNS time)
                diff_pct = ((ec2_val - ecs_val) / ec2_val) * 100
                winner = "ECS" if ecs_val < ec2_val else "EC2"
            
            network_differences[f"network_{metric}"] = {
                "ec2": ec2_val,
                "ecs": ecs_val,
                "difference_pct": diff_pct,
                "winner": winner
            }
        
        # Merge network differences into main differences
        differences.update(network_differences)
        
        comparison["differences"] = differences
        
        # Overall winner
        winner_score = {"EC2": 0, "ECS": 0}
        for metric, diff in differences.items():
            if diff["winner"]:
                winner_score[diff["winner"]] += 1
        
        comparison["overall_winner"] = max(winner_score, key=winner_score.get) if winner_score else "Tie"
        comparison["winner_score"] = winner_score
        
        return comparison
    
    def run_comparison(
        self,
        num_requests: int,
        scenario_id: str = "simple_trip",
        max_concurrent: int = 50,
        test_ec2: bool = True,
        test_ecs: bool = True
    ) -> Dict[str, Any]:
        """Run comparison tests on both platforms"""
        print(f"\n{'='*70}")
        print(f"EC2 vs ECS Comparison Test")
        print(f"Requests: {num_requests} | Scenario: {scenario_id}")
        print(f"{'='*70}")
        
        # Test EC2
        if test_ec2:
            try:
                ec2_results = self.run_test_on_platform(
                    platform="ec2",
                    num_requests=num_requests,
                    scenario_id=scenario_id,
                    max_concurrent=max_concurrent,
                    endpoint=self.ec2_endpoint
                )
                self.results["ec2"] = ec2_results
            except Exception as e:
                print(f"Error testing EC2: {e}")
                import traceback
                traceback.print_exc()
                self.results["ec2"] = {"error": str(e)}
        
        # Test ECS
        if test_ecs:
            try:
                ecs_results = self.run_test_on_platform(
                    platform="ecs",
                    num_requests=num_requests,
                    scenario_id=scenario_id,
                    max_concurrent=max_concurrent,
                    endpoint=self.ecs_endpoint
                )
                self.results["ecs"] = ecs_results
            except Exception as e:
                print(f"Error testing ECS: {e}")
                import traceback
                traceback.print_exc()
                self.results["ecs"] = {"error": str(e)}
        
        # Compare results if both succeeded
        if "error" not in self.results.get("ec2", {}) and "error" not in self.results.get("ecs", {}):
            comparison = self.compare_results(
                self.results["ec2"],
                self.results["ecs"]
            )
            self.results["comparison"] = comparison
            
            # Display comparison
            self._display_comparison(comparison)
        
        # Save results to results directory
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        results_file = results_dir / f"ec2_ecs_comparison_{num_requests}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Results saved to: {results_file}")
        print(f"{'='*70}")
        
        return self.results
    
    def _display_comparison(self, comparison: Dict[str, Any]):
        """Display comparison results"""
        print(f"\n{'='*70}")
        print("COMPARISON RESULTS")
        print(f"{'='*70}")
        
        differences = comparison.get("differences", {})
        
        print("\nMetric Comparison:")
        print(f"{'Metric':<25} {'EC2':<15} {'ECS':<15} {'Difference':<15} {'Winner':<10}")
        print("-" * 80)
        
        for metric, diff in differences.items():
            ec2_val = diff["ec2"]
            ecs_val = diff["ecs"]
            diff_pct = diff["difference_pct"]
            winner = diff["winner"]
            
            # Format values based on metric type
            if "latency" in metric or "dns_time" in metric:
                ec2_str = f"{ec2_val:.2f} ms"
                ecs_str = f"{ecs_val:.2f} ms"
            elif "rps" in metric:
                ec2_str = f"{ec2_val:.2f} RPS"
                ecs_str = f"{ecs_val:.2f} RPS"
            elif "rate" in metric:
                ec2_str = f"{ec2_val*100:.1f}%"
                ecs_str = f"{ecs_val*100:.1f}%"
            elif "duration" in metric:
                ec2_str = f"{ec2_val:.2f} s"
                ecs_str = f"{ecs_val:.2f} s"
            else:
                ec2_str = str(ec2_val)
                ecs_str = str(ecs_val)
            
            diff_str = f"{diff_pct:+.1f}%"
            
            print(f"{metric:<25} {ec2_str:<15} {ecs_str:<15} {diff_str:<15} {winner:<10}")
        
        print(f"\n{'='*70}")
        print(f"Overall Winner: {comparison.get('overall_winner', 'Tie')}")
        print(f"Score: EC2={comparison.get('winner_score', {}).get('EC2', 0)}, "
              f"ECS={comparison.get('winner_score', {}).get('ECS', 0)}")
        print(f"{'='*70}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EC2 vs ECS Comparison Tool")
    parser.add_argument(
        "--requests",
        type=int,
        required=True,
        choices=list(range(1000, 100001)),
        help="Number of requests to test (1000 or 10000)"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="simple_trip",
        choices=["simple_flight", "hotel", "weather", "currency", "simple_trip",
                 "complex_trip", "full_workflow", "events", "geocoding", "multi_location"],
        help="Test scenario to use"
    )
    parser.add_argument(
        "scenario_positional",
        type=str,
        nargs="?",
        default=None,
        choices=["simple_flight", "hotel", "weather", "currency", "simple_trip",
                 "complex_trip", "full_workflow", "events", "geocoding", "multi_location"],
        help="Test scenario to use (positional argument, overrides --scenario if provided)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=50,
        help="Maximum concurrent requests (default: 50)"
    )
    parser.add_argument(
        "--ec2-only",
        action="store_true",
        help="Test only EC2"
    )
    parser.add_argument(
        "--ecs-only",
        action="store_true",
        help="Test only ECS"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file (default: config/app_config.yaml)"
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="AWS profile to use (e.g., arunbhy)"
    )
    parser.add_argument(
        "--ec2-endpoint",
        type=str,
        default=None,
        help="EC2 HTTP endpoint URL (e.g., http://54.123.45.67:8501 or http://ec2.example.com:8501)"
    )
    parser.add_argument(
        "--ecs-endpoint",
        type=str,
        default=None,
        help="ECS HTTP endpoint URL (e.g., http://54.123.45.68:8501 or http://ecs.example.com:8501)"
    )
    
    args = parser.parse_args()
    
    # Clean endpoint URLs to remove any trailing argument fragments
    # This handles cases where shell parsing might incorrectly concatenate arguments
    if args.ec2_endpoint:
        args.ec2_endpoint = EC2ECSComparison._clean_endpoint(args.ec2_endpoint)
    if args.ecs_endpoint:
        args.ecs_endpoint = EC2ECSComparison._clean_endpoint(args.ecs_endpoint)
    
    # Use positional scenario if provided, otherwise use --scenario flag
    scenario = args.scenario_positional if args.scenario_positional else args.scenario
    
    # #region agent log
    try: log_path = '/Users/arunbhyashaswi/Drive/Code/Travel_Planner/mcp_travelassistant-main/Travel_assistant/.cursor/debug.log'; os.makedirs(os.path.dirname(log_path), exist_ok=True); log_file = open(log_path, 'a'); log_file.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"ec2_ecs_comparison.py:831","message":"Args parsed from command line","data":{"ec2_endpoint":args.ec2_endpoint,"ecs_endpoint":args.ecs_endpoint,"ec2_endpoint_repr":repr(args.ec2_endpoint) if args.ec2_endpoint else None,"ecs_endpoint_repr":repr(args.ecs_endpoint) if args.ecs_endpoint else None},"timestamp":int(time.time()*1000)}) + '\n'); log_file.close()
    except: pass
    # #endregion
    
    test_ec2 = not args.ecs_only
    test_ecs = not args.ec2_only
    
    try:
        comparison = EC2ECSComparison(
            config_path=args.config, 
            aws_profile=args.profile,
            ec2_endpoint=args.ec2_endpoint,
            ecs_endpoint=args.ecs_endpoint
        )
        results = comparison.run_comparison(
            num_requests=args.requests,
            scenario_id=scenario,
            max_concurrent=args.max_concurrent,
            test_ec2=test_ec2,
            test_ecs=test_ecs
        )
        
        print("\n" + "="*70)
        print("Comparison Complete!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nComparison interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running comparison: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
