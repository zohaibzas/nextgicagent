import { FilterBar } from "@/components/dashboard/FilterBar";
import { LiveFeed } from "@/components/activity/LiveFeed";

export default function LivePage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Live Activity</h1>
        <p className="page-subtitle">Real-time task feed — new rows via WebSocket</p>
      </div>
      <FilterBar />
      <LiveFeed />
    </div>
  );
}
