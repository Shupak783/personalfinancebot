import { Activity, Bot, AlertTriangle, Gauge } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { MetricTile } from "@/components/MetricTile";
import { AgentTrendChart } from "@/components/AgentTrendChart";
import { ActivityFeed } from "@/components/ActivityFeed";
import { AlertsPanel } from "@/components/AlertsPanel";
import {
  agents,
  metrics,
  activityFeed,
  alerts,
  financeActivity30d,
  clippingActivity30d,
} from "@/lib/mock-data";

export default function OverviewPage() {
  const connected = agents.filter((a) => a.live).length;

  return (
    <div className="pb-28 lg:pb-16">
      <PageHeader
        eyebrow="Command Center"
        title="Overview"
        subtitle="Live status, activity, and alerts across every agent connected to JARVIS."
      />

      <section className="mt-6 grid grid-cols-1 gap-4 px-4 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
        <MetricTile
          icon={<Bot className="h-4 w-4" style={{ color: "var(--color-cyan)" }} />}
          label="Active agents"
          value={`${connected}`}
          suffix={`/ ${agents.length}`}
          deltaLabel={metrics.activeAgents.deltaLabel}
          trend={metrics.activeAgents.trend}
          accent="var(--color-cyan)"
          delay={0}
        />
        <MetricTile
          icon={<Activity className="h-4 w-4" style={{ color: "var(--color-series-1)" }} />}
          label="Activity (7d)"
          value={metrics.recentActivity.value.toLocaleString()}
          deltaPct={metrics.recentActivity.deltaPct}
          upIsGood
          trend={metrics.recentActivity.trend}
          accent="var(--color-series-1)"
          delay={80}
        />
        <MetricTile
          icon={<AlertTriangle className="h-4 w-4" style={{ color: "var(--color-warning)" }} />}
          label="Alerts open"
          value={`${metrics.alertsOpen.value}`}
          deltaPct={metrics.alertsOpen.deltaPct}
          upIsGood={false}
          trend={metrics.alertsOpen.trend}
          accent="var(--color-warning)"
          delay={160}
        />
        <MetricTile
          icon={<Gauge className="h-4 w-4" style={{ color: "var(--color-series-3)" }} />}
          label="Avg response"
          value={`${metrics.avgResponseMs.value}`}
          suffix="ms"
          deltaPct={metrics.avgResponseMs.deltaPct}
          upIsGood={false}
          trend={metrics.avgResponseMs.trend}
          accent="var(--color-series-3)"
          delay={240}
        />
      </section>

      <section className="mt-4 grid grid-cols-1 gap-4 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
        <AgentTrendChart
          title="Finance Agent"
          subtitle="Transactions logged, syncs, and check-ins"
          data={financeActivity30d}
          color="var(--color-series-1)"
          status="online"
          delay={320}
        />
        <AgentTrendChart
          title="Clipping Bot"
          subtitle="Not yet connected — showing projected baseline"
          data={clippingActivity30d}
          color="var(--color-series-2)"
          status="pending"
          delay={380}
        />
      </section>

      <section className="mt-4 grid grid-cols-1 gap-4 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">
        <div className="lg:col-span-2">
          <ActivityFeed events={activityFeed} delay={440} />
        </div>
        <AlertsPanel alerts={alerts} delay={500} />
      </section>
    </div>
  );
}
