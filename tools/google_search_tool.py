"""
Custom Google Search Tool for Research Agent.

This tool provides web search capabilities using Google's Custom Search API.
"""

import os
import json
from typing import Dict, Any

class CustomGoogleSearchTool:
    """
    A custom tool that performs Google searches using the Custom Search API.
    Compatible with ADK's tool interface.
    """
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        """
        Initialize the Google Search tool.
        
        Args:
            api_key: Google API key for Custom Search
            search_engine_id: Custom Search Engine ID
        """
        self.name = "custom_google_search"
        self.description = "Search the web using Google Custom Search API"
        
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.search_engine_id = (
            search_engine_id or 
            os.environ.get("GOOGLE_SEARCH_ENGINE_ID") or 
            os.environ.get("PROGRAMMABLE_SEARCH_ENGINE_ID")
        )
        
        if not self.api_key:
            raise ValueError("Google API key is required for search functionality")
        if not self.search_engine_id:
            # Use a default public search engine ID if not provided
            self.search_engine_id = "017576662512468239146:omuauf_lfve"  # Default public CSE
    
    async def run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Perform a Google search.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Import here to avoid dependency issues
            from googleapiclient.discovery import build
            
            # Limit results to maximum of 10 (Google CSE limitation)
            num_results = min(num_results, 10)
            
            # Build the Custom Search service
            service = build("customsearch", "v1", developerKey=self.api_key)
            
            # Execute the search
            result = service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results
            ).execute()
            
            # Format the results
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayLink': item.get('displayLink', '')
                    })
            
            return {
                'status': 'success',
                'query': query,
                'total_results': result.get('searchInformation', {}).get('totalResults', '0'),
                'results': search_results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'query': query
            }
    
    async def run_async(self, args: Dict[str, Any], tool_context: Dict[str, Any] = None) -> Any:
        """
        Async wrapper for ADK compatibility.
        
        Args:
            args: Dictionary containing 'query' and optionally 'num_results'
            tool_context: Optional context from the agent
            
        Returns:
            Search results in ADK-compatible format
        """
        query = args.get('query', '')
        num_results = args.get('num_results', 5)
        
        if not query:
            error_msg = 'Query parameter is required'
            # Return in ADK expected format
            class ErrorResult:
                def __init__(self, text):
                    self.content = [type('obj', (object,), {'text': text})]
            
            return ErrorResult(f"Search failed: {error_msg}")
        
        result = await self.run(query, num_results)
        
        # Format as text for agent consumption
        if result['status'] == 'success':
            formatted_results = f"Search Results for '{query}':\n\n"
            if result['results']:
                for i, item in enumerate(result['results'], 1):
                    formatted_results += f"{i}. {item['title']}\n"
                    formatted_results += f"   URL: {item['link']}\n"
                    formatted_results += f"   {item['snippet']}\n\n"
            else:
                formatted_results += "No results found.\n"
            
            # Return in ADK expected format
            class Result:
                def __init__(self, text):
                    self.content = [type('obj', (object,), {'text': text})]
            
            return Result(formatted_results)
        else:
            class Result:
                def __init__(self, text):
                    self.content = [type('obj', (object,), {'text': text})]
            
            return Result(f"Search failed: {result.get('error', 'Unknown error')}")
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable for ADK compatibility."""
        import asyncio
        if args and isinstance(args[0], dict):
            return asyncio.create_task(self.run_async(args[0], kwargs.get('tool_context')))
        return asyncio.create_task(self.run_async(kwargs, kwargs.get('tool_context')))
