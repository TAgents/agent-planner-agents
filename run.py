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
                
            # Process the user input with the agent
            response = await agent.generate_content(user_input)
            print(f"\n{agent_name}: {response.text}\n")
    
    finally:
        # Clean up resources
        await exit_stack.__aexit__(None, None, None)

async def run_coordination_agent():
    """Initialize and run the Coordination Agent."""
    try:
        # Import coordination agent factory
        from coordination.agent import create_coordinator_agent
        
        # Create the agent and get its exit stack
        agent, exit_stack = await create_coordinator_agent()
        
        # Run the agent interactively
        await run_agent_interactive(agent, exit_stack, "Coordination Agent")
        
    except Exception as e:
        print(f"\nError initializing Coordination Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - PLANNING_MCP_PATH: Path to the planning MCP server")
        print("  - PLANNING_API_URL: URL of the planning API (default: http://localhost:3000)")
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
        
    except Exception as e:
        print(f"\nError initializing Backend Developer Agent: {e}")
        print("\nPlease check your .env file for correct configuration values:")
        print("  - FILESYSTEM_MCP_PATH: Path to the filesystem MCP server")
        print("  - CONTEXT7_MCP_PATH: Path to the Context7 MCP server")
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
    elif agent_type in ['frontend', 'designer', 'research', 'tester', 'optimizer']:
        print(f"\n{agent_type.capitalize()} Developer Agent not fully implemented yet")
        print(f"Please implement the create_{agent_type}_agent function in agents/{agent_type}/agent.py")
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
