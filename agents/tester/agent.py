"""
Tester Agent for ADK Multiagent System.

This agent specializes in quality verification with Playwright integration.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup functions
from tools.mcp_tools import setup_playwright_mcp_tools, setup_filesystem_mcp_tools

# Load environment variables
load_dotenv()

async def create_tester_agent():
    """
    Creates the Tester agent for quality verification.
    
    Returns:
        Tuple of (tester agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    # Initialize empty tool list
    all_tools = []
    
    try:
        # Define agent LLM
        tester_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools with graceful error handling
        try:
            print("--- Setting up Playwright tools for Tester Agent ---")
            playwright_tools, playwright_stack = await setup_playwright_mcp_tools()
            await exit_stack.enter_async_context(playwright_stack)
            all_tools.extend(playwright_tools)
            print(f"--- Successfully set up {len(playwright_tools)} Playwright tools ---")
        except Exception as e:
            print(f"Warning: Failed to initialize Playwright tools: {e}")
            print("Tester Agent will continue without Playwright tools")
        
        try:
            print("--- Setting up filesystem tools for Tester Agent ---")
            filesystem_tools, filesystem_stack = await setup_filesystem_mcp_tools()
            await exit_stack.enter_async_context(filesystem_stack)
            all_tools.extend(filesystem_tools)
            print(f"--- Successfully set up {len(filesystem_tools)} filesystem tools ---")
        except Exception as e:
            print(f"Warning: Failed to initialize filesystem tools: {e}")
            print("Tester Agent will continue without filesystem tools")

        # Create the Tester agent
        tester_agent = Agent(
            name="tester_agent",
            description="Specializes in quality verification with Playwright integration.",
            model=tester_llm,
            instruction=(
                "You are a Tester Agent specializing in quality verification using automated testing tools. "
                f"You have access to {len(all_tools)} tools for browser automation and filesystem access."
                "\n\nYour responsibilities include:"
                "\n1. Generating and executing test cases"
                "\n2. Performing automated UI and API testing"
                "\n3. Reporting bugs and quality issues"
                "\n4. Validating functionality against requirements"
                "\n\nWhen given a testing task:"
                "\n1. Analyze the requirements and determine the appropriate testing approach"
                "\n2. Create test cases that cover critical functionality"
                "\n3. Implement test scripts using Playwright when UI testing is needed"
                "\n4. Execute tests and document results"
                "\n5. Provide detailed reports on issues found"
                "\n\nYou should focus on thorough testing with good coverage, "
                "clear reproduction steps for any issues, and actionable feedback for developers."
            ),
            tools=all_tools,
        )

        return tester_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_tester_agent()
