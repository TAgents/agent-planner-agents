"""
Research Agent for ADK Multiagent System.

This agent specializes in gathering information with search capabilities.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import web search tool if available
web_search_tool = None
try:
    # Try different possible import paths for web search
    try:
        from google.adk.tools.web_search import WebSearchTool
        web_search_available = True
    except ImportError:
        try:
            from google.adk.tools import web_search
            WebSearchTool = web_search.WebSearchTool
            web_search_available = True
        except (ImportError, AttributeError):
            try:
                # Try looking for a search tool directly
                from google.adk.tools import search
                WebSearchTool = search.SearchTool
                web_search_available = True
            except (ImportError, AttributeError):
                web_search_available = False
except Exception:
    web_search_available = False

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
    
    # Initialize empty tool list
    all_tools = []
    search_capability = "without"
    
    try:
        # Define agent LLM
        research_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # Get Google API key
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable must be set")
        
        # Create the Google Search tool if available
        if web_search_available:
            try:
                print("--- Setting up Google Search tool for Research Agent ---")
                search_tool = WebSearchTool(api_key=google_api_key)
                all_tools.append(search_tool)
                search_capability = "with"
                print(f"--- Successfully set up Google Search tool ---")
            except Exception as e:
                print(f"Warning: Failed to initialize Google Search tool: {e}")
                print("Research Agent will continue without search capabilities")
        else:
            print("--- Web search tools not available in this ADK version ---")
            print("Research Agent will have limited capabilities")

        # Create the Research agent
        research_agent = Agent(
            name="research_agent",
            description=f"Specializes in gathering information {search_capability} search capabilities.",
            model=research_llm,
            instruction=(
                f"You are a Research Agent specializing in gathering information {search_capability} search capabilities. "
                f"You have access to {len(all_tools)} tools for information gathering."
                "\n\nYour responsibilities include:"
                "\n1. Conducting market and competitor analysis"
                "\n2. Researching technical solutions and best practices"
                "\n3. Finding and evaluating libraries, frameworks, and tools"
                "\n4. Summarizing findings for other agents"
                "\n\nWhen given a research task:"
                + ("\n1. Analyze the research question and break it down into searchable queries"
                   "\n2. Use the web_search tool to gather relevant information"
                   "\n3. Evaluate the credibility and relevance of sources" if web_search_available else
                   "\n1. Analyze the research question and provide information based on your existing knowledge"
                   "\n2. Be honest about the limitations of your knowledge"
                   "\n3. Suggest sources the user might want to check")
                + "\n\nALWAYS BE TRANSPARENT: If you don't have search capabilities or if your knowledge is limited, "
                "clearly explain this to the user and suggest they might want to seek more current information."
                "\n\nIf you do have search capabilities, prioritize recent, authoritative sources and provide "
                "balanced information that considers multiple perspectives when appropriate."
                "\n\nIMPORTANT: When using information from search results, always cite your sources. "
                "Keep direct quotes to a minimum (less than 25 words per quote) and properly attribute them. "
                "For longer information, provide a brief summary and direct users to the original source."
            ),
            tools=all_tools,
        )

        return research_agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_research_agent()
