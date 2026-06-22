"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchDashboardCharts } from "@/lib/api";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Area, AreaChart
} from "recharts";
import { Activity, BarChart3, AlertCircle } from "lucide-react";

export function OverviewCharts() {
  const { data: charts, isLoading, isError } = useQuery({
    queryKey: ["charts"],
    queryFn: () => fetchDashboardCharts(),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:gap-6">
        <div className="h-[300px] animate-pulse rounded-xl border bg-muted/50" />
        <div className="h-[300px] animate-pulse rounded-xl border bg-muted/50" />
      </div>
    );
  }

  if (isError || !charts) {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center text-sm text-red-500">
        <AlertCircle className="mx-auto mb-2 h-6 w-6 opacity-80" />
        Failed to load charts. Ensure the backend is running.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:gap-6">
      {/* Tasks by Agent Bar Chart */}
      <div className="flex flex-col rounded-xl border bg-card p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          <BarChart3 className="h-4 w-4" />
          Tasks by Agent
        </div>
        <div className="h-[240px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={charts.tasks_by_agent} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2d3748" />
              <XAxis dataKey="label" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                cursor={{ fill: '#1e2535' }}
                contentStyle={{ backgroundColor: '#0f1117', borderColor: '#1e2535', borderRadius: '8px' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hourly Success Rate Line Chart */}
      <div className="flex flex-col rounded-xl border bg-card p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          <Activity className="h-4 w-4" />
          Hourly Success Rate
        </div>
        <div className="h-[240px] w-full">
          {charts.hourly_success.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              No data in last 12 hours
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts.hourly_success} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2d3748" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f1117', borderColor: '#1e2535', borderRadius: '8px' }}
                  itemStyle={{ color: '#22c55e' }}
                />
                <Area type="monotone" dataKey="rate" stroke="#22c55e" strokeWidth={2} fillOpacity={1} fill="url(#colorSuccess)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
