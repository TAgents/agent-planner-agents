#!/usr/bin/env python3
"""
Test script for basic planning operations.

This script tests the Coordination Agent's ability to perform
basic planning operations through the MCP server.
"""

import os
import asyncio
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from coordination.agent import create_coordinator_agent

async def test_planning_operations():
    """Test basic planning operations through the Coordination Agent."""
    print("Initializing Coordination Agent for testing planning operations...")
    agent, exit_stack = await create_coordinator_agent()
    
    try:
        print("\nSTARTING PLANNING OPERATIONS TESTS\n")
        print("================================\n")
        
        # Test listing plans
        print("1. Testing list_plans operation...")
        response = await agent.generate_content("List all available plans")
        print(f"Response: {response.text}\n")
        
        # Test creating a new plan
        print("2. Testing create_plan operation...")
        test_plan_name = f"Test Project {os.urandom(4).hex()}"  # Create unique plan name
        response = await agent.generate_content(f"Create a new plan titled '{test_plan_name}' with the description 'A test project to verify planning operations'")
        print(f"Response: {response.text}\n")
        
        # Extract plan ID from response using regex for more reliable extraction
        plan_id = None
        id_matches = re.findall(r'ID[:\s]*[`"]?([0-9a-f-]+)[`"]?', response.text)
        if id_matches:
            plan_id = id_matches[0]
        
        if not plan_id:
            print("Could not extract plan ID from response.")
            return
        
        print(f"Extracted Plan ID: {plan_id}")
        
        # Test adding phases to the plan
        print("3. Testing create_node operation (adding phases)...")
        response = await agent.generate_content(f"Add a phase called 'Planning' to the plan with ID {plan_id}")
        print(f"Response: {response.text}\n")
        
        # Test adding tasks to a phase
        print("4. Testing create_node operation (adding tasks)...")
        response = await agent.generate_content(f"Add a task called 'Requirements Analysis' to the Planning phase in plan {plan_id}")
        print(f"Response: {response.text}\n")
        
        # Test updating a task status
        print("5. Testing update_node_status operation...")
        response = await agent.generate_content(f"Update the status of the Requirements Analysis task to in_progress in plan {plan_id}")
        print(f"Response: {response.text}\n")
        
        # Test getting plan details
        print("6. Testing get_plan_nodes operation...")
        response = await agent.generate_content(f"Show me the structure of plan {plan_id}")
        print(f"Response: {response.text}\n")
        
        # Test adding a comment to a task
        print("7. Testing add_comment operation...")
        response = await agent.generate_content(f"Add a comment to the Requirements Analysis task: 'Starting initial requirements gathering'")
        print(f"Response: {response.text}\n")
        
        # Test searching in a plan
        print("8. Testing search_plan operation...")
        response = await agent.generate_content(f"Search for 'requirements' in plan {plan_id}")
        print(f"Response: {response.text}\n")
        
        print("\nALL PLANNING OPERATIONS TESTS COMPLETED\n")
        return True
    
    except Exception as e:
        print(f"Error during planning operations test: {e}")
        return False
    
    finally:
        # Clean up resources
        await exit_stack.__aexit__(None, None, None)

def main():
    """Run the planning operations tests."""
    success = asyncio.run(test_planning_operations())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
