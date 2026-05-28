import logging
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from tavily import AsyncTavilyClient
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    url: str

class TavilySearchTool:
    """
    Production-grade Tavily search tool for deep iterative research.
    Provides async execution, structured outputs, logging, and retry handling.
    """
    def __init__(self, max_results: int = 5, search_depth: str = "basic"):
        if not settings.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set.")
        
        self.client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        self.max_results = max_results
        self.search_depth = search_depth
        logger.info("Initialized TavilySearchTool")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, Exception)),
        reraise=True
    )
    async def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Execute an asynchronous search query and return normalized, structured results.
        """
        limit = max_results if max_results is not None else self.max_results
        logger.debug(f"Executing Tavily search for query: '{query}' with limit {limit}")
        
        try:
            response = await self.client.search(
                query=query, 
                search_depth=self.search_depth,
                max_results=limit,
                include_raw_content=False
            )
            
            results = response.get("results", [])
            normalized_results = []
            
            for res in results:
                normalized_results.append(SearchResult(
                    title=res.get("title", "No Title"),
                    summary=res.get("content", ""), 
                    content=res.get("content", ""),
                    url=res.get("url", "")
                ))
                
            logger.debug(f"Successfully retrieved {len(normalized_results)} results for query: '{query}'")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Error during Tavily search for query '{query}': {str(e)}")
            raise

tavily_search_tool = TavilySearchTool()
