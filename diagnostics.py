#!/usr/bin/env python3
"""
Diagnostic script for the agent-planner-agents system.

This script checks the system configuration and connectivity.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from config import config

def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False

def check_node_package(package: str) -> bool:
    """Check if a Node.js package is available via npx."""
    try:
        result = subprocess.run(
            ["npx", "-y", package, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

async def check_planning_api() -> bool:
    """Check if the planning API is accessible."""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"ApiKey {config.planning_api_token}"}
            async with session.get(
                f"{config.planning_api_url}/health",
                headers=headers,
                timeout=5
            ) as response:
                return response.status == 200
    except:
        try:
            # Fallback to urllib
            import urllib.request
            import urllib.error
            req = urllib.request.Request(
                f"{config.planning_api_url}/health",
                headers={"Authorization": f"ApiKey {config.planning_api_token}"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except:
            return False

def main():
    """Run system diagnostics."""
    
    print("=" * 60)
    print("AGENT-PLANNER-AGENTS SYSTEM DIAGNOSTICS")
    print("=" * 60)
    
    # 1. Check Python version
    print("\n1. Python Environment")
    print("-" * 40)
    python_version = sys.version_info
    python_ok = python_version >= (3, 9)
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro} "
          f"{'✓' if python_ok else '✗ (requires 3.9+)'}")
    
    # 2. Check Node.js
    print("\n2. Node.js Environment")
    print("-" * 40)
    node_exists = check_command_exists("node")
    npm_exists = check_command_exists("npm")
    npx_exists = check_command_exists("npx")
    
    print(f"Node.js: {'✓' if node_exists else '✗ (required for MCP servers)'}")
    print(f"npm: {'✓' if npm_exists else '✗'}")
    print(f"npx: {'✓' if npx_exists else '✗ (required for MCP servers)'}")
    
    # 3. Check configuration
    print("\n3. Configuration")
    print("-" * 40)
    validation = config.validate()
    
    if validation["issues"]:
        print("Critical Issues:")
        for issue in validation["issues"]:
            print(f"  ✗ {issue}")
    else:
        print("✓ No critical issues")
    
    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠ {warning}")
    
    # 4. Check API Keys
    print("\n4. API Keys")
    print("-" * 40)
    print(f"Google API Key: {'✓ Set' if config.google_api_key else '✗ Not set'}")
    print(f"Planning API Token: {'✓ Set' if config.planning_api_token else '✗ Not set'}")
    print(f"Google Search Engine ID: {'✓ Set' if config.google_search_engine_id else '○ Using default'}")
    print(f"Brave API Key: {'✓ Set' if config.brave_api_key else '○ Not set (optional)'}")
    
    # 5. Check MCP Server Paths
    print("\n5. MCP Server Paths")
    print("-" * 40)
    
    if config.planning_mcp_path:
        exists = os.path.exists(config.planning_mcp_path)
        print(f"Planning MCP: {config.planning_mcp_path}")
        print(f"  Status: {'✓ Exists' if exists else '✗ Not found'}")
        if exists:
            index_path = os.path.join(config.planning_mcp_path, "src", "index.js")
            print(f"  Entry point: {'✓' if os.path.exists(index_path) else '✗ src/index.js not found'}")
    else:
        print("Planning MCP: Not configured")
    
    # 6. Check Planning API
    print("\n6. Planning API Connectivity")
    print("-" * 40)
    print(f"API URL: {config.planning_api_url}")
    
    if config.planning_api_token:
        api_accessible = asyncio.run(check_planning_api())
        print(f"API Status: {'✓ Accessible' if api_accessible else '✗ Not accessible'}")
    else:
        print("API Status: ⚠ Cannot check (no API token)")
    
    # 7. Check Python packages
    print("\n7. Python Dependencies")
    print("-" * 40)
    
    required_packages = [
        ("google.adk", "google-adk"),
        ("dotenv", "python-dotenv"),
        ("litellm", "litellm"),
        ("googleapiclient", "google-api-python-client")
    ]
    
    for import_name, package_name in required_packages:
        try:
            if import_name == "google.adk":
                import google.adk
                status = "✓"
            elif import_name == "dotenv":
                import dotenv
                status = "✓"
            elif import_name == "litellm":
                import litellm
                status = "✓"
            elif import_name == "googleapiclient":
                import googleapiclient
                status = "✓"
            else:
                status = "✗"
        except ImportError:
            status = "✗"
        
        print(f"{package_name}: {status}")
    
    # 8. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print("\n" + config.summary())
    
    # Provide recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if not validation["valid"]:
        print("\nTo fix critical issues:")
        for issue in validation["issues"]:
            if "GOOGLE_API_KEY" in issue:
                print("  1. Get a Google API key from https://ai.google.dev/")
                print("     Add to .env: GOOGLE_API_KEY=your_key_here")
            elif "PLANNING_MCP_PATH" in issue:
                print("  2. Clone the planning MCP server:")
                print("     git clone https://github.com/talkingagents/agent-planner-mcp.git")
                print("     Update .env: PLANNING_MCP_PATH=/path/to/agent-planner-mcp")
    
    if validation["warnings"]:
        print("\nTo enable additional features:")
        for warning in validation["warnings"]:
            if "PLANNING_API_TOKEN" in warning:
                print("  • Generate a planning API token and add to .env")
            elif "GOOGLE_SEARCH_ENGINE_ID" in warning:
                print("  • Create a Custom Search Engine at https://cse.google.com/")
            elif "BRAVE_API_KEY" in warning:
                print("  • Get a Brave Search API key from https://brave.com/search/api/")
    
    print("\nRun 'pip install -r requirements.txt' to install missing Python packages.")
    print("Run 'npm install -g @modelcontextprotocol/cli' for MCP CLI tools.")
    
    return validation["valid"]

if __name__ == "__main__":
    valid = main()
    sys.exit(0 if valid else 1)
