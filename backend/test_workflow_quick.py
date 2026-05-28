import asyncio
import json
from app.graph.workflow import research_graph

async def run_test():
    # Inject state that skips the massive Planner generation to avoid rate limits
    initial_state = {
        "query": "Is Microsoft (MSFT) a good buy?",
        "sector_classification": "Technology",
        "research_plan": "1. Analyze Microsoft latest earnings.\n2. Analyze AI growth.", # Fake simple plan
        "search_history": [],
        "findings": [],
        "next_search_queries": ["Microsoft Q3 earnings report summary", "Microsoft AI revenue growth"],
        "iteration_count": 0,
        "is_sufficient": False,
        "current_research_step": "start"
    }
    
    print("Sending query to the full LangGraph engine (Fast Mode)...")
    
    async for event in research_graph.astream(initial_state, config={"recursion_limit": 50}):
        for node, state in event.items():
            print(f"--- Node Completed: {node} ---")
            
            if node == "finance":
                finance_data = state.get("financial_data", {})
                print(f"Ticker Extracted: {finance_data.get('ticker')}")
                print(f"P/E Ratio: {finance_data.get('trailing_pe')}")
                
            elif node == "reporter":
                print("\n=== FINAL REPORT GENERATED ===")
                report = state.get("final_report", "")
                print(report)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env.dev")
    asyncio.run(run_test())
