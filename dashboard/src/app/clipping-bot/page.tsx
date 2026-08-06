import { Scissors, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { agents } from "@/lib/mock-data";

export default function ClippingBotPage() {
  const agent = agents.find((a) => a.id === "clipping")!;

  return (
    <div className="pb-28 lg:pb-16">
      <PageHeader
        eyebrow="Sub-agent"
        title="Clipping Bot"
        subtitle={agent.description}
      />

      <div className="px-4 pt-2 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-wider text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-cyan-soft)]"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to overview
        </Link>
      </div>

      <section className="mt-6 px-4 sm:px-6 lg:px-8">
        <div className="glass-panel animate-fade-up flex flex-col items-center rounded-lg px-6 py-16 text-center">
          <span className="relative flex h-16 w-16 items-center justify-center rounded-full border border-dashed border-[var(--color-panel-border-hi)]">
            <Scissors className="h-7 w-7 text-[var(--color-text-muted)]" />
          </span>
          <h2 className="mt-5 font-mono text-lg font-semibold text-[var(--color-text-primary)]">
            Not connected yet
          </h2>
          <p className="mt-2 max-w-md text-sm text-[var(--color-text-secondary)]">
            The content-clipping agent isn&apos;t wired into JARVIS yet. Once it&apos;s
            deployed, this page will show live clip activity, source breakdowns, and a
            30-day trend chart — the same layout as Finance Agent.
          </p>
          <span className="mt-6 rounded-full border border-[var(--color-panel-border-hi)] bg-white/[0.03] px-3 py-1 font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
            Awaiting setup
          </span>
        </div>
      </section>
    </div>
  );
}
