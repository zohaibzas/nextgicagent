import { FilterBar } from "@/components/dashboard/FilterBar";
import { ErrorList } from "@/components/errors/ErrorList";

export default function ErrorsPage() {
  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Error Center</h1>
        <p className="page-subtitle">Failed tasks — retry or resolve</p>
      </div>
      <FilterBar />
      <ErrorList />
    </div>
  );
}
