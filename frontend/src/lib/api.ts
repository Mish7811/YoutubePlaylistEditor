import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Get ID token from localStorage (assuming Google Sign-In sets it there)
const getAuthHeader = () => {
  const idToken = localStorage.getItem("id_token"); // Ensure your login process sets this
  return idToken ? { Authorization: `Bearer ${idToken}` } : {};
};

// Helper function to handle error logging
const handleError = (error: unknown, action: string) => {
  if (error instanceof Error) {
    console.error(`${action} - Error:`, error.message);
  } else {
    console.error(`${action} - Unknown error`, error);
  }
};

// Fetch playlist
export const fetchPlaylist = async () => {
  try {
    const res = await axios.get(`${API_URL}/playlist`, {
      headers: getAuthHeader(),
    });
    return res.data.items; // Return playlist items from the response
  } catch (error) {
    handleError(error, "Fetching playlist");
    return [];
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
    handleError(error, "Adding song");
  }
};

// Clear playlist (except first video)
export const clearPlaylist = async () => {
  try {
    await axios.delete(`${API_URL}/clear_playlist`, {
      headers: getAuthHeader(),
    });
  } catch (error) {
    handleError(error, "Clearing playlist");
  }
};
