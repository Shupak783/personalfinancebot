import { Landmark, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { AgentTrendChart } from "@/components/AgentTrendChart";
import { ActivityFeed } from "@/components/ActivityFeed";
import { agents, activityFeed, financeActivity30d } from "@/lib/mock-data";

export default function FinanceAgentPage() {
  const agent = agents.find((a) => a.id === "finance")!;
  const events = activityFeed.filter((e) => e.agent === "finance");

  return (
    <div className="pb-28 lg:pb-16">
      <PageHeader
        eyebrow="Sub-agent"
        title="Finance Agent"
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
        <div className="glass-panel animate-fade-up rounded-lg p-6 sm:p-8">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-lg border border-[var(--color-series-1)]/40 bg-[var(--color-series-1)]/10">
              <Landmark className="h-6 w-6 text-[var(--color-series-1)]" />
            </span>
            <div>
              <div className="font-mono text-lg font-semibold text-[var(--color-text-primary)]">
                Full agent console — coming soon
              </div>
              <p className="mt-0.5 text-sm text-[var(--color-text-secondary)]">
                This will host the live chat interface, budget breakdowns, and account
                sync controls wired directly to the finance agent&apos;s API.
              </p>
            </div>
          </div>

          <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-[var(--color-panel-border)] pt-6 sm:grid-cols-4">
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                Uptime
              </dt>
              <dd className="mt-1 font-mono text-lg text-[var(--color-text-primary)]">
                {agent.uptimePct}%
              </dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                Last event
              </dt>
              <dd className="mt-1 font-mono text-lg text-[var(--color-text-primary)]">
                {agent.lastEvent}
              </dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                Connection
              </dt>
              <dd className="mt-1 font-mono text-lg text-[var(--color-text-primary)]">Plaid</dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                Assistant
              </dt>
              <dd className="mt-1 font-mono text-lg text-[var(--color-text-primary)]">Claude</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="mt-4 grid grid-cols-1 gap-4 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">
        <div className="lg:col-span-2">
          <AgentTrendChart
            title="30-day activity"
            subtitle="Transactions, syncs, and check-ins"
            data={financeActivity30d}
            color="var(--color-series-1)"
            status="online"
            delay={80}
          />
        </div>
        <ActivityFeed events={events} delay={140} />
      </section>
    </div>
  );
}
