"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAgentStats } from "@/lib/api";
import { useFilterStore } from "@/stores/filter.store";
import { AGENT_COLORS } from "@/lib/constants";
import { Bot, AlertTriangle, CheckCircle2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export function AgentHealthGrid() {
  const date = useFilterStore((s) => s.date);
  const { data: agents, isLoading, isError } = useQuery({
    queryKey: ["agents", date],
    queryFn: () => fetchAgentStats({ date }),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-[160px] animate-pulse rounded-xl border bg-muted/50" />
        ))}
      </div>
    );
  }

  if (isError || !agents) {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center text-sm text-red-500">
        Failed to load agent health stats.
      </div>
    );
  }

  const formatDuration = (sec: number | undefined) => {
    if (sec === undefined || sec === null) return '—';
    return sec < 60 ? `${sec.toFixed(1)}s` : `${(sec / 60).toFixed(1)}m`;
  };

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {agents.map((agent) => (
        <div
          key={agent.key}
          className="flex flex-col gap-4 rounded-xl border p-5 shadow-sm"
          style={{ background: "var(--bg-card)", borderColor: "var(--border-default)" }}
        >
          
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-semibold text-foreground">
              <Bot className="h-5 w-5" style={{ color: AGENT_COLORS[agent.key] || "#818CF8" }} />
              {agent.label}
            </div>
            <div className={cn(
              "flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium border",
              agent.health === "green" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" :
              agent.health === "amber" ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" :
              "bg-red-500/10 text-red-500 border-red-500/20"
            )}>
              <div className={cn(
                "h-1.5 w-1.5 rounded-full",
                agent.health === "green" ? "bg-emerald-500" :
                agent.health === "amber" ? "bg-yellow-500" : "bg-red-500"
              )} />
              {agent.health === "green" ? "Healthy" : agent.health === "amber" ? "Degraded" : "Critical"}
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 rounded-lg bg-muted/30 p-3">
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Total Tasks</span>
              <span className="text-lg font-bold text-foreground">{agent.total}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Success Rate</span>
              <span className="flex items-center gap-1 text-lg font-bold text-emerald-500">
                {agent.success_rate}%
                <CheckCircle2 className="h-3.5 w-3.5 opacity-70" />
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Avg Duration</span>
              <span className="flex items-center gap-1 text-lg font-bold text-foreground">
                {formatDuration(agent.avg_duration)}
                <Clock className="h-3.5 w-3.5 text-muted-foreground opacity-70" />
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Failures</span>
              <span className={cn(
                "flex items-center gap-1 text-lg font-bold",
                agent.failed > 0 ? "text-red-500" : "text-foreground"
              )}>
                {agent.failed}
                {agent.failed > 0 && <AlertTriangle className="h-3.5 w-3.5 opacity-70" />}
              </span>
            </div>
          </div>

          {/* Footer */}
          <div className="text-xs text-muted-foreground">
            Last active: {agent.last_active ? new Date(agent.last_active).toLocaleString() : "Never"}
          </div>
        </div>
      ))}
    </div>
  );
}
