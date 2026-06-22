import { FilterBar } from "@/components/dashboard/FilterBar";
import { AgentHealthGrid } from "@/components/agents/AgentHealthGrid";

export default function AgentsPage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Agent Monitor</h1>
        <p className="page-subtitle">Per-agent health and performance</p>
      </div>
      <FilterBar />
      <AgentHealthGrid />
    </div>
  );
}
