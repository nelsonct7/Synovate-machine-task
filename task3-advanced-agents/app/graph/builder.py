"""Builds the advanced workflow with conditional routing.

    START -> recall -> router --+-- "research" --> researcher <--> tools
                                |                       |
                                |                       v
                                +-- "direct_answer" --> analyst -> END
                                |                       ^
                                +-- "answer_from_memory"-+

On the memory and direct routes the Researcher and every tool are skipped
entirely - that is requirement 3.8.
"""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.graph.nodes.analyst import analyst_node
from app.graph.nodes.recall import recall_node
from app.graph.nodes.researcher import research_node
from app.graph.nodes.router import router_node
from app.graph.state import AssistantState
from app.tools.registry import ALL_TOOLS


def _route_after_router(state: AssistantState) -> str:
    """Read the Router's decision and name the node that runs next."""
    return "researcher" if state.get("route") == "research" else "analyst"


@lru_cache
def get_assistant_graph() -> CompiledStateGraph:
    """Compile the workflow once and reuse it for every request."""
    builder = StateGraph(AssistantState)

    builder.add_node("recall", recall_node)
    builder.add_node("router", router_node)
    builder.add_node("researcher", research_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))
    builder.add_node("analyst", analyst_node)

    builder.add_edge(START, "recall")
    builder.add_edge("recall", "router")

    # Requirement 3.7: the next node is chosen at runtime from the Router's decision,
    # not fixed in advance as it was in Task 2.
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {"researcher": "researcher", "analyst": "analyst"},
    )

    # The tool loop. `tools_condition` inspects the last message: if the model asked
    # for tools, go run them and come back; otherwise research is finished.
    builder.add_conditional_edges(
        "researcher",
        tools_condition,
        {"tools": "tools", END: "analyst"},
    )
    builder.add_edge("tools", "researcher")

    builder.add_edge("analyst", END)

    return builder.compile()
