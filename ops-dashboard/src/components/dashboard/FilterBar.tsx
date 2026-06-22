"use client";

import { RefreshCw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useFilterStore } from "@/stores/filter.store";
import { useRealtimeStore } from "@/stores/realtime.store";
import { AGENTS, STATUSES } from "@/lib/constants";

export function FilterBar() {
  const { date, agent, status, setDate, setAgent, setStatus } = useFilterStore();
  const connected = useRealtimeStore((s) => s.connected);
  const queryClient = useQueryClient();

  const refresh = () => {
    queryClient.invalidateQueries();
  };

  return (
    <div className="filter-bar">
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        className="search-input"
        style={{ width: "auto", paddingLeft: 12 }}
      />
      <select
        value={agent}
        onChange={(e) => setAgent(e.target.value)}
        className="search-input"
        style={{ width: "auto", paddingLeft: 12 }}
      >
        {AGENTS.map((a) => (
          <option key={a.value} value={a.value}>
            {a.label}
          </option>
        ))}
      </select>
      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="search-input"
        style={{ width: "auto", paddingLeft: 12 }}
      >
        {STATUSES.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
      <button type="button" className="btn btn-ghost" onClick={refresh}>
        <RefreshCw size={14} />
        Refresh
      </button>
      <div
        className={connected ? "realtime-indicator" : ""}
        style={
          !connected
            ? {
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "4px 10px",
                fontSize: "0.6875rem",
                fontWeight: 600,
                color: "var(--text-muted)",
              }
            : undefined
        }
      >
        <span
          className={
            connected
              ? "status-dot status-dot-success status-dot-pulse"
              : "status-dot status-dot-muted"
          }
        />
        {connected ? "LIVE" : "Offline"}
      </div>
    </div>
  );
}
