#!/usr/bin/env python3
"""
Example script demonstrating an agent with working MCP tools.

This script creates an agent with MCP tools and allows direct interaction.
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Load environment variables
load_dotenv()

async def main():
    """Main function to create and interact with the agent."""
    # Set up the planning tools
    planning_mcp_path = os.environ.get("PLANNING_MCP_PATH", "/Users/michmalk/dev/talkingagents/agent-planner-mcp")
    planning_api_url = os.environ.get("PLANNING_API_URL", "http://localhost:3000")
    planning_api_token = os.environ.get("PLANNING_API_TOKEN", "")
    
    print("--- Attempting to connect to planning-system-mcp server ---")
    print(f"MCP Path: {planning_mcp_path}")
    
    result = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="node",
            args=[os.path.join(planning_mcp_path, "src/index.js")],
            env={
                "API_URL": planning_api_url,
                "API_TOKEN": planning_api_token
            }
        )
    )
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        tools, exit_stack = result
    else:
        # Handle unexpected return type
        print(f"Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print(f"Result: {result}")
        return
    
    async with exit_stack:
        # Print the tools discovered
        print(f"--- Connected to planning-system-mcp. Discovered {len(tools)} tool(s). ---")
        for tool in tools:
            print(f"  - Discovered tool: {tool.name}")
        
        # Create the Coordination agent
        coordinator = Agent(
            name="coordination_agent",
            description="Coordinates user communication and delegates tasks to specialized agents for software development.",
            model=LiteLlm(model="gemini/gemini-2.5-flash-lite", api_key=os.environ.get("GOOGLE_API_KEY")),
            instruction=(
                "You are the main coordination agent for a software development system. "
                "You handle user communication and delegate tasks to specialized agents:"
                "\n1. Backend Developer Agent - For backend code development"
                "\n2. Frontend Developer Agent - For frontend/UI development"
                "\n3. Designer Agent - For visual and UX design"
                "\n4. Research Agent - For gathering information and research"
                "\n5. Tester Agent - For automated testing"
                "\n6. Plan Optimizer Agent - For optimizing and refining project plans"
                "\n\nYou also manage project plans using the planning system. "
                "When users ask about project plans, use the appropriate planning tools to create, update, or query plans."
                "\n\nFOLLOW THESE WORKFLOW STEPS:\n"
                "1. ANALYZE USER REQUEST: Determine if the request is about:\n"
                "   - Project planning (creating, updating, viewing plans)\n"
                "   - Development task (backend, frontend, design)\n"
                "   - Research or information gathering\n"
                "   - Testing or quality verification\n"
                "   - Plan optimization or improvement\n"
                "\n2. PLAN MANAGEMENT WORKFLOW:\n"
                "   - For creating a new plan: Use 'create_plan' with title, description, and status\n"
                "   - For viewing plans: Use 'list_plans' or 'find_plans' or 'get_plan_by_name'\n"
                "   - For plan details: Use 'get_plan_nodes' to see structure\n"
                "   - For creating phases and tasks: Use 'create_node' with appropriate parameters\n"
                "   - For updating task status: Use 'update_node_status'\n"
                "   - For adding documentation: Use 'add_artifact'\n"
                "\n3. AGENT DELEGATION WORKFLOW:\n"
                "   - Backend tasks: Delegate to Backend Developer Agent for server-side code\n"
                "   - Frontend tasks: Delegate to Frontend Developer Agent for UI implementation\n"
                "   - Design tasks: Delegate to Designer Agent for visual and UX design\n"
                "   - Research needs: Delegate to Research Agent for information gathering\n"
                "   - Testing needs: Delegate to Tester Agent for verification\n"
                "   - Plan improvement: Delegate to Plan Optimizer Agent\n"
                "\n4. MAINTAIN CONTEXT: Keep track of the ongoing project, recent activities, and agent interactions"
                "\n5. PROVIDE UNIFIED UPDATES: Summarize progress and integrate feedback from specialized agents"
                "\nAlways think step-by-step, first understanding the user request, then determining the appropriate action "
                "path, and finally executing with the right tools or agent delegation."
            ),
            tools=tools,
        )
        
        # Test the list_plans tool
        print("--- Testing list_plans tool via agent ---")
        
        # This directly uses the API to run the tool to demonstrate usage
        list_plans_tool = next((tool for tool in tools if tool.name == "list_plans"), None)
        if list_plans_tool:
            # Create a proper context for the tool run
            tool_context = {"agent": coordinator}
            
            try:
                # Call the tool with empty args and the context
                print("Calling tool: list_plans with arguments: {}")
                result = await list_plans_tool.run_async(args={}, tool_context=tool_context)
                print(f"List plans result: {result}")
            except Exception as e:
                print(f"Error running list_plans tool: {e}")
        
        # Interactive agent session - Direct interaction with tools
        print("\n--- Interactive Agent Session ---")
        print("Type 'exit' to quit")
        print("Available commands:")
        print("  list_plans - List all available plans")
        print("  find_plans [query] - Search for plans containing the query")
        print("  get_plan [id] - Get details of a specific plan")
        print("  create_plan [title] [description] - Create a new plan")
        
        while True:
            # Get user input
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Simple command parser
            try:
                parts = user_input.split()
                command = parts[0].lower() if parts else ""
                
                if command == "list_plans":
                    list_plans_tool = next((tool for tool in tools if tool.name == "list_plans"), None)
                    if list_plans_tool:
                        result = await list_plans_tool.run_async(args={}, tool_context={"agent": coordinator})
                        print(f"\nPlans:\n{result.content[0].text if hasattr(result, 'content') else result}")
                    else:
                        print("list_plans tool not found")
                
                elif command == "find_plans" and len(parts) > 1:
                    query = " ".join(parts[1:])
                    find_plans_tool = next((tool for tool in tools if tool.name == "find_plans"), None)
                    if find_plans_tool:
                        result = await find_plans_tool.run_async(args={"query": query}, tool_context={"agent": coordinator})
                        print(f"\nSearch Results:\n{result.content[0].text if hasattr(result, 'content') else result}")
                    else:
                        print("find_plans tool not found")
                
                elif command == "get_plan" and len(parts) > 1:
                    plan_id = parts[1]
                    get_plan_nodes_tool = next((tool for tool in tools if tool.name == "get_plan_nodes"), None)
                    if get_plan_nodes_tool:
                        result = await get_plan_nodes_tool.run_async(args={"plan_id": plan_id}, tool_context={"agent": coordinator})
                        print(f"\nPlan Structure:\n{result.content[0].text if hasattr(result, 'content') else result}")
                    else:
                        print("get_plan_nodes tool not found")
                
                elif command == "create_plan" and len(parts) > 2:
                    title = parts[1]
                    description = " ".join(parts[2:])
                    create_plan_tool = next((tool for tool in tools if tool.name == "create_plan"), None)
                    if create_plan_tool:
                        result = await create_plan_tool.run_async(
                            args={"title": title, "description": description, "status": "draft"}, 
                            tool_context={"agent": coordinator}
                        )
                        print(f"\nPlan Created:\n{result.content[0].text if hasattr(result, 'content') else result}")
                    else:
                        print("create_plan tool not found")
                
                else:
                    print("Unknown command or missing arguments. Try one of the available commands.")
                    
            except Exception as e:
                print(f"Error processing command: {e}")

if __name__ == "__main__":
    asyncio.run(main())
