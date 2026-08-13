"""
Node 1: Extract.

Pulls the structured facts the rest of the agent needs out of the clinical
note - primarily the requested procedure code. Our synthetic notes already
carry a structured ServiceRequest, so this node mostly lifts that out and
records it in state. On a real free-text-only note this is where an LLM
call would parse the narrative; we keep the hook here for that.
"""
from agent.state import AgentState


def extract_node(state: AgentState) -> AgentState:
    note = state["note"]
    code = note.requested_service.code

    state["requested_code"] = code
    state.setdefault("trace", []).append(
        f"extract: identified requested procedure {code} "
        f"({note.requested_service.display})"
    )
    return state