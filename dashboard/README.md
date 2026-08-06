# JARVIS — Orchestrator Dashboard

A central hub for monitoring and interacting with personal automation agents
(starting with the Finance Agent from this repo, later a content-clipping bot
and others). Dark, sci-fi HUD aesthetic — glowing cyan accents, glass panels,
scanlines, and animated data.

Currently wired up with **realistic mock data** (`src/lib/mock-data.ts`) so the
design and layout can be nailed down before any sub-agent APIs are connected.

## Stack

- Next.js (App Router) + React + TypeScript
- Tailwind CSS v4
- [Recharts](https://recharts.org) for sparklines and 30-day trend charts
- [lucide-react](https://lucide.dev) for icons

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project layout

```
src/
  app/
    page.tsx              - Overview: metric tiles, per-agent 30-day trends, activity feed, alerts
    finance-agent/page.tsx - Finance Agent detail placeholder
    clipping-bot/page.tsx  - Clipping Bot detail placeholder (not connected)
    layout.tsx             - Root layout: sidebar, mobile header, voice orb, HUD backdrop
    globals.css            - Design tokens, glass-panel/scanline/glow effects, animations
  components/               - Sidebar, MetricTile, AgentTrendChart, ActivityFeed, AlertsPanel, VoiceOrb, ...
  lib/
    mock-data.ts            - Mock agents, 30-day activity series, activity feed, alerts
    format.ts                - Number/relative-time formatting helpers
```

## Notes

- The chart color palette (cyan / amber / violet / emerald) is validated for
  colorblind-safe contrast on the app's near-black surface — see
  `globals.css` for the token values.
- The voice orb (bottom-right) is a UI affordance only; it toggles a
  "Listening…" state locally and isn't wired to anything yet.
- Built responsively for desktop and mobile browsers as a first step toward a
  future PWA.
