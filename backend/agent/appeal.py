"""
Appeals agent.

When a claim's evaluation shows unmet or uncertain criteria - meaning the
prior auth would likely be denied - this drafts an appeal letter arguing
for reconsideration. It's honest about the gaps: it acknowledges unmet
criteria and leans on whatever supporting evidence the note does contain,
rather than pretending everything is met.

Reuses the same clinical note and matched policy the main agent already
produced, so it slots on top of the existing pipeline without re-running it.
"""
from agent.llm import llm
from agent.state import AgentState


APPEAL_PROMPT = """You are drafting a prior authorization APPEAL letter on behalf of a \
provider's office, after an initial determination that the request may be denied.

Write a professional, respectful appeal (one to two short paragraphs) that:
- argues for reconsideration of the requested procedure
- leans on the criteria that ARE met, citing specific facts from the note
- acknowledges any unmet criteria honestly, and explains any mitigating clinical context
- does not fabricate facts not present in the note

Patient: {patient_name}
Requested procedure: {procedure}
Payer: {payer}

Criteria determinations:
{criteria_summary}

Clinical note:
{note_text}"""


def draft_appeal(state: AgentState) -> str:
    note = state["note"]
    policy = state.get("matched_policy")
    checks = state.get("criteria_checks", [])

    criteria_summary = "\n".join(
        f"- [{c['status'].upper()}] {c['criterion']} -> {c['justification']}"
        for c in checks
    ) or "No specific criteria applied."

    prompt = APPEAL_PROMPT.format(
        patient_name=f"{note.patient.given_name} {note.patient.family_name}",
        procedure=note.requested_service.display,
        payer=policy.payer_name if policy else "the payer",
        criteria_summary=criteria_summary,
        note_text=note.note_text,
    )
    return llm.invoke(prompt).content.strip()