#!/usr/bin/env python3
"""
Test script to verify MCP servers are running and responding correctly
"""

import subprocess
import json
import os
import sys
from pathlib import Path


def check_processes():
    """Check if server processes are running."""
    print("=" * 60)
    print("MCP Server Status Check")
    print("=" * 60)
    print()
    
    # Server process names to check
    servers = {
        "itinerary": "itinerary_server.py",
        "maps": "maps_server.py",
        "booking": "booking_server.py"
    }
    
    print("🔍 Checking for running server processes...")
    print()
    
    results = {}
    
    # Use ps to find processes
    try:
        ps_output = subprocess.check_output(
            ["ps", "aux"],
            text=True
        )
        
        for server_name, script_name in servers.items():
            # Look for the script in process list
            matching_lines = [line for line in ps_output.split('\n') 
                            if script_name in line and 'grep' not in line]
            
            if matching_lines:
                # Extract PID and other info
                parts = matching_lines[0].split()
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                status = parts[7]
                
                results[server_name] = {
                    "running": True,
                    "pid": pid,
                    "cpu": cpu,
                    "memory": mem,
                    "status": status,
                    "process_line": matching_lines[0]
                }
                print(f"✅ {server_name.upper()} Server")
                print(f"   PID: {pid}")
                print(f"   Status: {status}")
                print(f"   CPU: {cpu}% | Memory: {mem}%")
                print()
            else:
                results[server_name] = {
                    "running": False
                }
                print(f"❌ {server_name.upper()} Server - NOT RUNNING")
                print()
    
    except subprocess.CalledProcessError as e:
        print(f"Error checking processes: {e}")
        return results
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    running_count = sum(1 for r in results.values() if r.get("running"))
    total_count = len(results)
    
    for server_name, info in results.items():
        status_icon = "✅" if info.get("running") else "❌"
        status_text = f"RUNNING (PID: {info.get('pid')})" if info.get("running") else "NOT RUNNING"
        print(f"{status_icon} {server_name.upper()}: {status_text}")
    
    print()
    
    if running_count == total_count:
        print("🎉 All servers are running!")
        print()
        print("Note: These servers use stdio transport and communicate via")
        print("stdin/stdout. To test their functionality, use the orchestrator")
        print("or the Streamlit UI application.")
    elif running_count > 0:
        print(f"⚠️  {running_count} out of {total_count} servers are running.")
        print("   Some servers may need to be restarted.")
    else:
        print("❌ No servers are running!")
        print("   Start them by running: streamlit run ui/app.py")
    
    print("=" * 60)
    
    return results


def check_ports():
    """Check if ports are in use (for HTTP/SSE transport)."""
    print()
    print("=" * 60)
    print("Port Status Check")
    print("=" * 60)
    print()
    
    ports = {
        "itinerary": 8000,
        "maps": 8001,
        "booking": 8002
    }
    
    print("🔍 Checking server ports...")
    print()
    
    for server_name, port in ports.items():
        try:
            # Try to check if port is in use
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ Port {port} ({server_name}) - IN USE")
                print(f"   {result.stdout.strip().split(chr(10))[0]}")
            else:
                print(f"⚪ Port {port} ({server_name}) - NOT IN USE")
                print("   (This is normal for stdio transport)")
            print()
        except FileNotFoundError:
            print(f"⚠️  Cannot check port {port} - lsof not available")
            print()
        except Exception as e:
            print(f"⚠️  Error checking port {port}: {e}")
            print()


if __name__ == "__main__":
    results = check_processes()
    check_ports()
    
    # Exit with error code if not all servers are running
    running_count = sum(1 for r in results.values() if r.get("running"))
    sys.exit(0 if running_count == len(results) else 1)

