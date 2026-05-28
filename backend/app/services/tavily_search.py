from tavily import TavilyClient
from app.core.config import settings
from typing import List, Dict, Any

class TavilySearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key) if settings.tavily_api_key else None
        
    def search(self, query: str, search_depth: str = "advanced") -> List[Dict[str, Any]]:
        """
        Perform a search query using Tavily API.
        """
        if not self.client:
            raise ValueError("TAVILY_API_KEY is not set.")
        response = self.client.search(query=query, search_depth=search_depth)
        return response.get("results", [])

tavily_service = TavilySearchService()
