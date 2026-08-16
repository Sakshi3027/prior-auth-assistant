"""
Postgres-backed store for processed requests. Same save/list/get shape as
the old in-memory store, so the service layer swaps to this with a one-line
import change.
"""
from sqlalchemy import select
from db.database import SessionLocal
from db.models import RequestRecord
from api.schemas import PriorAuthResult, CriterionResult


def save(result: PriorAuthResult) -> None:
    session = SessionLocal()
    try:
        session.add(RequestRecord(
            id=result.id,
            patient_name=result.patient_name,
            procedure_code=result.procedure_code,
            procedure_name=result.procedure_name,
            pa_required=result.pa_required,
            confidence=result.confidence,
            draft=result.draft,
            criteria=[c.model_dump() for c in result.criteria],
            trace=result.trace,
        ))
        session.commit()
    finally:
        session.close()


def list_all() -> list[PriorAuthResult]:
    session = SessionLocal()
    try:
        rows = session.execute(select(RequestRecord)).scalars().all()
        return [_to_schema(r) for r in reversed(rows)]
    finally:
        session.close()


def get(request_id: str) -> PriorAuthResult | None:
    session = SessionLocal()
    try:
        r = session.get(RequestRecord, request_id)
        return _to_schema(r) if r else None
    finally:
        session.close()


def _to_schema(r: RequestRecord) -> PriorAuthResult:
    return PriorAuthResult(
        id=r.id,
        patient_name=r.patient_name,
        procedure_code=r.procedure_code,
        procedure_name=r.procedure_name,
        pa_required=r.pa_required,
        criteria=[CriterionResult(**c) for c in (r.criteria or [])],
        draft=r.draft,
        confidence=r.confidence,
        trace=r.trace or [],
        overridden=r.overridden or False,
        override_decision=r.override_decision,
        override_reason=r.override_reason,
        override_by=r.override_by,
    )

def apply_override(request_id: str, decision: str, reason: str, reviewer: str) -> PriorAuthResult | None:
    session = SessionLocal()
    try:
        r = session.get(RequestRecord, request_id)
        if r is None:
            return None
        r.overridden = True
        r.override_decision = decision
        r.override_reason = reason
        r.override_by = reviewer
        session.commit()
        session.refresh(r)
        return _to_schema(r)
    finally:
        session.close()