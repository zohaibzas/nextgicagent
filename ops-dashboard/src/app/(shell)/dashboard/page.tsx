import { FilterBar } from "@/components/dashboard/FilterBar";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { OverviewCharts } from "@/components/dashboard/OverviewCharts";
import { SystemStatus } from "@/components/dashboard/SystemStatus";
import { ErrorList } from "@/components/errors/ErrorList";

export default function DashboardPage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Overview</h1>
        <p className="page-subtitle">Command center — system health at a glance</p>
      </div>
      <FilterBar />
      <KPIGrid />
      <OverviewCharts />
      <div className="chart-grid-2">
        <div>
          <div className="section-title mb-3">Recent errors</div>
          <ErrorList compact limit={5} />
        </div>
        <SystemStatus />
      </div>
    </div>
  );
}
