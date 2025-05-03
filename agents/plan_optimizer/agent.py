"""
Plan Optimizer Agent for ADK Multiagent System.

This agent specializes in plan structure improvement and organization.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup functions
from tools.mcp_tools import setup_planning_mcp_tools

# Load environment variables
load_dotenv()

async def create_plan_optimizer_agent():
    """
    Creates the Plan Optimizer agent for plan structure improvement.
    
    Returns:
        Tuple of (plan optimizer agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    # Initialize empty tool list
    all_tools = []
    
    try:
        # Define agent LLM
        optimizer_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools with graceful error handling
        try:
            print("--- Setting up planning tools for Plan Optimizer Agent ---")
            planning_tools, planning_stack = await setup_planning_mcp_tools()
            await exit_stack.enter_async_context(planning_stack)
            all_tools.extend(planning_tools)
            print(f"--- Successfully set up {len(planning_tools)} planning tools ---")
        except Exception as e:
            print(f"Warning: Failed to initialize planning tools: {e}")
            print("Plan Optimizer Agent will continue without planning tools")

        # Create the Plan Optimizer agent
        optimizer_agent = Agent(
            name="plan_optimizer_agent",
            description="Specializes in plan structure improvement and organization.",
            model=optimizer_llm,
            instruction=(
                "You are a Plan Optimizer Agent specializing in improving and organizing plan structures. "
                f"You have access to {len(all_tools)} tools for plan management."
                "\n\nYour responsibilities include:"
                "\n1. Identifying and removing redundant or unnecessary tasks"
                "\n2. Creating missing tasks and dependencies"
                "\n3. Reorganizing plan elements for improved coherence"
                "\n4. Generating suggestions for process improvement"
                "\n\nWhen given a plan optimization task:"
                "\n1. Analyze the current plan structure and identify issues"
                "\n2. Detect redundancies, gaps, or organizational problems"
                "\n3. Make targeted improvements to the plan"
                "\n4. Document your optimization decisions and approach"
                "\n\nYou should focus on creating clear, efficient, and logical plan structures "
                "that maintain all necessary functionality while removing unnecessary complexity."
            ),
            tools=all_tools,
        )

        return optimizer_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_plan_optimizer_agent()
