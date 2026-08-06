export function compactNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function relativeTime(iso: string, now = new Date("2026-08-06T09:00:00Z")): string {
  const diffMs = now.getTime() - new Date(iso).getTime();
  const min = Math.round(diffMs / 60_000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.round(hr / 24);
  return `${day}d ago`;
}

export function signed(value: number, digits = 1): string {
  const sign = value > 0 ? "+" : value < 0 ? "" : "±";
  return `${sign}${value.toFixed(digits)}`;
}
