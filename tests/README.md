# ADK Multiagent System Tests

This directory contains test scripts for various components of the ADK Multiagent System.

## Available Tests

### Planning Operations Test

Tests the Coordination Agent's ability to perform basic planning operations through the MCP server.

**Running the test:**

```bash
# From the project root
python -m tests.test_planning
```

This test verifies the following operations:
- Listing plans
- Creating a new plan
- Adding phases to a plan
- Adding tasks to a phase
- Updating task status
- Viewing plan structure
- Adding comments to tasks
- Searching within a plan

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create a new Python file with a descriptive name (e.g., `test_backend_agent.py`)
2. Import necessary components from the main package
3. Add clear print statements to indicate test progress
4. Handle exceptions appropriately
5. Document test purpose and execution instructions
