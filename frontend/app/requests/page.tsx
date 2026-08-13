"use client";

import { useEffect, useState } from "react";
import { listRequests, PriorAuthResult } from "@/lib/api";

export default function RequestsPage() {
  const [requests, setRequests] = useState<PriorAuthResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRequests().then(setRequests).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Processed requests</h1>
      <p className="mt-2 text-sm text-slate-400">
        Every prior authorization the agent has adjudicated this session.
      </p>

      {requests.length === 0 ? (
        <p className="mt-8 text-slate-500">Nothing submitted yet.</p>
      ) : (
        <div className="mt-8 overflow-hidden rounded-2xl border border-white/5 bg-white/[0.02]">
          <table className="w-full text-sm">
            <thead className="border-b border-white/5 text-left text-[11px] uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3.5 font-medium">Patient</th>
                <th className="px-5 py-3.5 font-medium">Procedure</th>
                <th className="px-5 py-3.5 font-medium">Determination</th>
                <th className="px-5 py-3.5 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-4 font-medium text-slate-200">{r.patient_name}</td>
                  <td className="px-5 py-4 text-slate-400">{r.procedure_name}</td>
                  <td className="px-5 py-4">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${r.pa_required ? "bg-amber-500/15 text-amber-400" : "bg-emerald-500/15 text-emerald-400"}`}>
                      {r.pa_required ? "PA required" : "Not required"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-slate-300">
                    {r.confidence !== null ? `${Math.round(r.confidence * 100)}%` : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}