import { StatusDot } from "./StatusDot";

export function PageHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4 px-4 pt-6 sm:px-6 lg:px-8 lg:pt-8">
      <div>
        <div className="font-mono text-[11px] uppercase tracking-[0.25em] text-[var(--color-cyan-soft)]">
          {eyebrow}
        </div>
        <h1 className="mt-1 font-mono text-2xl font-semibold tracking-wide text-[var(--color-text-primary)] sm:text-3xl">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1.5 max-w-2xl text-sm text-[var(--color-text-secondary)]">
            {subtitle}
          </p>
        )}
      </div>
      <div className="glass-panel flex items-center gap-2 rounded-full px-3 py-1.5">
        <StatusDot status="online" />
        <span className="font-mono text-xs text-[var(--color-text-secondary)]">
          All systems nominal
        </span>
      </div>
    </div>
  );
}
