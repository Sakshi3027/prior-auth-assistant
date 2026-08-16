"use client";

import { useState } from "react";
import { runBatch, PriorAuthResult, SubmitRequest } from "@/lib/api";

// A sample queue mixing approvals, a no-PA case, and a likely denial.
const QUEUE: SubmitRequest[] = [
  {
    patient_name: "Jordan Reyes", payer_name: "Meridian Health Plan",
    procedure_code: "72148", procedure_name: "MRI lumbar spine without contrast",
    note_text: "48F, 10 weeks persistent low back pain. Completed 6 weeks PT and NSAIDs. No red-flag symptoms.",
  },
  {
    patient_name: "Sam Okafor", payer_name: "Meridian Health Plan",
    procedure_code: "J3357", procedure_name: "Ustekinumab injection",
    note_text: "34M, plaque psoriasis 4% BSA, tried topical corticosteroids only.",
  },
  {
    patient_name: "Priya Nair", payer_name: "Meridian Health Plan",
    procedure_code: "99213", procedure_name: "Office visit, established patient",
    note_text: "26F, 3 days nasal congestion and sore throat. Routine visit.",
  },
  {
    patient_name: "Alex Kim", payer_name: "Meridian Health Plan",
    procedure_code: "J3357", procedure_name: "Ustekinumab injection",
    note_text: "41M, moderate-to-severe plaque psoriasis 22% BSA, failed 4-month methotrexate trial.",
  },
];

export default function BatchPage() {
  const [results, setResults] = useState<PriorAuthResult[]>([]);
  const [running, setRunning] = useState(false);

  async function run() {
    setRunning(true);
    setResults([]);
    try {
      setResults(await runBatch(QUEUE));
    } finally {
      setRunning(false);
    }
  }

  const chip = (r: PriorAuthResult) =>
    !r.pa_required ? "bg-emerald-500/15 text-emerald-400"
    : (r.confidence ?? 0) >= 1 ? "bg-amber-500/15 text-amber-400"
    : "bg-red-500/15 text-red-400";

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Batch processing</h1>
      <p className="mt-2 text-sm text-slate-400">
        Run a whole queue of pending requests through the agent at once. Useful for overnight processing of a day's submissions.
      </p>

      <button onClick={run} disabled={running}
        className="mt-6 rounded-lg bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 disabled:bg-slate-600 disabled:text-slate-400">
        {running ? `Processing ${QUEUE.length} requests...` : `Run batch (${QUEUE.length} requests)`}
      </button>

      {results.length > 0 && (
        <div className="mt-8 space-y-2">
          {results.map((r) => (
            <div key={r.id} className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] px-5 py-4">
              <div>
                <p className="font-medium text-slate-200">{r.patient_name}</p>
                <p className="text-sm text-slate-500">{r.procedure_name}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${chip(r)}`}>
                  {!r.pa_required ? "No PA needed" : (r.confidence ?? 0) >= 1 ? "PA required" : "Likely denial"}
                </span>
                <span className="text-sm text-slate-400">{r.confidence !== null ? `${Math.round((r.confidence ?? 0) * 100)}%` : "-"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}