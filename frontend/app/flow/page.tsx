"use client";

import { useState } from "react";
import ReactFlow, { Background, Controls, Node, Edge, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import { submitRequest } from "@/lib/api";

const SAMPLE = {
  patient_name: "Jordan Reyes",
  procedure_code: "72148",
  procedure_name: "MRI lumbar spine without contrast",
  payer_name: "Meridian Health Plan",
  note_text:
    "48-year-old female with 10 weeks of persistent low back pain. Completed 6 weeks of physical therapy and a trial of NSAIDs with minimal improvement. No red-flag symptoms.",
};

const NODES = [
  { id: "extract", label: "Extract", desc: "Read note, identify procedure" },
  { id: "triage", label: "Triage", desc: "Is PA required?" },
  { id: "retrieve", label: "Retrieve", desc: "Find payer policy (RAG)" },
  { id: "evaluate", label: "Evaluate", desc: "Check each criterion" },
  { id: "draft", label: "Draft", desc: "Write cited request" },
];

export default function FlowPage() {
  const [visited, setVisited] = useState<Set<string>>(new Set());
  const [running, setRunning] = useState(false);

  async function run() {
    setRunning(true);
    setVisited(new Set());
    // Animate nodes lighting up in sequence for effect
    for (const n of NODES) {
      await new Promise((r) => setTimeout(r, 400));
      setVisited((prev) => new Set(prev).add(n.id));
    }
    // Actually run the agent and reconcile with the real trace
    const result = await submitRequest(SAMPLE);
    const fired = new Set<string>();
    result.trace.forEach((line) => {
      NODES.forEach((n) => { if (line.startsWith(n.id)) fired.add(n.id); });
    });
    setVisited(fired);
    setRunning(false);
  }

  const nodes: Node[] = NODES.map((n, i) => {
    const active = visited.has(n.id);
    return {
      id: n.id,
      position: { x: 100, y: i * 110 },
      data: { label: (
        <div className="text-left">
          <div className="text-sm font-semibold">{n.label}</div>
          <div className="text-[11px] opacity-70">{n.desc}</div>
        </div>
      )},
      style: {
        width: 220,
        borderRadius: 12,
        border: active ? "1px solid #10b981" : "1px solid rgba(255,255,255,0.1)",
        background: active ? "rgba(16,185,129,0.12)" : "rgba(255,255,255,0.02)",
        color: active ? "#6ee7b7" : "#94a3b8",
        padding: 12,
      },
    };
  });

  const edges: Edge[] = NODES.slice(0, -1).map((n, i) => ({
    id: `${n.id}-${NODES[i + 1].id}`,
    source: n.id,
    target: NODES[i + 1].id,
    animated: running,
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { stroke: "rgba(255,255,255,0.15)" },
  }));

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Agent flow</h1>
      <p className="mt-2 text-sm text-slate-400">
        The five-node LangGraph pipeline. Run it to watch each node fire - nodes that don't apply (like retrieval when no PA is needed) stay dim.
      </p>

      <button onClick={run} disabled={running}
        className="mt-6 rounded-lg bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 disabled:bg-slate-600 disabled:text-slate-400">
        {running ? "Running..." : "Run pipeline"}
      </button>

      <div className="mt-6 h-[620px] rounded-2xl border border-white/5 bg-white/[0.02]">
        <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
          <Background color="#1e293b" gap={20} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}