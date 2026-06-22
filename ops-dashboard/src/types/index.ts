// src/types/index.ts
// Central TypeScript type definitions for NEXTGIC AI Operations Center

export type AgentName =
  | "intake_agent"
  | "oos_agent"
  | "duplicate_agent"
  | "new_product_agent";

export type TaskType = "oos" | "duplicate" | "new_product" | "unknown";

export type WorkflowStatus =
  | "running"
  | "success"
  | "failed"
  | "retrying"
  | "queued"
  | "cancelled";

export type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";

export type ErrorSeverity = "critical" | "error" | "warning" | "info";

export type UserRole = "admin" | "operator" | "developer" | "viewer";

export type QueueStatus = "queued" | "active" | "completed" | "failed" | "retrying" | "dead_letter";

export type MediaStatus = "pending" | "processing" | "completed" | "failed";

export type AgentHealth = "healthy" | "degraded" | "critical" | "offline";

// ── User ────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  avatar_url?: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

// ── Workflow ─────────────────────────────────────────────────────────────────

export interface WorkflowStep {
  id: number;
  step_name: string;
  step_order: number;
  status: WorkflowStatus;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  step_type?: string;
  input_data?: string;
  output_data?: string;
  error_data?: string;
}

export interface JobLog {
  id: number;
  created_at: string;
  task_type: string;
  agent_label: string;
  agent_icon: string;
  product?: string;
  input_text?: string;
  status: string;
  duration_sec?: number;
  whatsapp_msg_id?: string;
  error?: string;
}

export interface WorkflowRun {
  id: number;
  run_id: string;
  agent_name: AgentName;
  task_type: TaskType;
  status: WorkflowStatus;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  error_msg?: string;
  retry_count: number;
  whatsapp_msg_id?: string;
  user_phone?: string;
  wc_product_id?: number;
}

export interface WorkflowRunDetail extends WorkflowRun {
  steps: WorkflowStep[];
  input_data?: string;
  output_data?: string;
}

// ── Agents ───────────────────────────────────────────────────────────────────

export interface AgentMetrics {
  agent_name: AgentName;
  status: AgentHealth;
  tasks_total: number;
  tasks_today: number;
  success_rate: number;
  avg_duration_ms: number;
  retry_count: number;
  failure_count: number;
  ai_cost_today: number;
  last_active?: string;
  queue_depth: number;
}

// ── AI Monitoring ─────────────────────────────────────────────────────────────

export interface AIRequest {
  id: number;
  workflow_run_id?: number;
  model: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  cost_usd?: number;
  latency_ms?: number;
  success: boolean;
  request_type?: string;
  created_at: string;
}

export interface AIMetricsSummary {
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  success_rate: number;
  requests_today: number;
  cost_today: number;
  tokens_today: number;
}

// ── Errors ───────────────────────────────────────────────────────────────────

export interface ErrorEvent {
  id: number;
  workflow_run_id?: number;
  error_type: string;
  severity: ErrorSeverity;
  title: string;
  message?: string;
  stack_trace?: string;
  agent_name?: string;
  resolved: boolean;
  created_at: string;
}

// ── Logs ─────────────────────────────────────────────────────────────────────

export interface SystemLog {
  id: number;
  level: LogLevel;
  message: string;
  workflow_run_id?: number;
  agent_name?: string;
  step_name?: string;
  metadata_json?: string;
  created_at: string;
}

// ── Queue ─────────────────────────────────────────────────────────────────────

export interface QueueJob {
  id: number;
  job_id: string;
  queue_name: string;
  task_type: string;
  status: QueueStatus;
  priority: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  retry_count: number;
}

export interface QueueStats {
  queue_name: string;
  depth: number;
  active: number;
  waiting: number;
  failed: number;
  dead_letter: number;
  processed_today: number;
}

// ── Media ─────────────────────────────────────────────────────────────────────

export interface MediaAsset {
  id: number;
  workflow_run_id?: number;
  filename: string;
  file_type?: string;
  file_size_bytes?: number;
  processing_status: MediaStatus;
  storage_url?: string;
  processing_duration_ms?: number;
  is_duplicate: boolean;
  created_at: string;
}

// ── WooCommerce ───────────────────────────────────────────────────────────────

export interface WooCommerceOp {
  id: number;
  workflow_run_id?: number;
  operation_type: string;
  product_id?: number;
  product_name?: string;
  status: string;
  api_latency_ms?: number;
  created_at: string;
}

export interface WooCommerceStats {
  products_created: number;
  stock_updates: number;
  duplicates: number;
  api_failures: number;
  avg_latency_ms: number;
  operations_today: number;
}

// ── Alerts ────────────────────────────────────────────────────────────────────

export interface Alert {
  id: number;
  alert_type: string;
  severity: ErrorSeverity;
  title: string;
  message?: string;
  acknowledged: boolean;
  created_at: string;
}

// ── Overview KPIs ─────────────────────────────────────────────────────────────

export interface OverviewKPIs {
  total_tasks: number;
  tasks_today: number;
  success_rate: number;
  failed_tasks: number;
  avg_duration_ms: number;
  queue_size: number;
  active_agents: number;
  open_errors: number;
  gpt_calls_today: number;
  estimated_ai_cost_today: number;
}

// ── Chart ─────────────────────────────────────────────────────────────────────

export interface ChartDataPoint {
  label: string;
  value: number;
  secondary?: number;
  name?: string;
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ── WebSocket ─────────────────────────────────────────────────────────────────

export type WSEventType =
  | "task.created"
  | "workflow.started"
  | "workflow.completed"
  | "workflow.failed"
  | "agent.updated"
  | "queue.changed"
  | "error.created"
  | "log.created"
  | "alert.created"
  | "metrics.updated";

export interface WSEvent<T = Record<string, unknown>> {
  event: WSEventType;
  data: T;
  timestamp: string;
}
