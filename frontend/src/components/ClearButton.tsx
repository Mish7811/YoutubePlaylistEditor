"use client";  // Needed for hooks


import { useState } from "react";
import { clearPlaylist } from "@/lib/api";

export default function ClearButton({ onClear }: { onClear: () => void }) {
  const [loading, setLoading] = useState(false);

  const handleClear = async () => {
    setLoading(true);
    await clearPlaylist();
    setLoading(false);
    onClear(); // Refresh playlist
  };

  return (
    <button className="bg-red-500 mx-60 px-1 py-2 w-35 rounded-3xl cursor-pointer" onClick={handleClear} disabled={loading}>
      {loading ? "Clearing..." : "Clear Playlist"}
    </button>
  );
}
