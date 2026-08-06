"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import { SidebarContent } from "./Sidebar";

export function MobileHeader() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="glass-panel sticky top-0 z-30 flex items-center justify-between px-4 py-3 lg:hidden">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[var(--color-cyan)] shadow-[0_0_10px_var(--color-cyan)]" />
          <span className="font-mono text-sm font-semibold tracking-[0.2em] text-glow text-[var(--color-cyan-soft)]">
            JARVIS
          </span>
        </div>
        <button
          aria-label="Open navigation"
          onClick={() => setOpen(true)}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-[var(--color-panel-border)] text-[var(--color-text-secondary)] active:bg-white/5"
        >
          <Menu className="h-5 w-5" />
        </button>
      </header>

      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <div className="glass-panel absolute inset-y-0 left-0 w-72 max-w-[85vw] overflow-y-auto">
            <button
              aria-label="Close navigation"
              onClick={() => setOpen(false)}
              className="absolute right-3 top-4 flex h-8 w-8 items-center justify-center rounded-md text-[var(--color-text-secondary)]"
            >
              <X className="h-5 w-5" />
            </button>
            <SidebarContent onNavigate={() => setOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
