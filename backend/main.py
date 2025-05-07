import os
import json
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse, JSONResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configurations
PORT = int(os.getenv("PORT", 8000))
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/youtube.force-ssl").split(",")
PLAYLIST_ID = os.getenv("GOOGLE_PLAYLIST_ID")
GOOGLE_AUTH_URL = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={','.join(SCOPES)}&access_type=offline&prompt=consent"

# Initialize HTTPBearer for token verification
bearer_scheme = HTTPBearer()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yt-playlist-song-adder.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def authenticate():
    """Authenticate with YouTube API using credentials stored in environment variables."""
    token_json_str = os.getenv("TOKEN_JSON")
    if not token_json_str:
        raise HTTPException(status_code=500, detail="TOKEN_JSON environment variable not set.")

    try:
        credentials = Credentials.from_authorized_user_info(json.loads(token_json_str), SCOPES)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load credentials: {e}")

    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(GoogleRequest())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to refresh credentials: {e}")
    
    if not credentials.valid:
        raise HTTPException(status_code=500, detail="Invalid credentials.")

    return build("youtube", "v3", credentials=credentials)

def verify_token(token: str):
    """Verify the Google ID token."""
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        if idinfo['aud'] != CLIENT_ID:
            raise ValueError('Invalid audience.')
        if not idinfo.get("email_verified"):
            raise ValueError("Email not verified.")
        return idinfo
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Middleware: Verify Google ID token
async def verify_google_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return response.json()

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/login")
def login():
    return RedirectResponse(GOOGLE_AUTH_URL)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    """Handle the OAuth2 callback and exchange the authorization code for tokens."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="No code in request")

    token_url = "https://oauth2.googleapis.com/token"
    params = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=params)

    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    return token_res.json()

@app.get("/authenticate")
def auth():
    """Authenticate the user with the YouTube API."""
    youtube = authenticate()
    if not youtube:
        raise HTTPException(status_code=401, detail="YouTube API authentication failed.")
    return {"message": "YouTube API authenticated successfully"}

@app.get("/playlist")
async def get_playlist(user=Depends(verify_google_token)):
    """Get the playlist from YouTube."""
    youtube = authenticate()
    request = youtube.playlistItems().list(part="snippet", playlistId=PLAYLIST_ID, maxResults=50)
    response = request.execute()
    return response

@app.post("/add_song")
async def add_song(song_title: str, user=Depends(verify_google_token)):
    """Add a song to the YouTube playlist."""
    if not song_title:
        raise HTTPException(status_code=400, detail="Song title is required.")

    youtube = authenticate()
    search_request = youtube.search().list(q=song_title, part="id", type="video", maxResults=1)
    search_response = search_request.execute()

    if not search_response["items"]:
        raise HTTPException(status_code=404, detail="Song not found")

    video_id = search_response["items"][0]["id"]["videoId"]
    add_request = youtube.playlistItems().insert(
        part="snippet", body={
            "snippet": {
                "playlistId": PLAYLIST_ID,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    )
    add_request.execute()
    return {"message": f"Added {song_title} to playlist"}

@app.delete("/clear_playlist")
async def clear_playlist(user=Depends(verify_google_token)):
    """Clear all videos from the playlist except the last one."""
    youtube = authenticate()
    request = youtube.playlistItems().list(part="id", playlistId=PLAYLIST_ID, maxResults=50)
    response = request.execute()
    items = response.get("items", [])

    if not items:
        return {"message": "Playlist is already empty."}

    keep_video = items[-1]
    for item in items:
        if item["id"] != keep_video["id"]:
            youtube.playlistItems().delete(id=item["id"]).execute()

    return {"message": "Playlist reduced to 1 video."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
