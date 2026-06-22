import type { JobLog, User } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nextgic_token");
}

function buildQuery(params?: Record<string, string | number | undefined | null>): string {
  if (!params) return "";
  const clean: Record<string, string> = {};
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "" && v !== "all" && v !== "All levels" && v !== "All agents") {
      clean[k] = String(v);
    }
  });
  return Object.keys(clean).length > 0 ? `?${new URLSearchParams(clean).toString()}` : "";
}

export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey) {
    (headers as Record<string, string>)["X-API-Key"] = apiKey;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = (err as { detail?: string | { msg: string }[] }).detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : `API Error: ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

export async function authLogin(email: string, password: string) {
  const data = await apiFetch<{ access_token: string; user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("nextgic_token", data.access_token);
  }
  return data;
}

export async function authMe() {
  return apiFetch<User>("/auth/me");
}

export interface KpiResponse {
  total: number;
  today: number;
  success_rate: number;
  failed: number;
  total_tasks: number;
  success: number;
  avg_duration: number;
  open_errors: number;
  oos_count: number;
  new_products: number;
  ai_calls: number;
  ai_avg_duration: number;
  ai_error_rate: number;
  wc_errors: number;
  images_processed: number;
  wa_messages: number;
  dedup_blocked: number;
  cache_hits: number;
}

export async function fetchKpis(params?: { date?: string }) {
  return apiFetch<KpiResponse>(`/api/kpis${buildQuery(params)}`);
}

export async function fetchTasks(params?: {
  limit?: number;
  date?: string;
  agent?: string;
  status?: string;
  search?: string;
}) {
  return apiFetch<JobLog[]>(`/api/tasks${buildQuery(params)}`);
}

export async function fetchTaskDetail(id: number) {
  return apiFetch(`/api/workflows/${id}`);
}

export interface AgentStat {
  key: string;
  label: string;
  health: string;
  total: number;
  success_rate: number;
  avg_duration: number;
  failed: number;
  last_active?: string;
}

export async function fetchAgentStats(params?: { date?: string }) {
  return apiFetch<AgentStat[]>(`/api/agents${buildQuery(params)}`);
}

export interface ErrorRecord {
  id: number;
  error_msg?: string;
  agent_label?: string;
  created_at?: string;
  whatsapp_msg_id?: string;
  status?: string;
  task_type?: string;
}

export async function fetchErrors(params?: { limit?: number; date?: string }) {
  return apiFetch<ErrorRecord[]>(`/api/errors${buildQuery(params)}`);
}

export interface LogEntry {
  level: string;
  time: string;
  full_time?: string;
  agent: string;
  module?: string;
  msg: string;
}

export async function fetchLogs(params?: {
  level?: string;
  agent?: string;
  search?: string;
  limit?: number;
}) {
  return apiFetch<LogEntry[]>(`/api/logs${buildQuery(params)}`);
}

export interface AnalyticsResponse {
  task_volume: { date: string; count: number }[];
  success_vs_failed: { date: string; success: number; failed: number }[];
  tasks_by_agent: { agent: string; count: number }[];
  avg_duration_trend: { date: string; avg_sec: number }[];
  error_rate_trend: { date: string; rate: number }[];
  tasks_by_hour: { hour: number; avg_count: number }[];
  task_type_split: { type: string; count: number }[];
}

export async function fetchAnalytics() {
  return apiFetch<AnalyticsResponse>("/api/analytics");
}

export interface DashboardCharts {
  tasks_by_agent: { label: string; count: number }[];
  hourly_success: { hour: string; rate: number; total: number }[];
}

export async function fetchDashboardCharts(params?: { date?: string }) {
  return apiFetch<DashboardCharts>(`/dashboard/charts${buildQuery(params)}`);
}

export async function retryTask(taskId: number) {
  return apiFetch(`/api/tasks/${taskId}/retry`, { method: "POST" });
}

export async function resolveError(errorId: number) {
  return apiFetch(`/api/errors/${errorId}/resolve`, { method: "PATCH" });
}

// Legacy aliases
export const fetchDashboardKPIs = fetchKpis;
export const fetchJobs = fetchTasks;
