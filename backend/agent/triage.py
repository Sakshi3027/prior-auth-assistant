"""
Node 2: Triage.

Decides whether the requested procedure requires prior authorization at all.
If the payer policy says no PA is needed, the agent short-circuits here and
skips the retrieval, evaluation, and drafting steps entirely - no point
building a justification for something that doesn't need one.
"""
from agent.state import AgentState
from data.payer_policies import POLICIES_BY_CODE


def triage_node(state: AgentState) -> AgentState:
    code = state["requested_code"]
    policy = POLICIES_BY_CODE.get(code)

    if policy is None:
        # No policy on file for this code - default to requiring review,
        # since an unknown procedure is safer to flag than to wave through.
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