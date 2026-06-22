import { AnalyticsDashboard } from "@/components/charts/AnalyticsDashboard";

export default function AnalyticsPage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">30-day trends from job_log</p>
      </div>
      <AnalyticsDashboard />
    </div>
  );
}
