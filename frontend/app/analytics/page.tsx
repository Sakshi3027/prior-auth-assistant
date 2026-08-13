"use client";

import { useEffect, useState } from "react";
import { getAnalytics } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface Analytics {
  total_requests: number;
  pa_required: number;
  pa_not_required: number;
  avg_confidence: number;
}

const COLORS = ["#f59e0b", "#10b981"];

export default function AnalyticsPage() {
  const [data, setData] = useState<Analytics | null>(null);

  useEffect(() => { getAnalytics().then(setData); }, []);

  if (!data) return <p className="text-slate-400">Loading...</p>;

  const pieData = [
    { name: "PA required", value: data.pa_required },
    { name: "No PA needed", value: data.pa_not_required },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
      <p className="mt-2 text-sm text-slate-400">
        Aggregate view across all processed requests this session.
      </p>

      <div className="mt-8 grid grid-cols-3 gap-4">
        <Stat label="Total requests" value={data.total_requests} />
        <Stat label="PA required" value={data.pa_required} />
        <Stat label="Avg confidence" value={`${Math.round(data.avg_confidence * 100)}%`} />
      </div>

      <div className="mt-6 rounded-2xl border border-white/5 bg-white/[0.02] p-6">
        <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
          Determination breakdown
        </p>
        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={3}>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="none" />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#0d1526", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#e2e8f0" }} />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 13 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-5">
      <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}