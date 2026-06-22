"use client";

import { useRealtimeStore } from "@/stores/realtime.store";

export function SystemStatus() {
  const connected = useRealtimeStore((s) => s.connected);
  return (
    <div className="glass-card p-4">
      <div className="section-title mb-3">System status</div>
      <div className="flex flex-col gap-2 text-sm">
        <div className="flex justify-between">
          <span style={{ color: "var(--text-muted)" }}>Backend API</span>
          <span style={{ color: "var(--success)" }}>Online</span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "var(--text-muted)" }}>WebSocket</span>
          <span style={{ color: connected ? "var(--success)" : "var(--error)" }}>
            {connected ? "Connected" : "Disconnected"}
          </span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "var(--text-muted)" }}>Database</span>
          <span style={{ color: "var(--success)" }}>OK</span>
        </div>
      </div>
    </div>
  );
}
