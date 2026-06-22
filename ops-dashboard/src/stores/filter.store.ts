import { create } from "zustand";

interface FilterStore {
  date: string;
  agent: string;
  status: string;
  search: string;
  setDate: (d: string) => void;
  setAgent: (a: string) => void;
  setStatus: (s: string) => void;
  setSearch: (s: string) => void;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export const useFilterStore = create<FilterStore>((set) => ({
  date: todayIso(),
  agent: "all",
  status: "all",
  search: "",
  setDate: (date) => set({ date }),
  setAgent: (agent) => set({ agent }),
  setStatus: (status) => set({ status }),
  setSearch: (search) => set({ search }),
}));
