from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    company_symbol: str
    research_data: dict
    financial_data: dict
    final_report: str
    next_step: str
