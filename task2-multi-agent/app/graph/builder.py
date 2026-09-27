"""Builds the two-agent workflow.

    START -> researcher -> analyst -> END

This is the entire multi-agent orchestration: two nodes and three edges. The graph
decides *what runs in what order*; the nodes decide *what each step does*.
"""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes.analyst import analyst_node
from app.graph.nodes.researcher import research_node
from app.graph.state import ResearchState


@lru_cache
def get_research_graph() -> CompiledStateGraph:
    """Compile the workflow once and reuse it for every request."""
    builder = StateGraph(ResearchState)

    # Nodes: each name maps to the function that runs at that step.
    builder.add_node("researcher", research_node)
    builder.add_node("analyst", analyst_node)

    # Edges: plain arrows, always followed in this order.
    # Task 3 replaces the first of these with a *conditional* edge.
    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "analyst")
    builder.add_edge("analyst", END)

    return builder.compile()
