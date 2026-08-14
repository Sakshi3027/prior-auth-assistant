"""
Policy retrieval backed by pgvector semantic search. Instead of an exact
procedure-code lookup, this embeds the incoming request and finds the
closest policy by cosine distance - the real RAG retrieval step.

Isolated here so the agent's retrieve node just calls find_policy() and
doesn't care whether it's code-lookup or vector search underneath.
"""
from sqlalchemy import select
from db.database import SessionLocal
from db.models import PolicyRecord
from data.payer_policies import PayerPolicy
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def find_policy(query_text: str, procedure_code: str | None = None) -> PayerPolicy | None:
    """
    Semantic search over policy embeddings. If a procedure code is given we
    still prefer an exact code match when one exists (codes are precise);
    otherwise we fall back to nearest-neighbour on the text embedding.
    """
    session = SessionLocal()
    try:
        if procedure_code:
            exact = session.execute(
                select(PolicyRecord).where(PolicyRecord.procedure_code == procedure_code)
            ).scalar_one_or_none()
            if exact:
                return _to_domain(exact)

        emb = _model.encode(query_text).tolist()
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