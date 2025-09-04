#!/usr/bin/env python3
"""
Main script for running the ADK Multiagent System.

This script initializes and runs the selected agent, with the Coordination Agent
being the default entry point to the multiagent system.
"""

import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def run_agent_interactive(agent, exit_stack, agent_name):
    """
    Run an agent interactively with user input.
    
    Args:
        agent: The agent instance to run
        exit_stack: The async exit stack for cleanup
        agent_name: The name of the agent for display purposes
    """
    try:
        # Get user input and process it
        print(f"\n{agent_name} Initialized")
        print("="*len(f"{agent_name} Initialized"))
        print("Type 'exit' to quit\n")
        
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Process the user input with the agent - call it directly
            try:
                response = await agent(user_input)
                
                # Handle different response formats
                if hasattr(response, 'text'):
                    print(f"\n{agent_name}: {response.text}\n")
                elif hasattr(response, 'content'):
                    if isinstance(response.content, list) and len(response.content) > 0:
                        # Handle list of content items
                        content_text = ""
                        for item in response.content:
                            if hasattr(item, 'text'):
                                content_text += item.text
                            else:
                                content_text += str(item)
                        print(f"\n{agent_name}: {content_text}\n")
                    else:
                        print(f"\n{agent_name}: {response.content}\n")
                else:
                    print(f"\n{agent_name}: {response}\n")
                    
            except Exception as e:
                print(f"\nError processing request: {e}\n")
    
    finally:
        # Clean up resources
        await exit_stack.__aexit__(None, None, None)

async def run_coordination_agent():
    """Initialize and run the Coordination Agent."""
    try:
        # Import coordination agent factory
        from coordination.agent import create_coordinator_agent
        
        print("\nInitializing Coordination Agent with full delegation capabilities...")
        print("This may take a moment as all specialized agents are being initialized.")
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_coordinator_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Coordination Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Coordination Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Coordination Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Coordination Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - PLANNING_MCP_PATH: Path to the planning MCP server")
        print("  - PLANNING_API_URL: URL of the planning API")
        print("  - PLANNING_API_TOKEN: API token for the planning system")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_backend_dev_agent():
    """Initialize and run the Backend Developer Agent."""
    try:
        # Import backend developer agent factory
        from agents.backend_dev.agent import create_backend_dev_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_backend_dev_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Backend Developer Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Backend Developer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Backend Developer Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Backend Developer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_frontend_dev_agent():
    """Initialize and run the Frontend Developer Agent."""
    try:
        # Import frontend developer agent factory
        from agents.frontend_dev.agent import create_frontend_dev_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_frontend_dev_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Frontend Developer Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Frontend Developer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Frontend Developer Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Frontend Developer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_designer_agent():
    """Initialize and run the Designer Agent."""
    try:
        # Import designer agent factory
        from agents.designer.agent import create_designer_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_designer_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Designer Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Designer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Designer Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Designer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_research_agent():
    """Initialize and run the Research Agent."""
    try:
        # Import research agent factory
        from agents.research.agent import create_research_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_research_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Research Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Research Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Research Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Research Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_tester_agent():
    """Initialize and run the Tester Agent."""
    try:
        # Import tester agent factory
        from agents.tester.agent import create_tester_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_tester_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Tester Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Tester Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Tester Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Tester Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_plan_optimizer_agent():
    """Initialize and run the Plan Optimizer Agent."""
    try:
        # Import plan optimizer agent factory
        from agents.plan_optimizer.agent import create_plan_optimizer_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_plan_optimizer_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Plan Optimizer Agent")
        
    except ValueError as e:
        print(f"\nConfiguration Error in Plan Optimizer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nFile Not Found Error in Plan Optimizer Agent: {e}")
        print("\nPlease check that all MCP server paths exist and are correctly configured in your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error initializing Plan Optimizer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - PLANNING_MCP_PATH: Path to the planning MCP server")
        print("  - PLANNING_API_URL: URL of the planning API")
        print("  - PLANNING_API_TOKEN: API token for the planning system")
        print("  - GOOGLE_API_KEY: API key for the Google AI model")
        sys.exit(1)

async def run_selected_agent(agent_type):
    """
    Run the selected agent based on the agent_type parameter.
    
    Args:
        agent_type: The type of agent to run
    """
    if agent_type == 'coordination':
        await run_coordination_agent()
    elif agent_type == 'backend':
        await run_backend_dev_agent()
    elif agent_type == 'frontend':
        await run_frontend_dev_agent()
    elif agent_type == 'designer':
        await run_designer_agent()
    elif agent_type == 'research':
        await run_research_agent()
    elif agent_type == 'tester':
        await run_tester_agent()
    elif agent_type == 'optimizer':
        await run_plan_optimizer_agent()
    else:
        print(f"Unknown agent type: {agent_type}")

def check_environment_setup():
    """
    Check for required environment variables and paths.
    """
    required_vars = {
        "GOOGLE_API_KEY": "API key for Google AI model",
        "PLANNING_MCP_PATH": "Path to the planning MCP server",
        "PLANNING_API_TOKEN": "API token for the planning system"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("\nMissing required environment variables in .env file:")
        for var in missing_vars:
            print(var)
        print("\nPlease update your .env file with these values.")
        return False
    
    # Check that paths exist
    mcp_path = os.environ.get("PLANNING_MCP_PATH")
    if mcp_path and not os.path.exists(mcp_path):
        print(f"\nError: PLANNING_MCP_PATH ({mcp_path}) does not exist.")
        print("Please update your .env file with the correct path.")
        return False
    
    return True

def main():
    """Main entry point for the script."""
    # Check environment setup first
    if not check_environment_setup():
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run ADK Multiagent System')
    parser.add_argument('--agent', type=str, default='coordination',
                        choices=['coordination', 'backend', 'frontend', 'designer', 
                                'research', 'tester', 'optimizer'],
                        help='Agent type to run (default: coordination)')
    
    args = parser.parse_args()
    
    # Run the specified agent
    asyncio.run(run_selected_agent(args.agent))

if __name__ == '__main__':
    main()
