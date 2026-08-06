import { AlertTriangle, AlertOctagon } from "lucide-react";
import type { AlertItem } from "@/lib/mock-data";
import { relativeTime } from "@/lib/format";

const SEVERITY_STYLE: Record<AlertItem["severity"], { icon: typeof AlertTriangle; color: string }> = {
  warning: { icon: AlertTriangle, color: "var(--color-warning)" },
  critical: { icon: AlertOctagon, color: "var(--color-critical)" },
};

export function AlertsPanel({
  alerts,
  delay = 0,
}: {
  alerts: AlertItem[];
  delay?: number;
}) {
  return (
    <div
      className="glass-panel animate-fade-up rounded-lg p-4 sm:p-5"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-mono text-sm font-semibold tracking-wide text-[var(--color-text-primary)]">
          Needs attention
        </h3>
        <span
          className="rounded-full border px-2 py-0.5 font-mono text-[10px] font-semibold"
          style={{
            color: "var(--color-warning)",
            borderColor: "color-mix(in oklab, var(--color-warning) 45%, transparent)",
            background: "color-mix(in oklab, var(--color-warning) 10%, transparent)",
          }}
        >
          {alerts.length}
        </span>
      </div>

      {alerts.length === 0 ? (
        <p className="mt-4 text-sm text-[var(--color-text-muted)]">
          No open alerts. Everything is nominal.
        </p>
      ) : (
        <ul className="mt-3 space-y-2">
          {alerts.map((alert) => {
            const { icon: Icon, color } = SEVERITY_STYLE[alert.severity];
            return (
              <li
                key={alert.id}
                className="flex items-start gap-3 rounded-md border px-3 py-2.5"
                style={{
                  borderColor: "color-mix(in oklab, " + color + " 30%, var(--color-panel-border))",
                  background: "color-mix(in oklab, " + color + " 6%, transparent)",
                }}
              >
                <Icon className="mt-0.5 h-4 w-4 shrink-0" style={{ color }} aria-hidden />
                <div className="min-w-0 flex-1">
                  <p className="text-sm leading-snug text-[var(--color-text-primary)]">
                    {alert.message}
                  </p>
                  <div className="mt-0.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                    <span>{alert.agentName}</span>
                    <span aria-hidden>&middot;</span>
                    <span>{relativeTime(alert.timestamp)}</span>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
