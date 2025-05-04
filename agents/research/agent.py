"""
Research Agent for ADK Multiagent System.

This agent specializes in gathering information using a custom Google Search tool.
Uses google-adk version 0.4.0+.
"""

import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# --- Import the Custom Tool ---
try:
    from .google_search_custom_tool import CustomGoogleSearchTool
    custom_search_tool_class = CustomGoogleSearchTool
    print("--- Successfully imported CustomGoogleSearchTool ---")
except ImportError as e:
    custom_search_tool_class = None
    print(f"--- Failed to import CustomGoogleSearchTool: {e} ---")
    print("--- Research Agent will not have Google Search capability. ---")
# --- End Import ---

# Load environment variables
load_dotenv()

async def create_research_agent():
    """
    Creates the Research agent for information gathering using a custom tool.

    Returns:
        Tuple of (research agent, exit_stack)
    """
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()

    agent_tools = []
    tool_name = None # To store the actual tool name

    try:
        research_llm = LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY"))

        # --- Setup Custom Google Search Tool ---
        if custom_search_tool_class:
            print("--- Attempting to set up Custom Google Search tool ---")
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            programmable_search_engine_id = os.environ.get("PROGRAMMABLE_SEARCH_ENGINE_ID")

            if not google_api_key:
                print("Warning: GOOGLE_API_KEY environment variable missing. Custom Google Search tool disabled.")
            elif not programmable_search_engine_id:
                print("Warning: PROGRAMMABLE_SEARCH_ENGINE_ID environment variable missing. Custom Google Search tool disabled.")
            else:
                try:
                    # Instantiate the Custom Tool class, passing credentials
                    custom_search_tool_instance = custom_search_tool_class(
                        api_key=google_api_key,
                        search_engine_id=programmable_search_engine_id
                    )
                    agent_tools.append(custom_search_tool_instance)
                    # Get the actual tool name (should be 'custom_google_search' as defined in the class)
                    tool_name = custom_search_tool_instance.name
                    print(f"--- Successfully created Custom Google Search tool. Agent can call it using name: '{tool_name}' ---")

                except Exception as e:
                    # Catch errors during tool initialization (e.g., API client build failure)
                    print(f"ERROR: Failed to initialize CustomGoogleSearchTool: {e}")
                    print("--- Custom Google Search tool will be unavailable. ---")
                    tool_name = None # Ensure tool_name is None if init fails
        # --- End Setup Custom Google Search Tool ---

        # --- Dynamically Generate Instructions ---
        if tool_name:
            search_instruction = (
                f"\nWhen given a research task:"
                f"\n1. Formulate the appropriate search query based on the request."
                f"\n2. IMMEDIATELY call the '{tool_name}' tool with the formulated query. Do not describe your plan first, just call the tool."
                f"\n3. Once you receive results from the '{tool_name}' tool, evaluate credibility and relevance."
                f"\n4. Synthesize findings into clear, actionable insights."
                f"\n5. Organize the synthesized information to address the original request comprehensively."
                f"\n\nIMPORTANT: Always cite your sources using the URLs provided by the search results."
                f"Provide the source URL for each piece of information extracted from the search. "
                f"Keep direct quotes to a minimum (less than 25 words per quote) and properly attribute them. "
                f"For longer information, provide a brief summary and direct users to the original source."
            )
        else:
             # Instruction when search is not available
            search_instruction = (
                "\nNOTE: Web search capability is currently unavailable."
                "\nWhen given a research task:"
                "\n1. Analyze the research question and provide information based on your existing knowledge."
                "\n2. Clearly state that you cannot perform a live web search."
                "\n3. Be honest about the limitations of your knowledge."
                "\n4. Suggest keywords or sources the user might check independently for more current information."
            )
        # --- End Instruction Generation ---

        # Create the Research agent
        research_agent = Agent(
            name="research_agent",
            description="Specializes in gathering information. May have web search capabilities via a custom tool.",
            model=research_llm,
            instruction=(
                "You are a Research Agent specializing in gathering information. "
                "Your primary role is to find, analyze, and summarize information to inform development decisions."
                "\n\nYour responsibilities include:"
                "\n1. Conducting market and competitor analysis"
                "\n2. Researching technical solutions and best practices"
                "\n3. Finding and evaluating libraries, frameworks, and tools"
                "\n4. Summarizing findings for other agents"
                + search_instruction +
                "\n\nYou should prioritize recent, authoritative sources and provide "
                "balanced information that considers multiple perspectives when appropriate."
            ),
            # --- Use the 'tools' parameter ---
            tools=agent_tools, # Pass the list containing the custom tool (or empty list)
        )

        return research_agent, exit_stack

    except Exception as e:
        print(f"FATAL ERROR during Research Agent creation: {e}")
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise

# Expose the awaitable agent factory for ADK discovery
root_agent = create_research_agent()