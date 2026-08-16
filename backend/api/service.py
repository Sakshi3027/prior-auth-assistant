"""
Service layer: takes an API submission, runs it through the agent, and
converts the agent's raw state into a clean PriorAuthResult the API returns.
Keeps the route handlers thin - they just call this.
"""
import uuid
from datetime import date

from agent.graph import agent
from agent.appeal import draft_appeal
from models.fhir import Patient, ServiceRequest, ClinicalNote
from api.schemas import SubmitRequest, PriorAuthResult, CriterionResult
from db import request_repo as store


def _build_note(req: SubmitRequest, reason: str) -> ClinicalNote:
    """Build a minimal FHIR ClinicalNote from a raw submission."""
    given, _, family = req.patient_name.partition(" ")
    return ClinicalNote(
        patient=Patient(
            id="PT-" + uuid.uuid4().hex[:8],
            given_name=given or req.patient_name,
            family_name=family or "",
            birth_date=date(1970, 1, 1),
            gender="unknown",
        ),
        conditions=[],
        requested_service=ServiceRequest(
            code=req.procedure_code,
            display=req.procedure_name,
            reason=reason,
        ),
        note_text=req.note_text,
    )


def process_submission(req: SubmitRequest) -> PriorAuthResult:
    note = _build_note(req, "Submitted via API")
    final = agent.invoke({"note": note})

    result = PriorAuthResult(
        id=uuid.uuid4().hex[:12],
        patient_name=req.patient_name,
        procedure_code=req.procedure_code,
        procedure_name=req.procedure_name,
        pa_required=bool(final.get("pa_required")),
        criteria=[CriterionResult(**c) for c in final.get("criteria_checks", [])],
        draft=final.get("draft"),
        confidence=final.get("confidence"),
        trace=final.get("trace", []),
    )

    store.save(result)
    return result


def draft_appeal_for(req: SubmitRequest) -> str:
    """Rebuild the agent state for a submission and draft an appeal letter."""
    note = _build_note(req, "Appeal draft")
    final = agent.invoke({"note": note})
    return draft_appeal(final)