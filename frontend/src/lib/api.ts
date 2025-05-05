import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Get ID token from localStorage (assuming Google Sign-In sets it there)
const getAuthHeader = () => {
  const idToken = localStorage.getItem("id_token"); // Ensure your login process sets this
  return idToken ? { Authorization: `Bearer ${idToken}` } : {};
};

// Fetch playlist
export const fetchPlaylist = async () => {
  try {
    const res = await axios.get(`${API_URL}/playlist`, {
      headers: getAuthHeader(),
    });
    return res.data.items; // Return playlist items from the response
  } catch (error) {
    console.error("Error fetching playlist:", error.response ? error.response.data : error.message);
    // Optionally, you can return an empty array or handle the error as per the app's needs
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
    console.error("Error adding song:", error.response ? error.response.data : error.message);
    // Optionally, handle the error (e.g., show an alert or retry logic)
  }
};

// Clear playlist (except first video)
export const clearPlaylist = async () => {
  try {
    await axios.delete(`${API_URL}/clear_playlist`, {
      headers: getAuthHeader(),
    });
  } catch (error) {
    console.error("Error clearing playlist:", error.response ? error.response.data : error.message);
    // Optionally, handle the error (e.g., show an alert or retry logic)
  }
};
