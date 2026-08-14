"""
SQLAlchemy models for persisted prior auth requests and payer policies.
The policy table carries a pgvector embedding column so retrieval can be
a real semantic search rather than an exact code lookup.
"""
from sqlalchemy import String, Boolean, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from db.database import Base


class RequestRecord(Base):
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    patient_name: Mapped[str] = mapped_column(String(200))
    procedure_code: Mapped[str] = mapped_column(String(20))
    procedure_name: Mapped[str] = mapped_column(String(300))
    pa_required: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    draft: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    trace: Mapped[list] = mapped_column(JSON, default=list)


class PolicyRecord(Base):
    __tablename__ = "policies"

    policy_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    payer_name: Mapped[str] = mapped_column(String(200))
    procedure_code: Mapped[str] = mapped_column(String(20), index=True)
    procedure_name: Mapped[str] = mapped_column(String(300))
    prior_auth_required: Mapped[bool] = mapped_column(Boolean)
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    policy_text: Mapped[str] = mapped_column(Text)
    # 384 dims = the sentence-transformers all-MiniLM-L6-v2 embedding size
    embedding: Mapped[list] = mapped_column(Vector(384))