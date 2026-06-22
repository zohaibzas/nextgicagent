// src/stores/realtime.store.ts
import { create } from "zustand";
import type { WorkflowRun, SystemLog, Alert, WSEvent } from "@/types";

interface RealtimeStore {
  connected: boolean;
  liveEvents: WSEvent[];
  liveWorkflows: WorkflowRun[];
  liveLogs: SystemLog[];
  liveAlerts: Alert[];
  setConnected: (v: boolean) => void;
  pushEvent: (event: WSEvent) => void;
  pushLog: (log: SystemLog) => void;
  pushAlert: (alert: Alert) => void;
  upsertWorkflow: (run: WorkflowRun) => void;
  clearEvents: () => void;
}

const MAX_EVENTS = 500;
const MAX_LOGS = 1000;

export const useRealtimeStore = create<RealtimeStore>((set) => ({
  connected: false,
  liveEvents: [],
  liveWorkflows: [],
  liveLogs: [],
  liveAlerts: [],

  setConnected: (v) => set({ connected: v }),

  pushEvent: (event) =>
    set((s) => ({
      liveEvents: [event, ...s.liveEvents].slice(0, MAX_EVENTS),
    })),

  pushLog: (log) =>
    set((s) => ({
      liveLogs: [log, ...s.liveLogs].slice(0, MAX_LOGS),
    })),

  pushAlert: (alert) =>
    set((s) => ({ liveAlerts: [alert, ...s.liveAlerts] })),

  upsertWorkflow: (run) =>
    set((s) => {
      const idx = s.liveWorkflows.findIndex((w) => w.run_id === run.run_id);
      if (idx >= 0) {
        const updated = [...s.liveWorkflows];
        updated[idx] = run;
        return { liveWorkflows: updated };
      }
      return { liveWorkflows: [run, ...s.liveWorkflows].slice(0, 200) };
    }),

  clearEvents: () => set({ liveEvents: [] }),
}));
