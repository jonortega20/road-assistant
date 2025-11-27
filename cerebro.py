# cerebro.py
import os
import datetime
from fastapi import FastAPI, Request, HTTPException
import uvicorn
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- CONFIGURATION ---
# Credentials provided by user
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "____")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "____")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

# The Spotify Playlist URI for "Diggin"
DIGGIN_PLAYLIST_URI = os.getenv("DIGGIN_PLAYLIST_URI", "spotify:playlist:____")

# File path for notes
NOTES_FILE = "notas_coche.md"

app = FastAPI()

# --- SPOTIFY SETUP ---
# Scope needed to control playback
SCOPE = "user-modify-playback-state user-read-playback-state"

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    open_browser=False, # Important for headless/Termux environment
    cache_path=".spotify_cache" # Saves token to avoid re-login
)

sp = spotipy.Spotify(auth_manager=auth_manager)

@app.get("/")
async def root():
    return {"status": "Cerebro is running"}

@app.get("/callback")
async def callback(code: str):
    """
    Callback endpoint for Spotify OAuth. 
    In a real headless setup, you might need to copy-paste the URL, 
    but if you open the auth URL on the same device, it might redirect here.
    """
    auth_manager.get_access_token(code)
    return {"status": "Authenticated with Spotify!"}

@app.post("/music")
async def musica_maestro():
    """
    Trigger: "Música Maestro"
    Action: Shuffle ON, Play 'Diggin' playlist.
    """
    try:
        # Check if we have a valid token
        if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
            return {"status": "error", "message": "Spotify token expired or missing. Authenticate first."}

        # 1. Enable Shuffle
        sp.shuffle(True)
        
        # 2. Start Playback
        # Note: This requires an active device. If no device is active, 
        # you might need to specify device_id.
        devices = sp.devices()
        active_devices = [d for d in devices['devices'] if d['is_active']]
        
        if not active_devices:
             # Try to find the smartphone itself if listed, or just the first available
            if devices['devices']:
                device_id = devices['devices'][0]['id']
                sp.start_playback(device_id=device_id, context_uri=DIGGIN_PLAYLIST_URI)
                return {"status": "success", "message": f"Playing on {devices['devices'][0]['name']}"}
            else:
                return {"status": "error", "message": "No active Spotify devices found. Open Spotify on your phone."}
        
        # If there is an active device, just play there
        sp.start_playback(context_uri=DIGGIN_PLAYLIST_URI)
        return {"status": "success", "message": "Playing Diggin playlist shuffled"}

    except Exception as e:
        print(f"Error in /music: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/note")
async def apunta_esto(request: Request):
    """
    Trigger: "Apunta esto"
    Action: Append text to a local markdown file.
    """
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        
        if not text:
            return {"status": "ignored", "message": "No text provided"}

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        note_entry = f"- [ ] **{timestamp}**: {text}\n"

        # Append to local file
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(note_entry)
            
        print(f"Note saved: {text}")
        return {"status": "success", "message": "Note saved", "saved_text": text}

    except Exception as e:
        print(f"Error in /note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible via localhost in Termux
    uvicorn.run(app, host="0.0.0.0", port=9000)