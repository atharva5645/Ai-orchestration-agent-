from langgraph.graph import StateGraph, END
from app.state.research_state import ResearchState
from app.graph.nodes import (
    router_node,
    planner_node,
    researcher_node,
    reflection_node,
    finance_node,
    analyst_node,
    reporter_node
)

def route_after_classification(state: ResearchState) -> str:
    """Conditional routing based on the sector classification."""
    sector = state.get("sector_classification", "")
    if sector == "Rejected":
        return "end"
    return "planner"

def route_after_reflection(state: ResearchState) -> str:
    """Determines whether to loop back to the researcher or proceed to finance extraction."""
    is_sufficient = state.get("is_sufficient", False)
    iteration_count = state.get("iteration_count", 0)
    
    # PERFORMANCE FIX: Cap iterations at 1 (down from 10) to prevent rate-limit loops and slow research.
    if is_sufficient or iteration_count >= 1:
        return "finance"
    return "researcher"

def create_research_graph():
    workflow = StateGraph(ResearchState)

    # 1. Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("reporter", reporter_node)

    # 2. Set Entry Point
    workflow.set_entry_point("router")

    # 3. Define Edges and Conditional Routing
    workflow.add_conditional_edges(
        "router",
        route_after_classification,
        {
            "end": END,
            "planner": "planner"
        }
    )
    
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "reflection")
    
    # Cyclic Loop
    workflow.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "researcher": "researcher",
            "finance": "finance"
        }
    )
    
    # Post-Research Finalization
    workflow.add_edge("finance", "analyst")
    workflow.add_edge("analyst", "reporter")
    workflow.add_edge("reporter", END)

    # Compile the graph
    return workflow.compile()

research_graph = create_research_graph()
