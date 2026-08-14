"""
Node 3: Retrieve.

Finds the payer policy governing the requested procedure via pgvector
semantic search. Prefers an exact code match when one exists, otherwise
falls back to nearest-neighbour on the policy-text embedding.

The retrieval logic lives in db.policy_repo, so this node stays thin - and
swapping code-lookup for vector search never touched triage, evaluate,
or draft.
"""
from agent.state import AgentState
from db.policy_repo import find_policy


def retrieve_node(state: AgentState) -> AgentState:
    code = state["requested_code"]
    note = state["note"]
    query = f"{note.requested_service.display}. {note.note_text}"

    policy = find_policy(query_text=query, procedure_code=code)

    state["matched_policy"] = policy
    if policy is not None:
        state.setdefault("trace", []).append(
            f"retrieve: matched policy {policy.policy_id} "
            f"({policy.payer_name}) via vector search, {len(policy.criteria)} criteria"
        )
    else:
        state.setdefault("trace", []).append(f"retrieve: no policy found for {code}")
    return state