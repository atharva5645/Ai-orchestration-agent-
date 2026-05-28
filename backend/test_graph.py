import asyncio
from app.agents.graph import research_graph

async def run_test():
    initial_state = {
        "query": "Give me a quick 1-paragraph summary of Tesla's (TSLA) latest earnings.",
        "sector_classification": "Technology",
        "search_history": [],
        "findings": [],
        "next_search_queries": [],
        "iteration_count": 0,
        "is_sufficient": False,
        "current_research_step": "start"
    }
    
    print("Sending query to the cyclic LangGraph engine...")
    
    # We use astream to see the nodes executing in real-time
    async for event in research_graph.astream(initial_state, config={"recursion_limit": 50}):
        for node, state in event.items():
            print(f"--- Node Executed: {node} ---")
            print(f"Current Step: {state.get('current_research_step')}")
            
            if node == "reflection":
                print(f"Is Sufficient: {state.get('is_sufficient')}")
                print(f"Next Queries: {state.get('next_search_queries')}\n")
            elif node == "researcher":
                print(f"Iteration Count: {state.get('iteration_count')}")
                print(f"Total Findings Gathered: {len(state.get('findings', []))}\n")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env.dev")
    asyncio.run(run_test())
