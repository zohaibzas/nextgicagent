"use client";

import { useEffect, useState } from "react";
import { useUIStore } from "@/stores/ui.store";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard, Radio, Bot, GitBranch, AlertTriangle,
  ScrollText, BarChart3, Bell, Settings, Brain, ShoppingCart,
  Image, Layers, Search, ArrowRight, ListTodo,
} from "lucide-react";

const COMMANDS = [
  { label: "Overview Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "Pages" },
  { label: "Live Activity", href: "/dashboard/live", icon: Radio, group: "Pages" },
  { label: "Agents", href: "/dashboard/agents", icon: Bot, group: "Pages" },
  { label: "Workflows", href: "/dashboard/workflows", icon: GitBranch, group: "Pages" },
  { label: "Tasks", href: "/dashboard/tasks", icon: ListTodo, group: "Pages" },
  { label: "Queue Monitor", href: "/dashboard/queue", icon: Layers, group: "Pages" },
  { label: "AI Monitoring", href: "/dashboard/ai", icon: Brain, group: "Pages" },
  { label: "WooCommerce", href: "/dashboard/woocommerce", icon: ShoppingCart, group: "Pages" },
  { label: "Media Pipeline", href: "/dashboard/media", icon: Image, group: "Pages" },
  { label: "Errors", href: "/dashboard/errors", icon: AlertTriangle, group: "Pages" },
  { label: "Logs", href: "/dashboard/logs", icon: ScrollText, group: "Pages" },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3, group: "Pages" },
  { label: "Alerts", href: "/dashboard/alerts", icon: Bell, group: "Pages" },
  { label: "Settings", href: "/dashboard/settings", icon: Settings, group: "Pages" },
];

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPalette } = useUIStore();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const router = useRouter();

  const filtered = query
    ? COMMANDS.filter((c) =>
        c.label.toLowerCase().includes(query.toLowerCase())
      )
    : COMMANDS;

  useEffect(() => {
    setSelected(0);
  }, [query]);

  useEffect(() => {
    if (!commandPaletteOpen) {
      setQuery("");
      setSelected(0);
    }
  }, [commandPaletteOpen]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (!commandPaletteOpen) return;
      if (e.key === "Escape") setCommandPalette(false);
      if (e.key === "ArrowDown") setSelected((s) => Math.min(s + 1, filtered.length - 1));
      if (e.key === "ArrowUp") setSelected((s) => Math.max(s - 1, 0));
      if (e.key === "Enter" && filtered[selected]) {
        router.push(filtered[selected].href);
        setCommandPalette(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [commandPaletteOpen, filtered, selected, router, setCommandPalette]);

  if (!commandPaletteOpen) return null;

  return (
    <div className="command-overlay" onClick={() => setCommandPalette(false)}>
      <div className="command-box" onClick={(e) => e.stopPropagation()}>
        {/* Search Input */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "14px 16px",
            borderBottom: "1px solid var(--border-default)",
          }}
        >
          <Search size={16} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search pages, agents, workflows..."
            style={{
              flex: 1,
              background: "none",
              border: "none",
              outline: "none",
              fontSize: "0.9375rem",
              color: "var(--text-primary)",
              fontFamily: "var(--font-sans)",
            }}
          />
          <kbd
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: 4,
              padding: "2px 6px",
              fontSize: "0.6875rem",
              color: "var(--text-muted)",
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div style={{ maxHeight: 380, overflowY: "auto", padding: 6 }}>
          {filtered.length === 0 ? (
            <div
              style={{
                padding: 32,
                textAlign: "center",
                color: "var(--text-muted)",
                fontSize: "0.875rem",
              }}
            >
              No results found
            </div>
          ) : (
            filtered.map((cmd, i) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={cmd.href}
                  onClick={() => {
                    router.push(cmd.href);
                    setCommandPalette(false);
                  }}
                  onMouseEnter={() => setSelected(i)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    width: "100%",
                    padding: "9px 12px",
                    borderRadius: "var(--radius-md)",
                    background: i === selected ? "var(--brand-dim)" : "transparent",
                    border: "none",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "background var(--transition-fast)",
                  }}
                >
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "var(--radius-sm)",
                      background: i === selected ? "rgba(99,102,241,0.2)" : "var(--bg-elevated)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    <Icon size={15} style={{ color: i === selected ? "var(--brand-soft)" : "var(--text-muted)" }} />
                  </div>
                  <span
                    style={{
                      fontSize: "0.875rem",
                      fontWeight: 500,
                      color: i === selected ? "var(--brand-soft)" : "var(--text-secondary)",
                      flex: 1,
                    }}
                  >
                    {cmd.label}
                  </span>
                  {i === selected && (
                    <ArrowRight size={14} style={{ color: "var(--brand-soft)" }} />
                  )}
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "8px 16px",
            borderTop: "1px solid var(--border-default)",
            display: "flex",
            gap: 16,
            fontSize: "0.6875rem",
            color: "var(--text-disabled)",
          }}
        >
          <span>↑↓ navigate</span>
          <span>↵ open</span>
          <span>esc close</span>
        </div>
      </div>
    </div>
  );
}
