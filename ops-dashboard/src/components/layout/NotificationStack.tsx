"use client";

import { useUIStore } from "@/stores/ui.store";

export function NotificationStack() {
  const { notifications } = useUIStore();

  if (!notifications.length) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {notifications.map((notif) => (
        <div key={notif.id} className="pointer-events-auto flex w-80 items-start gap-3 rounded-lg border border-white/10 bg-card p-4 shadow-lg">
          <div className="flex-1 flex flex-col">
            <span className="text-sm font-semibold">{notif.title}</span>
            <span className="text-xs text-muted-foreground">{notif.message}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
