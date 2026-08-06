"use client";

import { useState } from "react";
import { Mic } from "lucide-react";
import { clsx } from "clsx";

export function VoiceOrb() {
  const [active, setActive] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-40 flex flex-col items-end gap-2 lg:bottom-8 lg:right-8">
      {active && (
        <div className="glass-panel animate-fade-up rounded-lg px-3 py-1.5 font-mono text-[11px] text-[var(--color-cyan-soft)]">
          Listening<span className="animate-blink">…</span>
        </div>
      )}
      <button
        aria-pressed={active}
        aria-label="Voice activation"
        onClick={() => setActive((v) => !v)}
        className="group relative flex h-12 w-12 items-center justify-center rounded-full lg:h-16 lg:w-16"
      >
        <span className="absolute inset-0 animate-orb-ring rounded-full border border-[var(--color-cyan)]/60" />
        <span
          className={clsx(
            "absolute inset-0 rounded-full border border-[var(--color-cyan)]/50 animate-orb-pulse",
          )}
        />
        <span
          className={clsx(
            "relative flex h-full w-full items-center justify-center rounded-full border transition-colors",
            active
              ? "border-[var(--color-cyan-soft)] bg-[var(--color-cyan)]/25"
              : "border-[var(--color-cyan)]/40 bg-[var(--color-panel)]/90",
          )}
          style={{ backdropFilter: "blur(6px)" }}
        >
          <span
            className="absolute inset-2 rounded-full opacity-40"
            style={{
              background:
                "radial-gradient(circle at 35% 30%, rgba(103,232,249,0.5), transparent 60%)",
            }}
          />
          <Mic
            className={clsx(
              "relative h-5 w-5 transition-colors lg:h-6 lg:w-6",
              active ? "text-white" : "text-[var(--color-cyan-soft)]",
            )}
          />
        </span>
      </button>
    </div>
  );
}
