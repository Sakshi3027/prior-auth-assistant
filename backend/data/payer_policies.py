"""
Synthetic payer prior-authorization policies.

Fabricated but structured like real payer medical policies: each names a
procedure, states whether prior auth is required, and lists the specific
criteria a patient must meet to qualify. The agent retrieves the relevant
policy (RAG) and checks the patient against these criteria.

Kept in a plain list for now. This is deliberately isolated from the agent
so that later, a real ingestion pipeline can replace these synthetic
policies with chunked real payer-policy PDFs without touching agent logic.
"""
from pydantic import BaseModel, Field


class PayerPolicy(BaseModel):
    policy_id: str
    payer_name: str
    procedure_code: str = Field(description="CPT/HCPCS code this policy governs")
    procedure_name: str
    prior_auth_required: bool
    criteria: list[str] = Field(
        default_factory=list,
        description="Conditions the patient must meet for approval",
    )
    policy_text: str = Field(description="Full policy narrative, used for retrieval")


POLICIES: list[PayerPolicy] = [
    PayerPolicy(
        policy_id="POL-MRI-72148",
        payer_name="Meridian Health Plan",
        procedure_code="72148",
        procedure_name="MRI lumbar spine without contrast",
        prior_auth_required=True,
        criteria=[
            "Documented low back pain persisting at least 6 weeks",
            "Completion of at least 6 weeks of conservative treatment "
            "(physical therapy and/or NSAIDs)",
            "Absence of red-flag symptoms requiring emergent imaging",
        ],
        policy_text=(
            "Prior authorization is required for MRI of the lumbar spine "
            "(CPT 72148). Approval requires documentation of low back pain "
            "persisting for a minimum of 6 weeks, completion of at least 6 "
            "weeks of conservative management including physical therapy or "
            "a trial of NSAIDs, and no red-flag symptoms (such as suspected "
            "malignancy, infection, cauda equina, or acute neurological "
            "deficit) that would warrant emergent imaging without a "
            "conservative-care trial."
        ),
    ),
    PayerPolicy(
        policy_id="POL-DRUG-J3357",
        payer_name="Meridian Health Plan",
        procedure_code="J3357",
        procedure_name="Ustekinumab injection",
        prior_auth_required=True,
        criteria=[
            "Diagnosis of moderate-to-severe plaque psoriasis",
            "Affected body surface area of at least 10 percent",
            "Documented failure of, or intolerance to, at least one "
            "conventional systemic therapy (e.g., methotrexate)",
        ],
        policy_text=(
            "Prior authorization is required for ustekinumab (HCPCS J3357). "
            "Approval requires a diagnosis of moderate-to-severe plaque "
            "psoriasis with at least 10 percent body surface area involvement, "
            "and documented failure of, or intolerance to, at least one "
            "conventional systemic agent such as methotrexate (step therapy). "
            "This is a specialty biologic subject to step-therapy requirements."
        ),
    ),
    PayerPolicy(
        policy_id="POL-VISIT-99213",
        payer_name="Meridian Health Plan",
        procedure_code="99213",
        procedure_name="Office/outpatient visit, established patient",
        prior_auth_required=False,
        criteria=[],
        policy_text=(
            "Routine established-patient office and outpatient evaluation and "
            "management visits (CPT 99213) do not require prior authorization."
        ),
    ),
]


POLICIES_BY_CODE = {p.procedure_code: p for p in POLICIES}