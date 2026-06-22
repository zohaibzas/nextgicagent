// src/stores/ui.store.ts
import { create } from "zustand";

interface UIStore {
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
  sidebarMobileOpen: boolean;
  notifications: Notification[];
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
  setCommandPalette: (v: boolean) => void;
  toggleMobileSidebar: () => void;
  addNotification: (n: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
}

interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message?: string;
}

let notifId = 0;

export const useUIStore = create<UIStore>((set) => ({
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  sidebarMobileOpen: false,
  notifications: [],

  toggleSidebar: () =>
    set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setSidebarCollapsed: (v) =>
    set({ sidebarCollapsed: v }),
  setCommandPalette: (v) =>
    set({ commandPaletteOpen: v }),
  toggleMobileSidebar: () =>
    set((s) => ({ sidebarMobileOpen: !s.sidebarMobileOpen })),
  addNotification: (n) => {
    const id = `notif-${++notifId}`;
    set((s) => ({
      notifications: [...s.notifications, { ...n, id }],
    }));
    // Auto-remove after 5s
    setTimeout(() => {
      set((s) => ({
        notifications: s.notifications.filter((x) => x.id !== id),
      }));
    }, 5000);
  },
  removeNotification: (id) =>
    set((s) => ({
      notifications: s.notifications.filter((x) => x.id !== id),
    })),
}));
