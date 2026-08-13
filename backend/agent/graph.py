"""
The prior authorization agent, assembled from the five nodes.

Flow:
    extract -> triage -> (branch)
        if PA required:  retrieve -> evaluate -> draft -> END
        if not required: END

The branch after triage is the short-circuit: procedures that don't need
prior auth skip retrieval, evaluation, and drafting entirely.
"""
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.extract import extract_node
from agent.triage import triage_node
from agent.retrieve import retrieve_node
from agent.evaluate import evaluate_node
from agent.draft import draft_node


def _needs_pa(state: AgentState) -> str:
    """Routing function: decides the path after triage."""
    return "retrieve" if state.get("pa_required") else "end"


def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("extract_step", extract_node)
    graph.add_node("triage_step", triage_node)
    graph.add_node("retrieve_step", retrieve_node)
    graph.add_node("evaluate_step", evaluate_node)
    graph.add_node("draft_step", draft_node)

    graph.set_entry_point("extract_step")
    graph.add_edge("extract_step", "triage_step")

    # Conditional branch: only continue the full pipeline if PA is required.
    graph.add_conditional_edges(
        "triage_step",
        _needs_pa,
        {"retrieve": "retrieve_step", "end": END},
    )

    graph.add_edge("retrieve_step", "evaluate_step")
    graph.add_edge("evaluate_step", "draft_step")
    graph.add_edge("draft_step", END)

    return graph.compile()


# Compile once at import so callers just import and run.
agent = build_agent()