import { useState } from "react";
import { addSong } from "@/lib/api";

// Update the prop type of onAdd to match the expected function signature
export default function AddSong({ onAdd }: { onAdd: () => void }) {
  const [songTitle, setSongTitle] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    if (!songTitle) return;
    setLoading(true);
    await addSong(songTitle); // Add the song via API
    setSongTitle(""); // Clear input field after adding
    setLoading(false);
    onAdd(); // Refresh playlist without passing songTitle
  };

  return (
    <div className="flex flex-col items-center place-content-evenly">
      <input
        type="text"
        className="p-2 text-white border-2 text-center border-blue-500 rounded-3xl focus:outline-none focus:ring-2 focus:ring-blue-400"
        placeholder="Enter song title"
        value={songTitle}
        onChange={(e) => setSongTitle(e.target.value)}
      />
      <button
        className="bg-blue-500 cursor-pointer px-4 py-2 mx-5 mt-5 mb-0 ml-2 rounded-3xl"
        onClick={handleAdd}
        disabled={loading}
      >
        {loading ? "Adding..." : "Add Song"}
      </button>
    </div>
  );
}
