export const AGENT_COLORS: Record<string, string> = {
  intake: "#818CF8",
  unknown: "#818CF8",
  oos: "#22C55E",
  duplicate: "#F59E0B",
  new_product: "#EC4899",
};

export const STATUS_BADGE: Record<string, { bg: string; text: string }> = {
  success: { bg: "#052E16", text: "#22C55E" },
  failed: { bg: "#2D0A0A", text: "#EF4444" },
  pending: { bg: "#1C1A05", text: "#F59E0B" },
  skipped: { bg: "#1C1A05", text: "#94A3B8" },
  resolved: { bg: "#1E2535", text: "#64748B" },
};

export const AGENTS = [
  { value: "all", label: "All agents" },
  { value: "unknown", label: "Intake" },
  { value: "oos", label: "OOS" },
  { value: "duplicate", label: "Duplicate" },
  { value: "new_product", label: "New product" },
];

export const STATUSES = [
  { value: "all", label: "All statuses" },
  { value: "success", label: "Success" },
  { value: "failed", label: "Failed" },
  { value: "pending", label: "Pending" },
  { value: "skipped", label: "Skipped" },
];
