// src/lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ── Formatters ───────────────────────────────────────────────────────────────

export function formatDuration(ms?: number | null): string {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const mins = Math.floor(ms / 60000);
  const secs = Math.floor((ms % 60000) / 1000);
  return `${mins}m ${secs}s`;
}

export function formatCost(usd?: number | null): string {
  if (usd === undefined || usd === null) return "—";
  if (usd < 0.001) return `$${(usd * 1000).toFixed(3)}m`;
  return `$${usd.toFixed(4)}`;
}

export function formatBytes(bytes?: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)}MB`;
  return `${(bytes / 1073741824).toFixed(2)}GB`;
}

export function formatNumber(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
}

export function formatPercent(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy");
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), "MMM d, HH:mm:ss");
}

export function formatTime(date: string | Date): string {
  return format(new Date(date), "HH:mm:ss");
}

export function timeAgo(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

// ── Status helpers ────────────────────────────────────────────────────────────

export const STATUS_COLORS: Record<string, string> = {
  success:    "var(--success)",
  failed:     "var(--error)",
  running:    "var(--brand-primary)",
  retrying:   "var(--warning)",
  queued:     "var(--info)",
  cancelled:  "var(--text-muted)",
  pending:    "var(--text-muted)",
};

export const STATUS_BG: Record<string, string> = {
  success:   "badge-success",
  failed:    "badge-error",
  running:   "badge-brand",
  retrying:  "badge-warning",
  queued:    "badge-info",
  cancelled: "badge-muted",
  pending:   "badge-muted",
};

export const SEVERITY_BG: Record<string, string> = {
  critical: "badge-error",
  error:    "badge-error",
  warning:  "badge-warning",
  info:     "badge-info",
};

export const AGENT_LABELS: Record<string, string> = {
  intake_agent:      "Intake Agent",
  oos_agent:         "OOS Agent",
  duplicate_agent:   "Duplicate Agent",
  new_product_agent: "New Product Agent",
};

export const TASK_LABELS: Record<string, string> = {
  oos:         "Out of Stock",
  duplicate:   "Duplicate",
  new_product: "New Product",
  unknown:     "Unknown",
};

export function getStatusBadgeClass(status: string): string {
  return STATUS_BG[status] ?? "badge-muted";
}

export function getSeverityBadgeClass(severity: string): string {
  return SEVERITY_BG[severity] ?? "badge-muted";
}

export function getAgentLabel(name: string): string {
  return AGENT_LABELS[name] ?? name;
}

export function getTaskLabel(type: string): string {
  return TASK_LABELS[type] ?? type;
}

// ── Health status helper ─────────────────────────────────────────────────────

export function getHealthClass(health: string): string {
  const map: Record<string, string> = {
    healthy:  "health-healthy",
    degraded: "health-degraded",
    critical: "health-critical",
    offline:  "health-offline",
  };
  return map[health] ?? "health-offline";
}

// ── Random ID generator ───────────────────────────────────────────────────────

export function nanoid(len = 8): string {
  return Math.random().toString(36).substring(2, 2 + len);
}

// ── Truncate ──────────────────────────────────────────────────────────────────

export function truncate(str: string, maxLen = 60): string {
  if (!str) return "";
  return str.length > maxLen ? str.slice(0, maxLen) + "…" : str;
}

// ── Color for recharts ───────────────────────────────────────────────────────

export const CHART_COLORS = {
  primary:  "#6366f1",
  success:  "#22c55e",
  error:    "#ef4444",
  warning:  "#f59e0b",
  info:     "#3b82f6",
  muted:    "#6b7280",
  purple:   "#a855f7",
  cyan:     "#06b6d4",
  orange:   "#f97316",
  pink:     "#ec4899",
};

export const RECHARTS_TOOLTIP_STYLE = {
  backgroundColor: "#14141e",
  border: "1px solid #1e1e30",
  borderRadius: "8px",
  color: "#f1f1f5",
  fontSize: "12px",
};
