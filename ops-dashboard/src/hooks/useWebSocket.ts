"use client";

import { useEffect, useRef } from "react";
import { useRealtimeStore } from "@/stores/realtime.store";
import { useTaskStore } from "@/stores/task.store";
import type { JobLog, WSEvent } from "@/types";
import { useAuthStore } from "@/stores/auth.store";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { setConnected, pushEvent } = useRealtimeStore();
  const prependTask = useTaskStore((s) => s.prependTask);
  const token = useAuthStore((s) => s.token);

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const url = `${WS_BASE}/ws/live`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }
    };

    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as WSEvent & { data?: JobLog };
        pushEvent(event);

        const taskEvents = [
          "task.created",
          "workflow.started",
          "workflow.completed",
          "workflow.failed",
        ];
        if (taskEvents.includes(event.event) && event.data) {
          const d = event.data as JobLog & { workflow_id?: string };
          prependTask({
            id: d.id,
            created_at: d.created_at || new Date().toISOString(),
            task_type: d.task_type || "",
            agent_label: d.agent_label || "Intake",
            agent_icon: "",
            product: d.product,
            input_text: d.input_text,
            status: d.status || "pending",
            duration_sec: d.duration_sec,
            whatsapp_msg_id: d.whatsapp_msg_id,
            error: d.error,
          });
        }
      } catch {
        /* ignore */
      }
    };

    ws.onerror = () => setConnected(false);

    ws.onclose = () => {
      setConnected(false);
      reconnectRef.current = setTimeout(connect, 3000);
    };
  };

  useEffect(() => {
    connect();
    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 25000);
    return () => {
      clearInterval(ping);
      wsRef.current?.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return { connected: useRealtimeStore((s) => s.connected) };
}
