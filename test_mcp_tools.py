#!/usr/bin/env python3
"""
Test script for MCP tools integration.

This script tests the connection to the MCP server and the ability to use MCP tools.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Import the refactored MCP tool setup function
from tools.mcp_tools import setup_planning_mcp_tools

async def test_mcp_tools():
    """Test the connection to the MCP server and the ability to use MCP tools."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["PLANNING_MCP_PATH", "PLANNING_API_TOKEN", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease check your .env file.")
        return False
    
    try:
        # Connect to the MCP server using the async factory function
        print("--- Attempting to connect to planning-system-mcp server ---")
        planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
        planning_api_url = os.environ.get("PLANNING_API_URL", "http://localhost:3000")
        planning_api_token = os.environ.get("PLANNING_API_TOKEN")
        
        print(f"MCP Path: {planning_mcp_path}")
        print(f"API URL: {planning_api_url}")
        print(f"API Token: {'*' * (len(planning_api_token) - 4) + planning_api_token[-4:] if planning_api_token else 'Not set'}")
        
        # Get the tools and exit stack
        planning_tools, exit_stack = await setup_planning_mcp_tools()
        
        async with exit_stack:
            # Print the tools discovered
            print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s). ---")
            for tool in planning_tools:
                print(f"  - Discovered tool: {tool.name}")
            
            # Create a simple agent for testing context
            test_agent = Agent(
                name="test_agent",
                description="A test agent for MCP tools",
                model=LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY")),
                instruction="You are a test agent for MCP tools.",
                tools=planning_tools,
            )
            
            # Test the list_plans tool if available
            list_plans_tool = next((tool for tool in planning_tools if tool.name == "list_plans"), None)
            if list_plans_tool:
                print("--- Testing list_plans tool ---")
                try:
                    # Create a proper context for the tool run
                    tool_context = {"agent": test_agent}
                    
                    # Run the tool with empty args and the context
                    result = await list_plans_tool.run_async(args={}, tool_context=tool_context)
                    
                    # Check if result has content field (newer ADK format) or is direct result
                    result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                    print(f"Result: {result_text[:500]}...")  # Print first 500 chars of result
                    
                    print("\nTest successful!")
                    return True
                except Exception as e:
                    print(f"Error running list_plans tool: {e}")
                    return False
            else:
                print("--- list_plans tool not found ---")
                return False
    
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_mcp_tools())
    sys.exit(0 if success else 1)  # Exit with appropriate code for CI/automation
