from langgraph.graph import StateGraph, END
from app.state.research_state import ResearchState
from app.graph.nodes import (
    router_planner_node,
    researcher_analyst_node,
    finance_node,
    reporter_node
)

def create_research_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("router_planner", router_planner_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("researcher_analyst", researcher_analyst_node)
    workflow.add_node("reporter", reporter_node)

    workflow.set_entry_point("router_planner")

    workflow.add_conditional_edges(
        "router_planner",
        lambda state: "end" if state.get("sector_classification") == "Rejected" else "finance",
        {"end": END, "finance": "finance"}
    )

    workflow.add_edge("finance", "researcher_analyst")
    workflow.add_edge("researcher_analyst", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()
