"""
Policy retrieval for the serving API: exact procedure-code lookup.

Embeddings live in the policies table (generated in the offline seeding
step, db/init_db.py) and power semantic search in development. The deployed
API deliberately uses precise code matching only, so it doesn't need to load
the embedding model / torch at runtime - keeping the service lightweight
enough for small instances.
"""
from sqlalchemy import select
from db.database import SessionLocal
from db.models import PolicyRecord
from data.payer_policies import PayerPolicy


def find_policy(query_text: str, procedure_code: str | None = None) -> PayerPolicy | None:
    session = SessionLocal()
    try:
        if procedure_code:
            rec = session.execute(
                select(PolicyRecord).where(PolicyRecord.procedure_code == procedure_code)
            ).scalar_one_or_none()
            if rec:
                return _to_domain(rec)
        return None
    finally:
        session.close()


def _to_domain(rec: PolicyRecord) -> PayerPolicy:
    return PayerPolicy(
        policy_id=rec.policy_id,
        payer_name=rec.payer_name,
        procedure_code=rec.procedure_code,
        procedure_name=rec.procedure_name,
        prior_auth_required=rec.prior_auth_required,
        criteria=rec.criteria,
        policy_text=rec.policy_text,
    )