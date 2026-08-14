"""
Node 2: Triage.

Decides whether the requested procedure requires prior authorization, by
looking up the governing policy. If no PA is needed, the agent
short-circuits here and skips retrieve/evaluate/draft.
"""
from agent.state import AgentState
from db.policy_repo import find_policy


def triage_node(state: AgentState) -> AgentState:
    code = state["requested_code"]
    note = state["note"]
    query = f"{note.requested_service.display}. {note.note_text}"

    policy = find_policy(query_text=query, procedure_code=code)

    if policy is None:
        state["pa_required"] = True
        state.setdefault("trace", []).append(
            f"triage: no policy found for {code}; defaulting to PA required"
        )
        return state

    state["pa_required"] = policy.prior_auth_required
    state.setdefault("trace", []).append(
        f"triage: policy {policy.policy_id} says PA "
        f"{'required' if policy.prior_auth_required else 'NOT required'}"
    )
    return state