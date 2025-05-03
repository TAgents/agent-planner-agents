# ADK Multiagent System with MCP Integration

This project implements a multiagent system using Google's Agent Development Kit (ADK) that interacts with the planning system through MCP (Model Context Protocol).

## Overview

The system features specialized agents for different development roles, each with access to role-specific MCP servers. The Coordination Agent serves as the central orchestrator, delegating tasks to specialized agents and managing overall workflow.

### Agent Architecture

- **Coordination Agent**: Central orchestrator with access to all specialized agents as tools
  - Delegates tasks to appropriate specialized agents based on the nature of the request
  - Manages project plans through the planning system
  - Provides unified interface for users

- **Specialized Agents**:
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

- **Phase 2: Developer Agents Implementation** ✅
  - Backend Developer Agent implemented with filesystem and Context7 tools
  - Frontend Developer Agent implemented with filesystem and Context7 tools
  - Delegation patterns established between Coordination Agent and specialized agents

- **Phase 3: Support Agents Implementation** ✅
  - Designer Agent implemented with filesystem access
  - Research Agent implemented with web search capabilities
  - Tester Agent implemented with Playwright and filesystem access

- **Phase 4: Plan Optimization** ✅
  - Plan Optimizer Agent implemented with planning system access

- **Phase 5: Integration and Testing** ✅
  - End-to-end workflows established across all agents
  - Delegation from Coordination Agent to specialized agents implemented

- **Phase 6: Documentation and Deployment** 🔄
  - Documentation created
  - System ready for testing and refinement

## Project Structure

```
agent-planner-agents/
├── coordination/               # Coordination Agent implementation
│   ├── __init__.py             # Exports the async factory and root_agent
│   └── agent.py                # Main coordination agent with delegation
├── agents/                     # Specialized agent implementations
│   ├── backend_dev/            # Backend Developer Agent
│   ├── frontend_dev/           # Frontend Developer Agent
│   ├── designer/               # Designer Agent
│   ├── research/               # Research Agent
│   ├── tester/                 # Tester Agent
│   └── plan_optimizer/         # Plan Optimizer Agent
├── tools/                      # Common tools used by multiple agents
│   └── mcp_tools.py            # MCP integration utilities
├── tests/                      # Test scripts
│   └── test_planning.py        # Tests for basic planning operations
├── run.py                      # Main script for running the multiagent system
├── direct_tool_calls.py        # Utility for direct MCP tool calls
└── test_mcp_tools.py           # Script for testing MCP connections
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

5. Test the MCP connections:

```bash
# Test a specific MCP server
python test_mcp_tools.py --server planning

# Test all MCP servers
python test_mcp_tools.py --server all
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

### 1. Run the Coordination Agent with the Complete Multiagent System

```bash
python run.py
```

This runs the Coordination Agent with all specialized agents as tools, enabling full delegation.

### 2. Run a Specific Agent for Testing

```bash
python run.py --agent [backend|frontend|designer|research|tester|optimizer]
```

### 3. Use Direct MCP Tool Calls

```bash
python direct_tool_calls.py
```

### 4. Use the ADK Web Interface (if ADK CLI is installed)

```bash
adk web
```

## Testing

### 1. Test MCP Connections

```bash
python test_mcp_tools.py --server [planning|context7|filesystem|playwright|websearch|all]
```

### 2. Test Planning Operations

```bash
python -m tests.test_planning
```

## Usage Examples

### 1. Planning Operations

- **List plans**: "Show me all available plans"
- **Create a plan**: "Create a new plan called 'Project Alpha' for developing a mobile app"
- **Add phases**: "Add a Design phase to Project Alpha"
- **Add tasks**: "Create a task for wireframing in the Design phase"
- **Update status**: "Mark the wireframing task as in progress"

### 2. Development Tasks

- **Backend development**: "Create a Node.js API for user authentication"
- **Frontend development**: "Design a responsive login form using React"
- **Design request**: "Create a color scheme for our e-commerce site"

### 3. Research and Information

- **Market research**: "Research the top competitors in the project management space"
- **Technical research**: "Find the best React state management libraries in 2025"

### 4. Testing and Quality

- **Website testing**: "Test our login page for accessibility issues"
- **Performance testing**: "Check the response time of our API endpoints"

### 5. Plan Optimization

- **Analyze plan**: "Analyze our Project Alpha plan for completeness"
- **Suggest improvements**: "Suggest improvements to our development workflow"

## Delegation Architecture

The Coordination Agent has access to all specialized agents as tools. When a user sends a request, the Coordination Agent:

1. Analyzes the request to determine which specialized agent should handle it
2. Delegates the task to the appropriate agent
3. Receives the response from the specialized agent
4. Formats and returns the final response to the user

This delegation pattern allows each agent to focus on its specific domain while providing a unified interface for users.

## MCP Integration

This system leverages the Model Context Protocol (MCP) for standardized communication between AI agents and external systems:

- **Planning System MCP**: For plan and task management
- **Context7 MCP**: For accessing documentation
- **Filesystem MCP**: For code management
- **Playwright MCP**: For automated testing
- **Web Search MCP**: For research and information gathering

## License

This project is licensed under the MIT License - see the LICENSE file for details.
