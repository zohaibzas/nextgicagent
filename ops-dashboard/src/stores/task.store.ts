import { create } from "zustand";
import type { JobLog } from "@/types";

interface TaskStore {
  tasks: JobLog[];
  setTasks: (tasks: JobLog[]) => void;
  prependTask: (task: JobLog) => void;
  updateTask: (id: number, patch: Partial<JobLog>) => void;
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],
  setTasks: (tasks) => set({ tasks }),
  prependTask: (task) =>
    set((s) => {
      const exists = s.tasks.some((t) => t.id === task.id);
      if (exists) {
        return {
          tasks: s.tasks.map((t) => (t.id === task.id ? { ...t, ...task } : t)),
        };
      }
      return { tasks: [task, ...s.tasks].slice(0, 500) };
    }),
  updateTask: (id, patch) =>
    set((s) => ({
      tasks: s.tasks.map((t) => (t.id === id ? { ...t, ...patch } : t)),
    })),
}));
