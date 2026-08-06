"use client";

import type { ReactNode } from "react";
import { AreaChart, Area, ResponsiveContainer } from "recharts";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

export function MetricTile({
  icon,
  label,
  value,
  suffix,
  deltaPct,
  deltaLabel,
  upIsGood = true,
  trend,
  accent = "var(--color-cyan)",
  delay = 0,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  suffix?: string;
  deltaPct?: number;
  deltaLabel?: string;
  upIsGood?: boolean;
  trend: number[];
  accent?: string;
  delay?: number;
}) {
  const data = trend.map((v, i) => ({ i, v }));
  const hasDelta = typeof deltaPct === "number";
  const isUp = (deltaPct ?? 0) > 0;
  const isFlat = (deltaPct ?? 0) === 0;
  const goodDirection = isFlat ? true : isUp === upIsGood;
  const deltaColor = isFlat
    ? "var(--color-text-muted)"
    : goodDirection
      ? "var(--color-good)"
      : "var(--color-critical)";
  const gradId = `spark-${label.replace(/\s+/g, "-").toLowerCase()}`;

  return (
    <div
      className="glass-panel corner-brackets animate-fade-up rounded-lg p-4 sm:p-5"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span
            className="flex h-8 w-8 items-center justify-center rounded-md border"
            style={{
              borderColor: `color-mix(in oklab, ${accent} 45%, transparent)`,
              background: `color-mix(in oklab, ${accent} 12%, transparent)`,
            }}
          >
            {icon}
          </span>
          <span className="font-mono text-[11px] uppercase tracking-[0.15em] text-[var(--color-text-secondary)]">
            {label}
          </span>
        </div>
      </div>

      <div className="mt-4 flex items-end justify-between gap-3">
        <div>
          <div className="font-mono text-3xl font-semibold text-[var(--color-text-primary)] sm:text-[2rem]">
            {value}
            {suffix && (
              <span className="ml-1 text-base font-normal text-[var(--color-text-secondary)]">
                {suffix}
              </span>
            )}
          </div>
          {(hasDelta || deltaLabel) && (
            <div className="mt-1.5 flex items-center gap-1 font-mono text-xs">
              {hasDelta && !isFlat && (
                <span style={{ color: deltaColor }} className="flex items-center">
                  {isUp ? (
                    <ArrowUpRight className="h-3.5 w-3.5" />
                  ) : (
                    <ArrowDownRight className="h-3.5 w-3.5" />
                  )}
                  {Math.abs(deltaPct!).toFixed(1)}%
                </span>
              )}
              {hasDelta && isFlat && (
                <span style={{ color: deltaColor }} className="flex items-center">
                  <Minus className="h-3.5 w-3.5" />
                  0%
                </span>
              )}
              <span className="text-[var(--color-text-muted)]">
                {deltaLabel ?? "vs last 7d"}
              </span>
            </div>
          )}
        </div>

        <div className="h-12 w-24 shrink-0 sm:h-14 sm:w-28">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={accent} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={accent} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke={accent}
                strokeWidth={2}
                fill={`url(#${gradId})`}
                isAnimationActive={true}
                animationDuration={900}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
