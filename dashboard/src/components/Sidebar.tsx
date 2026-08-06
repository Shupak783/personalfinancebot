"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { LayoutGrid, Landmark, Scissors, Radio } from "lucide-react";
import { agents } from "@/lib/mock-data";
import { StatusDot } from "./StatusDot";

const AGENT_ICON: Record<string, React.ComponentType<{ className?: string }>> = {
  finance: Landmark,
  clipping: Scissors,
};

const navItems = [
  { href: "/", label: "Overview", icon: LayoutGrid },
  ...agents.map((a) => ({
    href: `/${a.id === "finance" ? "finance-agent" : "clipping-bot"}`,
    label: a.name,
    icon: AGENT_ICON[a.id] ?? Radio,
    agent: a,
  })),
];

export function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col">
      <div className="px-5 pt-6 pb-5">
        <div className="flex items-center gap-2.5">
          <div className="relative flex h-9 w-9 items-center justify-center">
            <span className="absolute inset-0 rounded-full border border-[var(--color-cyan)]/40" />
            <span className="absolute inset-[3px] rounded-full border border-[var(--color-cyan)]/70" />
            <span className="h-2 w-2 rounded-full bg-[var(--color-cyan)] shadow-[0_0_10px_var(--color-cyan)]" />
          </div>
          <div className="leading-tight">
            <div className="font-mono text-base font-semibold tracking-[0.2em] text-glow text-[var(--color-cyan-soft)]">
              JARVIS
            </div>
            <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--color-text-muted)]">
              Orchestrator
            </div>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        <div className="px-2 pb-1.5 pt-2 font-mono text-[10px] uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
          Navigation
        </div>
        {navItems.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={clsx(
                "group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-all",
                active
                  ? "bg-[var(--color-cyan)]/10 text-[var(--color-text-primary)]"
                  : "text-[var(--color-text-secondary)] hover:bg-white/[0.03] hover:text-[var(--color-text-primary)]",
              )}
            >
              <span
                className={clsx(
                  "absolute left-0 top-1/2 h-5 w-[2px] -translate-y-1/2 rounded-full bg-[var(--color-cyan)] transition-opacity",
                  active ? "opacity-100 shadow-[0_0_8px_var(--color-cyan)]" : "opacity-0",
                )}
              />
              <Icon
                className={clsx(
                  "h-4 w-4 shrink-0 transition-colors",
                  active ? "text-[var(--color-cyan-soft)]" : "text-[var(--color-text-muted)] group-hover:text-[var(--color-cyan-soft)]",
                )}
              />
              <span className="flex-1 truncate">{item.label}</span>
              {"agent" in item && item.agent && (
                <StatusDot status={item.agent.status} />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="mx-3 mb-4 mt-2 rounded-md border border-[var(--color-panel-border)] bg-white/[0.02] px-3 py-3">
        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
          <span>System</span>
          <StatusDot status="online" />
        </div>
        <div className="mt-1.5 font-mono text-xs text-[var(--color-text-secondary)]">
          All systems nominal
        </div>
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="glass-panel sticky top-0 hidden h-dvh w-64 shrink-0 flex-col overflow-y-auto lg:flex">
      <SidebarContent />
    </aside>
  );
}
