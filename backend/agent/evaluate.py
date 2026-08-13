"""
Node 4: Evaluate.

The first real reasoning step. For each criterion in the matched policy, it
asks the LLM whether the clinical note satisfies that criterion - met,
unmet, or uncertain - along with a short justification grounded in the note.
This is what turns a pile of policy text into an actual per-criterion
determination.
"""
import json
from agent.state import AgentState
from agent.llm import llm


EVAL_PROMPT = """You are a prior authorization reviewer. Given a clinical note and a single \
policy criterion, decide whether the note satisfies that criterion.

Clinical note:
{note_text}

Requested procedure: {procedure}

Policy criterion to evaluate:
"{criterion}"

Respond with ONLY a JSON object, no other text, in exactly this form:
{{"status": "met" | "unmet" | "uncertain", "justification": "<one sentence, cite what in the note supports this>"}}"""


def evaluate_node(state: AgentState) -> AgentState:
    policy = state.get("matched_policy")
    note = state["note"]

    # No policy or no criteria (e.g. a no-PA procedure) - nothing to check.
    if policy is None or not policy.criteria:
        state["criteria_checks"] = []
        state.setdefault("trace", []).append(
            "evaluate: no criteria to check"
        )
        return state

    checks = []
    for criterion in policy.criteria:
        prompt = EVAL_PROMPT.format(
            note_text=note.note_text,
            procedure=note.requested_service.display,
            criterion=criterion,
        )
        raw = llm.invoke(prompt).content.strip()
        try:
            # The model can wrap JSON in stray text; grab the object.
            start, end = raw.find("{"), raw.rfind("}") + 1
            parsed = json.loads(raw[start:end])
            status = parsed.get("status", "uncertain")
            justification = parsed.get("justification", "")
        except (json.JSONDecodeError, ValueError):
            status = "uncertain"
            justification = "Could not parse a determination for this criterion."

        checks.append({
            "criterion": criterion,
            "status": status,
            "justification": justification,
        })

    state["criteria_checks"] = checks
    met = sum(1 for c in checks if c["status"] == "met")
    state.setdefault("trace", []).append(
        f"evaluate: {met}/{len(checks)} criteria met"
    )
    return state