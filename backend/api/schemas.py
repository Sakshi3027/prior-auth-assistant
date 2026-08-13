"""
API request/response schemas. Separate from the internal FHIR models so
the API contract with the frontend can stay stable even if internals change.
"""
from typing import Optional
from pydantic import BaseModel


class SubmitRequest(BaseModel):
    """A raw clinical note submitted for adjudication."""
    note_text: str
    procedure_code: str
    procedure_name: str
    patient_name: str
    payer_name: Optional[str] = None


class CriterionResult(BaseModel):
    criterion: str
    status: str
    justification: str


class PriorAuthResult(BaseModel):
    id: str
    patient_name: str
    procedure_code: str
    procedure_name: str
    pa_required: bool
    criteria: list[CriterionResult]
    draft: Optional[str]
    confidence: Optional[float]
    trace: list[str]