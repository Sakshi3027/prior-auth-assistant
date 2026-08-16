"""
FHIR Prior Authorization Support (PAS) representation.

The CMS interoperability rule requires prior authorization to run over FHIR
APIs following the Da Vinci PAS implementation guide, where a request is a
FHIR Claim resource and the decision is a ClaimResponse. This module maps a
stored PriorAuthResult into that shape, so the API can speak the exact
standard payers are mandated to adopt.

This is a faithful, readable subset of PAS - not a full IG-conformant
bundle - focused on the Claim/ClaimResponse pair and the adjudication
disposition.
"""
from api.schemas import PriorAuthResult

def _justification(c) -> str:
    """Criteria may be Pydantic objects or plain dicts depending on source."""
    return c.justification if hasattr(c, "justification") else c.get("justification", "")


def _disposition(result: PriorAuthResult) -> str:
    if result.overridden and result.override_decision:
        return result.override_decision.lower()
    if not result.pa_required:
        return "no-auth-required"
    if (result.confidence or 0) >= 1:
        return "approved"
    return "pended"  # needs manual review / likely denial


def to_claim(result: PriorAuthResult) -> dict:
    """The prior auth request as a FHIR Claim resource (PAS profile)."""
    return {
        "resourceType": "Claim",
        "id": result.id,
        "status": "active",
        "use": "preauthorization",
        "patient": {"display": result.patient_name},
        "insurer": {"display": result.procedure_name and "Payer"},
        "item": [
            {
                "sequence": 1,
                "productOrService": {
                    "coding": [
                        {
                            "system": "http://www.ama-assn.org/go/cpt",
                            "code": result.procedure_code,
                            "display": result.procedure_name,
                        }
                    ]
                },
            }
        ],
    }


def to_claim_response(result: PriorAuthResult) -> dict:
    """The adjudication decision as a FHIR ClaimResponse resource."""
    disposition = _disposition(result)
    outcome = "complete" if disposition in ("approved", "no-auth-required", "denied") else "queued"

    return {
        "resourceType": "ClaimResponse",
        "id": f"resp-{result.id}",
        "status": "active",
        "use": "preauthorization",
        "outcome": outcome,
        "disposition": disposition,
        "patient": {"display": result.patient_name},
        "request": {"reference": f"Claim/{result.id}"},
        "item": [
            {
                "itemSequence": 1,
                "adjudication": [
                    {
                        "category": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/adjudication",
                                    "code": "submitted",
                                }
                            ]
                        },
                        "reason": {"text": _justification(c)},
                    }
                    for c in result.criteria
                ],
            }
        ],
    }


def to_pas_bundle(result: PriorAuthResult) -> dict:
    """Both resources wrapped in a FHIR Bundle, as PAS exchanges them."""
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": to_claim(result)},
            {"resource": to_claim_response(result)},
        ],
    }