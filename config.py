"""
Configuration management for the agent-planner-agents system.

This module centralizes configuration and provides validation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for an individual agent."""
    name: str
    model: str = "gemini/gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    enabled: bool = True

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    path: Optional[str] = None
    command: str = "node"
    args: list = None
    env: Dict[str, str] = None
    enabled: bool = True

class Config:
    """Central configuration management."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        
        # API Keys
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.google_search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        self.brave_api_key = os.environ.get("BRAVE_API_KEY")
        
        # Planning System
        self.planning_api_url = os.environ.get("PLANNING_API_URL", "http://localhost:3000")
        self.planning_api_token = os.environ.get("PLANNING_API_TOKEN")
        
        # MCP Server Paths
        self.planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
        self.context7_mcp_path = os.environ.get("CONTEXT7_MCP_PATH")
        self.filesystem_mcp_path = os.environ.get("FILESYSTEM_MCP_PATH")
        self.playwright_mcp_path = os.environ.get("PLAYWRIGHT_MCP_PATH")
        self.websearch_mcp_path = os.environ.get("WEBSEARCH_MCP_PATH")
        
        # Workspace
        self.workspace_path = os.environ.get("WORKSPACE_PATH", "/Users/michmalk/dev/talkingagents")
        
        # Agent Configurations
        self.agents = {
            "coordinator": AgentConfig(
                name="coordination_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "backend_dev": AgentConfig(
                name="backend_developer_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "frontend_dev": AgentConfig(
                name="frontend_developer_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "designer": AgentConfig(
                name="designer_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "research": AgentConfig(
                name="research_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "tester": AgentConfig(
                name="tester_agent",
                model="gemini/gemini-1.5-flash"
            ),
            "plan_optimizer": AgentConfig(
                name="plan_optimizer_agent",
                model="gemini/gemini-1.5-flash"
            )
        }
        
        # MCP Server Configurations
        self.mcp_servers = {
            "planning": MCPServerConfig(
                name="planning-system-mcp",
                path=self.planning_mcp_path,
                command="sh",
                args=["-c", f"cd {self.planning_mcp_path} && node src/index.js"] if self.planning_mcp_path else [],
                env={
                    "API_URL": self.planning_api_url,
                    "USER_API_TOKEN": self.planning_api_token or "",
                    "API_TOKEN": self.planning_api_token or ""
                },
                enabled=bool(self.planning_mcp_path and self.planning_api_token)
            ),
            "filesystem": MCPServerConfig(
                name="filesystem-mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", self.workspace_path],
                enabled=True
            ),
            "context7": MCPServerConfig(
                name="context7-mcp",
                command="npx",
                args=["-y", "@upstash/context7-mcp@latest"],
                enabled=True
            ),
            "playwright": MCPServerConfig(
                name="playwright-mcp",
                command="npx",
                args=["@playwright/mcp@latest"],
                enabled=True
            ),
            "websearch": MCPServerConfig(
                name="websearch-mcp",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": self.brave_api_key or ""},
                enabled=bool(self.brave_api_key)
            )
        }
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the configuration and return issues.
        
        Returns:
            Dictionary of validation results
        """
        issues = []
        warnings = []
        
        # Check required API keys
        if not self.google_api_key:
            issues.append("GOOGLE_API_KEY is not set")
        
        # Check planning system configuration
        if not self.planning_api_token:
            warnings.append("PLANNING_API_TOKEN is not set - planning features will be disabled")
        
        if self.planning_mcp_path and not os.path.exists(self.planning_mcp_path):
            issues.append(f"PLANNING_MCP_PATH does not exist: {self.planning_mcp_path}")
        
        # Check optional configurations
        if not self.google_search_engine_id:
            warnings.append("GOOGLE_SEARCH_ENGINE_ID not set - using default public search engine")
        
        if not self.brave_api_key:
            warnings.append("BRAVE_API_KEY not set - Brave search will be unavailable")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_enabled_mcp_servers(self) -> Dict[str, MCPServerConfig]:
        """Get only the enabled MCP servers."""
        return {
            name: config 
            for name, config in self.mcp_servers.items() 
            if config.enabled
        }
    
    def get_enabled_agents(self) -> Dict[str, AgentConfig]:
        """Get only the enabled agents."""
        return {
            name: config 
            for name, config in self.agents.items() 
            if config.enabled
        }
    
    def summary(self) -> str:
        """Generate a configuration summary."""
        lines = [
            "Configuration Summary",
            "=" * 40,
            f"Google API Key: {'✓' if self.google_api_key else '✗'}",
            f"Planning API Token: {'✓' if self.planning_api_token else '✗'}",
            f"Planning MCP Path: {'✓' if self.planning_mcp_path and os.path.exists(self.planning_mcp_path) else '✗'}",
            f"Google Search Engine ID: {'✓' if self.google_search_engine_id else '○ (using default)'}",
            f"Brave API Key: {'✓' if self.brave_api_key else '○'}",
            "",
            "Enabled MCP Servers:",
        ]
        
        for name, config in self.get_enabled_mcp_servers().items():
            lines.append(f"  - {name}")
        
        lines.extend([
            "",
            "Enabled Agents:",
        ])
        
        for name, config in self.get_enabled_agents().items():
            lines.append(f"  - {name} ({config.model})")
        
        return "\n".join(lines)

# Singleton instance
config = Config()
