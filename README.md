# ADK Multiagent System with MCP Integration

A sophisticated multiagent system using Google's Agent Development Kit (ADK) that coordinates specialized AI agents through the Model Context Protocol (MCP) for comprehensive software development workflows.

## 🚀 Overview

This system features a Coordination Agent that orchestrates specialized agents for different development roles, each with access to role-specific tools and MCP servers. The architecture enables seamless agent-to-agent communication and delegation for complex software development tasks.

### 🤖 Agent Architecture

#### **Coordination Agent** (Central Orchestrator)
- Manages user communication and workflow orchestration
- Delegates tasks to specialized agents via ADK's AgentTool
- Direct access to planning system for project management
- Provides unified interface for all development operations

#### **Specialized Agents**

| Agent | Role | Tools & Capabilities |
|-------|------|---------------------|
| **Backend Developer** | Server-side implementation | Filesystem access, documentation (Context7), API design, database schemas |
| **Frontend Developer** | Client-side implementation | Filesystem access, UI frameworks, responsive design |
| **Designer** | Visual and UX design | Filesystem access, design patterns, style guides |
| **Research** | Information gathering | Google Search API, web research, market analysis |
| **Tester** | Quality verification | Playwright automation, filesystem access, test generation |
| **Plan Optimizer** | Plan improvement | Planning system access, structure optimization |

## 📋 Prerequisites

- **Python 3.9+** with pip
- **Node.js 16+** with npm/npx
- **Google AI API Key** ([Get one here](https://ai.google.dev/))
- **Planning System** (API and MCP server)
- **API Token** for planning system

### Optional for Enhanced Features
- Google Custom Search Engine ID
- Brave Search API Key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/talkingagents/agent-planner-agents.git
cd agent-planner-agents
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Required variables in `.env`:
```env
# Required
GOOGLE_API_KEY=your_google_ai_api_key
PLANNING_MCP_PATH=/path/to/agent-planner-mcp
PLANNING_API_URL=http://localhost:3000
PLANNING_API_TOKEN=your_planning_api_token

# Optional but recommended
GOOGLE_SEARCH_ENGINE_ID=your_custom_search_id
BRAVE_API_KEY=your_brave_api_key
WORKSPACE_PATH=/path/to/your/workspace
```

### 4. Verify Installation

```bash
# Run diagnostics to check system setup
python diagnostics.py

# Test MCP connections
python test_mcp_tools.py --server all

# Run integration tests
python -m tests.test_integration
```

## 🚀 Usage

### Basic Usage - Run the Coordination Agent

```bash
python run.py
```

This starts the Coordination Agent with all specialized agents available as tools.

### Run Specific Agents

```bash
# Run a specific agent independently
python run.py --agent backend    # Backend Developer Agent
python run.py --agent frontend   # Frontend Developer Agent
python run.py --agent designer   # Designer Agent
python run.py --agent research   # Research Agent
python run.py --agent tester     # Tester Agent
python run.py --agent optimizer  # Plan Optimizer Agent
```

### Direct Tool Testing

```bash
# Test direct MCP tool calls
python direct_tool_calls.py
```

## 💡 Example Workflows

### 1. Project Planning
```
User: Create a new project plan for building a task management app
Coordinator: [Creates plan using planning tools]

User: Add phases for development
Coordinator: [Adds phases: Planning, Development, Testing, Deployment]

User: Create tasks for the Planning phase
Coordinator: [Creates tasks: Requirements, Design, Architecture]
```

### 2. Development Task Delegation
```
User: Ask the backend developer to design a REST API for user authentication
Coordinator: [Delegates to Backend Developer Agent]
Backend Agent: [Designs API with endpoints, schemas, and security]

User: Have the frontend developer create a login form
Coordinator: [Delegates to Frontend Developer Agent]
Frontend Agent: [Creates React component with validation]
```

### 3. Research and Analysis
```
User: Research the best authentication methods for web applications
Coordinator: [Delegates to Research Agent]
Research Agent: [Searches and summarizes JWT, OAuth2, SAML options]
```

### 4. Testing and Quality
```
User: Test the login page for accessibility issues
Coordinator: [Delegates to Tester Agent]
Tester Agent: [Runs Playwright tests, reports WCAG compliance]
```

## 🏗️ Project Structure

```
agent-planner-agents/
├── coordination/           # Coordination Agent
│   ├── __init__.py
│   └── agent.py           # Main coordinator with delegation
├── agents/                # Specialized agents
│   ├── backend_dev/       # Backend Developer Agent
│   ├── frontend_dev/      # Frontend Developer Agent
│   ├── designer/          # Designer Agent
│   ├── research/          # Research Agent
│   ├── tester/           # Tester Agent
│   └── plan_optimizer/    # Plan Optimizer Agent
├── tools/                 # Shared tools and utilities
│   ├── mcp_tools.py      # MCP integration utilities
│   └── google_search_tool.py  # Custom search tool
├── tests/                 # Test suite
│   ├── test_planning.py   # Planning operations tests
│   ├── test_integration.py # Full system integration tests
│   └── test_mcp_tools.py  # MCP connectivity tests
├── config.py             # Configuration management
├── diagnostics.py        # System diagnostics script
├── run.py               # Main entry point
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration Management

The system uses a centralized configuration module (`config.py`) that:
- Validates environment variables
- Manages agent configurations
- Controls MCP server settings
- Provides configuration summaries

Run diagnostics to check your configuration:
```bash
python diagnostics.py
```

## 🧪 Testing

### Unit Tests
```bash
# Test planning operations
python -m tests.test_planning

# Test MCP connectivity
python test_mcp_tools.py --server planning
```

### Integration Tests
```bash
# Full system integration test
python -m tests.test_integration
```

### Diagnostics
```bash
# Check system configuration and dependencies
python diagnostics.py
```

## 🔌 MCP Integration

The system leverages MCP for standardized communication:

| MCP Server | Purpose | Configuration |
|------------|---------|---------------|
| Planning System | Plan/task management | Requires API token |
| Filesystem | Code file access | Workspace path |
| Context7 | Documentation access | Auto-configured |
| Playwright | Browser automation | Auto-configured |
| Web Search | Research capabilities | Optional API key |

## 🐛 Troubleshooting

### Common Issues and Solutions

1. **"PLANNING_MCP_PATH does not exist"**
   - Clone the planning MCP server repository
   - Update the path in your `.env` file

2. **"API token is required"**
   - Generate a token from the planning system UI
   - Add to `.env`: `PLANNING_API_TOKEN=your_token`

3. **Agent initialization failures**
   - Run `python diagnostics.py` to identify issues
   - Check that all required npm packages are available
   - Verify Node.js and Python versions

4. **Search functionality not working**
   - Ensure `GOOGLE_API_KEY` is set
   - Optionally set `GOOGLE_SEARCH_ENGINE_ID` for better results

## 📈 Performance Optimization

- Agents are initialized lazily when first needed
- MCP connections are pooled and reused
- Error handling ensures graceful degradation
- Tools are optional - agents work with available resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Agent Planner API](https://github.com/talkingagents/agent-planner) - REST API backend
- [Agent Planner MCP](https://github.com/talkingagents/agent-planner-mcp) - MCP server interface
- [Agent Planner UI](https://github.com/talkingagents/agent-planner-ui) - Web interface

## 📞 Support

- Open an issue on GitHub for bugs
- Check diagnostics first: `python diagnostics.py`
- Review logs in agent output for debugging

## 🚦 Project Status

✅ **Completed**
- Core framework and coordination agent
- All specialized agents implementation
- Agent-to-agent delegation via AgentTool
- Planning system integration
- Error handling and graceful degradation
- Configuration management
- Diagnostic tools

🔄 **In Progress**
- Extended testing coverage
- Performance optimizations
- Additional MCP server integrations

📋 **Planned**
- Multi-agent collaboration patterns
- Advanced workflow templates
- Cloud deployment configurations
