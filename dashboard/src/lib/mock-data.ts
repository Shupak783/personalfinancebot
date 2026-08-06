export type AgentStatus = "online" | "degraded" | "offline" | "pending";

export type AgentId = "finance" | "clipping";

export interface AgentSummary {
  id: AgentId | string;
  name: string;
  shortLabel: string;
  status: AgentStatus;
  description: string;
  seriesColor: string;
  uptimePct: number;
  lastEvent: string;
  live: boolean;
}

export interface DayPoint {
  date: string;
  value: number;
}

export interface ActivityEvent {
  id: string;
  agent: AgentId | string;
  agentName: string;
  message: string;
  timestamp: string;
  level: "info" | "good" | "warning" | "critical";
}

export interface AlertItem {
  id: string;
  agent: AgentId | string;
  agentName: string;
  message: string;
  severity: "warning" | "critical";
  timestamp: string;
}

const MS_DAY = 86_400_000;

function seededRandom(seed: number) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function buildSeries(
  days: number,
  base: number,
  amplitude: number,
  seed: number,
  trendPerDay = 0,
): DayPoint[] {
  const rand = seededRandom(seed);
  const now = new Date("2026-08-06T09:00:00Z").getTime();
  const points: DayPoint[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const t = now - i * MS_DAY;
    const noise = (rand() - 0.5) * amplitude;
    const weekday = new Date(t).getUTCDay();
    const weekendDip = weekday === 0 || weekday === 6 ? -amplitude * 0.35 : 0;
    const trend = trendPerDay * (days - 1 - i);
    const value = Math.max(0, Math.round(base + noise + weekendDip + trend));
    points.push({ date: new Date(t).toISOString().slice(0, 10), value });
  }
  return points;
}

export const agents: AgentSummary[] = [
  {
    id: "finance",
    name: "Finance Agent",
    shortLabel: "FIN",
    status: "online",
    description:
      "Tracks balances, budgets, and transactions; answers spending questions from real account data.",
    seriesColor: "var(--color-series-1)",
    uptimePct: 99.94,
    lastEvent: "2m ago",
    live: true,
  },
  {
    id: "clipping",
    name: "Clipping Bot",
    shortLabel: "CLP",
    status: "pending",
    description:
      "Content-clipping agent for saving and summarizing articles, threads, and videos. Not yet connected.",
    seriesColor: "var(--color-series-2)",
    uptimePct: 0,
    lastEvent: "not connected",
    live: false,
  },
];

export const financeActivity30d = buildSeries(30, 34, 16, 11, 0.35);
export const clippingActivity30d = buildSeries(30, 12, 9, 42, -0.05);

export const financeActivity7d = financeActivity30d.slice(-7);
export const clippingActivity7d = clippingActivity30d.slice(-7);

export const alertsHistory7d = buildSeries(7, 1.4, 2, 7);
export const responseTimeHistory7d = buildSeries(7, 210, 40, 91, -1.2);

export const metrics = {
  activeAgents: {
    value: 1,
    ofTotal: 2,
    deltaLabel: "+0 vs last week",
    trend: [1, 1, 1, 1, 1, 1, 1],
  },
  recentActivity: {
    value: financeActivity7d.reduce((a, b) => a + b.value, 0) +
      clippingActivity7d.reduce((a, b) => a + b.value, 0),
    deltaPct: 12.4,
    direction: "up" as const,
    trend: financeActivity7d.map((d, i) => d.value + clippingActivity7d[i].value),
  },
  alertsOpen: {
    value: 3,
    deltaPct: -25,
    direction: "down" as const,
    trend: alertsHistory7d.map((d) => d.value),
  },
  avgResponseMs: {
    value: 184,
    deltaPct: -8.1,
    direction: "down" as const,
    trend: responseTimeHistory7d.map((d) => d.value),
  },
};

export const activityFeed: ActivityEvent[] = [
  {
    id: "evt-1",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Logged manual expense: $85.00 at Costco → Groceries",
    timestamp: "2026-08-06T08:58:00Z",
    level: "info",
  },
  {
    id: "evt-2",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Daily check-in complete — all budgets within range",
    timestamp: "2026-08-06T08:00:00Z",
    level: "good",
  },
  {
    id: "evt-3",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Dining budget at 91% with 9 days left in cycle",
    timestamp: "2026-08-06T08:00:03Z",
    level: "warning",
  },
  {
    id: "evt-4",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Plaid sync completed — 14 new transactions imported",
    timestamp: "2026-08-05T22:14:00Z",
    level: "info",
  },
  {
    id: "evt-5",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Paycheck detected: +$2,200.00 → Checking",
    timestamp: "2026-08-05T09:03:00Z",
    level: "good",
  },
  {
    id: "evt-6",
    agent: "clipping",
    agentName: "Clipping Bot",
    message: "Agent not yet connected — no live events",
    timestamp: "2026-08-04T00:00:00Z",
    level: "info",
  },
  {
    id: "evt-7",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Weekly recap email sent to kaplanjack01@gmail.com",
    timestamp: "2026-08-03T18:00:00Z",
    level: "info",
  },
  {
    id: "evt-8",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Unusual charge flagged: $412.00 at unrecognized merchant",
    timestamp: "2026-08-02T14:22:00Z",
    level: "critical",
  },
];

export const alerts: AlertItem[] = [
  {
    id: "alrt-1",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Unrecognized merchant charge of $412.00 needs review",
    severity: "critical",
    timestamp: "2026-08-02T14:22:00Z",
  },
  {
    id: "alrt-2",
    agent: "finance",
    agentName: "Finance Agent",
    message: "Dining budget at 91% of monthly limit",
    severity: "warning",
    timestamp: "2026-08-06T08:00:03Z",
  },
  {
    id: "alrt-3",
    agent: "clipping",
    agentName: "Clipping Bot",
    message: "Agent has no active connection — setup incomplete",
    severity: "warning",
    timestamp: "2026-08-01T00:00:00Z",
  },
];
