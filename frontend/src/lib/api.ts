import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Fetch playlist
export const fetchPlaylist = async () => {
  try {
    const res = await axios.get(`/api/playlist`);
    return res.data.items;
  } catch (error) {
    console.error("Error fetching playlist:", error);
    return [];
  }
};

// Add song to playlist
export const addSong = async (songTitle: string) => {
  if (!songTitle) return;
  try {
    await axios.post(`${API_URL}/add_song?song_title=${encodeURIComponent(songTitle)}`);
  } catch (error) {
    console.error("Error adding song:", error);
  }
};

// Clear playlist (except first video)
export const clearPlaylist = async () => {
  try {
    await axios.delete(`${API_URL}/clear_playlist`);
  } catch (error) {
    console.error("Error clearing playlist:", error);
  }
};
