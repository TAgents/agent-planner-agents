"""
Designer Agent for ADK Multiagent System.

This agent specializes in visual and UX design with design-specific tools.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup functions
from tools.mcp_tools import setup_filesystem_mcp_tools

# Load environment variables
load_dotenv()

async def create_designer_agent():
    """
    Creates the Designer agent for visual and UX design.
    
    Returns:
        Tuple of (designer agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Define agent LLM
        designer_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools
        filesystem_tools, filesystem_stack = await setup_filesystem_mcp_tools()
        await exit_stack.enter_async_context(filesystem_stack)

        # Create the Designer agent
        designer_agent = Agent(
            name="designer_agent",
            description="Specializes in visual and UX design with design-specific tools.",
            model=designer_llm,
            instruction=(
                "You are a Designer Agent specializing in visual and UX design. "
                "You have access to the filesystem for storing and retrieving design assets."
                "\n\nYour responsibilities include:"
                "\n1. Creating design mockups and prototypes"
                "\n2. Developing visual assets and style guides"
                "\n3. Defining user flows and interaction patterns"
                "\n4. Ensuring consistent design language"
                "\n\nWhen given a design task:"
                "\n1. Analyze the requirements and user needs"
                "\n2. Research design patterns and inspiration"
                "\n3. Create design specifications and assets"
                "\n4. Document design decisions and guidelines"
                "\n\nYou should prioritize user-centered design principles, "
                "accessibility, consistency, and visual appeal in all your work."
            ),
            tools=filesystem_tools,
        )

        return designer_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_designer_agent()
