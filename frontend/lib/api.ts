// Central place for talking to the FastAPI backend. The base URL comes from
// an env var so we can point at the deployed API in production without code
// changes - same pattern as the claims project.

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

export interface CriterionResult {
  criterion: string;
  status: string;
  justification: string;
}

export interface PriorAuthResult {
  id: string;
  patient_name: string;
  procedure_code: string;
  procedure_name: string;
  pa_required: boolean;
  criteria: CriterionResult[];
  draft: string | null;
  confidence: number | null;
  trace: string[];
  overridden?: boolean;
  override_decision?: string | null;
  override_reason?: string | null;
  override_by?: string | null;
}

export interface SubmitRequest {
  note_text: string;
  procedure_code: string;
  procedure_name: string;
  patient_name: string;
  payer_name?: string;
}

export async function submitRequest(body: SubmitRequest): Promise<PriorAuthResult> {
  const res = await fetch(`${API_BASE}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Submit failed: ${res.status}`);
  return res.json();
}

export async function listRequests(): Promise<PriorAuthResult[]> {
  const res = await fetch(`${API_BASE}/requests`);
  if (!res.ok) throw new Error(`List failed: ${res.status}`);
  return res.json();
}

export async function getAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error(`Analytics failed: ${res.status}`);
  return res.json();
}

export async function draftAppeal(body: SubmitRequest): Promise<{ appeal: string }> {
  const res = await fetch(`${API_BASE}/appeal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Appeal failed: ${res.status}`);
  return res.json();
}

export async function overrideRequest(
  request_id: string, decision: string, reason: string, reviewer: string
): Promise<PriorAuthResult> {
  const res = await fetch(`${API_BASE}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id, decision, reason, reviewer }),
  });
  if (!res.ok) throw new Error(`Override failed: ${res.status}`);
  return res.json();
}