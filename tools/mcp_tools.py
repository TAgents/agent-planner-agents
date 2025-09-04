"""
MCP integration utilities for ADK Multiagent System.

This module provides tools for integrating with various MCP servers,
including the planning system MCP server.
"""

import os
import os.path
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

async def setup_planning_mcp_tools():
    """
    Sets up MCP tools for interacting with the planning system.
    
    Returns:
        Tuple of (list of MCP tools, exit_stack) for planning operations.
    """
    # Check if the MCP path environment variable is set
    planning_mcp_path = os.environ.get("PLANNING_MCP_PATH")
    if not planning_mcp_path:
        raise ValueError("PLANNING_MCP_PATH environment variable must be set")
    
    # Check if the MCP path exists
    if not os.path.exists(planning_mcp_path):
        raise FileNotFoundError(f"PLANNING_MCP_PATH path does not exist: {planning_mcp_path}")

    # Get API URL and token
    planning_api_url = os.environ.get("PLANNING_API_URL", "http://localhost:3000")
    planning_api_token = os.environ.get("PLANNING_API_TOKEN")
    if not planning_api_token:
        raise ValueError("PLANNING_API_TOKEN environment variable must be set")
    
    print(f"Setting up Planning MCP server at {planning_mcp_path}")
    print(f"Environment parameters: API_URL={planning_api_url}, API_TOKEN={planning_api_token[:4]}...{planning_api_token[-4:]}")
    
    # Server parameters for the MCP server
    server_params = StdioServerParameters(
        command="sh",
        args=[
            "-c",
            f"cd {planning_mcp_path} && node src/index.js"
        ],
        env={
            "API_URL": planning_api_url,
            "USER_API_TOKEN": planning_api_token,
            "API_TOKEN": planning_api_token
        }
    )
    
    # Create MCP toolset using the async factory method
    result = await MCPToolset.from_server(connection_params=server_params)
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        return result
    else:
        # In newer versions of MCPToolset, it might return an object
        # with tools and exit_stack attributes
        print(f"Warning: Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print("Attempting to extract tools and exit_stack...")
        
        # Try to extract tools and exit_stack from the result
        tools = getattr(result, "tools", [])
        exit_stack = getattr(result, "exit_stack", None)
        
        if tools and exit_stack:
            return tools, exit_stack
        else:
            raise ValueError(f"Could not extract tools and exit_stack from MCPToolset.from_server() result: {result}")

async def setup_context7_mcp_tools():
    """
    Sets up MCP tools for interacting with the Context7 documentation server.
    
    Returns:
        Tuple of (list of MCP tools, exit_stack) for documentation access.
    """
    print("Setting up Context7 MCP server")
    
    # Server parameters for the Context7 MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@upstash/context7-mcp@latest"
        ],
        env={}
    )
    
    # Create MCP toolset using the async factory method
    result = await MCPToolset.from_server(connection_params=server_params)
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        return result
    else:
        # In newer versions of MCPToolset, it might return an object
        # with tools and exit_stack attributes
        print(f"Warning: Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print("Attempting to extract tools and exit_stack...")
        
        # Try to extract tools and exit_stack from the result
        tools = getattr(result, "tools", [])
        exit_stack = getattr(result, "exit_stack", None)
        
        if tools and exit_stack:
            return tools, exit_stack
        else:
            raise ValueError(f"Could not extract tools and exit_stack from MCPToolset.from_server() result: {result}")

async def setup_filesystem_mcp_tools():
    """
    Sets up MCP tools for interacting with the filesystem.
    
    Returns:
        Tuple of (list of MCP tools, exit_stack) for filesystem operations.
    """
    # Get workspace path
    workspace_path = os.environ.get("WORKSPACE_PATH", "/Users/michmalk/dev/talkingagents")
    print(f"Setting up Filesystem MCP server with workspace path: {workspace_path}")
    
    # Server parameters for the Filesystem MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            workspace_path
        ],
        env={}
    )
    
    # Create MCP toolset using the async factory method
    result = await MCPToolset.from_server(connection_params=server_params)
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        return result
    else:
        # In newer versions of MCPToolset, it might return an object
        # with tools and exit_stack attributes
        print(f"Warning: Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print("Attempting to extract tools and exit_stack...")
        
        # Try to extract tools and exit_stack from the result
        tools = getattr(result, "tools", [])
        exit_stack = getattr(result, "exit_stack", None)
        
        if tools and exit_stack:
            return tools, exit_stack
        else:
            raise ValueError(f"Could not extract tools and exit_stack from MCPToolset.from_server() result: {result}")

async def setup_playwright_mcp_tools():
    """
    Sets up MCP tools for browser automation via Playwright.
    
    Returns:
        Tuple of (list of MCP tools, exit_stack) for browser automation.
    """
    print("Setting up Playwright MCP server")
    
    # Server parameters for the Playwright MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "@playwright/mcp@latest"
        ],
        env={}
    )
    
    # Create MCP toolset using the async factory method
    result = await MCPToolset.from_server(connection_params=server_params)
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        return result
    else:
        # In newer versions of MCPToolset, it might return an object
        # with tools and exit_stack attributes
        print(f"Warning: Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print("Attempting to extract tools and exit_stack...")
        
        # Try to extract tools and exit_stack from the result
        tools = getattr(result, "tools", [])
        exit_stack = getattr(result, "exit_stack", None)
        
        if tools and exit_stack:
            return tools, exit_stack
        else:
            raise ValueError(f"Could not extract tools and exit_stack from MCPToolset.from_server() result: {result}")

async def setup_web_search_mcp_tools():
    """
    Sets up MCP tools for web search operations.
    
    Returns:
        Tuple of (list of MCP tools, exit_stack) for web search.
    """
    print("Setting up Web Search MCP server")
    
    # Server parameters for the Brave Search MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-brave-search"
        ],
        env={
            "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")
        }
    )
    
    # Create MCP toolset using the async factory method
    result = await MCPToolset.from_server(connection_params=server_params)
    
    # Check the structure of the result to determine if it's a tuple or an object
    if isinstance(result, tuple) and len(result) == 2:
        # It's a tuple of (tools, exit_stack)
        return result
    else:
        # In newer versions of MCPToolset, it might return an object
        # with tools and exit_stack attributes
        print(f"Warning: Unexpected return type from MCPToolset.from_server(): {type(result)}")
        print("Attempting to extract tools and exit_stack...")
        
        # Try to extract tools and exit_stack from the result
        tools = getattr(result, "tools", [])
        exit_stack = getattr(result, "exit_stack", None)
        
        if tools and exit_stack:
            return tools, exit_stack
        else:
            raise ValueError(f"Could not extract tools and exit_stack from MCPToolset.from_server() result: {result}")
