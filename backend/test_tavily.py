import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env.dev
load_dotenv(".env.dev")

from app.tools.search.tavily_search import tavily_search_tool

async def main():
    print("Testing Tavily Search Integration...\n")
    try:
        # Perform a search
        query = "What are the latest financial reports for Apple (AAPL)?"
        results = await tavily_search_tool.search(query=query, max_results=2)
        
        print(f"Found {len(results)} results:\n")
        for idx, res in enumerate(results, 1):
            print(f"--- Result {idx} ---")
            print(f"Title: {res.title}")
            print(f"URL: {res.url}")
            print(f"Summary: {res.summary[:150]}...")
            print()
            
        print("✅ Tavily integration is working successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
