# NEXTGIC AI OPS CENTER — Master Build Prompt

> **Purpose:** Transform the attached `nextgic_dashboard.html` into a production-grade,
> realtime, fullstack SaaS monitoring platform for AI agent pipelines.
> Use this prompt with an AI coding agent (Cursor, Claude Code, Windsurf, etc.)
> or a senior full-stack engineer as the complete specification.

---

## 0 · CONTEXT — WHAT EXISTS TODAY

The uploaded `nextgic_dashboard.html` is a single-file vanilla HTML dashboard that
already contains the following working sections:

| Section | Current implementation |
|---|---|
| KPI Grid | 8 metric cards (total tasks, success %, failed, dedup, cache hits, WA messages, avg duration) |
| Live Activity Feed | `<table>` fed by `genJobs(50)` mock data generator |
| Agent Health | 4 agents: Intake · OOS · Duplicate · New product — health dot + stats |
| DB Inspector | SQLite overview, dedup log, product cache TTL table |
| Workflow Map | SVG-like flow diagram: WhatsApp → Intake → branch(OOS/Duplicate/New product) → WooCommerce → DB |
| Structured Logs | Filterable log lines: INFO / WARNING / ERROR with agent correlation |
| Error Center | Failed-job cards with retry + resolve buttons |
| Charts | Chart.js bar (tasks by agent) + line (success rate over time) |
| Filters | Date picker, agent selector, status selector, refresh button |

**Design DNA to preserve:**
- Background `#0f1117` (near-black)
- Panel color `#1a1f2e`
- Border color `#1e2535`
- Accent green `#22c55e` · red `#ef4444` · amber `#f59e0b` · indigo `#818cf8` · sky `#38bdf8`
- Monospace font for IDs, timestamps, log messages
- Badge system: success / failed / running / skipped / info / warn
- Health dots: green ≥80% · amber ≥60% · red <60%

---

## 1 · PROJECT IDENTITY

```
App name:     NEXTGIC AI OPS CENTER
Tagline:      Real-time intelligence for AI-agent operations
Domain model: AI agents process WhatsApp messages → classify task →
              route to specialized agents (OOS / Duplicate / New product) →
              call WooCommerce REST API → log results to PostgreSQL
```

---

## 2 · MANDATORY TECH STACK

### Frontend
| Layer | Library / Version |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript 5.x — strict mode |
| Styling | TailwindCSS 3.x + `tailwind-animate` plugin |
| UI primitives | shadcn/ui (Radix-based) |
| State | Zustand 4.x |
| Server state | TanStack Query v5 |
| Tables | TanStack Table v8 |
| Charts | Recharts 2.x |
| Animation | Framer Motion 11.x |
| Realtime | Socket.IO Client 4.x |
| Icons | Lucide React |
| Forms | React Hook Form + Zod |
| Date handling | date-fns |

### Backend
| Layer | Library |
|---|---|
| Framework | FastAPI 0.111+ |
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.x (async) |
| DB | PostgreSQL 16 |
| Cache / Pub-Sub | Redis 7 (via `redis-py` async) |
| WebSocket | `python-socketio` (ASGI) |
| Auth | `python-jose` JWT + `passlib` bcrypt |
| Migrations | Alembic |
| Task queue | ARQ (async Redis Queue) |
| HTTP client | `httpx` |

### Infrastructure
| Concern | Tool |
|---|---|
| Containerisation | Docker + Docker Compose |
| Frontend hosting | Vercel (zero-config Next.js) |
| Backend hosting | Railway · Render · Fly.io (all supported) |
| PostgreSQL cloud | Supabase or Neon |
| Redis cloud | Upstash |
| Secrets | `.env.local` (frontend) · `.env` (backend) |

---

## 3 · MONOREPO STRUCTURE

```
nextgic-ops/
├── apps/
│   ├── web/                          # Next.js 15 frontend
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── (auth)/
│   │   │   │   │   └── login/
│   │   │   │   │       └── page.tsx
│   │   │   │   ├── (dashboard)/
│   │   │   │   │   ├── layout.tsx    # sidebar + topnav shell
│   │   │   │   │   ├── page.tsx      # redirect → /overview
│   │   │   │   │   ├── overview/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── activity/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── agents/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── workflows/
│   │   │   │   │   │   ├── page.tsx
│   │   │   │   │   │   └── [id]/
│   │   │   │   │   │       └── page.tsx
│   │   │   │   │   ├── errors/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── logs/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── queue/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── ai-monitor/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── analytics/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   └── settings/
│   │   │   │   │       └── page.tsx
│   │   │   │   ├── api/
│   │   │   │   │   └── health/
│   │   │   │   │       └── route.ts
│   │   │   │   └── layout.tsx        # root layout + providers
│   │   │   │
│   │   │   ├── components/
│   │   │   │   ├── layout/
│   │   │   │   │   ├── Sidebar.tsx
│   │   │   │   │   ├── TopNav.tsx
│   │   │   │   │   ├── CommandPalette.tsx
│   │   │   │   │   └── MobileNav.tsx
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── KPIGrid.tsx
│   │   │   │   │   ├── KPICard.tsx
│   │   │   │   │   └── WidgetGrid.tsx
│   │   │   │   ├── activity/
│   │   │   │   │   ├── LiveFeed.tsx
│   │   │   │   │   ├── FeedRow.tsx
│   │   │   │   │   └── WorkflowDrawer.tsx
│   │   │   │   ├── agents/
│   │   │   │   │   ├── AgentHealth.tsx
│   │   │   │   │   ├── AgentCard.tsx
│   │   │   │   │   └── AgentDetailPanel.tsx
│   │   │   │   ├── workflows/
│   │   │   │   │   ├── WorkflowMap.tsx
│   │   │   │   │   ├── WorkflowTimeline.tsx
│   │   │   │   │   ├── StepDetail.tsx
│   │   │   │   │   └── ReplayControls.tsx
│   │   │   │   ├── errors/
│   │   │   │   │   ├── ErrorCenter.tsx
│   │   │   │   │   ├── ErrorCard.tsx
│   │   │   │   │   └── ErrorHeatmap.tsx
│   │   │   │   ├── logs/
│   │   │   │   │   ├── LogViewer.tsx
│   │   │   │   │   ├── LogLine.tsx
│   │   │   │   │   └── LogFilters.tsx
│   │   │   │   ├── charts/
│   │   │   │   │   ├── TasksByAgent.tsx
│   │   │   │   │   ├── SuccessRateLine.tsx
│   │   │   │   │   ├── AICostArea.tsx
│   │   │   │   │   ├── WorkflowVolume.tsx
│   │   │   │   │   └── AgentPerformanceRadar.tsx
│   │   │   │   ├── queue/
│   │   │   │   │   ├── QueueMonitor.tsx
│   │   │   │   │   └── WorkerStatus.tsx
│   │   │   │   ├── ai/
│   │   │   │   │   ├── AIMonitor.tsx
│   │   │   │   │   └── TokenUsageGauge.tsx
│   │   │   │   └── ui/               # shadcn/ui auto-generated
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   ├── useSocket.ts
│   │   │   │   ├── useRealtimeFeed.ts
│   │   │   │   ├── useKPIs.ts
│   │   │   │   ├── useAgents.ts
│   │   │   │   ├── useWorkflow.ts
│   │   │   │   ├── useLogs.ts
│   │   │   │   ├── useErrors.ts
│   │   │   │   └── useAuth.ts
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── api.ts            # Axios instance + interceptors
│   │   │   │   ├── socket.ts         # Socket.IO singleton
│   │   │   │   └── auth.ts
│   │   │   │
│   │   │   ├── stores/
│   │   │   │   ├── useAppStore.ts    # global UI state
│   │   │   │   ├── useSocketStore.ts # connection status + event buffer
│   │   │   │   └── useAuthStore.ts
│   │   │   │
│   │   │   ├── lib/
│   │   │   │   ├── utils.ts
│   │   │   │   ├── formatters.ts
│   │   │   │   └── constants.ts
│   │   │   │
│   │   │   ├── types/
│   │   │   │   ├── api.ts
│   │   │   │   ├── events.ts
│   │   │   │   └── domain.ts
│   │   │   │
│   │   │   └── styles/
│   │   │       └── globals.css
│   │   │
│   │   ├── public/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   └── api/                          # FastAPI backend
│       ├── app/
│       │   ├── main.py               # FastAPI app + ASGI + Socket.IO mount
│       │   ├── config.py             # Settings (pydantic-settings)
│       │   ├── database.py           # async SQLAlchemy engine + session
│       │   ├── redis_client.py
│       │   │
│       │   ├── models/               # SQLAlchemy ORM models
│       │   │   ├── workflow.py
│       │   │   ├── agent.py
│       │   │   ├── log.py
│       │   │   ├── error.py
│       │   │   ├── queue_job.py
│       │   │   ├── ai_request.py
│       │   │   └── user.py
│       │   │
│       │   ├── schemas/              # Pydantic v2 schemas
│       │   │   ├── workflow.py
│       │   │   ├── agent.py
│       │   │   ├── log.py
│       │   │   ├── error.py
│       │   │   └── auth.py
│       │   │
│       │   ├── routers/
│       │   │   ├── auth.py
│       │   │   ├── dashboard.py
│       │   │   ├── workflows.py
│       │   │   ├── agents.py
│       │   │   ├── logs.py
│       │   │   ├── errors.py
│       │   │   ├── queue.py
│       │   │   └── ai.py
│       │   │
│       │   ├── services/
│       │   │   ├── workflow_service.py
│       │   │   ├── agent_service.py
│       │   │   ├── log_service.py
│       │   │   ├── error_service.py
│       │   │   └── ai_service.py
│       │   │
│       │   ├── socket/
│       │   │   ├── manager.py        # Socket.IO server + room management
│       │   │   └── events.py         # emit helpers + event schemas
│       │   │
│       │   ├── workers/
│       │   │   └── simulator.py      # seed + fake-event generator (dev only)
│       │   │
│       │   └── migrations/           # Alembic
│       │       ├── env.py
│       │       └── versions/
│       │
│       ├── Dockerfile
│       ├── requirements.txt
│       └── .env.example
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

---

## 4 · DATABASE SCHEMA (PostgreSQL 16)

Implement all tables with `SQLAlchemy` async ORM. Use JSONB for flexible payloads.

```sql
-- Users & Auth
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT UNIQUE NOT NULL,
  name        TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role        TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin','operator','viewer')),
  created_at  TIMESTAMPTZ DEFAULT now(),
  last_login  TIMESTAMPTZ
);

-- Workflow runs (top-level unit)
CREATE TABLE workflow_runs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wa_msg_id       TEXT UNIQUE NOT NULL,          -- WhatsApp message ID
  agent           TEXT NOT NULL,                  -- intake | oos | duplicate | new_product
  task            TEXT NOT NULL,                  -- classified task name
  status          TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running','success','failed','skipped')),
  product_name    TEXT,
  sku             TEXT,
  error_msg       TEXT,
  duration_ms     INTEGER,
  retry_count     INTEGER DEFAULT 0,
  metadata        JSONB DEFAULT '{}',
  started_at      TIMESTAMPTZ DEFAULT now(),
  completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_workflow_runs_agent    ON workflow_runs(agent);
CREATE INDEX idx_workflow_runs_status   ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_started  ON workflow_runs(started_at DESC);
CREATE INDEX idx_workflow_runs_wa       ON workflow_runs(wa_msg_id);

-- Individual steps within a workflow
CREATE TABLE workflow_steps (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
  step_name       TEXT NOT NULL,                  -- e.g. "vision.classify_task"
  step_type       TEXT NOT NULL,                  -- gpt | woocommerce | image | internal
  status          TEXT NOT NULL,
  input_payload   JSONB,
  output_payload  JSONB,
  error_msg       TEXT,
  duration_ms     INTEGER,
  gpt_tokens      INTEGER,
  gpt_cost_usd    NUMERIC(10,6),
  executed_at     TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_steps_run ON workflow_steps(workflow_run_id);

-- Structured log entries
CREATE TABLE task_logs (
  id              BIGSERIAL PRIMARY KEY,
  workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE SET NULL,
  level           TEXT NOT NULL CHECK (level IN ('DEBUG','INFO','WARNING','ERROR')),
  agent           TEXT NOT NULL,
  message         TEXT NOT NULL,
  extra           JSONB DEFAULT '{}',
  logged_at       TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_logs_run      ON task_logs(workflow_run_id);
CREATE INDEX idx_logs_level    ON task_logs(level);
CREATE INDEX idx_logs_agent    ON task_logs(agent);
CREATE INDEX idx_logs_logged   ON task_logs(logged_at DESC);

-- Error events (denormalized for fast error center queries)
CREATE TABLE error_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
  agent           TEXT NOT NULL,
  error_type      TEXT,
  error_msg       TEXT NOT NULL,
  stack_trace     TEXT,
  severity        TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning','error','critical')),
  resolved        BOOLEAN DEFAULT false,
  resolved_by     UUID REFERENCES users(id),
  resolved_at     TIMESTAMPTZ,
  occurred_at     TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_errors_agent    ON error_events(agent);
CREATE INDEX idx_errors_resolved ON error_events(resolved);
CREATE INDEX idx_errors_occurred ON error_events(occurred_at DESC);

-- AI / GPT request log
CREATE TABLE ai_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE SET NULL,
  step_id         UUID REFERENCES workflow_steps(id) ON DELETE SET NULL,
  model           TEXT NOT NULL DEFAULT 'gpt-4o',
  prompt_tokens   INTEGER,
  completion_tokens INTEGER,
  total_tokens    INTEGER,
  cost_usd        NUMERIC(10,6),
  latency_ms      INTEGER,
  is_valid_json   BOOLEAN,
  retried         BOOLEAN DEFAULT false,
  requested_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_ai_requests_run ON ai_requests(workflow_run_id);
CREATE INDEX idx_ai_requests_ts  ON ai_requests(requested_at DESC);

-- Queue jobs (ARQ / Redis-backed, mirrored to PG for history)
CREATE TABLE queue_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_type        TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','active','success','failed','dead')),
  payload         JSONB DEFAULT '{}',
  result          JSONB,
  error_msg       TEXT,
  retry_count     INTEGER DEFAULT 0,
  max_retries     INTEGER DEFAULT 3,
  worker_id       TEXT,
  enqueued_at     TIMESTAMPTZ DEFAULT now(),
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_queue_status ON queue_jobs(status);

-- Retry events
CREATE TABLE retry_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
  step_id         UUID REFERENCES workflow_steps(id),
  attempt         INTEGER NOT NULL,
  error_msg       TEXT,
  retried_at      TIMESTAMPTZ DEFAULT now()
);

-- Alerts
CREATE TABLE alerts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title           TEXT NOT NULL,
  body            TEXT,
  severity        TEXT NOT NULL CHECK (severity IN ('info','warning','error','critical')),
  source          TEXT,
  acknowledged    BOOLEAN DEFAULT false,
  acknowledged_by UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT now()
);
```

---

## 5 · BACKEND — FASTAPI

### 5.1 Application entry point (`app/main.py`)

```python
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, dashboard, workflows, agents, logs, errors, queue, ai
from app.socket.manager import sio

app = FastAPI(title="NEXTGIC AI OPS CENTER", version="1.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in [auth, dashboard, workflows, agents, logs, errors, queue, ai]:
    app.include_router(router.router, prefix="/api/v1")

# Mount Socket.IO as ASGI sub-app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
```

### 5.2 Socket.IO event schema

Emit these events to all connected dashboard clients:

```typescript
// TypeScript types (copy to apps/web/src/types/events.ts)
export type SocketEvent =
  | { event: "workflow.started";   data: WorkflowRun }
  | { event: "workflow.completed"; data: WorkflowRun }
  | { event: "workflow.failed";    data: WorkflowRun }
  | { event: "workflow.step";      data: WorkflowStep }
  | { event: "log.created";        data: LogEntry }
  | { event: "error.created";      data: ErrorEvent }
  | { event: "agent.updated";      data: AgentStats }
  | { event: "queue.updated";      data: QueueSnapshot }
  | { event: "kpi.tick";           data: KPISnapshot }   // every 5s
```

### 5.3 REST API routes (all return paginated JSON)

```
GET  /api/v1/dashboard/kpis          → KPISnapshot
GET  /api/v1/dashboard/overview      → aggregated overview

GET  /api/v1/workflows               → paginated list (filters: agent, status, date_from, date_to)
GET  /api/v1/workflows/{id}          → full workflow detail with steps
POST /api/v1/workflows/{id}/retry    → re-queue workflow
GET  /api/v1/workflows/{id}/replay   → replay-safe read-only trace

GET  /api/v1/agents                  → all agent stats
GET  /api/v1/agents/{name}           → single agent detail

GET  /api/v1/logs                    → paginated (filters: level, agent, query, workflow_id)
GET  /api/v1/logs/stream             → SSE stream (alternative to Socket.IO for logs)

GET  /api/v1/errors                  → paginated error events
POST /api/v1/errors/{id}/resolve     → mark resolved
POST /api/v1/errors/{id}/retry       → retry parent workflow

GET  /api/v1/queue                   → queue snapshot
GET  /api/v1/queue/jobs              → paginated job list
POST /api/v1/queue/jobs/{id}/retry   → retry dead-letter job

GET  /api/v1/ai/stats                → token usage, cost, latency, accuracy
GET  /api/v1/ai/requests             → paginated AI request log

POST /api/v1/auth/login              → { access_token, token_type }
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

### 5.4 Dev simulator (`workers/simulator.py`)

When `APP_ENV=development`, run a background task that:
1. Every 3–8 seconds: generates a new `WorkflowRun` (random agent / status / duration)
2. Emits `workflow.started` → waits → emits `workflow.completed` or `workflow.failed`
3. Appends 2–5 `task_logs` entries per workflow
4. 15% chance of creating an `error_event`
5. Updates `KPISnapshot` and emits `kpi.tick` every 5 seconds
6. Simulates queue drain/fill cycles

---

## 6 · FRONTEND — NEXT.JS 15

### 6.1 Tailwind color palette (tailwind.config.ts)

Extend the default palette to match the HTML dashboard's exact colors:

```typescript
colors: {
  ops: {
    bg:       '#0f1117',
    surface:  '#1a1f2e',
    border:   '#1e2535',
    border2:  '#2d3748',
    muted:    '#475569',
    subtle:   '#64748b',
    text:     '#94a3b8',
    heading:  '#e2e8f0',
    white:    '#f1f5f9',
    green:    '#22c55e',
    'green-dim': '#052e16',
    red:      '#ef4444',
    'red-dim':   '#2d0a0a',
    amber:    '#f59e0b',
    'amber-dim': '#1c1a05',
    indigo:   '#818cf8',
    sky:      '#38bdf8',
    purple:   '#7c3aed',
    magenta:  '#e879f9',
  }
}
```

### 6.2 Sidebar navigation (Sidebar.tsx)

Render a collapsible dark sidebar with these nav items. Group them visually:

**Monitoring**
- Overview (`/overview`) — LayoutDashboard icon
- Live Activity (`/activity`) — Activity icon + live green dot
- Agents (`/agents`) — Bot icon

**Operations**
- Workflows (`/workflows`) — GitBranch icon
- Queue Monitor (`/queue`) — ListOrdered icon
- AI Monitor (`/ai-monitor`) — Brain icon

**Integrations**
- WooCommerce (`/woocommerce`) — ShoppingCart icon
- WhatsApp (`/whatsapp`) — MessageCircle icon

**Debugging**
- Errors (`/errors`) — AlertTriangle icon + red badge with open error count
- Logs (`/logs`) — Terminal icon

**Insights**
- Analytics (`/analytics`) — BarChart3 icon

**System**
- Alerts (`/alerts`) — Bell icon
- Settings (`/settings`) — Settings icon

**Sidebar states:**
- Desktop: 240px wide, always visible
- Tablet (md): icon-only collapsed mode (56px)
- Mobile: hidden; replaced by bottom nav bar

### 6.3 Top navigation (TopNav.tsx)

Left: hamburger (mobile only) | breadcrumb
Center: global search bar (opens CommandPalette on click)
Right:
- WebSocket status indicator (green pulsing dot = connected, amber = reconnecting, red = disconnected) + text "Live" / "Reconnecting" / "Offline"
- Notification bell with badge
- Light/dark mode toggle
- User avatar dropdown (name, role, logout)

**CommandPalette.tsx:**
Open with `⌘K` / `Ctrl+K`. Show:
- Recent pages
- Quick nav to all routes
- Search workflows by ID
- Search logs

### 6.4 Page: Overview (`/overview`)

**KPI Grid (2×5 on desktop, 2×3 on tablet, 1×10 on mobile):**

| KPI | Icon | Color variant |
|---|---|---|
| Total Tasks | ListCheck | neutral |
| Success Rate | CircleCheck | green |
| Failed Tasks | CircleX | red |
| Open Errors | AlertTriangle | amber |
| Avg Duration | Clock | neutral |
| WA Messages | MessageCircle | neutral |
| Dedup Blocked | Ban | neutral |
| GPT Calls | Brain | indigo |
| AI Cost Today | DollarSign | neutral |
| Queue Size | ListOrdered | neutral |

Each `KPICard` must:
- Show a sparkline (7-point mini Recharts LineChart) in the card background
- Animate the number counting up on first load (Framer Motion)
- Show trend arrow (↑↓) with % delta vs previous period
- Pulse green border briefly when updated via WebSocket

**Charts section (2-column grid):**
- `TasksByAgent`: Recharts BarChart — same 4 agents as HTML, styled with ops palette
- `SuccessRateLine`: Recharts AreaChart — hourly success %, area fill ops-green/10
- `WorkflowVolume`: Recharts BarChart stacked — success / failed / skipped
- `AICostArea`: Recharts AreaChart — cumulative USD cost

**Widgets section (3-column grid):**
- Active Workflows widget — list of in-flight `workflow.started` events, auto-removes on complete
- Recent Errors widget — last 5 errors, link to `/errors`
- Queue Health widget — active / waiting / dead counts with progress bars
- Agent Status widget — 4 agents with health dots + last-seen timestamp

### 6.5 Page: Live Activity (`/activity`)

Full-page TanStack Table with these columns:

| Column | Notes |
|---|---|
| Timestamp | Relative ("2s ago") with absolute on hover |
| Workflow ID | Monospace, click → opens WorkflowDrawer |
| WA Msg ID | Monospace, truncated |
| Agent | Colored badge matching agent |
| Task | Text |
| Status | Badge (success/failed/skipped/running) |
| Duration | Right-aligned, "12.4s" |
| Retry | Count badge, red if >0 |
| AI Cost | "$0.0042", right-aligned |

Features:
- New rows slide in from top when `workflow.completed` or `workflow.failed` received
- Row highlights amber for 1.5s on arrival
- Search bar (debounced 300ms)
- Multi-select filter chips: Agent · Status
- Date range picker
- Export CSV button
- Pagination (25/50/100 per page)
- Click row → opens `WorkflowDrawer` (right-side sheet)

**WorkflowDrawer:**
Full details of a single workflow run including:
- Header: workflow ID, agent, status badge, duration, WA msg ID
- Timeline: step-by-step execution (WorkflowTimeline component)
- Logs tab: filtered logs for this workflow
- Raw JSON tab: full `workflow_run` + `workflow_steps` as formatted JSON
- Actions: "Retry Workflow" button (operator/admin only)

### 6.6 Page: Agents (`/agents`)

**Agent cards (grid 2×2):** One card per agent: Intake · OOS · Duplicate · New product

Each card shows:
- Agent name + icon + health status pill (Healthy / Degraded / Critical)
- Sparkline of tasks/minute (last 30 min)
- Metrics: Total tasks | Success % | Avg duration | Retry rate | Failures | AI cost
- Last activity timestamp
- "View details" → `/agents/{name}` (single agent drill-down)

Agent detail page (`/agents/[name]`):
- Full Recharts charts for that agent
- Recent errors from this agent
- Recent logs from this agent
- Performance over time

### 6.7 Page: Workflow Explorer (`/workflows` + `/workflows/[id]`)

List view: Table similar to Activity but scoped to workflow-level summary.

Detail view (`/workflows/[id]`) — the flagship feature:
- **Execution Timeline** (horizontal step diagram, inspired by LangSmith / Airflow):
  - Each step rendered as a node: step name + type icon + duration + status
  - Connecting arrows with duration labels
  - Failed steps rendered in red with error tooltip
  - Retry attempts shown as branching nodes
- **Step Detail panel** (click any step):
  - Input / Output JSON (syntax-highlighted, collapsible)
  - GPT prompt & response (if step_type = "gpt")
  - WooCommerce action + response code (if step_type = "woocommerce")
  - Image thumbnail (if step_type = "image")
  - Error + stack trace (if failed)
- **Replay controls:**
  - "Replay" button: renders a step-by-step animation of the workflow execution
  - "Retry failed step" button (operator/admin only)
  - "View raw JSON" toggle

### 6.8 Page: Error Center (`/errors`)

Layout: left panel (error list) + right panel (error detail).

**Error list:**
- Grouped by `error_type` (like Sentry)
- Each group shows: error count, affected agents, last seen, severity badge
- Expand group → individual error cards
- Filter: severity · agent · resolved/open · date range
- Bulk actions: resolve all, retry all

**Error card:**
- Red-dimmed background (`ops-red-dim`)
- Error message + agent + workflow ID + timestamp
- "Retry" button → POST `/api/v1/errors/{id}/retry`
- "Resolve" button → POST `/api/v1/errors/{id}/resolve` → fades out card

**Error Heatmap widget:**
- 7×24 grid (7 days × 24 hours)
- Cell color intensity = error count in that hour
- Click cell → filters error list to that time window

### 6.9 Page: Log Viewer (`/logs`)

- Real-time streaming: new logs prepend to top of list
- Log line component matches HTML design exactly:
  - `[INFO]` / `[WARNING]` / `[ERROR]` colored badge
  - Agent name (purple)
  - Timestamp + message (monospace)
- Filter bar: Level · Agent · Workflow ID · Free text search (debounced)
- Auto-scroll toggle (scroll lock releases on manual scroll, re-locks on click)
- Virtualized list (TanStack Virtual) for performance with 10k+ lines
- JSON detection: if message contains `{…}`, render expandable JSON block
- "Pause stream" toggle

### 6.10 Page: AI Monitor (`/ai-monitor`)

- Token usage chart (area, grouped by model)
- Cost over time (area)
- Latency distribution (histogram)
- Malformed JSON rate (gauge 0-100%)
- Extraction accuracy (gauge)
- GPT retry rate
- Table: recent AI requests with prompt/response preview

### 6.11 Page: Queue Monitor (`/queue`)

- Stats row: Active · Waiting · Completed · Failed · Dead-letter
- Real-time worker status cards (one per worker)
- Job table: TanStack Table with status, job_type, retry count, enqueued_at, worker_id
- Dead-letter queue section: failed jobs with "Retry" button

### 6.12 Mobile design

**Bottom navigation (mobile only, < 768px):**
Icons for: Overview · Activity · Agents · Errors · More (opens drawer with full nav)

**Responsive overrides:**
- KPI Grid: `grid-cols-2` on mobile
- All tables → card-based layout on mobile (one row = one card)
- Sidebar: hidden on mobile
- Charts: single-column, reduced height (180px)
- WorkflowDrawer: full-screen bottom sheet on mobile

---

## 7 · REALTIME ARCHITECTURE

### 7.1 useSocket hook

```typescript
// hooks/useSocket.ts
import { useEffect } from 'react'
import { io } from 'socket.io-client'
import { useSocketStore } from '@/stores/useSocketStore'

const SOCKET_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

let socket: ReturnType<typeof io> | null = null

export function useSocket() {
  const { setStatus, setConnected } = useSocketStore()

  useEffect(() => {
    if (socket?.connected) return

    socket = io(SOCKET_URL, {
      auth: { token: localStorage.getItem('access_token') },
      transports: ['websocket'],
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    })

    socket.on('connect',    () => setConnected(true))
    socket.on('disconnect', () => setConnected(false))
    socket.on('reconnecting', () => setStatus('reconnecting'))

    return () => { socket?.disconnect() }
  }, [])

  return socket
}
```

### 7.2 Event handling in stores

```typescript
// stores/useSocketStore.ts  (Zustand)
interface SocketStore {
  connected: boolean
  status: 'connected' | 'reconnecting' | 'offline'
  recentWorkflows: WorkflowRun[]
  kpiSnapshot: KPISnapshot | null

  setConnected: (v: boolean) => void
  setStatus:    (s: SocketStore['status']) => void
  pushWorkflow: (w: WorkflowRun) => void
  setKPI:       (k: KPISnapshot) => void
}
```

Mount all global socket listeners in the dashboard layout (`layout.tsx`):
```typescript
useSocket()
socket.on('workflow.completed', (data) => {
  useSocketStore.getState().pushWorkflow(data)
  queryClient.invalidateQueries({ queryKey: ['kpis'] })
})
socket.on('kpi.tick',           (data) => useSocketStore.getState().setKPI(data))
socket.on('error.created',      (data) => queryClient.invalidateQueries({ queryKey: ['errors'] }))
socket.on('log.created',        (data) => useLogStore.getState().prependLog(data))
```

---

## 8 · AUTHENTICATION

### 8.1 JWT flow
- POST `/api/v1/auth/login` → `{ access_token: string, token_type: 'bearer' }`
- Store in `localStorage` (or httpOnly cookie for production)
- Attach via `Authorization: Bearer <token>` header (Axios interceptor)
- On 401 → redirect to `/login`
- Refresh token endpoint: POST `/api/v1/auth/refresh`

### 8.2 Protected routes
Wrap all `(dashboard)` routes in an `AuthGuard` server component that checks the JWT.

### 8.3 RBAC
| Action | Admin | Operator | Viewer |
|---|---|---|---|
| View all pages | ✓ | ✓ | ✓ |
| Retry workflow | ✓ | ✓ | ✗ |
| Resolve error | ✓ | ✓ | ✗ |
| Manage settings | ✓ | ✗ | ✗ |

### 8.4 Default seed credentials (dev only)
```
admin@nextgic.com   / admin123   → role: admin
operator@nextgic.com / ops123    → role: operator
viewer@nextgic.com  / view123   → role: viewer
```

---

## 9 · DOCKER SETUP

### docker-compose.yml

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: nextgic_ops
      POSTGRES_USER: nextgic
      POSTGRES_PASSWORD: nextgic_secret
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nextgic"]
      interval: 5s; timeout: 5s; retries: 5

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  api:
    build: ./apps/api
    env_file: ./apps/api/.env
    environment:
      DATABASE_URL: postgresql+asyncpg://nextgic:nextgic_secret@postgres:5432/nextgic_ops
      REDIS_URL: redis://redis:6379
      APP_ENV: development
    ports: ["8000:8000"]
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }
    command: >
      sh -c "alembic upgrade head &&
             python -m app.workers.seed &&
             uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload"

  web:
    build: ./apps/web
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports: ["3000:3000"]
    depends_on: [api]

volumes:
  postgres_data:
```

### Local dev commands
```bash
# Start everything
docker compose up

# Frontend only (hot reload)
cd apps/web && npm run dev

# Backend only (hot reload)
cd apps/api && uvicorn app.main:socket_app --reload

# Seed database
docker compose exec api python -m app.workers.seed

# Run migrations
docker compose exec api alembic upgrade head

# Reset DB
docker compose exec api alembic downgrade base && alembic upgrade head
```

---

## 10 · DEPLOYMENT

### Frontend → Vercel
```bash
# vercel.json in apps/web
{
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@nextgic_api_url"
  }
}
```
Push `apps/web` to Vercel. Set `NEXT_PUBLIC_API_URL` environment variable to backend URL.

### Backend → Railway / Render / Fly.io
Set these environment variables:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=rediss://user:pass@host:6380          # Upstash TLS URL
SECRET_KEY=<256-bit random>
APP_ENV=production
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

**Railway:** Push `apps/api` → auto-detects Dockerfile → runs.
**Render:** Web Service → Docker → set env vars → auto-deploy.
**Fly.io:** `fly launch` from `apps/api/` → `fly secrets set DATABASE_URL=...`

### Database → Neon / Supabase
Create a project → copy the connection string → set `DATABASE_URL`.
Run `alembic upgrade head` once after first deploy.

### Redis → Upstash
Create a Redis database → copy TLS URL → set `REDIS_URL`.

---

## 11 · PERFORMANCE REQUIREMENTS

| Concern | Implementation |
|---|---|
| Large tables | TanStack Virtual (windowed rendering) |
| Charts | Recharts with `isAnimationActive={false}` after initial render |
| Heavy pages | `React.lazy` + `Suspense` + skeleton loaders |
| Socket delta updates | Only mutate changed rows, not full refetch |
| Image thumbnails | Next.js `<Image>` with blur placeholder |
| API responses | Redis cache (60s TTL) for KPI endpoints |
| Memoization | `useMemo` / `useCallback` for expensive derived data |
| Log virtualization | `@tanstack/react-virtual` for log viewer |

---

## 12 · LOADING & EMPTY STATES

Every page and widget must implement:

1. **Skeleton loaders** — match the exact shape of the loaded content (not generic grey blocks)
2. **Empty states** — illustrated, with CTA (e.g. "No errors — system is healthy 🎉")
3. **Error states** — "Failed to load — Retry" button with TanStack Query `refetch`
4. **Loading indicators** — spinner on buttons during async operations

---

## 13 · ANIMATION GUIDELINES (Framer Motion)

```typescript
// Shared variants — import from lib/animations.ts
export const fadeUp = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.25 } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.15 } },
}

export const staggerChildren = {
  animate: { transition: { staggerChildren: 0.06 } }
}

// KPI card entrance
export const kpiEntrance = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 25 } },
}
```

Apply `AnimatePresence` around:
- KPI grid (re-animates on filter change)
- Feed rows (new rows slide in)
- Error cards (fade out on resolve)
- Drawer/sheet (slide in from right)
- Page transitions

---

## 14 · ENGINEERING RULES

### Must do
- [ ] TypeScript `strict: true` — no `any`
- [ ] All API responses typed with Zod schemas, validated at runtime
- [ ] All environment variables typed via `t3-env` or manual `z.object()`
- [ ] `axios` instance with `baseURL`, auth interceptor, global error toast
- [ ] Custom error boundary per page section
- [ ] All date/time in UTC from backend, format in user's local timezone on frontend
- [ ] Accessibility: all interactive elements have `aria-label`, keyboard navigable
- [ ] `eslint` + `prettier` configured and passing

### Must not do
- [ ] No inline styles except dynamic values (e.g. `style={{ width: pct + '%' }}`)
- [ ] No `any` in TypeScript
- [ ] No `useEffect` for data fetching (use TanStack Query)
- [ ] No Bootstrap, jQuery, or CDN-linked CSS
- [ ] No fake/mock data outside the dev simulator

---

## 15 · WHAT THE AGENT MUST PRODUCE

Deliver all of the following files:

**Root**
- `docker-compose.yml`
- `docker-compose.dev.yml` (with hot reload volumes)
- `README.md` (quick start: clone → `docker compose up` → open localhost:3000)

**apps/web** (complete Next.js app)
- All pages listed in Section 3
- All components listed in Section 3
- All hooks, stores, services, types, lib files
- `tailwind.config.ts` with ops palette
- `next.config.ts`
- `package.json`

**apps/api** (complete FastAPI app)
- All routers, models, schemas, services
- Socket.IO manager and events
- Dev simulator
- Alembic migration with full schema
- Seed script (creates users + 200 fake workflow runs across last 24h)
- `Dockerfile`
- `requirements.txt`
- `.env.example`

---

## 16 · ACCEPTANCE CRITERIA

The system is complete when:

1. `docker compose up` starts without errors
2. `http://localhost:3000` shows the login page
3. Login with `admin@nextgic.com / admin123` works
4. Overview dashboard shows live-updating KPI cards (new data every 5s)
5. Live Activity feed receives new rows in real-time without page refresh
6. Error Center shows errors; "Resolve" fades the card; "Retry" re-queues
7. Log Viewer streams new log lines in real-time
8. Workflow detail page shows step timeline for a workflow
9. All pages render correctly on mobile (375px), tablet (768px), desktop (1440px)
10. WebSocket indicator in TopNav shows green "Live" when connected
11. Typing `⌘K` opens the command palette
12. All TypeScript types are strict — `tsc --noEmit` passes with 0 errors
13. `docker compose down && docker compose up` re-seeds and works fresh

---

*End of prompt. Everything above is the complete specification. Build it.*
