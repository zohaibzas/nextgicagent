"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchErrors, resolveError, retryTask } from "@/lib/api";
import { useFilterStore } from "@/stores/filter.store";
import { AlertTriangle, Check, RefreshCcw } from "lucide-react";

interface ErrorListProps {
  compact?: boolean;
  limit?: number;
}

export function ErrorList({ compact = false, limit = 50 }: ErrorListProps) {
  const date = useFilterStore((s) => s.date);
  const queryClient = useQueryClient();

  const { data: errors, isLoading, isError } = useQuery({
    queryKey: ["errors", date, limit],
    queryFn: () => fetchErrors({ limit, date }),
    refetchInterval: 15000,
  });

  const resolveMutation = useMutation({
    mutationFn: resolveError,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["errors"] }),
  });

  const retryMutation = useMutation({
    mutationFn: retryTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["errors"] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        {Array.from({ length: compact ? 3 : 5 }).map((_, i) => (
          <div key={i} className="skeleton h-[80px] rounded-lg" />
        ))}
      </div>
    );
  }

  if (isError || !errors) {
    return (
      <div className="rounded-xl border p-6 text-center text-sm" style={{ color: "var(--error)" }}>
        Failed to load errors.
      </div>
    );
  }

  if (errors.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-xl border border-dashed p-8 text-center"
        style={{ color: "var(--text-muted)" }}
      >
        <Check size={24} style={{ color: "var(--success)", marginBottom: 8 }} />
        <p className="text-sm font-medium">No active errors</p>
      </div>
    );
  }

  const list = compact ? errors.slice(0, limit) : errors;

  return (
    <div className="flex flex-col gap-3">
      {list.map((error) => (
        <div
          key={error.id}
          className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
          style={{
            borderColor: "rgba(239,68,68,0.25)",
            background: "var(--error-dim)",
          }}
        >
          <div className="flex items-start gap-3">
            <AlertTriangle size={20} style={{ color: "var(--error)", flexShrink: 0 }} />
            <div>
              <p className="text-sm font-medium break-words" style={{ color: "var(--error)" }}>
                {error.error_msg || "Unknown error"}
              </p>
              <div className="mt-1 flex flex-wrap gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
                <span style={{ color: "#818CF8" }}>{error.agent_label}</span>
                {error.created_at && <span>{new Date(error.created_at).toLocaleString()}</span>}
              </div>
            </div>
          </div>
          {!compact && (
            <div className="flex shrink-0 gap-2">
              <button
                type="button"
                className="btn btn-ghost"
                disabled={retryMutation.isPending}
                onClick={() => retryMutation.mutate(error.id)}
              >
                <RefreshCcw size={14} />
                Retry
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={resolveMutation.isPending || error.status === "resolved"}
                onClick={() => resolveMutation.mutate(error.id)}
              >
                <Check size={14} />
                Resolve
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
