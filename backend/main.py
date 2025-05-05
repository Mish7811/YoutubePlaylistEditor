import os
import json
import uvicorn
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from fastapi.responses import RedirectResponse, JSONResponse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

# Load .env locally (ignored on Railway but helpful during dev)
load_dotenv()

app = FastAPI()
port = int(os.environ.get("PORT", 8000))
bearer_scheme = HTTPBearer()

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
        credentials_data = json.loads(token_json_str)
        print("🔍 Loaded TOKEN_JSON:", credentials_data)
        credentials = Credentials.from_authorized_user_info(json.loads(token_json_str))

        print("✅ creds.valid:", credentials.valid)
        print("⏳ creds.expired:", credentials.expired)
        print("🔁 creds.refresh_token present:", bool(credentials.refresh_token))

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
async def verify_google_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
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

@app.get("/example")
async def example():
    response = JSONResponse({"message": "Hello, world!"})
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
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
        print(token_res.text)
        raise HTTPException(status_code=400, detail="Token exchange failed")

    tokens = token_res.json()

    # Optionally save `tokens` somewhere (database, session, etc.)
    # For now, just return them
    return tokens

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

