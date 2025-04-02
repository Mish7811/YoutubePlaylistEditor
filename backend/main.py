import os
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = FastAPI()
port = int(os.environ.get("PORT", 8000))

load_dotenv()

# Load environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/youtube.force-ssl").split(",")
PLAYLIST_ID = os.getenv("GOOGLE_PLAYLIST_ID")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authenticate only when needed
def authenticate():
    credentials = None

    # Load stored credentials from Railway environment variable
    token_json_str = os.getenv("TOKEN_JSON")
    if token_json_str:
        credentials = Credentials.from_authorized_user_info(json.loads(token_json_str))

    # Refresh the token if expired
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # If credentials are missing, re-authenticate manually and store the token JSON
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/youtube.force-ssl").split(","),
        )

        # 🚀 On Railway, you should authenticate locally first and store the token manually
        print("⚠️ Run this script locally first to generate a token.")
        credentials = flow.run_local_server(port=8080)

        # Save new credentials to Railway's environment (copy manually)
        print("Copy this token JSON and set it as the 'TOKEN_JSON' environment variable in Railway:")
        print(credentials.to_json())

    return build("youtube", "v3", credentials=credentials)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/authenticate")
def auth():
    """Authenticate with YouTube API and store token."""
    global youtube
    youtube = authenticate()
    return {"message": "YouTube API authenticated successfully"}

@app.get("/playlist")
def get_playlist():
    """Fetches all videos in the playlist"""
    youtube = authenticate()
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=PLAYLIST_ID,
        maxResults=50
    )
    response = request.execute()
    return response

@app.post("/add_song")
def add_song(song_title: str):
    """Search for a song and add it to the playlist"""
    youtube = authenticate()
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
    """Removes all but one video from the playlist"""
    youtube = authenticate()
    request = youtube.playlistItems().list(part="id", playlistId=PLAYLIST_ID, maxResults=50)
    response = request.execute()
    items = response.get("items", [])
    
    if len(items) <= 1:
        return {"message": "Playlist already has 1 or fewer videos."}
    
    keep_video = items[-1]  # Keep last added video
    for item in items:
        if item["id"] != keep_video["id"]:
            youtube.playlistItems().delete(id=item["id"]).execute()
    
    return {"message": "Playlist reduced to 1 video."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
