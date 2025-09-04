"""
Coordination Agent for ADK Multiagent System.

This agent manages user communication and delegates tasks to specialized agents.
It has direct access to the planning system through the MCP server and can
delegate tasks to specialized agents using ADK's AgentTool.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup
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
    
    # List to collect all tools
    all_tools = []
    
    try:
        # Connect to the planning MCP server
        print("--- Initializing Coordination Agent ---")
        print("--- Connecting to planning-system-mcp server ---")
        
        try:
            planning_tools, planning_stack = await setup_planning_mcp_tools()
            await exit_stack.enter_async_context(planning_stack)
            all_tools.extend(planning_tools)
            print(f"--- Connected to planning-system-mcp. Discovered {len(planning_tools)} tool(s). ---")
        except Exception as e:
            print(f"Warning: Failed to initialize planning tools: {e}")
            print("Coordination Agent will continue without planning tools")
        
        # Initialize specialized agents as tools
        print("--- Initializing specialized agents as tools ---")
        
        # Import agent factories only when needed to avoid circular imports
        # Backend Developer Agent
        try:
            print("Creating Backend Developer Agent...")
            from agents.backend_dev.agent import create_backend_dev_agent
            backend_agent, backend_stack = await create_backend_dev_agent()
            await exit_stack.enter_async_context(backend_stack)
            backend_tool = AgentTool(agent=backend_agent)
            all_tools.append(backend_tool)
            print("✓ Backend Developer Agent initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Backend Developer Agent: {e}")
        
        # Frontend Developer Agent
        try:
            print("Creating Frontend Developer Agent...")
            from agents.frontend_dev.agent import create_frontend_dev_agent
            frontend_agent, frontend_stack = await create_frontend_dev_agent()
            await exit_stack.enter_async_context(frontend_stack)
            frontend_tool = AgentTool(agent=frontend_agent)
            all_tools.append(frontend_tool)
            print("✓ Frontend Developer Agent initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Frontend Developer Agent: {e}")
        
        # Designer Agent
        try:
            print("Creating Designer Agent...")
            from agents.designer.agent import create_designer_agent
            designer_agent, designer_stack = await create_designer_agent()
            await exit_stack.enter_async_context(designer_stack)
            designer_tool = AgentTool(agent=designer_agent)
            all_tools.append(designer_tool)
            print("✓ Designer Agent initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Designer Agent: {e}")
        
        # Research Agent - with custom search tool fallback
        try:
            print("Creating Research Agent...")
            try:
                from agents.research.agent import create_research_agent
                research_agent, research_stack = await create_research_agent()
                await exit_stack.enter_async_context(research_stack)
                research_tool = AgentTool(agent=research_agent)
                all_tools.append(research_tool)
                print("✓ Research Agent initialized")
            except ImportError as e:
                print(f"Warning: Research Agent import failed: {e}")
                # Try to add search tool directly to coordinator
                try:
                    from tools.google_search_tool import CustomGoogleSearchTool
                    search_tool = CustomGoogleSearchTool()
                    all_tools.append(search_tool)
                    print("✓ Added Google Search tool directly to Coordinator")
                except Exception as se:
                    print(f"Warning: Failed to add search tool: {se}")
        except Exception as e:
            print(f"Warning: Failed to initialize Research Agent: {e}")
        
        # Tester Agent
        try:
            print("Creating Tester Agent...")
            from agents.tester.agent import create_tester_agent
            tester_agent, tester_stack = await create_tester_agent()
            await exit_stack.enter_async_context(tester_stack)
            tester_tool = AgentTool(agent=tester_agent)
            all_tools.append(tester_tool)
            print("✓ Tester Agent initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Tester Agent: {e}")
        
        # Plan Optimizer Agent
        try:
            print("Creating Plan Optimizer Agent...")
            from agents.plan_optimizer.agent import create_plan_optimizer_agent
            optimizer_agent, optimizer_stack = await create_plan_optimizer_agent()
            await exit_stack.enter_async_context(optimizer_stack)
            optimizer_tool = AgentTool(agent=optimizer_agent)
            all_tools.append(optimizer_tool)
            print("✓ Plan Optimizer Agent initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Plan Optimizer Agent: {e}")

        print(f"--- Total tools available: {len(all_tools)} ---")

        # Define a multi-model coordinator LLM
        coordinator_llm = LiteLlm(
            model="gemini/gemini-1.5-flash", 
            api_key=os.environ.get("GOOGLE_API_KEY")
        )

        # Create the Coordinator agent
        coordinator = Agent(
            name="coordination_agent",
            description="Coordinates user communication, manages plans, and delegates tasks to specialized agents.",
            model=coordinator_llm,
            instruction=(
                "You are the main coordination agent for a software development system. "
                "You handle user communication and have access to both planning tools and specialized agents as tools.\n\n"
                
                "AVAILABLE SPECIALIZED AGENTS (callable as tools):\n"
                "- backend_developer_agent: For server-side code implementation\n"
                "- frontend_developer_agent: For client-side UI implementation\n"
                "- designer_agent: For visual and UX design\n"
                "- research_agent: For information gathering and research\n"
                "- tester_agent: For automated testing and quality verification\n"
                "- plan_optimizer_agent: For optimizing and refining project plans\n"
                "- custom_google_search: Direct web search capability\n\n"
                
                "WORKFLOW STEPS:\n"
                "1. ANALYZE USER REQUEST: Determine if the request requires:\n"
                "   - Project planning (use planning tools directly)\n"
                "   - Development task (delegate to appropriate developer agent)\n"
                "   - Research (delegate to research_agent or use custom_google_search)\n"
                "   - Testing (delegate to tester_agent)\n"
                "   - Design (delegate to designer_agent)\n"
                "   - Plan optimization (delegate to plan_optimizer_agent)\n\n"
                
                "2. DELEGATION WORKFLOW:\n"
                "   When delegating to an agent, call it as a tool with the specific request.\n"
                "   Example: For backend tasks, call backend_developer_agent with the task description.\n\n"
                
                "3. PLAN MANAGEMENT WORKFLOW:\n"
                "   - Use 'search' for finding plans and nodes\n"
                "   - Use 'create_plan' for new plans\n"
                "   - Use 'create_node' for phases/tasks/milestones\n"
                "   - Use 'update_node' for status updates\n"
                "   - Use 'add_log' for comments and progress tracking\n"
                "   - Use 'manage_artifact' for documents and files\n\n"
                
                "4. MAINTAIN CONTEXT: Track ongoing projects and agent interactions\n"
                
                "5. PROVIDE UNIFIED UPDATES: Integrate feedback from all agents\n\n"
                
                "Always think step-by-step and use the appropriate tools or agents for each task."
            ),
            tools=all_tools,
        )
        
        return coordinator, exit_stack
    
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_coordinator_agent()
