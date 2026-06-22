"use client";

import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { fetchAnalytics, type AnalyticsResponse } from "@/lib/api";

const CHART_COLORS = ["#818CF8", "#22C55E", "#F59E0B", "#EC4899", "#38BDF8", "#6366F1"];

const tooltipStyle = {
  contentStyle: { backgroundColor: "#0f1117", borderColor: "#1e2535", borderRadius: 8 },
  itemStyle: { color: "#e2e8f0" },
};

function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="chart-container">
      <div className="chart-title">{title}</div>
      {subtitle && <div className="chart-subtitle">{subtitle}</div>}
      <div className="h-[220px] w-full">{children}</div>
    </div>
  );
}

export function AnalyticsDashboard() {
  const { data, isLoading, isError } = useQuery<AnalyticsResponse>({
    queryKey: ["analytics"],
    queryFn: fetchAnalytics,
  });

  if (isLoading) {
    return (
      <div className="chart-grid-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="chart-container skeleton h-[280px]" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-xl border p-6 text-center text-sm" style={{ color: "var(--error)" }}>
        Failed to load analytics.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="chart-grid-2">
        <ChartCard title="Task volume" subtitle="Last 30 days">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.task_volume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(d) => d.slice(5)} />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip {...tooltipStyle} />
              <Area type="monotone" dataKey="count" stroke="#818CF8" fill="#818CF8" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Success vs failed" subtitle="Daily breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.success_vs_failed}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(d) => d.slice(5)} />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip {...tooltipStyle} />
              <Legend />
              <Bar dataKey="success" fill="#22C55E" stackId="a" />
              <Bar dataKey="failed" fill="#EF4444" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Tasks by agent">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.tasks_by_agent} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis type="number" stroke="#64748b" fontSize={10} />
              <YAxis type="category" dataKey="agent" stroke="#64748b" fontSize={10} width={80} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Error rate trend" subtitle="% failed per day">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.error_rate_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(d) => d.slice(5)} />
              <YAxis stroke="#64748b" fontSize={10} unit="%" />
              <Tooltip {...tooltipStyle} />
              <Line type="monotone" dataKey="rate" stroke="#EF4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Avg duration trend" subtitle="Seconds per day">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.avg_duration_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickFormatter={(d) => d.slice(5)} />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip {...tooltipStyle} />
              <Line type="monotone" dataKey="avg_sec" stroke="#F59E0B" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Tasks by hour" subtitle="Average count">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.tasks_by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2535" />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="avg_count" fill="#38BDF8" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Task type split">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data.task_type_split}
                dataKey="count"
                nameKey="type"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
              >
                {data.task_type_split.map((_: unknown, i: number) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...tooltipStyle} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
