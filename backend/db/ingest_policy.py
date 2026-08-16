"""
Payer-policy ingestion pipeline.

Takes a real payer-policy PDF and turns it into a structured, searchable
policy record:

  PDF -> extract text -> LLM structures it (procedure code, PA flag,
  criteria) -> embed the policy text -> upsert into the policies table

This is why the policy layer was kept isolated from the agent: real
published policies flow into the exact same table the agent already reads
from, so ingesting a new policy needs zero changes to the agent.

Run: python -m db.ingest_policy data/sample_policy_mri_brain.pdf
"""
import json
import sys

from pypdf import PdfReader
from sqlalchemy import select

from agent.llm import llm
from db.database import SessionLocal
from db.models import PolicyRecord


STRUCTURE_PROMPT = """You are reading a payer medical policy for prior authorization.
Extract the following as a JSON object, and nothing else:

{{
  "policy_id": "<the policy number if present, else invent a short id>",
  "payer_name": "<the payer/plan name>",
  "procedure_code": "<the CPT/HCPCS code the policy governs>",
  "procedure_name": "<the procedure name>",
  "prior_auth_required": <true or false>,
  "criteria": ["<each approval criterion as a short standalone string>"]
}}

Policy text:
{policy_text}"""


def _extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _structure(policy_text: str) -> dict:
    raw = llm.invoke(STRUCTURE_PROMPT.format(policy_text=policy_text)).content.strip()
    start, end = raw.find("{"), raw.rfind("}") + 1
    return json.loads(raw[start:end])


def _embed(text: str) -> list[float]:
    # Lazy import so the serving API never loads this heavy dep.
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(text).tolist()


def ingest(pdf_path: str) -> str:
    print(f"reading {pdf_path}")
    text = _extract_text(pdf_path)

    print("structuring with LLM...")
    data = _structure(text)
    print(f"  -> {data['procedure_code']} ({data['procedure_name']}), "
          f"{len(data['criteria'])} criteria")

    print("embedding policy text...")
    embedding = _embed(text)

    session = SessionLocal()
    try:
        existing = session.get(PolicyRecord, data["policy_id"])
        if existing:
            existing.payer_name = data["payer_name"]
            existing.procedure_code = data["procedure_code"]
            existing.procedure_name = data["procedure_name"]
            existing.prior_auth_required = data["prior_auth_required"]
            existing.criteria = data["criteria"]
            existing.policy_text = text
            existing.embedding = embedding
            action = "updated"
        else:
            session.add(PolicyRecord(
                policy_id=data["policy_id"],
                payer_name=data["payer_name"],
                procedure_code=data["procedure_code"],
                procedure_name=data["procedure_name"],
                prior_auth_required=data["prior_auth_required"],
                criteria=data["criteria"],
                policy_text=text,
                embedding=embedding,
            ))
            action = "inserted"
        session.commit()
    finally:
        session.close()

    print(f"{action} policy {data['policy_id']} into the database")
    return data["policy_id"]


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_policy_mri_brain.pdf"
    ingest(path)