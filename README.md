# ADK Multiagent System with MCP Integration

This project implements a multiagent system using Google's Agent Development Kit (ADK) that interacts with the planning system through MCP (Model Context Protocol).

## Overview

The system features specialized agents for different development roles, each with access to role-specific MCP servers:

- **Coordination Agent**: User communication and workflow orchestration, manages plan structure
- **Backend Developer Agent**: Server-side code implementation with filesystem and documentation access
- **Frontend Developer Agent**: Client-side implementation with UI-specific MCP integrations
- **Designer Agent**: Visual and UX design with design-specific tools
- **Research Agent**: Information gathering with web search capabilities
- **Tester Agent**: Quality verification with Playwright integration
- **Plan Optimizer Agent**: Plan structure improvement and organization

## Project Status

- **Phase 1: Core Framework and Coordination Agent** ✅
  - Project structure set up
  - MCP integration utilities implemented
  - Coordination Agent implemented with planning tools
  - Basic planning operations tested

- **Phase 2: Developer Agents Implementation** 🔄
  - Backend Developer Agent implementation in progress
  - Frontend Developer Agent (not started)
  - Developer Agent Collaboration (not started)

- **Phase 3-6**: Support Agents, Plan Optimization, Integration, Documentation (not started)

## Project Structure

```
agent-planner-agents/
├── agents/                     # Agent implementations
│   ├── backend_dev/            # Backend Developer Agent
│   ├── frontend_dev/           # Frontend Developer Agent
│   ├── designer/               # Designer Agent
│   ├── research/               # Research Agent
│   ├── tester/                 # Tester Agent
│   └── plan_optimizer/         # Plan Optimizer Agent
├── coordination/               # Coordination Agent implementation
├── tools/                      # Common tools used by multiple agents
│   └── mcp_tools.py            # MCP integration utilities
├── tests/                      # Test scripts
│   └── test_planning.py        # Tests for basic planning operations
├── run.py                      # Main script for running the multiagent system
├── direct_tool_calls.py        # Utility for direct MCP tool calls
└── test_mcp_tools.py           # Script for testing MCP connection
```

## Prerequisites

- Python 3.9+ with pip
- Node.js 16+ (for MCP servers)
- Google AI API Key
- Planning System MCP Server
- Context7 MCP Server (for documentation)
- Filesystem MCP Server (for code files)
- Playwright MCP Server (for testing)
- Web Search MCP Server (for research)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/talkingagents/agent-planner-agents.git
cd agent-planner-agents
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Copy the example configuration file
cp .env.example .env

# Edit .env with your actual values
# IMPORTANT: Update all paths to point to the actual MCP server directories
```

5. Test the MCP connection:

```bash
python test_mcp_tools.py
```

## Configuration

The `.env` file contains important configuration values required for the system to work:

- **GOOGLE_API_KEY**: Your Google AI API key (required)
- **PLANNING_MCP_PATH**: Absolute path to the planning MCP server directory (required)
- **PLANNING_API_URL**: URL of the planning system API (default: http://localhost:3000)
- **PLANNING_API_TOKEN**: API token for the planning system (required)
- **CONTEXT7_MCP_PATH**: Path to the Context7 MCP server (required for documentation access)
- **FILESYSTEM_MCP_PATH**: Path to the filesystem MCP server (required for code file access)
- **PLAYWRIGHT_MCP_PATH**: Path to the Playwright MCP server (required for testing)
- **WEBSEARCH_MCP_PATH**: Path to the web search MCP server (required for research)

## Running the System

1. Start the Coordination Agent with planning tools:

```bash
python run.py
```

2. To run a specific agent for testing:

```bash
python run.py --agent [backend|frontend|designer|research|tester|optimizer]
```

3. To use direct MCP tool calls for specific planning operations:

```bash
python direct_tool_calls.py
```

## Testing

Run the MCP tools test to verify the connection to the planning system:

```bash
python test_mcp_tools.py
```

Run the planning operations test to verify the Coordination Agent's ability to interact with the planning system:

```bash
python -m tests.test_planning
```

## Development Workflow

### Adding a New Agent

1. Create a new directory under `agents/` (e.g., `agents/new_agent/`)
2. Create these files:
   - `__init__.py`: Exports the async factory function
   - `agent.py`: Implements the agent using the ADK framework

3. Example agent implementation:

```python
# agents/new_agent/agent.py
import os
from contextlib import AsyncExitStack
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import necessary MCP tools
from tools.mcp_tools import setup_required_mcp_tools

# Load environment variables
load_dotenv()

async def create_new_agent():
    """
    Creates a new agent with required tools.
    
    Returns:
        Tuple of (agent, exit_stack)
    """
    # Manage exit stack for async operations
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    
    try:
        # Setup required MCP tools
        tools, tool_stack = await setup_required_mcp_tools()
        await exit_stack.enter_async_context(tool_stack)
        
        # Create the agent
        agent = Agent(
            name="new_agent",
            description="Description of the new agent",
            model=LiteLlm(model="gemini/gemini-2.5-flash-preview-04-17", api_key=os.environ.get("GOOGLE_API_KEY")),
            instruction="Detailed instructions for the agent...",
            tools=tools,
        )
        
        return agent, exit_stack
        
    except Exception as e:
        # Clean up the exit stack if there was an error
        await exit_stack.__aexit__(type(e), e, e.__traceback__)
        raise
```

4. Update `__init__.py`:

```python
# agents/new_agent/__init__.py
from .agent import create_new_agent
```

5. Update `run.py` to include the new agent type

### Integrating with MCP Servers

1. Identify the required MCP tools for the agent
2. Use the appropriate setup functions from `tools/mcp_tools.py`:
   - `setup_planning_mcp_tools()` - For planning system access
   - `setup_context7_mcp_tools()` - For documentation access
   - `setup_filesystem_mcp_tools()` - For filesystem access
   - `setup_playwright_mcp_tools()` - For browser automation
   - `setup_web_search_mcp_tools()` - For web search

3. Update the agent's async factory function to use these tools
4. Properly manage the exit stack for clean resource handling

## MCP Integration

This system leverages the Model Context Protocol (MCP) for standardized communication between AI agents and external systems:

- **Planning System MCP**: For plan and task management
- **Context7 MCP**: For accessing documentation
- **Filesystem MCP**: For code management
- **Playwright MCP**: For automated testing
- **Web Search MCP**: For research and information gathering

## Best Practices

- Always use async patterns for agent creation and MCP tool setup
- Properly manage exit stacks to ensure resources are cleaned up
- Use environment variables for configuration, not hardcoded paths
- Validate required environment variables before attempting connections
- Handle errors properly and provide helpful error messages

## Next Steps

- Complete implementation of specialized agents
- Integrate agents with their respective MCP servers
- Establish collaboration patterns between agents
- Test end-to-end workflows
- Create comprehensive documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
