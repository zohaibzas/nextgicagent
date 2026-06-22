"use client";

import { useQuery } from "@tanstack/react-query";
import { X, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { fetchTaskDetail } from "@/lib/api";
import { cn } from "@/lib/utils";

interface WorkflowDetail {
  agent_label?: string;
  status?: string;
  duration_sec?: number;
  product?: string;
  error?: string;
  ai_request?: string;
  ai_response?: unknown;
  steps?: { step_name: string; status: string; duration_ms?: number }[];
}

interface WorkflowDrawerProps {
  taskId: number | null;
  onClose: () => void;
}

export function WorkflowDrawer({ taskId, onClose }: WorkflowDrawerProps) {
  const { data, isLoading } = useQuery<WorkflowDetail>({
    queryKey: ["workflow", taskId],
    queryFn: () => fetchTaskDetail(taskId!) as Promise<WorkflowDetail>,
    enabled: taskId != null,
  });

  if (taskId == null) return null;

  const formatDuration = (sec?: number) => {
    if (sec == null) return "—";
    return sec < 60 ? `${sec.toFixed(1)}s` : `${(sec / 60).toFixed(1)}m`;
  };

  return (
    <>
      <div
        className="fixed inset-0 z-[60] bg-black/50"
        onClick={onClose}
        aria-hidden
      />
      <aside
        className="fixed right-0 top-0 z-[70] flex h-full w-full max-w-md flex-col border-l shadow-2xl animate-slide-in"
        style={{
          background: "var(--bg-card)",
          borderColor: "var(--border-default)",
        }}
      >
        <div
          className="flex items-center justify-between border-b px-5 py-4"
          style={{ borderColor: "var(--border-default)" }}
        >
          <div>
            <div className="font-mono text-sm font-semibold" style={{ color: "var(--brand-soft)" }}>
              wf_{String(taskId).padStart(5, "0")}
            </div>
            <div className="text-xs" style={{ color: "var(--text-muted)" }}>
              Workflow trace
            </div>
          </div>
          <button type="button" className="btn btn-ghost" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" style={{ color: "var(--brand-primary)" }} />
            </div>
          ) : data ? (
            <div className="flex flex-col gap-6">
              <div className="flex flex-wrap gap-3 text-sm">
                <span style={{ color: "var(--text-secondary)" }}>
                  Agent: <strong style={{ color: "var(--text-primary)" }}>{data.agent_label}</strong>
                </span>
                <span
                  className="badge"
                  style={{
                    background: data.status === "success" ? "var(--success-dim)" : "var(--error-dim)",
                    color: data.status === "success" ? "var(--success)" : "var(--error)",
                  }}
                >
                  {data.status}
                </span>
                <span className="flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
                  <Clock size={14} />
                  {formatDuration(data.duration_sec)}
                </span>
              </div>

              {data.product && (
                <div>
                  <div className="section-title mb-2">Product</div>
                  <p className="text-sm" style={{ color: "var(--text-primary)" }}>
                    {data.product}
                  </p>
                </div>
              )}

              <div>
                <div className="section-title mb-3">Step timeline</div>
                <div className="flex flex-col gap-2">
                  {(data.steps || []).map((step: { step_name: string; status: string; duration_ms?: number }, i: number) => (
                    <div
                      key={i}
                      className={cn("workflow-step", step.status)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">{step.step_name}</span>
                        {step.status === "success" ? (
                          <CheckCircle2 size={16} className="text-green-500" />
                        ) : step.status === "failed" ? (
                          <XCircle size={16} className="text-red-500" />
                        ) : null}
                      </div>
                      {step.duration_ms != null && (
                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                          {(step.duration_ms / 1000).toFixed(1)}s
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {data.ai_request && (
                <details className="rounded-lg border p-3" style={{ borderColor: "var(--border-default)" }}>
                  <summary className="cursor-pointer text-sm font-medium">AI request</summary>
                  <pre
                    className="mt-2 max-h-32 overflow-auto text-xs"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {data.ai_request}
                  </pre>
                </details>
              )}

              {data.ai_response != null && (
                <details className="rounded-lg border p-3" style={{ borderColor: "var(--border-default)" }}>
                  <summary className="cursor-pointer text-sm font-medium">AI response</summary>
                  <pre
                    className="mt-2 max-h-48 overflow-auto text-xs"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {JSON.stringify(data.ai_response, null, 2)}
                  </pre>
                </details>
              )}

              {data.error && (
                <div
                  className="rounded-lg border p-3 text-sm"
                  style={{
                    borderColor: "rgba(239,68,68,0.3)",
                    background: "var(--error-dim)",
                    color: "var(--error)",
                  }}
                >
                  {data.error}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </aside>
    </>
  );
}
