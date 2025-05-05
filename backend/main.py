import os
import json
import uvicorn
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def authenticate():
    token_json_str = os.getenv("TOKEN_JSON")
    if not token_json_str:
        print("\u274c TOKEN_JSON environment variable not set.")
        return None

    try:
        credentials = Credentials.from_authorized_user_info(json.loads(token_json_str))
    except Exception as e:
        print(f"\u274c Failed to parse credentials: {e}")
        return None

    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(GoogleRequest())
        except Exception as e:
            print(f"\u274c Failed to refresh credentials: {e}")
            return None

    if not credentials.valid:
        print("\u274c Credentials are invalid even after refresh.")
        return None

    return build("youtube", "v3", credentials=credentials)

# Middleware: Verify Google ID token\
async def verify_google_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json()

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
async def get_playlist(user=Depends(verify_google_token)):
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
async def add_song(song_title: str, user=Depends(verify_google_token)):
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
async def clear_playlist(user=Depends(verify_google_token)):
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
    print(json.loads(token_json_str))

