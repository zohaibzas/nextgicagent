"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { NotificationStack } from "@/components/layout/NotificationStack";
import { useUIStore } from "@/stores/ui.store";
import { useWebSocket } from "@/hooks/useWebSocket";

interface DashboardShellProps {
  children: React.ReactNode;
  title?: string;
}

export function DashboardShell({ children, title }: DashboardShellProps) {
  const { sidebarCollapsed } = useUIStore();
  useWebSocket();

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-base)" }}>
      <Sidebar />
      <TopNavbar title={title} />
      <CommandPalette />
      <NotificationStack />

      <main
        className={`main-content ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}
      >
        {children}
      </main>
    </div>
  );
}
