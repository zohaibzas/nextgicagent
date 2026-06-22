"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap, Loader2 } from "lucide-react";
import { useAuthStore } from "@/stores/auth.store";
import { authLogin } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@nextgic.com");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const res = await authLogin(email, password);
      setAuth(res.user, res.access_token);
      router.push("/dashboard");
    } catch {
      setError("Invalid credentials");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-screen items-center justify-center p-4"
      style={{ background: "#0F1117", fontFamily: "system-ui" }}
    >
      <div className="w-full max-w-[400px]">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl" style={{ background: "var(--grad-brand)" }}>
            <Zap size={28} color="white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: "#38BDF8" }}>
            NEXTGIC
          </h1>
          <p className="mt-2 text-sm" style={{ color: "#64748B" }}>
            AI Operations Center
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-xl border p-8"
          style={{ background: "#1A1F2E", borderColor: "#1E2535" }}
        >
          <div className="mb-4">
            <label className="mb-1 block text-xs font-medium" style={{ color: "#94A3B8" }}>
              Email address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              required
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2"
              style={{
                background: "#1E2535",
                borderColor: "#1E2535",
                color: "#F1F5F9",
              }}
            />
          </div>
          <div className="mb-6">
            <label className="mb-1 block text-xs font-medium" style={{ color: "#94A3B8" }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2"
              style={{
                background: "#1E2535",
                borderColor: "#1E2535",
                color: "#F1F5F9",
              }}
            />
          </div>

          {error && (
            <p className="mb-4 text-center text-sm" style={{ color: "#EF4444" }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="flex h-11 w-full items-center justify-center gap-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
            style={{ background: "#38BDF8" }}
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
