"use client";

import { useState } from "react";
import { submitRequest, draftAppeal, PriorAuthResult } from "@/lib/api";

const SAMPLE = {
  patient_name: "Jordan Reyes",
  procedure_code: "72148",
  procedure_name: "MRI lumbar spine without contrast",
  payer_name: "Meridian Health Plan",
  note_text:
    "48-year-old female with 10 weeks of persistent low back pain. Completed 6 weeks of physical therapy and a trial of NSAIDs with minimal improvement. No red-flag symptoms.",
};

const field =
  "mt-1.5 w-full rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-emerald-500/50 focus:bg-white/[0.05]";
const label = "text-xs font-medium uppercase tracking-wide text-slate-400";

export default function SubmitPage() {
  const [form, setForm] = useState(SAMPLE);
  const [result, setResult] = useState<PriorAuthResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [appeal, setAppeal] = useState<string | null>(null);
  const [appealing, setAppealing] = useState(false);

  const update = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm({ ...form, [k]: e.target.value });

  async function onSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);
    setAppeal(null);
    try {
      setResult(await submitRequest(form));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function onAppeal() {
    setAppealing(true);
    setAppeal(null);
    try {
      const res = await draftAppeal(form);
      setAppeal(res.appeal);
    } catch (e) {
      setAppeal(e instanceof Error ? e.message : "Appeal failed");
    } finally {
      setAppealing(false);
    }
  }

  const statusChip = (s: string) =>
    s === "met" ? "bg-emerald-500/15 text-emerald-400"
    : s === "unmet" ? "bg-red-500/15 text-red-400"
    : "bg-amber-500/15 text-amber-400";

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Submit a prior authorization</h1>
      <p className="mt-2 text-sm text-slate-400">
        Paste a clinical note and the requested procedure. The agent reads it, checks the payer policy, and drafts a justified request.
      </p>

      <div className="mt-8 space-y-5 rounded-2xl border border-white/5 bg-white/[0.02] p-6">
        <div className="grid grid-cols-2 gap-5">
          <div><span className={label}>Patient name</span><input className={field} value={form.patient_name} onChange={update("patient_name")} /></div>
          <div><span className={label}>Payer</span><input className={field} value={form.payer_name} onChange={update("payer_name")} /></div>
          <div><span className={label}>Procedure code</span><input className={field} value={form.procedure_code} onChange={update("procedure_code")} /></div>
          <div><span className={label}>Procedure name</span><input className={field} value={form.procedure_name} onChange={update("procedure_name")} /></div>
        </div>
        <div><span className={label}>Clinical note</span><textarea className={field} rows={5} value={form.note_text} onChange={update("note_text")} /></div>
        <button onClick={onSubmit} disabled={loading}
          className="rounded-lg bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 disabled:bg-slate-600 disabled:text-slate-400">
          {loading ? "Processing..." : "Run agent"}
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {result && (
        <div className="mt-6 overflow-hidden rounded-2xl border border-white/5 bg-white/[0.02]">
          <div className={`flex items-center justify-between px-6 py-4 ${result.pa_required ? "bg-amber-500/10" : "bg-emerald-500/10"}`}>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Determination</p>
              <p className={`text-lg font-semibold ${result.pa_required ? "text-amber-400" : "text-emerald-400"}`}>
                {result.pa_required ? "Prior authorization required" : "No prior authorization needed"}
              </p>
            </div>
            {result.confidence !== null && (
              <div className="text-right">
                <p className="text-xs uppercase tracking-wide text-slate-400">Confidence</p>
                <p className="text-lg font-semibold">{Math.round(result.confidence * 100)}%</p>
              </div>
            )}
          </div>

          <div className="space-y-5 p-6">
            {result.criteria.length > 0 && (
              <div className="space-y-2.5">
                {result.criteria.map((c, i) => (
                  <div key={i} className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <span className="text-sm font-medium text-slate-200">{c.criterion}</span>
                      <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusChip(c.status)}`}>{c.status}</span>
                    </div>
                    <p className="mt-1.5 text-sm text-slate-400">{c.justification}</p>
                  </div>
                ))}
              </div>
            )}

            {result.draft && (
              <div>
                <p className={label}>Drafted request</p>
                <p className="mt-2 whitespace-pre-wrap rounded-xl border border-white/5 bg-white/[0.02] p-4 text-sm leading-relaxed text-slate-300">{result.draft}</p>
              </div>
            )}

            {/* Appeal: offered when any criterion is not clearly met */}
            {result.criteria.some((c) => c.status !== "met") && (
              <div className="border-t border-white/5 pt-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={label}>Likely to be challenged</p>
                    <p className="mt-1 text-sm text-slate-400">Some criteria are unmet or uncertain. Draft an appeal arguing for reconsideration.</p>
                  </div>
                  <button onClick={onAppeal} disabled={appealing}
                    className="shrink-0 rounded-lg border border-emerald-500/40 px-4 py-2 text-sm font-semibold text-emerald-400 transition hover:bg-emerald-500/10 disabled:opacity-50">
                    {appealing ? "Drafting..." : "Draft appeal"}
                  </button>
                </div>
                {appeal && (
                  <p className="mt-4 whitespace-pre-wrap rounded-xl border border-white/5 bg-white/[0.02] p-4 text-sm leading-relaxed text-slate-300">{appeal}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}