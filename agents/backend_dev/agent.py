"""
Backend Developer Agent for ADK Multiagent System.

This agent specializes in server-side code implementation with access to
filesystem and documentation through MCP servers.
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

async def create_backend_dev_agent():
    """
    Creates the Backend Developer agent for server-side implementation.
    
    Returns:
        Tuple of (backend developer agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Define agent LLM
        backend_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools
        filesystem_tools, filesystem_stack = await setup_filesystem_mcp_tools()
        await exit_stack.enter_async_context(filesystem_stack)
        
        context7_tools, context7_stack = await setup_context7_mcp_tools()
        await exit_stack.enter_async_context(context7_stack)
        
        # Combine all tools
        all_tools = filesystem_tools + context7_tools

        # Create the Backend Developer agent
        backend_agent = Agent(
            name="backend_developer_agent",
            description="Specializes in server-side code implementation with access to filesystem and documentation.",
            model=backend_llm,
            instruction=(
                "You are a Backend Developer Agent specializing in server-side code implementation. "
                "You have access to the filesystem and documentation through MCP servers."
                "\n\nYour responsibilities include:"
                "\n1. Generating, reviewing, and refactoring backend code"
                "\n2. Designing database schemas and API endpoints"
                "\n3. Implementing business logic and integration points"
                "\n\nWhen given a development task:"
                "\n1. Analyze the requirements and determine the appropriate technologies"
                "\n2. Access relevant documentation through the Context7 tool if needed"
                "\n3. Examine existing code in the filesystem if relevant"
                "\n4. Generate or modify code to implement the requested functionality"
                "\n5. Document your implementation decisions and approach"
                "\n\nYou should always follow best practices for the language and framework being used, "
                "write clean, maintainable code, and include appropriate error handling and logging."
            ),
            tools=all_tools,
        )

        return backend_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_backend_dev_agent()
