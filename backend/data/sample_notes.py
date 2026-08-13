"""
Synthetic clinical notes for development and testing.

All patients, conditions, and narratives here are entirely fabricated -
no real patient data. Modeled as FHIR-shaped ClinicalNote bundles so the
agent works against realistic, standards-aligned input.
"""
from datetime import date
from models.fhir import Patient, Condition, ServiceRequest, ClinicalNote


# Case 1: MRI for chronic back pain - typically requires prior auth,
# and payers usually want documented conservative treatment first.
CASE_MRI_BACK = ClinicalNote(
    patient=Patient(
        id="PT-1001",
        given_name="Jordan",
        family_name="Reyes",
        birth_date=date(1979, 3, 14),
        gender="female",
    ),
    conditions=[
        Condition(code="M54.5", display="Low back pain", onset_date=date(2025, 11, 1)),
    ],
    requested_service=ServiceRequest(
        code="72148",
        display="MRI lumbar spine without contrast",
        reason="Persistent low back pain unresponsive to conservative care",
    ),
    note_text=(
        "48-year-old female with 10 weeks of persistent low back pain. "
        "Completed 6 weeks of physical therapy and a trial of NSAIDs with "
        "minimal improvement. No red-flag symptoms. Requesting MRI lumbar "
        "spine to evaluate for disc pathology before considering referral "
        "to orthopedics."
    ),
)


# Case 2: High-cost specialty drug - almost always requires prior auth,
# usually with step-therapy criteria.
CASE_SPECIALTY_DRUG = ClinicalNote(
    patient=Patient(
        id="PT-1002",
        given_name="Sam",
        family_name="Okafor",
        birth_date=date(1990, 7, 22),
        gender="male",
    ),
    conditions=[
        Condition(code="L40.0", display="Plaque psoriasis", onset_date=date(2023, 5, 10)),
    ],
    requested_service=ServiceRequest(
        code="J3357",
        display="Ustekinumab injection",
        reason="Moderate-to-severe plaque psoriasis, inadequate response to prior therapy",
    ),
    note_text=(
        "34-year-old male with moderate-to-severe plaque psoriasis affecting "
        "18% body surface area. Has failed topical corticosteroids and a "
        "3-month trial of methotrexate with continued active disease. "
        "Requesting ustekinumab."
    ),
)


# Case 3: Routine office visit - does NOT require prior auth. Tests the
# agent's ability to short-circuit early.
CASE_ROUTINE_VISIT = ClinicalNote(
    patient=Patient(
        id="PT-1003",
        given_name="Priya",
        family_name="Nair",
        birth_date=date(1998, 1, 5),
        gender="female",
    ),
    conditions=[
        Condition(code="J06.9", display="Acute upper respiratory infection"),
    ],
    requested_service=ServiceRequest(
        code="99213",
        display="Office/outpatient visit, established patient",
        reason="Evaluation of cold symptoms",
    ),
    note_text=(
        "26-year-old female presents with 3 days of nasal congestion and "
        "sore throat. Routine established-patient office visit."
    ),
)


ALL_CASES = {
    "mri_back": CASE_MRI_BACK,
    "specialty_drug": CASE_SPECIALTY_DRUG,
    "routine_visit": CASE_ROUTINE_VISIT,
}