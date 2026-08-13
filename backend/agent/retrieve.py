"""
Node 3: Retrieve.

Finds the payer policy that governs the requested procedure and loads it
into state so the evaluation node can check the patient against its
criteria.

For now this is a direct lookup by procedure code against the in-memory
policies. Later this becomes a semantic search over policy text embeddings
in pgvector - which is why the retrieval logic lives in its own node,
isolated from everything downstream. Swapping the lookup for vector search
won't touch triage, evaluate, or draft.
"""
from agent.state import AgentState
from data.payer_policies import POLICIES_BY_CODE


def retrieve_node(state: AgentState) -> AgentState:
    code = state["requested_code"]
    policy = POLICIES_BY_CODE.get(code)

    state["matched_policy"] = policy
    if policy is not None:
        state.setdefault("trace", []).append(
            f"retrieve: matched policy {policy.policy_id} "
            f"({policy.payer_name}) with {len(policy.criteria)} criteria"
        )
    else:
        state.setdefault("trace", []).append(
            f"retrieve: no policy found for {code}"
        )
    return state