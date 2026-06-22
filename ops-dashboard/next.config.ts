import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      { source: "/dashboard/live", destination: "/live", permanent: false },
      { source: "/dashboard/agents", destination: "/agents", permanent: false },
      { source: "/dashboard/errors", destination: "/errors", permanent: false },
      { source: "/dashboard/logs", destination: "/logs", permanent: false },
      { source: "/dashboard/workflows", destination: "/workflows", permanent: false },
      { source: "/dashboard/analytics", destination: "/analytics", permanent: false },
      { source: "/dashboard/settings", destination: "/settings", permanent: false },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/v1/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "**" },
    ],
  },
};

export default nextConfig;
