import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/playlist",
        destination: "https://youtubeplaylisteditor-production.up.railway.app/playlist",
      },
    ];
  },
};

export default nextConfig;
