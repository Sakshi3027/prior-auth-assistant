import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Prior Authorization Assistant",
  description: "AI agent that drafts prior authorization requests from clinical notes",
};

const nav = [
  { href: "/", label: "Submit", icon: "＋" },
  { href: "/flow", label: "Agent flow", icon: "◈" },
  { href: "/requests", label: "Requests", icon: "▤" },
  { href: "/analytics", label: "Analytics", icon: "▧" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0b1220] text-slate-100 antialiased">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 bg-[#0d1526] px-5 py-7 md:flex">
            <div className="mb-10">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">✦</span>
                <span className="text-sm font-semibold tracking-tight">PriorAuth<span className="text-emerald-400">AI</span></span>
              </div>
              <p className="mt-1 pl-10 text-[11px] text-slate-500">Provider-side agent</p>
            </div>

            <nav className="flex flex-col gap-1">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"
                >
                  <span className="text-xs opacity-70">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="mt-auto rounded-xl border border-white/5 bg-white/[0.02] p-3">
              <p className="text-[11px] leading-relaxed text-slate-500">
                Synthetic data only. No real patient information.
              </p>
            </div>
          </aside>

          {/* Main */}
          <div className="flex-1">
            <div className="mx-auto max-w-4xl px-6 py-10 md:px-10">{children}</div>
          </div>
        </div>
      </body>
    </html>
  );
}