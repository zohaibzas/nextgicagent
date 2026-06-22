"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchKpis } from "@/lib/api";
import { useFilterStore } from "@/stores/filter.store";
import {
  ListChecks,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Ban,
  Database,
  MessageCircle,
  Package,
  Sparkles,
  ShoppingCart,
  ImageIcon,
} from "lucide-react";

interface KPICardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  valueColor?: string;
}

function KPICard({ label, value, sub, icon, valueColor }: KPICardProps) {
  return (
    <div className="kpi-card">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
        {icon}
        {label}
      </div>
      <div className="kpi-value" style={valueColor ? { color: valueColor } : undefined}>
        {value}
      </div>
      {sub && (
        <div className="text-xs" style={{ color: "var(--text-muted)" }}>
          {sub}
        </div>
      )}
    </div>
  );
}

export function KPIGrid() {
  const date = useFilterStore((s) => s.date);
  const { data: kpis, isLoading, isError } = useQuery({
    queryKey: ["kpis", date],
    queryFn: () => fetchKpis({ date }),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="kpi-grid">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="kpi-card skeleton h-[100px]" />
        ))}
      </div>
    );
  }

  if (isError || !kpis) {
    return (
      <div
        className="rounded-xl border p-6 text-center text-sm"
        style={{ borderColor: "var(--error)", color: "var(--error)", background: "var(--error-dim)" }}
      >
        Failed to load KPIs. Start FastAPI: uvicorn main:app --port 8000
      </div>
    );
  }

  const srColor =
    kpis.success_rate >= 85
      ? "var(--success)"
      : kpis.success_rate >= 70
        ? "var(--warning)"
        : "var(--error)";

  const durColor =
    kpis.avg_duration > 30
      ? "var(--error)"
      : kpis.avg_duration > 15
        ? "var(--warning)"
        : undefined;

  const fmtDur = (s: number) => (s < 60 ? `${s.toFixed(1)}s` : `${(s / 60).toFixed(1)}m`);

  return (
    <div className="flex flex-col gap-4">
      <div className="kpi-grid">
        <KPICard label="Total tasks" value={kpis.total_tasks} icon={<ListChecks size={16} />} />
        <KPICard label="Tasks today" value={kpis.today} icon={<ListChecks size={16} />} />
        <KPICard
          label="Success rate"
          value={`${kpis.success_rate}%`}
          sub={`${kpis.success} succeeded`}
          icon={<CheckCircle2 size={16} />}
          valueColor={srColor}
        />
        <KPICard
          label="Failed"
          value={`${kpis.failed} / ${kpis.total_tasks}`}
          icon={<XCircle size={16} />}
          valueColor={kpis.failed > 0 ? "var(--error)" : undefined}
        />
        <KPICard
          label="Avg duration"
          value={fmtDur(kpis.avg_duration)}
          icon={<Clock size={16} />}
          valueColor={durColor}
        />
        <KPICard
          label="Open errors"
          value={kpis.open_errors}
          icon={<AlertTriangle size={16} />}
          valueColor={kpis.open_errors > 0 ? "var(--error)" : undefined}
        />
        <KPICard label="OOS updates" value={kpis.oos_count} icon={<Package size={16} />} />
        <KPICard label="Products added" value={kpis.new_products} icon={<Sparkles size={16} />} />
      </div>
      <div className="kpi-grid">
        <KPICard label="NVIDIA calls" value={kpis.ai_calls} icon={<Sparkles size={16} />} />
        <KPICard label="Avg AI response" value={fmtDur(kpis.ai_avg_duration)} icon={<Clock size={16} />} />
        <KPICard label="AI error rate" value={`${kpis.ai_error_rate}%`} icon={<AlertTriangle size={16} />} />
        <KPICard
          label="WC API errors"
          value={kpis.wc_errors}
          valueColor={kpis.wc_errors > 0 ? "var(--error)" : undefined}
          icon={<ShoppingCart size={16} />}
        />
        <KPICard label="Images processed" value={kpis.images_processed} icon={<ImageIcon size={16} />} />
        <KPICard label="WhatsApp msgs" value={kpis.wa_messages} icon={<MessageCircle size={16} />} />
        <KPICard label="Dedup blocked" value={kpis.dedup_blocked} icon={<Ban size={16} />} />
        <KPICard label="Cache entries" value={kpis.cache_hits} icon={<Database size={16} />} />
      </div>
    </div>
  );
}
