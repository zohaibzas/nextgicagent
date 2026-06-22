"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useUIStore } from "@/stores/ui.store";
import { useRealtimeStore } from "@/stores/realtime.store";
import { useAuthStore } from "@/stores/auth.store";
import { useQuery } from "@tanstack/react-query";
import { fetchErrors } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Activity,
  Bot,
  GitBranch,
  AlertTriangle,
  FileText,
  BarChart2,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
  LogOut,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/live", label: "Live feed", icon: Activity, realtime: true },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/workflows", label: "Workflows", icon: GitBranch },
  { href: "/errors", label: "Errors", icon: AlertTriangle, badge: "errors" },
  { href: "/logs", label: "Logs", icon: FileText },
  { href: "/analytics", label: "Analytics", icon: BarChart2 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarCollapsed, toggleSidebar, sidebarMobileOpen } = useUIStore();
  const { connected } = useRealtimeStore();
  const { user, clearAuth } = useAuthStore();

  const { data: errors } = useQuery({
    queryKey: ["errors", "badge"],
    queryFn: () => fetchErrors({ limit: 20 }),
    refetchInterval: 30000,
  });
  const openErrors = errors?.filter((e: { status?: string }) => e.status !== "resolved").length ?? 0;

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  const logout = () => {
    clearAuth();
    router.push("/login");
  };

  return (
    <>
      {sidebarMobileOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          style={{ background: "rgba(0,0,0,0.6)" }}
          onClick={() => useUIStore.getState().toggleMobileSidebar()}
        />
      )}

      <aside className={cn("sidebar", sidebarCollapsed && "collapsed", sidebarMobileOpen && "open")}>
        <div
          style={{
            padding: "0 14px",
            height: "var(--topbar-height)",
            display: "flex",
            alignItems: "center",
            gap: 10,
            borderBottom: "1px solid var(--border-default)",
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: "var(--grad-brand)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Zap size={16} color="white" />
          </div>
          {!sidebarCollapsed && (
            <div>
              <div style={{ fontSize: "0.8125rem", fontWeight: 700, color: "var(--text-primary)" }}>
                NEXTGIC
              </div>
              <div
                style={{
                  fontSize: "0.625rem",
                  color: "var(--text-muted)",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                }}
              >
                AI Operations
              </div>
            </div>
          )}
        </div>

        <nav style={{ flex: 1, overflowY: "auto", padding: "8px" }}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn("sidebar-nav-item", active && "active")}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <Icon className="nav-icon" size={16} />
                {!sidebarCollapsed && (
                  <>
                    <span style={{ flex: 1 }}>{item.label}</span>
                    {item.realtime && connected && (
                      <span className="status-dot status-dot-success status-dot-pulse" />
                    )}
                    {item.badge === "errors" && openErrors > 0 && (
                      <span
                        style={{
                          background: "var(--error)",
                          color: "white",
                          fontSize: "0.625rem",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: 9999,
                        }}
                      >
                        {openErrors}
                      </span>
                    )}
                  </>
                )}
              </Link>
            );
          })}
        </nav>

        {!sidebarCollapsed && user && (
          <div
            style={{
              borderTop: "1px solid var(--border-default)",
              padding: "12px 14px",
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="avatar">{user.email[0].toUpperCase()}</div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div
                  className="truncate text-xs font-medium"
                  style={{ color: "var(--text-primary)" }}
                >
                  {user.email}
                </div>
                <span className="badge badge-muted">{user.role}</span>
              </div>
            </div>
            <button type="button" className="sidebar-nav-item w-full" onClick={logout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        )}

        <div
          style={{ borderTop: "1px solid var(--border-default)", padding: "10px 8px" }}
          className="hidden md:block"
        >
          <button
            type="button"
            onClick={toggleSidebar}
            className="sidebar-nav-item"
            style={{ width: "100%", background: "none", border: "none" }}
          >
            {sidebarCollapsed ? <ChevronRight size={16} /> : <><ChevronLeft size={16} /> Collapse</>}
          </button>
        </div>
      </aside>
    </>
  );
}
