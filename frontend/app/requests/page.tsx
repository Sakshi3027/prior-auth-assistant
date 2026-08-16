"use client";

import { useEffect, useState } from "react";
import { listRequests, overrideRequest, PriorAuthResult } from "@/lib/api";

export default function RequestsPage() {
  const [requests, setRequests] = useState<PriorAuthResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState<string | null>(null);

  useEffect(() => {
    listRequests().then(setRequests).finally(() => setLoading(false));
  }, []);

  function onOverridden(updated: PriorAuthResult) {
    setRequests((rs) => rs.map((r) => (r.id === updated.id ? updated : r)));
    setOpenId(null);
  }

  if (loading) return <p className="text-slate-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Processed requests</h1>
      <p className="mt-2 text-sm text-slate-400">
        Every prior authorization the agent has adjudicated. A reviewer can override any determination.
      </p>

      {requests.length === 0 ? (
        <p className="mt-8 text-slate-500">Nothing submitted yet.</p>
      ) : (
        <div className="mt-8 space-y-2">
          {requests.map((r) => (
            <div key={r.id} className="overflow-hidden rounded-xl border border-white/5 bg-white/[0.02]">
              <button
                onClick={() => setOpenId(openId === r.id ? null : r.id)}
                className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-white/[0.02]"
              >
                <div>
                  <p className="font-medium text-slate-200">{r.patient_name}</p>
                  <p className="text-sm text-slate-500">{r.procedure_name}</p>
                </div>
                <div className="flex items-center gap-3">
                  {r.overridden && (
                    <span className="rounded-full bg-blue-500/15 px-2.5 py-0.5 text-xs font-semibold text-blue-400">
                      overridden → {r.override_decision}
                    </span>
                  )}
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${r.pa_required ? "bg-amber-500/15 text-amber-400" : "bg-emerald-500/15 text-emerald-400"}`}>
                    {r.pa_required ? "PA required" : "Not required"}
                  </span>
                  <span className="text-sm text-slate-400">{r.confidence !== null ? `${Math.round((r.confidence ?? 0) * 100)}%` : "-"}</span>
                </div>
              </button>

              {openId === r.id && <OverridePanel request={r} onDone={onOverridden} />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function OverridePanel({ request, onDone }: { request: PriorAuthResult; onDone: (r: PriorAuthResult) => void }) {
  const [decision, setDecision] = useState<"APPROVED" | "DENIED">("APPROVED");
  const [reason, setReason] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit() {
    setSaving(true);
    try {
      onDone(await overrideRequest(request.id, decision, reason, reviewer));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-3 border-t border-white/5 px-5 py-4">
      {request.overridden && (
        <p className="text-sm text-blue-400">
          Currently overridden to <strong>{request.override_decision}</strong> by {request.override_by} — {request.override_reason}
        </p>
      )}
      <div className="flex gap-2">
        {(["APPROVED", "DENIED"] as const).map((d) => (
          <button key={d} onClick={() => setDecision(d)}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold ${decision === d ? (d === "APPROVED" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400") : "bg-white/[0.03] text-slate-400"}`}>
            {d}
          </button>
        ))}
      </div>
      <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="Reviewer name"
        className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-emerald-500/50" />
      <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason for override"
        className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-emerald-500/50" />
      <button onClick={submit} disabled={saving || !reviewer || !reason}
        className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-emerald-950 hover:bg-emerald-400 disabled:opacity-50">
        {saving ? "Saving..." : "Submit override"}
      </button>
    </div>
  );
}