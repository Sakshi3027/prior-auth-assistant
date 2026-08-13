"""
Shared state passed between agent nodes. Each node reads what it needs
and writes its output back here, so by the end the state holds the full
trace of the agent's reasoning - which is exactly what we persist and
show in the UI.
"""
from typing import Optional, TypedDict
from models.fhir import ClinicalNote
from data.payer_policies import PayerPolicy


class CriterionCheck(TypedDict):
    criterion: str
    status: str          # "met" | "unmet" | "uncertain"
    justification: str    # why, citing the note


class AgentState(TypedDict, total=False):
    # Input
    note: ClinicalNote

    # Node outputs, filled in as the agent runs
    requested_code: str
    pa_required: Optional[bool]
    matched_policy: Optional[PayerPolicy]
    criteria_checks: list[CriterionCheck]
    draft: str
    confidence: float

    # A running log of which nodes fired, for the UI's agent-flow view
    trace: list[str]