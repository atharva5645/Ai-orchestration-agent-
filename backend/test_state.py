from app.state.research_state import ResearchState
from langgraph.graph import StateGraph, START, END

# Define a mock node that modifies the new state
def mock_node(state: ResearchState):
    # We will test appending to the search_history list (operator.add)
    return {
        "search_history": [{"query": "test query", "result": "success"}],
        "current_research_step": "completed"
    }

def test_research_state():
    print("1. Initializing StateGraph with new ResearchState...")
    workflow = StateGraph(ResearchState)
    workflow.add_node("mock_node", mock_node)
    workflow.add_edge(START, "mock_node")
    workflow.add_edge("mock_node", END)
    
    app = workflow.compile()
    
    print("2. Providing Initial State...")
    initial_state = {
        "messages": [],
        "query": "Test Apple",
        "research_plan": "Basic plan",
        "sector_classification": "Technology",
        "search_history": [],
        "findings": [],
        "reflection_output": "",
        "next_search_query": "",
        "current_research_step": "started",
        "financial_data": {},
        "retrieved_documents": [],
        "final_report": ""
    }
    
    print("3. Invoking Graph...")
    final_state = app.invoke(initial_state)
    
    print("4. Resulting State Validation:")
    print(f"Current Step: {final_state.get('current_research_step')}")
    print(f"Search History Length: {len(final_state.get('search_history', []))}")
    print(f"Search History Data: {final_state.get('search_history')}")
    print("\n✅ ResearchState successfully processed by LangGraph!")

if __name__ == "__main__":
    test_research_state()
