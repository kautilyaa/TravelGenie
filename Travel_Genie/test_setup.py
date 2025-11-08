#!/usr/bin/env python3
"""
Quick Setup Test - Verify all components are properly installed and configured
Run this script to check if your environment is ready for Travel Genie
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("⚠️  Warning: Python 3.11+ recommended (you have 3.12+)")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = {
        'streamlit': 'Streamlit',
        'fastmcp': 'FastMCP',
        'anthropic': 'Anthropic',
        'ultralytics': 'Ultralytics (YOLO11)',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'plotly': 'Plotly'
    }
    
    missing = []
    installed = []
    
    for package, name in required_packages.items():
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            installed.append(name)
            print(f"✓ {name} installed")
        except ImportError:
            missing.append(name)
            print(f"✗ {name} NOT installed")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has API key."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_example.exists():
        print("⚠️  .env.example not found")
        return False
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Create it with: cp .env.example .env")
        print("   Then add your ANTHROPIC_API_KEY")
        return False
    
    # Check if API key is set
    with open(env_file, 'r') as f:
        content = f.read()
        if 'ANTHROPIC_API_KEY' in content and 'your_anthropic_api_key_here' not in content:
            print("✓ .env file exists with API key configured")
            return True
        else:
            print("⚠️  .env file exists but API key not configured")
            print("   Edit .env and add your ANTHROPIC_API_KEY")
            return False

def check_project_structure():
    """Check if project structure is correct."""
    required_dirs = [
        'agents',
        'mcp_servers',
        'ui',
        'utils',
        'examples'
    ]
    
    required_files = [
        'ui/app.py',
        'mcp_servers/orchestrator.py',
        'agents/claude_agent.py',
        'agents/video_analyzer.py',
        'requirements.txt'
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory '{dir_name}' exists")
        else:
            print(f"✗ Directory '{dir_name}' missing")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ File '{file_name}' exists")
        else:
            print(f"✗ File '{file_name}' missing")
            all_good = False
    
    return all_good

def test_imports():
    """Test if main modules can be imported."""
    print("\nTesting imports...")
    
    try:
        from agents.claude_agent import ClaudeAgent
        print("✓ ClaudeAgent imports successfully")
    except Exception as e:
        print(f"✗ ClaudeAgent import failed: {e}")
        return False
    
    try:
        from agents.video_analyzer import YOLO11Analyzer
        print("✓ YOLO11Analyzer imports successfully")
    except Exception as e:
        print(f"✗ YOLO11Analyzer import failed: {e}")
        return False
    
    try:
        from mcp_servers.orchestrator import MCPOrchestrator
        print("✓ MCPOrchestrator imports successfully")
    except Exception as e:
        print(f"✗ MCPOrchestrator import failed: {e}")
        return False
    
    try:
        from utils.config import get_config
        print("✓ Config utilities import successfully")
    except Exception as e:
        print(f"✗ Config utilities import failed: {e}")
        return False
    
    return True

def main():
    """Run all checks."""
    print("=" * 60)
    print("Travel Genie - Setup Verification")
    print("=" * 60)
    print()
    
    checks = {
        "Python Version": check_python_version(),
        "Project Structure": check_project_structure(),
        "Dependencies": check_dependencies(),
        "Environment File": check_env_file(),
        "Module Imports": test_imports()
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run Travel Genie!")
        print("\nNext steps:")
        print("  1. Run: streamlit run ui/app.py")
        print("  2. Or test components: python examples/integration_example.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file: cp .env.example .env")
        print("  3. Add API key to .env file")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

