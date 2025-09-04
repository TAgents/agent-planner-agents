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
    
    # Initialize empty tool list
    all_tools = []
    
    try:
        # Define agent LLM
        backend_llm = LiteLlm(
            model="gemini/gemini-1.5-flash", 
            api_key=os.environ.get("GOOGLE_API_KEY")
        )

        # Setup MCP tools with graceful error handling
        try:
            print("--- Setting up filesystem tools for Backend Developer Agent ---")
            filesystem_tools, filesystem_stack = await setup_filesystem_mcp_tools()
            await exit_stack.enter_async_context(filesystem_stack)
            all_tools.extend(filesystem_tools)
            print(f"--- Successfully set up {len(filesystem_tools)} filesystem tools ---")
        except Exception as e:
            print(f"Warning: Failed to initialize filesystem tools: {e}")
            print("Backend Developer Agent will continue without filesystem tools")
        
        try:
            print("--- Setting up Context7 tools for Backend Developer Agent ---")
            context7_tools, context7_stack = await setup_context7_mcp_tools()
            await exit_stack.enter_async_context(context7_stack)
            all_tools.extend(context7_tools)
            print(f"--- Successfully set up {len(context7_tools)} Context7 tools ---")
        except Exception as e:
            print(f"Warning: Failed to initialize Context7 tools: {e}")
            print("Backend Developer Agent will continue without Context7 tools")

        # Create the Backend Developer agent
        backend_agent = Agent(
            name="backend_developer_agent",
            description="Specializes in server-side code implementation with access to filesystem and documentation.",
            model=backend_llm,
            instruction=(
                "You are a Backend Developer Agent specializing in server-side code implementation. "
                f"You have access to {len(all_tools)} tools for filesystem and documentation access.\n\n"
                
                "Your responsibilities include:\n"
                "1. Generating, reviewing, and refactoring backend code\n"
                "2. Designing database schemas and API endpoints\n"
                "3. Implementing business logic and integration points\n"
                "4. Setting up server infrastructure and deployment configurations\n"
                "5. Optimizing performance and scalability\n\n"
                
                "When given a development task:\n"
                "1. Analyze the requirements and determine the appropriate technologies\n"
                "2. Access relevant documentation through the Context7 tool if available\n"
                "3. Examine existing code in the filesystem if available\n"
                "4. Generate or modify code to implement the requested functionality\n"
                "5. Document your implementation decisions and approach\n\n"
                
                "Best practices to follow:\n"
                "- Write clean, maintainable, and well-documented code\n"
                "- Include appropriate error handling and logging\n"
                "- Follow SOLID principles and design patterns\n"
                "- Consider security implications (input validation, authentication, etc.)\n"
                "- Write unit tests when appropriate\n"
                "- Use environment variables for configuration\n"
                "- Implement proper API versioning and documentation\n\n"
                
                "Technologies you're proficient in:\n"
                "- Node.js/Express, Python/FastAPI/Django, Java/Spring Boot\n"
                "- PostgreSQL, MongoDB, Redis, Elasticsearch\n"
                "- REST APIs, GraphQL, WebSockets, gRPC\n"
                "- Docker, Kubernetes, CI/CD pipelines\n"
                "- AWS, GCP, Azure cloud services\n"
                "- Message queues (RabbitMQ, Kafka)\n"
                "- Authentication/Authorization (JWT, OAuth2, SAML)"
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
