# coordination/agent.py

import os
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# --- Import AgentTool and other agent factories ---
from google.adk.tools.agent_tool import AgentTool
from agents.backend_dev.agent import create_backend_dev_agent
from agents.frontend_dev.agent import create_frontend_dev_agent
from agents.designer.agent import create_designer_agent
# --- REMOVE RESEARCH AGENT IMPORT ---
# from agents.research.agent import create_research_agent
from agents.tester.agent import create_tester_agent
from agents.plan_optimizer.agent import create_plan_optimizer_agent

# --- Import CustomGoogleSearchTool ---
from agents.research.google_search_custom_tool import CustomGoogleSearchTool

# Import MCP tools
from tools.mcp_tools import setup_planning_mcp_tools

load_dotenv()

async def create_coordinator_agent():
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    all_coordinator_tools = []

    try:
        print("--- Initializing Coordination Agent ---")
        # ... (connect to planning MCP, add planning_tools) ...
        print("--- Connecting to planning-system-mcp server ---")
        planning_tools, planning_stack = await setup_planning_mcp_tools()
        await exit_stack.enter_async_context(planning_stack)
        all_coordinator_tools.extend(planning_tools)
        print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s). ---")


        # --- Add Custom Google Search Tool Directly to Coordinator ---
        print("--- Attempting to set up Custom Google Search tool for Coordinator ---")
        try:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            programmable_search_engine_id = os.environ.get("PROGRAMMABLE_SEARCH_ENGINE_ID")
            if not google_api_key or not programmable_search_engine_id:
                print("Warning: API Key or CX ID missing. Google Search tool disabled.")
            else:
                search_tool_instance = CustomGoogleSearchTool(
                    api_key=google_api_key,
                    search_engine_id=programmable_search_engine_id
                )
                all_coordinator_tools.append(search_tool_instance)
                print(f"--- Successfully added '{search_tool_instance.name}' tool to Coordinator ---")
        except Exception as e:
            print(f"ERROR: Failed to initialize CustomGoogleSearchTool for Coordinator: {e}")
        # --- End Adding Search Tool ---


        # --- Initialize and Wrap OTHER Specialized Agents ---
        specialized_agent_factories = [
            ("Backend Developer Agent", create_backend_dev_agent, "backend_developer_agent"),
            ("Frontend Developer Agent", create_frontend_dev_agent, "frontend_developer_agent"),
            ("Designer Agent", create_designer_agent, "designer_agent"),
            # --- REMOVE RESEARCH AGENT FROM THIS LIST ---
            ("Tester Agent", create_tester_agent, "tester_agent"),
            ("Plan Optimizer Agent", create_plan_optimizer_agent, "plan_optimizer_agent")
        ]
        agent_descriptions_map = {} # Still useful for other agents

        for display_name, factory_func, agent_id in specialized_agent_factories:
            try:
                print(f"--- Creating {display_name} ---")
                agent_instance, agent_stack = await factory_func()
                await exit_stack.enter_async_context(agent_stack)
                wrapped_agent_tool = AgentTool(agent=agent_instance)
                all_coordinator_tools.append(wrapped_agent_tool)
                agent_descriptions_map[agent_id] = agent_instance.description
                print(f"--- Successfully created and wrapped agent '{agent_id}' using AgentTool ---")
            except Exception as e:
                print(f"Warning: Failed to initialize or wrap {display_name} ({agent_id}): {e}")

        print(f"--- Total tools/agents available to Coordinator: {len(all_coordinator_tools)} ---")

        coordinator_llm = LiteLlm(model="gemini/gemini-1.5-flash", api_key=os.environ.get("GOOGLE_API_KEY"))

        # --- Adjust Instructions for Coordinator Handling Search ---
        available_agent_tools_instruction = "\nYou have access to these specialized agents, which you can call as tools:\n"
        delegation_workflow_instruction = "\n2. DELEGATION WORKFLOW (USING AGENTS AS TOOLS):"
        search_handling_instruction = "\n3. RESEARCH WORKFLOW: If the user asks for research or current information, use the 'custom_google_search' tool directly to find relevant web pages. Summarize the findings for the user."
        planning_workflow_instruction = "\n4. PLAN MANAGEMENT WORKFLOW:" # Renumber
        agent_tool_names = []

        for agent_tool in all_coordinator_tools:
            if isinstance(agent_tool, AgentTool) and agent_tool.name in agent_descriptions_map: # Check if it's a wrapped agent we know
                 agent_name = agent_tool.name
                 agent_tool_names.append(agent_name)
                 agent_desc = agent_descriptions_map[agent_name]
                 available_agent_tools_instruction += f"- '{agent_name}': {agent_desc}\n"
                 delegation_workflow_instruction += f"\n   - For {agent_name.replace('_agent','').replace('_',' ')} tasks: Call the '{agent_name}' tool with the specific request/query."

        if not agent_tool_names:
            # Adjust if only planning/search tools are left
            available_agent_tools_instruction = "\nNOTE: No specialized agent tools (like backend/frontend) are available."
            delegation_workflow_instruction = "\n2. DELEGATION: No specialized agents available."


        # Create the Coordinator agent
        coordinator = Agent(
            name="coordination_agent",
            description="Coordinates user communication, performs web searches, manages plans, and delegates tasks to specialized agents.",
            model=coordinator_llm,
            instruction=(
                "You are the main coordination agent. You handle user communication."
                " You manage project plans using planning tools, PERFORM WEB SEARCHES using the 'custom_google_search' tool, "
                "AND delegate tasks to specialized agents by calling them directly as tools (if available)."
                f"{available_agent_tools_instruction}"
                "\n\nWORKFLOW STEPS:\n"
                "1. ANALYZE USER REQUEST: Determine if it's for planning, research, or requires a specialized agent."
                f"{delegation_workflow_instruction}"
                f"{search_handling_instruction}" # Add the specific research workflow
                f"{planning_workflow_instruction}\n" # Add planning workflow
                "   - Use 'create_plan', 'list_plans', 'find_plans', 'get_plan_nodes', etc., as needed."
                # ... (rest of planning workflow) ...
                "\n5. MAINTAIN CONTEXT & PROVIDE UPDATES."
                "\nAlways think step-by-step. If research is needed, call 'custom_google_search'. If delegation is needed, call the appropriate agent tool."
            ),
            tools=all_coordinator_tools, # Pass list including planning tools, SEARCH tool & AgentTool instances
        )

        print(f"--- Coordinator Agent created with tools: {[getattr(t, 'name', 'Unknown') for t in all_coordinator_tools]} ---")
        return coordinator, exit_stack

    except Exception as e:
        print(f"FATAL ERROR during Coordination Agent creation: {e}")
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

root_agent = create_coordinator_agent()
