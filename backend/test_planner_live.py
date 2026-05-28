import asyncio
import os
from app.agents.planner.planner import planner_node

async def run_test():
    state = {
        "query": "What is the financial outlook for Apple (AAPL)?",
        "sector_classification": "IT",
    }
    
    print("Sending query to Planner Agent...")
    result = await planner_node(state)
    
    print("\n--- TEST RESULTS ---")
    print("Current Step:", result.get("current_research_step"))
    print("Generated Plan:\n", result.get("research_plan"))
    print("--------------------")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env.dev")
    asyncio.run(run_test())
