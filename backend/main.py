import os
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load .env locally (ignored on Railway but helpful during dev)
load_dotenv()

app = FastAPI()
port = int(os.environ.get("PORT", 8000))

# Load environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/youtube.force-ssl").split(",")
PLAYLIST_ID = os.getenv("GOOGLE_PLAYLIST_ID")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yt-playlist-song-adder.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def authenticate():
    """Load credentials from Railway env and refresh if needed."""
    token_json_str = os.getenv("TOKEN_JSON")
    if not token_json_str:
        print("❌ TOKEN_JSON environment variable not set.")
        return None

    try:
        credentials = Credentials.from_authorized_user_info(json.loads(token_json_str))
    except Exception as e:
        print(f"❌ Failed to parse credentials: {e}")
        return None

    # Refresh token if needed
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception as e:
            print(f"❌ Failed to refresh credentials: {e}")
            return None

    if not credentials.valid:
        print("❌ Credentials are invalid even after refresh.")
        return None

    return build("youtube", "v3", credentials=credentials)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/authenticate")
def auth():
    youtube = authenticate()
    if not youtube:
        raise HTTPException(status_code=401, detail="YouTube API authentication failed.")
    return {"message": "YouTube API authenticated successfully"}

@app.get("/playlist")
def get_playlist():
    youtube = authenticate()
    if not youtube:
        raise HTTPException(status_code=401, detail="YouTube API authentication failed.")
    
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=PLAYLIST_ID,
        maxResults=50
    )
    response = request.execute()
    return response

@app.post("/add_song")
def add_song(song_title: str):
    youtube = authenticate()
    if not youtube:
        raise HTTPException(status_code=401, detail="YouTube API authentication failed.")

    search_request = youtube.search().list(
        q=song_title,
        part="id",
        type="video",
        maxResults=1
    )
    search_response = search_request.execute()

    if not search_response["items"]:
        raise HTTPException(status_code=404, detail="Song not found")

    video_id = search_response["items"][0]["id"]["videoId"]

    add_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": PLAYLIST_ID,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    add_request.execute()
    return {"message": f"Added {song_title} to playlist"}

@app.delete("/clear_playlist")
def clear_playlist():
    youtube = authenticate()
    if not youtube:
        raise HTTPException(status_code=401, detail="YouTube API authentication failed.")
    
    request = youtube.playlistItems().list(part="id", playlistId=PLAYLIST_ID, maxResults=50)
    response = request.execute()
    items = response.get("items", [])

    if len(items) <= 1:
        return {"message": "Playlist already has 1 or fewer videos."}

    keep_video = items[-1]
    for item in items:
        if item["id"] != keep_video["id"]:
            youtube.playlistItems().delete(id=item["id"]).execute()

    return {"message": "Playlist reduced to 1 video."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
