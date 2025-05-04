# agents/research/google_search_custom_tool.py
import os
import asyncio
from typing import Type, Dict, Any # Added Dict, Any for typing

# --- CORRECT IMPORT ---
from google.adk.tools import BaseTool
# --- END ---

from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Pydantic Input Schema ---
class GoogleSearchArgs(BaseModel):
    query: str = Field(..., description="Web search query")
    num_results: int = Field(default=5, description="Number of results to return (max 10)")

# --- Inherit from BaseTool ---
class CustomGoogleSearchTool(BaseTool):
    """ Custom tool inheriting from BaseTool for Google Search. """

    # --- Define attributes directly ---
    name = "custom_google_search" # Keep the name consistent
    description = "Performs a Google search using the Custom Search API to find relevant web pages."
    args_schema: Type[BaseModel] = GoogleSearchArgs # Use args_schema
    return_direct = False # Let LLM process results unless specified otherwise

    def __init__(self, api_key: str, search_engine_id: str):
        # No need to call super().__init__() explicitly if BaseTool doesn't require it,
        # or if you don't need custom initialization logic beyond setting attributes.
        # If BaseTool's __init__ does something important, you might need it, but
        # often for simple tools, just defining class attributes is enough. Let's omit it for now.

        if not api_key: raise ValueError("API key required")
        if not search_engine_id: raise ValueError("Search Engine ID required")
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        try:
            # Consider making service build lazy or handle errors more gracefully if network isn't ready at startup
            self.service = build("customsearch", "v1", developerKey=self.api_key)
            print(f"--- CustomGoogleSearchTool: Service object built for tool '{self.name}' ---")
        except Exception as e:
            print(f"ERROR building Google API client service: {e}")
            # You might want a way to signal this tool is non-functional
            self.service = None # Mark service as unavailable

    def _run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """ Sync execution (optional, implement if needed) """
        # You would typically run the async version from sync context if needed
        # For now, let's just raise NotImplementedError or delegate to async
        raise NotImplementedError("Sync execution not implemented for CustomGoogleSearchTool. Use async.")
        # Or: return asyncio.run(self._arun(query=query, num_results=num_results)) # If running outside an event loop

    # --- Implement _arun for async execution ---
    async def _arun(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Executes the Google search asynchronously. Returns a dictionary.
        """
        if not self.service:
            return {"status": "error", "message": "Google API service not initialized."}

        # Clamp num_results (Google Custom Search API max is typically 10)
        num = max(1, min(num_results, 10))

        print(f"--- CustomGoogleSearchTool ('{self.name}') received query: '{query}', num_results: {num} ---")
        try:
            # Define the actual search execution function
            def search_sync():
                return self.service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=num
                ).execute()

            # Run the potentially blocking API call in a separate thread
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, search_sync)

            search_items = results.get("items", [])
            formatted_results = []

            if not search_items:
                message = f"No results found for query: '{query}'."
                print(f"--- CustomGoogleSearchTool ('{self.name}') found no results. ---")
            else:
                message = f"Successfully found {len(search_items)} results for query: '{query}'."
                for i, item in enumerate(search_items):
                    formatted_results.append({
                        "title": item.get('title', 'N/A'),
                        "link": item.get('link', '#'),
                        "snippet": item.get('snippet', 'N/A').replace('\n', ' ').strip()
                    })
                print(f"--- CustomGoogleSearchTool ('{self.name}') processed {len(search_items)} results. ---")

            # --- Return a dictionary ---
            return {"status": "success", "message": message, "results": formatted_results}

        except HttpError as e:
            status_code = getattr(e.resp, 'status', 'Unknown status')
            print(f"ERROR CustomGoogleSearchTool ('{self.name}'): HTTP error {status_code}")
            return {"status": "error", "message": f"API error {status_code}. Check API Key/CX ID/Quotas."}
        except Exception as e:
            print(f"ERROR CustomGoogleSearchTool ('{self.name}'): Unexpected error: {e}")
            return {"status": "error", "message": f"Unexpected error during search: {e}"}