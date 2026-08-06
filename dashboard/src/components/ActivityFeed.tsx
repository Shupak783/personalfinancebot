import { CheckCircle2, Info, AlertTriangle, AlertOctagon } from "lucide-react";
import type { ActivityEvent } from "@/lib/mock-data";
import { relativeTime } from "@/lib/format";

const LEVEL_STYLE: Record<
  ActivityEvent["level"],
  { icon: typeof Info; color: string }
> = {
  info: { icon: Info, color: "var(--color-cyan-soft)" },
  good: { icon: CheckCircle2, color: "var(--color-good)" },
  warning: { icon: AlertTriangle, color: "var(--color-warning)" },
  critical: { icon: AlertOctagon, color: "var(--color-critical)" },
};

export function ActivityFeed({
  events,
  delay = 0,
}: {
  events: ActivityEvent[];
  delay?: number;
}) {
  return (
    <div
      className="glass-panel animate-fade-up rounded-lg p-4 sm:p-5"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-mono text-sm font-semibold tracking-wide text-[var(--color-text-primary)]">
          Activity feed
        </h3>
        <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
          Live
        </span>
      </div>

      <ul className="mt-3 space-y-0.5">
        {events.map((event) => {
          const { icon: Icon, color } = LEVEL_STYLE[event.level];
          return (
            <li
              key={event.id}
              className="flex items-start gap-3 rounded-md px-2 py-2.5 transition-colors hover:bg-white/[0.03]"
            >
              <Icon
                className="mt-0.5 h-4 w-4 shrink-0"
                style={{ color }}
                aria-hidden
              />
              <div className="min-w-0 flex-1">
                <p className="text-sm leading-snug text-[var(--color-text-primary)]">
                  {event.message}
                </p>
                <div className="mt-0.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                  <span>{event.agentName}</span>
                  <span aria-hidden>&middot;</span>
                  <span>{relativeTime(event.timestamp)}</span>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
