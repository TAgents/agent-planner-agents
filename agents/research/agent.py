"""
Research Agent for ADK Multiagent System.

This agent specializes in gathering information with web search capabilities.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import MCP tools setup functions
from tools.mcp_tools import setup_web_search_mcp_tools

# Load environment variables
load_dotenv()

async def create_research_agent():
    """
    Creates the Research agent for information gathering.
    
    Returns:
        Tuple of (research agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Define agent LLM
        research_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Setup MCP tools
        web_search_tools, web_search_stack = await setup_web_search_mcp_tools()
        await exit_stack.enter_async_context(web_search_stack)

        # Create the Research agent
        research_agent = Agent(
            name="research_agent",
            description="Specializes in gathering information with web search capabilities.",
            model=research_llm,
            instruction=(
                "You are a Research Agent specializing in gathering information using web search capabilities. "
                "Your primary role is to find, analyze, and summarize information to inform development decisions."
                "\n\nYour responsibilities include:"
                "\n1. Conducting market and competitor analysis"
                "\n2. Researching technical solutions and best practices"
                "\n3. Finding and evaluating libraries, frameworks, and tools"
                "\n4. Summarizing findings for other agents"
                "\n\nWhen given a research task:"
                "\n1. Analyze the research question and break it down into searchable queries"
                "\n2. Use web search tools to gather relevant information"
                "\n3. Evaluate the credibility and relevance of sources"
                "\n4. Synthesize findings into clear, actionable insights"
                "\n5. Organize information to address the original question"
                "\n\nYou should prioritize recent, authoritative sources and provide "
                "balanced information that considers multiple perspectives when appropriate."
            ),
            tools=web_search_tools,
        )

        return research_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_research_agent()
