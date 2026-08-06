import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { MobileHeader } from "@/components/MobileHeader";
import { VoiceOrb } from "@/components/VoiceOrb";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JARVIS — Orchestrator",
  description: "Central command dashboard for personal automation agents.",
};

export const viewport: Viewport = {
  themeColor: "#05070a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full">
        <div className="hud-backdrop" />
        <div className="hud-scanline" />
        <div className="relative z-10 flex min-h-dvh">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <MobileHeader />
            <main className="flex-1">{children}</main>
          </div>
        </div>
        <VoiceOrb />
      </body>
    </html>
  );
}
