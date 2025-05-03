"""
Coordination Agent for ADK Multiagent System.

This agent manages user communication and delegates tasks to specialized agents.
It has direct access to the planning system through the MCP server.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Load environment variables
load_dotenv()

async def create_coordinator_agent():
    """
    Creates the Coordination agent that manages user communication and delegates to specialized agents.
    
    Returns:
        Tuple of (coordinator agent, exit_stack)
    """
    # Manage multiple exit stacks for async sub-agents
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Connect to the planning MCP server
        print("--- Attempting to connect to planning-system-mcp server ---")
        planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
        if not planning_mcp_path:
            raise ValueError("PLANNING_MCP_PATH environment variable must be set")
        
        planning_api_url = os.environ.get("PLANNING_API_URL", "http://localhost:3000")
        planning_api_token = os.environ.get("PLANNING_API_TOKEN")
        if not planning_api_token:
            raise ValueError("PLANNING_API_TOKEN environment variable must be set")
        
        planning_tools, planning_stack = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command="node",
                args=[os.path.join(planning_mcp_path, "src/index.js")],
                env={
                    "API_URL": planning_api_url,
                    "API_TOKEN": planning_api_token
                }
            )
        )
        await exit_stack.enter_async_context(planning_stack)
        
        # Print the tools discovered
        print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s). ---")
        for tool in planning_tools:
            print(f"  - Discovered tool: {tool.name}")

        # Define a multi-model coordinator LLM
        coordinator_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Create the Coordinator agent
        coordinator = Agent(
            name="coordination_agent",
            description="Coordinates user communication and delegates tasks to specialized agents for software development.",
            model=coordinator_llm,
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
            tools=planning_tools,
        )
        
        return coordinator, exit_stack
    
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
# This assigns the coroutine object returned by calling the async function
root_agent = create_coordinator_agent()
