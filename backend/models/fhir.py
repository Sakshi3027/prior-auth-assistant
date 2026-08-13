"""
Simplified FHIR-style models for the clinical data we work with.

These follow the shape of real FHIR resources (Patient, Condition,
ServiceRequest) without pulling in a full FHIR library - enough to be
authentic to the standard while staying readable. The CMS prior auth
rule is built around FHIR, which is why we model our data this way
rather than inventing an arbitrary JSON shape.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class Patient(BaseModel):
    """FHIR Patient resource (trimmed to what we use)."""
    id: str
    given_name: str
    family_name: str
    birth_date: date
    gender: str


class Condition(BaseModel):
    """FHIR Condition resource - a diagnosis."""
    code: str = Field(description="ICD-10 diagnosis code")
    display: str = Field(description="Human-readable diagnosis name")
    onset_date: Optional[date] = None


class ServiceRequest(BaseModel):
    """FHIR ServiceRequest - the procedure/treatment being requested."""
    code: str = Field(description="CPT/HCPCS procedure code")
    display: str = Field(description="Human-readable procedure name")
    reason: str = Field(description="Clinical reason for the request")


class ClinicalNote(BaseModel):
    """
    A bundle tying together the patient, their conditions, and the
    requested service - the full input to the prior auth agent.
    """
    patient: Patient
    conditions: list[Condition]
    requested_service: ServiceRequest
    note_text: str = Field(description="Free-text clinical narrative")