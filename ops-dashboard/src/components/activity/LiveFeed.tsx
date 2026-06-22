"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTasks, retryTask } from "@/lib/api";
import { useFilterStore } from "@/stores/filter.store";
import { useTaskStore } from "@/stores/task.store";
import { WorkflowDrawer } from "@/components/activity/WorkflowDrawer";
import { STATUS_BADGE, AGENT_COLORS } from "@/lib/constants";
import { Activity, RefreshCcw, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import type { JobLog } from "@/types";

function StatusBadge({ status }: { status: string }) {
  const style = STATUS_BADGE[status] || STATUS_BADGE.pending;
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold uppercase"
      style={{ background: style.bg, color: style.text }}
    >
      {status}
    </span>
  );
}

export function LiveFeed() {
  const { date, agent, status, search, setSearch } = useFilterStore();
  const { tasks, setTasks } = useTaskStore();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const filters = { date, agent, status, search: search || undefined, limit: 100 };

  const { data, isLoading, isError } = useQuery({
    queryKey: ["tasks", filters],
    queryFn: () => fetchTasks(filters),
    refetchInterval: 10000,
  });

  useEffect(() => {
    if (data) setTasks(data);
  }, [data, setTasks]);

  const retryMutation = useMutation({
    mutationFn: retryTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
  });

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const formatDuration = (sec?: number) => {
    if (sec == null) return "—";
    const slow = sec > 15;
    return (
      <span style={{ color: slow ? "var(--warning)" : undefined }}>
        {sec < 60 ? `${sec.toFixed(1)}s` : `${(sec / 60).toFixed(1)}m`}
      </span>
    );
  };

  const displayTasks = tasks.length > 0 ? tasks : data || [];

  return (
    <>
      <div
        className="flex flex-col overflow-hidden rounded-xl border shadow-sm"
        style={{ background: "var(--bg-card)", borderColor: "var(--border-default)" }}
      >
        <div
          className="flex flex-col justify-between gap-4 border-b p-4 sm:flex-row sm:items-center"
          style={{ borderColor: "var(--border-default)" }}
        >
          <div className="flex items-center gap-2 font-semibold">
            <Activity size={20} style={{ color: "#818CF8" }} />
            Live Activity Feed
            <span
              className="rounded-full px-2 py-0.5 text-xs font-medium"
              style={{ background: "var(--brand-dim)", color: "var(--brand-soft)" }}
            >
              {displayTasks.length}
            </span>
          </div>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4" style={{ color: "var(--text-muted)" }} />
            <input
              type="text"
              placeholder="Search product or wf_ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Workflow ID</th>
                <th>Agent</th>
                <th>Task</th>
                <th>Product</th>
                <th>Status</th>
                <th>Duration</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 8 }).map((_, j) => (
                      <td key={j}>
                        <div className="skeleton h-4 w-16" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : isError ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center" style={{ color: "var(--error)" }}>
                    Failed to load tasks. Is the backend running on port 8000?
                  </td>
                </tr>
              ) : displayTasks.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center" style={{ color: "var(--text-muted)" }}>
                    No activity for selected filters.
                  </td>
                </tr>
              ) : (
                displayTasks.map((job: JobLog) => (
                  <tr
                    key={job.id}
                    className={cn(
                      "cursor-pointer",
                      job.status === "pending" && "border-l-2 border-l-amber-500",
                    )}
                    onClick={() => setSelectedId(job.id)}
                  >
                    <td className="font-mono text-xs">{formatTime(job.created_at)}</td>
                    <td
                      className="font-mono text-xs"
                      style={{ color: "var(--brand-soft)" }}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(`wf_${String(job.id).padStart(5, "0")}`);
                      }}
                    >
                      wf_{String(job.id).padStart(5, "0")}
                    </td>
                    <td
                      style={{
                        color: AGENT_COLORS[job.task_type] || AGENT_COLORS.unknown,
                        fontWeight: 500,
                      }}
                    >
                      {job.agent_label}
                    </td>
                    <td className="text-xs capitalize">{job.task_type?.replace("_", " ") || "—"}</td>
                    <td className="max-w-[200px] truncate" title={job.product || job.input_text}>
                      {(job.product || job.input_text || "—").slice(0, 40)}
                    </td>
                    <td>
                      <StatusBadge status={job.status} />
                    </td>
                    <td>{formatDuration(job.duration_sec)}</td>
                    <td className="text-right" onClick={(e) => e.stopPropagation()}>
                      {job.status === "failed" && (
                        <button
                          type="button"
                          className="btn btn-ghost text-xs"
                          disabled={retryMutation.isPending}
                          onClick={() => retryMutation.mutate(job.id)}
                        >
                          <RefreshCcw size={12} />
                          Retry
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <WorkflowDrawer taskId={selectedId} onClose={() => setSelectedId(null)} />
    </>
  );
}
