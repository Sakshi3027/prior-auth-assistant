"""
Node 5: Draft.

Writes the final prior authorization request as a clean, professional
paragraph a staffer could submit, grounding each justification in the note
and policy. Also computes a confidence score from how cleanly the criteria
were met - all met is high confidence, any uncertain or unmet pulls it down.
"""
from agent.state import AgentState
from agent.llm import llm


DRAFT_PROMPT = """You are drafting a prior authorization request for a provider's office.
Write a concise, professional justification (one short paragraph) supporting approval
of the requested procedure, based only on the information below. Reference the specific
clinical facts that satisfy the policy criteria. Do not invent facts.

Patient: {patient_name}
Requested procedure: {procedure}
Payer: {payer}

Criteria determinations:
{criteria_summary}

Clinical note:
{note_text}"""


def _confidence(checks: list[dict]) -> float:
    if not checks:
        return 1.0
    weights = {"met": 1.0, "uncertain": 0.5, "unmet": 0.0}
    return round(sum(weights.get(c["status"], 0.5) for c in checks) / len(checks), 2)


def draft_node(state: AgentState) -> AgentState:
    note = state["note"]
    policy = state.get("matched_policy")
    checks = state.get("criteria_checks", [])

    criteria_summary = "\n".join(
        f"- [{c['status'].upper()}] {c['criterion']} -> {c['justification']}"
        for c in checks
    ) or "No specific criteria applied."

    prompt = DRAFT_PROMPT.format(
        patient_name=f"{note.patient.given_name} {note.patient.family_name}",
        procedure=note.requested_service.display,
        payer=policy.payer_name if policy else "Unknown payer",
        criteria_summary=criteria_summary,
        note_text=note.note_text,
    )

    state["draft"] = llm.invoke(prompt).content.strip()
    state["confidence"] = _confidence(checks)
    state.setdefault("trace", []).append(
        f"draft: authorization drafted, confidence {state['confidence']}"
    )
    return state