"""
Research Agent for ADK Multiagent System.

This agent specializes in gathering information with web search capabilities.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import custom search tool
from tools.google_search_tool import CustomGoogleSearchTool

# Try to import MCP web search tools as fallback
try:
    from tools.mcp_tools import setup_web_search_mcp_tools
    MCP_AVAILABLE = True
except:
    MCP_AVAILABLE = False

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
    
    try:
        # Define agent LLM
        research_llm = LiteLlm(
            model="gemini/gemini-1.5-flash", 
            api_key=os.environ.get("GOOGLE_API_KEY")
        )

        # Try to set up custom Google search tool
        try:
            print("--- Setting up Google Search tool for Research Agent ---")
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
            
            if google_api_key:
                search_tool = CustomGoogleSearchTool(
                    api_key=google_api_key,
                    search_engine_id=search_engine_id
                )
                all_tools.append(search_tool)
                print("✓ Google Search tool initialized")
            else:
                print("Warning: GOOGLE_API_KEY not found, search tool disabled")
        except Exception as e:
            print(f"Warning: Failed to initialize Google Search tool: {e}")
            
            # Fall back to MCP web search if available
            if MCP_AVAILABLE and os.environ.get("BRAVE_API_KEY"):
                try:
                    print("Falling back to MCP web search tools...")
                    web_search_tools, web_search_stack = await setup_web_search_mcp_tools()
                    await exit_stack.enter_async_context(web_search_stack)
                    all_tools.extend(web_search_tools)
                    print(f"✓ MCP web search tools initialized ({len(web_search_tools)} tools)")
                except Exception as e:
                    print(f"Warning: Failed to initialize MCP web search tools: {e}")

        # Create the Research agent
        research_agent = Agent(
            name="research_agent",
            description="Specializes in gathering information with web search capabilities.",
            model=research_llm,
            instruction=(
                "You are a Research Agent specializing in gathering information using web search capabilities. "
                f"You have access to {len(all_tools)} search tool(s) for finding information online.\n\n"
                
                "Your responsibilities include:\n"
                "1. Conducting market and competitor analysis\n"
                "2. Researching technical solutions and best practices\n"
                "3. Finding and evaluating libraries, frameworks, and tools\n"
                "4. Gathering information about current trends and technologies\n"
                "5. Summarizing findings for other agents and users\n\n"
                
                "When given a research task:\n"
                "1. Break down the research question into searchable queries\n"
                "2. Use the google_search tool to gather relevant information\n"
                "3. Search for multiple perspectives and sources\n"
                "4. Evaluate the credibility and relevance of sources\n"
                "5. Synthesize findings into clear, actionable insights\n"
                "6. Organize information to directly address the original question\n\n"
                
                "Search effectively by:\n"
                "- Using specific keywords and phrases\n"
                "- Trying different search queries if initial results are insufficient\n"
                "- Looking for recent and authoritative sources\n"
                "- Cross-referencing information from multiple sources\n\n"
                
                "Always provide balanced information that considers multiple perspectives, "
                "cite your sources when possible, and clearly distinguish between facts and opinions."
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
