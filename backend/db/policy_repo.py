"""
Policy retrieval. Prefers an exact procedure-code match (precise, and covers
the normal case). Only falls back to pgvector semantic search when there's
no code match - and only then loads the embedding model, so the API stays
light on memory at startup (important on small free-tier instances).
"""
from sqlalchemy import select
from db.database import SessionLocal
from db.models import PolicyRecord
from data.payer_policies import PayerPolicy

_model = None


def _get_model():
    """Lazily load the embedding model only when a fuzzy search is needed."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def find_policy(query_text: str, procedure_code: str | None = None) -> PayerPolicy | None:
    session = SessionLocal()
    try:
        # 1. Exact code match - the precise, common path. No model needed.
        if procedure_code:
            exact = session.execute(
                select(PolicyRecord).where(PolicyRecord.procedure_code == procedure_code)
            ).scalar_one_or_none()
            if exact:
                return _to_domain(exact)

        # 2. Fallback: semantic search. Loads the model on first use only.
        emb = _get_model().encode(query_text).tolist()
        nearest = session.execute(
            select(PolicyRecord).order_by(PolicyRecord.embedding.cosine_distance(emb)).limit(1)
        ).scalar_one_or_none()
        return _to_domain(nearest) if nearest else None
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