"""
Coordination Agent for ADK Multiagent System.

This agent manages user communication and delegates tasks to specialized agents.
It has direct access to the planning system through the MCP server and can delegate
tasks to specialized agents based on the nature of the request.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import specialized agent factories
from agents.backend_dev.agent import create_backend_dev_agent
from agents.frontend_dev.agent import create_frontend_dev_agent
from agents.designer.agent import create_designer_agent
from agents.research.agent import create_research_agent
from agents.tester.agent import create_tester_agent
from agents.plan_optimizer.agent import create_plan_optimizer_agent

# Import MCP tools
from tools.mcp_tools import setup_planning_mcp_tools

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
    
    # Initialize lists to track successfully created agents
    specialized_agents = []
    
    try:
        print("--- Initializing Coordination Agent with specialized agents ---")
        
        # Connect to the planning MCP server first
        print("--- Connecting to planning-system-mcp server ---")
        planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
        if not planning_mcp_path:
            raise ValueError("PLANNING_MCP_PATH environment variable must be set")
        
        planning_tools, planning_stack = await setup_planning_mcp_tools()
        await exit_stack.enter_async_context(planning_stack)
        
        # Print the tools discovered
        print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s). ---")
        
        # Initialize specialized agents with graceful error handling
        specialized_agent_factories = [
            ("Backend Developer Agent", create_backend_dev_agent),
            ("Frontend Developer Agent", create_frontend_dev_agent),
            ("Designer Agent", create_designer_agent),
            ("Research Agent", create_research_agent),
            ("Tester Agent", create_tester_agent),
            ("Plan Optimizer Agent", create_plan_optimizer_agent)
        ]
        
        for agent_name, factory_func in specialized_agent_factories:
            try:
                print(f"--- Creating {agent_name} ---")
                agent, agent_stack = await factory_func()
                await exit_stack.enter_async_context(agent_stack)
                specialized_agents.append(agent)
                print(f"--- Successfully created {agent_name} ---")
            except Exception as e:
                print(f"Warning: Failed to initialize {agent_name}: {e}")
                print(f"Coordination Agent will continue without {agent_name}")
        
        print(f"--- Total resources available: {len(planning_tools)} planning tools and {len(specialized_agents)} specialized agents ---")

        # Define a multi-model coordinator LLM
        coordinator_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Create the agent instruction, listing only the available specialized agents
        agent_names = [agent.name for agent in specialized_agents]
        agent_descriptions = []
        
        if "backend_developer_agent" in agent_names:
            agent_descriptions.append("'backend_developer_agent' - For backend code development, database design, and server-side implementation")
        
        if "frontend_developer_agent" in agent_names:
            agent_descriptions.append("'frontend_developer_agent' - For frontend/UI development, React components, and client-side implementation")
        
        if "designer_agent" in agent_names:
            agent_descriptions.append("'designer_agent' - For visual and UX design, mockups, and style guides")
        
        if "research_agent" in agent_names:
            agent_descriptions.append("'research_agent' - For gathering information, market analysis, and technical research")
        
        if "tester_agent" in agent_names:
            agent_descriptions.append("'tester_agent' - For automated testing, quality verification, and bug reporting")
        
        if "plan_optimizer_agent" in agent_names:
            agent_descriptions.append("'plan_optimizer_agent' - For optimizing and refining project plans")
        
        # Dynamic instruction based on available agents
        specialized_agents_instruction = "\n\nYou have access to these specialized agents for delegation:\n" + "\n".join([f"{i+1}. {desc}" for i, desc in enumerate(agent_descriptions)]) if agent_descriptions else ""
        
        delegation_workflow = "\n2. DELEGATION WORKFLOW:"
        if "backend_developer_agent" in agent_names:
            delegation_workflow += "\n   - For backend tasks: Delegate to the 'backend_developer_agent' for server-side code and DB designs"
        
        if "frontend_developer_agent" in agent_names:
            delegation_workflow += "\n   - For frontend tasks: Delegate to the 'frontend_developer_agent' for UI components"
        
        if "designer_agent" in agent_names:
            delegation_workflow += "\n   - For design tasks: Delegate to the 'designer_agent' for visual and UX design"
        
        if "research_agent" in agent_names:
            delegation_workflow += "\n   - For research needs: Delegate to the 'research_agent' for gathering information"
        
        if "tester_agent" in agent_names:
            delegation_workflow += "\n   - For testing needs: Delegate to the 'tester_agent' for verification"
        
        if "plan_optimizer_agent" in agent_names:
            delegation_workflow += "\n   - For plan improvement: Delegate to the 'plan_optimizer_agent'"
        
        if not agent_names:
            delegation_workflow = "\n2. NOTE: No specialized agents are currently available. Only planning operations are supported."

        # Create the Coordinator agent
        coordinator = Agent(
            name="coordination_agent",
            description="Coordinates user communication and delegates tasks to specialized agents for software development.",
            model=coordinator_llm,
            instruction=(
                "You are the main coordination agent for a software development system. "
                "You handle user communication and delegate tasks to specialized agents:"
                f"{specialized_agents_instruction}"
                "\n\nYou also manage project plans using the planning system tools. "
                "When users ask about project plans, use the appropriate planning tools to create, update, or query plans."
                "\n\nHOW DELEGATION WORKS: When you need to delegate a task to a specialized agent, "
                "you should think about which agent is most appropriate for the task based on its domain. "
                "The ADK system will automatically route your response to the appropriate sub-agent when you "
                "mention that you are delegating to a specific agent. You don't need to use any special syntax "
                "or call tools - just clearly state which agent you're delegating to in your response."
                "\n\nFOLLOW THESE WORKFLOW STEPS:\n"
                "1. ANALYZE USER REQUEST: Determine if the request is about:\n"
                "   - Project planning (creating, updating, viewing plans)\n"
                "   - Development task (backend, frontend, design)\n"
                "   - Research or information gathering\n"
                "   - Testing or quality verification\n"
                "   - Plan optimization or improvement\n"
                f"{delegation_workflow}"
                "\n\n3. PLAN MANAGEMENT WORKFLOW:\n"
                "   - For creating a new plan: Use 'create_plan' with title, description, and status\n"
                "   - For viewing plans: Use 'list_plans' or 'find_plans' or 'get_plan_by_name'\n"
                "   - For plan details: Use 'get_plan_nodes' to see structure\n"
                "   - For creating phases and tasks: Use 'create_node' with appropriate parameters\n"
                "   - For updating task status: Use 'update_node_status'\n"
                "   - For adding documentation: Use 'add_artifact'\n"
                "\n4. MAINTAIN CONTEXT: Keep track of the ongoing project, recent activities, and agent interactions"
                "\n5. PROVIDE UNIFIED UPDATES: Summarize progress and integrate feedback from specialized agents"
                "\nAlways think step-by-step, first understanding the user request, then determining the appropriate action "
                "path, and finally executing with the right tools or agent delegation."
                "\n\nNOTE ABOUT RESEARCH AGENT: The Research Agent may have limited search capabilities. "
                "If a user asks for current information and the Research Agent indicates limitations, "
                "acknowledge this and suggest that the user consult external sources for the most up-to-date information."
            ),
            tools=planning_tools,
            sub_agents=specialized_agents,
        )
        
        return coordinator, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_coordinator_agent()
