import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Helper function to get auth header from localStorage
const getAuthHeader = () => {
  const idToken = localStorage.getItem("id_token"); // Ensure your login process sets this
  return idToken ? { Authorization: `Bearer ${idToken}` } : {};
};

// Fetch playlist
export const fetchPlaylist = async () => {
  try {
    const url = `${API_URL}/playlist`;
    const headers = getAuthHeader();

    console.log("Calling playlist API:", url);
    console.log("Headers:", headers);
    
    const res = await axios.get(`${API_URL}/playlist`, {
      headers: getAuthHeader(),
    });
    return res.data.items; // Return playlist items from the response
  } catch (error) {
    console.error("Error fetching playlist", error);
    throw error;
  }
};

// Add song to playlist
export const addSong = async (songTitle: string) => {
  if (!songTitle) return; // Exit if no song title is provided
  try {
    await axios.post(
      `${API_URL}/add_song?song_title=${encodeURIComponent(songTitle)}`,
      null,
      {
        headers: getAuthHeader(),
      }
    );
  } catch (error) {
    console.error("Error adding song", error);
    throw error;
  }
};

// Clear playlist
export const clearPlaylist = async () => {
  try {
    await axios.delete(`${API_URL}/clear_playlist`, {
      headers: getAuthHeader(),
    });
  } catch (error) {
    console.error("Error clearing playlist", error);
    throw error;
  }
};
