"""
One-time setup: enables the pgvector extension, creates tables, and seeds
the payer policies (with embeddings) from our synthetic policy data.
Run directly: python -m db.init_db
"""
from sqlalchemy import text
from db.database import engine, SessionLocal, Base
from db.models import PolicyRecord
from data.payer_policies import POLICIES
from sentence_transformers import SentenceTransformer


def init():
    # 1. Enable pgvector (safe to run repeatedly)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("pgvector extension ready")

    # 2. Create tables
    Base.metadata.create_all(engine)
    print("tables created")

    # 3. Seed policies with embeddings of their policy_text
    model = SentenceTransformer("all-MiniLM-L6-v2")
    session = SessionLocal()
    try:
        for p in POLICIES:
            if session.get(PolicyRecord, p.policy_id):
                continue  # already seeded
            emb = model.encode(p.policy_text).tolist()
            session.add(PolicyRecord(
                policy_id=p.policy_id,
                payer_name=p.payer_name,
                procedure_code=p.procedure_code,
                procedure_name=p.procedure_name,
                prior_auth_required=p.prior_auth_required,
                criteria=p.criteria,
                policy_text=p.policy_text,
                embedding=emb,
            ))
        session.commit()
        print(f"seeded {len(POLICIES)} policies with embeddings")
    finally:
        session.close()


if __name__ == "__main__":
    init()