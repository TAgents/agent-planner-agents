"""
Frontend Developer Agent for ADK Multiagent System.

This agent specializes in client-side implementation with UI-specific MCP integrations.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup functions
from tools.mcp_tools import setup_filesystem_mcp_tools, setup_context7_mcp_tools

# Load environment variables
load_dotenv()

async def create_frontend_dev_agent():
    """
    Creates the Frontend Developer agent for client-side implementation.
    
    Returns:
        Tuple of (frontend developer agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Define agent LLM
        frontend_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools
        filesystem_tools, filesystem_stack = await setup_filesystem_mcp_tools()
        await exit_stack.enter_async_context(filesystem_stack)
        
        context7_tools, context7_stack = await setup_context7_mcp_tools()
        await exit_stack.enter_async_context(context7_stack)
        
        # Combine all tools
        all_tools = filesystem_tools + context7_tools

        # Create the Frontend Developer agent
        frontend_agent = Agent(
            name="frontend_developer_agent",
            description="Specializes in client-side implementation with UI-specific MCP integrations.",
            model=frontend_llm,
            instruction=(
                "You are a Frontend Developer Agent specializing in client-side implementation. "
                "You have access to the filesystem and documentation through MCP servers."
                "\n\nYour responsibilities include:"
                "\n1. Generating React/Angular/Vue components and interfaces"
                "\n2. Implementing responsive layouts and user interfaces"
                "\n3. Integrating with backend APIs"
                "\n4. Ensuring accessibility and cross-browser compatibility"
                "\n\nWhen given a development task:"
                "\n1. Analyze the requirements and determine the appropriate technologies"
                "\n2. Access relevant documentation through the Context7 tool if needed"
                "\n3. Examine existing code in the filesystem if relevant"
                "\n4. Generate or modify code to implement the requested UI components"
                "\n5. Document your implementation decisions and approach"
                "\n\nYou should always follow modern frontend best practices, "
                "write clean, maintainable code, ensure responsive design, "
                "and consider performance and accessibility."
            ),
            tools=all_tools,
        )

        return frontend_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_frontend_dev_agent()
