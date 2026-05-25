"""
api/models/schemas.py
Pydantic schemas for all dashboard API responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

class WorkflowStepOut(BaseModel):
    id: int
    step_name: str
    step_order: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    step_type: Optional[str]
    input_data: Optional[str]
    output_data: Optional[str]
    error_data: Optional[str]

    class Config:
        from_attributes = True

class WorkflowRunOut(BaseModel):
    id: int
    run_id: str
    agent_name: str
    task_type: Optional[str]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    error_msg: Optional[str]
    retry_count: int
    whatsapp_msg_id: Optional[str]
    user_phone: Optional[str]
    wc_product_id: Optional[int]

    class Config:
        from_attributes = True

class WorkflowRunDetail(WorkflowRunOut):
    steps: List[WorkflowStepOut] = []
    input_data: Optional[str]
    output_data: Optional[str]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AgentMetricsOut(BaseModel):
    agent_name: str
    status: str            # healthy | degraded | critical | offline
    tasks_total: int
    tasks_today: int
    success_rate: float
    avg_duration_ms: float
    retry_count: int
    failure_count: int
    ai_cost_today: float
    last_active: Optional[datetime]
    queue_depth: int


# ---------------------------------------------------------------------------
# AI Monitoring
# ---------------------------------------------------------------------------

class AIRequestOut(BaseModel):
    id: int
    workflow_run_id: Optional[int]
    model: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost_usd: Optional[float]
    latency_ms: Optional[int]
    success: bool
    request_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AIMetricsSummary(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    success_rate: float
    requests_today: int
    cost_today: float
    tokens_today: int


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ErrorEventOut(BaseModel):
    id: int
    workflow_run_id: Optional[int]
    error_type: str
    severity: str
    title: str
    message: Optional[str]
    stack_trace: Optional[str]
    agent_name: Optional[str]
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

class SystemLogOut(BaseModel):
    id: int
    level: str
    message: str
    workflow_run_id: Optional[int]
    agent_name: Optional[str]
    step_name: Optional[str]
    metadata_json: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

class QueueJobOut(BaseModel):
    id: int
    job_id: str
    queue_name: str
    task_type: str
    status: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int

    class Config:
        from_attributes = True

class QueueStats(BaseModel):
    queue_name: str
    depth: int
    active: int
    waiting: int
    failed: int
    dead_letter: int
    processed_today: int


# ---------------------------------------------------------------------------
# Metrics / Overview
# ---------------------------------------------------------------------------

class OverviewKPIs(BaseModel):
    total_tasks: int
    tasks_today: int
    success_rate: float
    failed_tasks: int
    avg_duration_ms: float
    queue_size: int
    active_agents: int
    open_errors: int
    gpt_calls_today: int
    estimated_ai_cost_today: float

class ChartDataPoint(BaseModel):
    label: str
    value: float
    secondary: Optional[float] = None

class OverviewCharts(BaseModel):
    tasks_by_day: List[ChartDataPoint]
    success_vs_failure: List[ChartDataPoint]
    ai_cost_trend: List[ChartDataPoint]
    workflow_duration: List[ChartDataPoint]
    agent_activity: Dict[str, List[ChartDataPoint]]


# ---------------------------------------------------------------------------
# WooCommerce
# ---------------------------------------------------------------------------

class WooCommerceOpOut(BaseModel):
    id: int
    workflow_run_id: Optional[int]
    operation_type: str
    product_id: Optional[int]
    product_name: Optional[str]
    status: str
    api_latency_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class WooCommerceStats(BaseModel):
    products_created: int
    stock_updates: int
    duplicates: int
    api_failures: int
    avg_latency_ms: float
    operations_today: int


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class MediaAssetOut(BaseModel):
    id: int
    workflow_run_id: Optional[int]
    filename: str
    file_type: Optional[str]
    file_size_bytes: Optional[int]
    processing_status: str
    storage_url: Optional[str]
    processing_duration_ms: Optional[int]
    is_duplicate: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

class AlertOut(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    message: Optional[str]
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int


# ---------------------------------------------------------------------------
# WebSocket Events
# ---------------------------------------------------------------------------

class WSEvent(BaseModel):
    event: str
    data: Dict[str, Any]
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)
