"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { DayPoint, AgentStatus } from "@/lib/mock-data";
import { StatusDot } from "./StatusDot";

function formatDay(iso: string) {
  const d = new Date(iso + "T00:00:00Z");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
}

function ChartTooltip({
  active,
  payload,
  color,
  unit,
}: {
  active?: boolean;
  payload?: { payload: DayPoint }[];
  color: string;
  unit: string;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="glass-panel rounded-md px-3 py-2">
      <div className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
        {formatDay(point.date)}
      </div>
      <div className="mt-0.5 flex items-center gap-1.5 font-mono text-sm font-semibold text-[var(--color-text-primary)]">
        <span
          className="inline-block h-[2px] w-3"
          style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }}
        />
        {point.value.toLocaleString()} {unit}
      </div>
    </div>
  );
}

export function AgentTrendChart({
  title,
  subtitle,
  data,
  color,
  status,
  unit = "events",
  delay = 0,
}: {
  title: string;
  subtitle?: string;
  data: DayPoint[];
  color: string;
  status?: AgentStatus;
  unit?: string;
  delay?: number;
}) {
  const total = data.reduce((a, b) => a + b.value, 0);
  const gradId = `trend-${title.replace(/\s+/g, "-").toLowerCase()}`;

  return (
    <div
      className="glass-panel animate-fade-up rounded-lg p-4 sm:p-5"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-mono text-sm font-semibold tracking-wide text-[var(--color-text-primary)]">
              {title}
            </h3>
            {status && <StatusDot status={status} />}
          </div>
          {subtitle && (
            <p className="mt-0.5 text-xs text-[var(--color-text-muted)]">{subtitle}</p>
          )}
        </div>
        <div className="text-right">
          <div className="font-mono text-lg font-semibold text-[var(--color-text-primary)]">
            {total.toLocaleString()}
          </div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
            30d total
          </div>
        </div>
      </div>

      <div className="mt-4 h-48 sm:h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.32} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              vertical={false}
              stroke="var(--color-panel-border)"
              strokeDasharray="0"
            />
            <XAxis
              dataKey="date"
              tickFormatter={formatDay}
              tick={{ fill: "var(--color-text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--color-panel-border)" }}
              interval={6}
              minTickGap={20}
            />
            <YAxis
              tick={{ fill: "var(--color-text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={40}
              allowDecimals={false}
            />
            <Tooltip
              content={<ChartTooltip color={color} unit={unit} />}
              cursor={{ stroke: "var(--color-cyan)", strokeWidth: 1, strokeDasharray: "3 3" }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              fill={`url(#${gradId})`}
              activeDot={{ r: 4, stroke: "var(--color-void)", strokeWidth: 2 }}
              isAnimationActive={true}
              animationDuration={1100}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
