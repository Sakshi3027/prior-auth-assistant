"""
FastAPI application exposing the prior auth agent.

Endpoints:
  POST /api/submit        - run a clinical note through the agent
  GET  /api/requests      - list all processed requests
  GET  /api/requests/{id} - one request with full trace
  GET  /api/analytics     - aggregate metrics for the dashboard
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import SubmitRequest, PriorAuthResult
from api import service
from db import request_repo as store

app = FastAPI(title="Prior Authorization Assistant")

# Allow localhost for dev, and any of this project's Vercel URLs
# (production + preview) via regex - robust against trailing slashes
# and changing preview URLs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://prior-auth-assistant.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/submit", response_model=PriorAuthResult)
def submit(req: SubmitRequest):
    return service.process_submission(req)

@app.post("/api/appeal")
def appeal(req: SubmitRequest):
    return {"appeal": service.draft_appeal_for(req)}

@app.get("/api/requests", response_model=list[PriorAuthResult])
def list_requests():
    return store.list_all()


@app.get("/api/requests/{request_id}", response_model=PriorAuthResult)
def get_request(request_id: str):
    result = store.get(request_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return result


@app.get("/api/analytics")
def analytics():
    requests = store.list_all()
    total = len(requests)
    pa_required = sum(1 for r in requests if r.pa_required)
    avg_conf = (
        round(sum(r.confidence for r in requests if r.confidence is not None)
              / max(1, sum(1 for r in requests if r.confidence is not None)), 2)
    )
    return {
        "total_requests": total,
        "pa_required": pa_required,
        "pa_not_required": total - pa_required,
        "avg_confidence": avg_conf if total else 0,
    }