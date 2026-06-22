// src/app/layout.tsx
import type { Metadata } from "next";
import "@/styles/globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "NEXTGIC AI Operations Center",
    template: "%s | NEXTGIC AI OPS",
  },
  description:
    "Enterprise realtime AI operations dashboard — monitor AI agents, workflows, WooCommerce automation, queues, logs, and analytics.",
  keywords: ["AI monitoring", "WooCommerce automation", "WhatsApp bot", "operations dashboard"],
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
