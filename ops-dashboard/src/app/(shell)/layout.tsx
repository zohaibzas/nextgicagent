"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { useAuthStore } from "@/stores/auth.store";
import { authMe } from "@/lib/api";

export default function ShellLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, token, setAuth, clearAuth, user } = useAuthStore();

  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }
    if (user) return;
    authMe()
      .then((u) => setAuth(u, token!))
      .catch(() => {
        clearAuth();
        router.replace("/login");
      });
  }, [token, user, router, setAuth, clearAuth]);

  if (!isAuthenticated && !token) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "var(--bg-base)" }}>
        <div className="spinner" />
      </div>
    );
  }

  return <DashboardShell>{children}</DashboardShell>;
}
