import { useEffect, useState } from "react";
import { fetchPlaylist } from "@/lib/api";

type PlaylistItem = {
  id: string;
  snippet: {
    title: string;
  };
};

export default function Playlist() {
  const [playlist, setPlaylist] = useState<PlaylistItem[]>([]); // ✅ Explicit type

  useEffect(() => {
    loadPlaylist();
  }, []);

  const loadPlaylist = async () => {
    const items: PlaylistItem[] = await fetchPlaylist();
    setPlaylist(items);
  };

  return (
    <div>
      <h2 className="text-2xl mt-5" style={{ fontFamily: "var(--font-permanent-marker)" }}>
        Playlist:
      </h2>
      <ul className="list-disc list-inside text-justify my-4 mx-2 px-2">
        {playlist.map((item) => (
          <li key={item.id}>{item.snippet.title}</li>
        ))}
      </ul>
    </div>
  );
}
