"use client";

import { useAuthStore } from "@/stores/auth.store";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Team and configuration</p>
      </div>
      <div className="glass-card max-w-lg p-6">
        <div className="section-title mb-4">Current user</div>
        {user ? (
          <dl className="flex flex-col gap-2 text-sm">
            <div className="flex justify-between">
              <dt style={{ color: "var(--text-muted)" }}>Email</dt>
              <dd>{user.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt style={{ color: "var(--text-muted)" }}>Role</dt>
              <dd className="badge badge-brand">{user.role}</dd>
            </div>
          </dl>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>Loading…</p>
        )}
        <p className="mt-6 text-xs" style={{ color: "var(--text-muted)" }}>
          Default dev login: admin@nextgic.com / nextgic — set DASHBOARD_ADMIN_* in backend .env
        </p>
      </div>
    </div>
  );
}
