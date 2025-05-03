#!/usr/bin/env python3
"""
Test script for MCP tools integration.

This script tests the connection to the MCP server and the ability to use MCP tools.
It can test different MCP servers based on the provided server type.
"""

import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Import the refactored MCP tool setup functions
from tools.mcp_tools import (
    setup_planning_mcp_tools,
    setup_context7_mcp_tools,
    setup_filesystem_mcp_tools,
    setup_playwright_mcp_tools
)

async def test_mcp_connection(server_type):
    """
    Test the connection to the specified MCP server.
    
    Args:
        server_type: The type of MCP server to test (planning, context7, filesystem, playwright)
    
    Returns:
        True if the connection was successful, False otherwise
    """
    # Load environment variables
    load_dotenv()
    
    try:
        # Setup MCP tools based on the server type
        if server_type == "planning":
            print(f"--- Testing connection to Planning MCP server ---")
            tools, exit_stack = await setup_planning_mcp_tools()
        elif server_type == "context7":
            print(f"--- Testing connection to Context7 MCP server ---")
            tools, exit_stack = await setup_context7_mcp_tools()
        elif server_type == "filesystem":
            print(f"--- Testing connection to Filesystem MCP server ---")
            tools, exit_stack = await setup_filesystem_mcp_tools()
        elif server_type == "playwright":
            print(f"--- Testing connection to Playwright MCP server ---")
            tools, exit_stack = await setup_playwright_mcp_tools()
        else:
            print(f"Unknown server type: {server_type}")
            return False
        
        async with exit_stack:
            # Print the tools discovered
            print(f"--- Connected to {server_type}-mcp. Discovered {len(tools)} tool(s). ---")
            for tool in tools:
                print(f"  - Discovered tool: {tool.name}")
            
            # Create a simple agent for testing context
            test_agent = Agent(
                name="test_agent",
                description=f"A test agent for {server_type} MCP tools",
                model=LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY")),
                instruction=f"You are a test agent for {server_type} MCP tools.",
                tools=tools,
            )
            
            # For planning tools, test a specific tool
            if server_type == "planning":
                list_plans_tool = next((tool for tool in tools if tool.name == "list_plans"), None)
                if list_plans_tool:
                    print("--- Testing list_plans tool ---")
                    try:
                        # Create a proper context for the tool run
                        tool_context = {"agent": test_agent}
                        
                        # Run the tool with empty args and the context
                        result = await list_plans_tool.run_async(args={}, tool_context=tool_context)
                        
                        # Check if result has content field (newer ADK format) or is direct result
                        result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                        print(f"Result (first 500 chars): {result_text[:500]}...")
                    except Exception as e:
                        print(f"Error running list_plans tool: {e}")
                        return False
                else:
                    print("--- list_plans tool not found ---")
            
            print(f"\nSuccessfully connected to {server_type} MCP server and discovered {len(tools)} tools.")
            return True
    
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        return False
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test MCP server connections')
    parser.add_argument('--server', type=str, default='planning',
                        choices=['planning', 'context7', 'filesystem', 'playwright', 'all'],
                        help='MCP server type to test (default: planning)')
    
    args = parser.parse_args()
    
    if args.server == 'all':
        # Test all MCP servers
        servers = ['planning', 'context7', 'filesystem', 'playwright']
        results = {}
        
        for server in servers:
            print(f"\n{'=' * 40}")
            print(f"Testing {server.upper()} MCP Server")
            print(f"{'=' * 40}")
            
            success = asyncio.run(test_mcp_connection(server))
            results[server] = success
        
        # Print summary
        print("\n" + "=" * 40)
        print("MCP Connection Test Results")
        print("=" * 40)
        
        all_successful = True
        for server, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"{server.ljust(10)}: {status}")
            all_successful = all_successful and success
        
        sys.exit(0 if all_successful else 1)
    else:
        # Test a specific MCP server
        success = asyncio.run(test_mcp_connection(args.server))
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
