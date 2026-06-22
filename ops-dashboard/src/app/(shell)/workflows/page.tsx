import { LiveFeed } from "@/components/activity/LiveFeed";
import { FilterBar } from "@/components/dashboard/FilterBar";

export default function WorkflowsPage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Workflow Explorer</h1>
        <p className="page-subtitle">Click any row to open the step trace drawer</p>
      </div>
      <FilterBar />
      <LiveFeed />
    </div>
  );
}
