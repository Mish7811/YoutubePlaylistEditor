import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/playlist",
        destination: "https://youtubeplaylisteditor-production.up.railway.app/playlist", // Backend URI
      },
    ];
  },

  async headers() {
    return [
      {
        source: "/api/playlist",
        headers: [
          {
            key: "Access-Control-Allow-Origin",
            value: "https://yt-playlist-song-adder.vercel.app", // Frontend URI
          },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET,POST,PUT,DELETE,OPTIONS",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
