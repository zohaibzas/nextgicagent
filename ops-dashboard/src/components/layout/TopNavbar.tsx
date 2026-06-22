"use client";

import { useUIStore } from "@/stores/ui.store";
import { useAuthStore } from "@/stores/auth.store";
import { useRealtimeStore } from "@/stores/realtime.store";
import { Search, Bell, Menu, Command, LogOut, ChevronDown, Sun, Moon } from "lucide-react";
import { useState, useEffect } from "react";

export function TopNavbar({ title }: { title?: string }) {
  const { sidebarCollapsed, setCommandPalette, toggleMobileSidebar } = useUIStore();
  const { user, clearAuth } = useAuthStore();
  const { connected, liveAlerts } = useRealtimeStore();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [dark, setDark] = useState(true);

  const unreadAlerts = liveAlerts.filter((a) => !a.acknowledged).length;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPalette(true);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [setCommandPalette]);

  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "NG";

  return (
    <header
      className={`topbar ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}
      style={{ gap: 12 }}
    >
      {/* Mobile menu */}
      <button
        className="btn btn-ghost md:hidden"
        style={{ padding: "6px", minWidth: 0 }}
        onClick={toggleMobileSidebar}
      >
        <Menu size={18} />
      </button>

      {/* Page title */}
      {title && (
        <div
          style={{
            fontSize: "0.875rem",
            fontWeight: 600,
            color: "var(--text-primary)",
            letterSpacing: "-0.02em",
            whiteSpace: "nowrap",
          }}
        >
          {title}
        </div>
      )}

      {/* Search */}
      <button
        onClick={() => setCommandPalette(true)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "var(--bg-elevated)",
          border: "1px solid var(--border-default)",
          borderRadius: "var(--radius-md)",
          padding: "6px 12px",
          color: "var(--text-muted)",
          cursor: "pointer",
          fontSize: "0.8125rem",
          flex: 1,
          maxWidth: 320,
          transition: "all var(--transition-fast)",
        }}
        className="hover:border-[var(--border-strong)] hover:text-[var(--text-secondary)]"
      >
        <Search size={14} />
        <span style={{ flex: 1, textAlign: "left" }}>Search anything...</span>
        <span
          style={{
            display: "flex",
            alignItems: "center",
            gap: 2,
            background: "var(--bg-card)",
            border: "1px solid var(--border-default)",
            borderRadius: "4px",
            padding: "2px 6px",
            fontSize: "0.6875rem",
            color: "var(--text-disabled)",
          }}
        >
          <Command size={10} />K
        </span>
      </button>

      <div style={{ flex: 1 }} />

      {/* Connection status */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "4px 10px",
          background: connected ? "var(--success-dim)" : "var(--error-dim)",
          border: `1px solid ${connected ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"}`,
          borderRadius: "var(--radius-full)",
          fontSize: "0.6875rem",
          fontWeight: 600,
          color: connected ? "var(--success)" : "var(--error)",
          whiteSpace: "nowrap",
        }}
        className="hidden sm:flex"
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: connected ? "var(--success)" : "var(--error)",
            boxShadow: connected ? "0 0 5px var(--success)" : undefined,
            animation: connected ? "pulse-dot 2s ease-in-out infinite" : undefined,
          }}
        />
        {connected ? "Live" : "Offline"}
      </div>

      {/* Notifications */}
      <div style={{ position: "relative" }}>
        <button
          className="btn btn-ghost"
          style={{ padding: "7px", minWidth: 0 }}
        >
          <Bell size={16} />
          {unreadAlerts > 0 && (
            <span className="notif-badge">{unreadAlerts > 9 ? "9+" : unreadAlerts}</span>
          )}
        </button>
      </div>

      {/* User menu */}
      <div style={{ position: "relative" }}>
        <button
          onClick={() => setUserMenuOpen((v) => !v)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "none",
            border: "1px solid var(--border-default)",
            borderRadius: "var(--radius-md)",
            padding: "5px 10px",
            cursor: "pointer",
            transition: "all var(--transition-fast)",
          }}
          className="hover:bg-[var(--bg-elevated)]"
        >
          <div className="avatar" style={{ width: 26, height: 26, fontSize: "0.6875rem" }}>
            {initials}
          </div>
          <span
            style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", fontWeight: 500 }}
            className="hidden sm:block"
          >
            {user?.name ?? "User"}
          </span>
          <ChevronDown size={12} style={{ color: "var(--text-muted)" }} />
        </button>

        {userMenuOpen && (
          <>
            <div
              style={{ position: "fixed", inset: 0, zIndex: 99 }}
              onClick={() => setUserMenuOpen(false)}
            />
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 8px)",
                right: 0,
                width: 220,
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-strong)",
                borderRadius: "var(--radius-lg)",
                boxShadow: "var(--shadow-lg)",
                zIndex: 100,
                overflow: "hidden",
                animation: "fadeIn 0.15s ease both",
              }}
            >
              <div
                style={{
                  padding: "12px 14px",
                  borderBottom: "1px solid var(--border-default)",
                }}
              >
                <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-primary)" }}>
                  {user?.name}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 2 }}>
                  {user?.email}
                </div>
                <div style={{ marginTop: 6 }}>
                  <span
                    className="badge badge-brand"
                    style={{ textTransform: "capitalize" }}
                  >
                    {user?.role}
                  </span>
                </div>
              </div>
              <div style={{ padding: 6 }}>
                <button
                  onClick={() => {
                    clearAuth();
                    window.location.href = "/login";
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 10px",
                    width: "100%",
                    background: "none",
                    border: "none",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    color: "var(--error)",
                    fontSize: "0.8125rem",
                    transition: "all var(--transition-fast)",
                  }}
                  className="hover:bg-[var(--error-dim)]"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
