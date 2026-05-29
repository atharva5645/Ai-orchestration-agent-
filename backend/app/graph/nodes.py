"""
Centralized registry for all LangGraph nodes.
"""

from app.agents.nodes.router_planner import router_planner_node
from app.agents.nodes.researcher_analyst import researcher_analyst_node
from app.agents.nodes.finance import finance_node
from app.agents.reporter.reporter import reporter_node

__all__ = [
    "router_planner_node",
    "researcher_analyst_node",
    "finance_node",
    "reporter_node"
]
