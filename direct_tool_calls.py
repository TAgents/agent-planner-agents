#!/usr/bin/env python3
"""
Example script demonstrating direct MCP tool calls.

This script creates a coordination agent with MCP tools and allows
direct interaction with specific tools through a simple command interface.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Import the refactored MCP tool setup
from tools.mcp_tools import setup_planning_mcp_tools

# Load environment variables
load_dotenv()

async def main():
    """Main function to create and interact with the agent directly through tools."""
    try:
        # Check required environment variables
        planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
        if not planning_mcp_path:
            raise ValueError("PLANNING_MCP_PATH environment variable must be set")
        
        planning_api_token = os.environ.get("PLANNING_API_TOKEN")
        if not planning_api_token:
            raise ValueError("PLANNING_API_TOKEN environment variable must be set")
        
        # Connect to the planning MCP server
        print("--- Connecting to planning-system-mcp server ---")
        planning_tools, planning_stack = await setup_planning_mcp_tools()
        
        async with planning_stack:
            # Print the tools discovered
            print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s): ---")
            for tool in planning_tools:
                print(f"  - {tool.name}")
            
            # Create agent context for tool calls
            tool_context = {"agent": {"name": "direct_tool_calls"}}
            
            # Interactive agent session - Direct interaction with tools
            print("\n--- Direct Tool Call Session ---")
            print("Type 'exit' to quit")
            print("Available commands:")
            print("  list_plans - List all available plans")
            print("  find_plans [query] - Search for plans containing the query")
            print("  get_plan [id] - Get details of a specific plan")
            print("  create_plan [title] [description] - Create a new plan")
            print("  help - Show available commands")
            
            while True:
                # Get user input
                user_input = input("\nCommand: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                # Simple command parser
                try:
                    parts = user_input.split()
                    command = parts[0].lower() if parts else ""
                    
                    if command == "help":
                        print("\nAvailable commands:")
                        print("  list_plans - List all available plans")
                        print("  find_plans [query] - Search for plans containing the query")
                        print("  get_plan [id] - Get details of a specific plan")
                        print("  create_plan [title] [description] - Create a new plan")
                        print("  help - Show this help message")
                        print("  exit - Quit the program")
                    
                    elif command == "list_plans":
                        list_plans_tool = next((tool for tool in planning_tools if tool.name == "list_plans"), None)
                        if list_plans_tool:
                            result = await list_plans_tool.run_async(args={}, tool_context=tool_context)
                            result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                            print(f"\nPlans:\n{result_text}")
                        else:
                            print("list_plans tool not found")
                    
                    elif command == "find_plans" and len(parts) > 1:
                        query = " ".join(parts[1:])
                        find_plans_tool = next((tool for tool in planning_tools if tool.name == "find_plans"), None)
                        if find_plans_tool:
                            result = await find_plans_tool.run_async(args={"query": query}, tool_context=tool_context)
                            result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                            print(f"\nSearch Results:\n{result_text}")
                        else:
                            print("find_plans tool not found")
                    
                    elif command == "get_plan" and len(parts) > 1:
                        plan_id = parts[1]
                        get_plan_nodes_tool = next((tool for tool in planning_tools if tool.name == "get_plan_nodes"), None)
                        if get_plan_nodes_tool:
                            result = await get_plan_nodes_tool.run_async(args={"plan_id": plan_id}, tool_context=tool_context)
                            result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                            print(f"\nPlan Structure:\n{result_text}")
                        else:
                            print("get_plan_nodes tool not found")
                    
                    elif command == "create_plan" and len(parts) > 2:
                        title = parts[1]
                        description = " ".join(parts[2:])
                        create_plan_tool = next((tool for tool in planning_tools if tool.name == "create_plan"), None)
                        if create_plan_tool:
                            result = await create_plan_tool.run_async(
                                args={"title": title, "description": description, "status": "draft"}, 
                                tool_context=tool_context
                            )
                            result_text = result.content[0].text if hasattr(result, 'content') else str(result)
                            print(f"\nPlan Created:\n{result_text}")
                        else:
                            print("create_plan tool not found")
                    
                    else:
                        print("Unknown command or missing arguments. Type 'help' for available commands.")
                        
                except Exception as e:
                    print(f"Error processing command: {e}")
    
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
