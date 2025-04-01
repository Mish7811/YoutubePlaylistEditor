from fastapi import FastAPI, HTTPException
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
PLAYLIST_ID = "PL3HaZwqJ7M7IAYpJWZjwFxpW8TIqV4CLn"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins (change for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# OAuth authentication
def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

youtube = authenticate()

@app.get("/playlist")
def get_playlist():
    """Fetches all videos in the playlist"""
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
