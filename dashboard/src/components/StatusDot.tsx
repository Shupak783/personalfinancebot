import { clsx } from "clsx";
import type { AgentStatus } from "@/lib/mock-data";

const STATUS_STYLE: Record<AgentStatus, { color: string; label: string }> = {
  online: { color: "var(--color-good)", label: "Online" },
  degraded: { color: "var(--color-warning)", label: "Degraded" },
  offline: { color: "var(--color-critical)", label: "Offline" },
  pending: { color: "var(--color-text-muted)", label: "Not connected" },
};

export function StatusDot({
  status,
  withLabel = false,
  className,
}: {
  status: AgentStatus;
  withLabel?: boolean;
  className?: string;
}) {
  const { color, label } = STATUS_STYLE[status];
  const pulsing = status === "online" || status === "degraded";
  return (
    <span className={clsx("inline-flex items-center gap-1.5", className)}>
      <span className="relative inline-flex h-2 w-2">
        {pulsing && (
          <span
            className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60"
            style={{ backgroundColor: color }}
          />
        )}
        <span
          className="relative inline-flex h-2 w-2 rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }}
        />
      </span>
      {withLabel && (
        <span className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)]">
          {label}
        </span>
      )}
    </span>
  );
}
