import requests
import subprocess
import os
import json # We need this to read the track's information

# --- GET DETAILS FROM GITHUB SECRETS ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- PASTE YOUR DETAILS HERE ---
SOUNDCLOUD_USER_URL = "https://soundcloud.com/xosri" # Replace with the target SoundCloud user's URL

# --- SCRIPT LOGIC (No need to edit below this line) ---

# Define a static base filename for easy reference
BASE_FILENAME = "track"
TRACK_FILE = f"{BASE_FILENAME}.mp3"
INFO_FILE = f"{BASE_FILENAME}.info.json"

# 1. Download the latest track and its metadata using yt-dlp
command = [
    "yt-dlp",
    "--quiet",
    "--no-warnings",
    "-f", "bestaudio",
    "--extract-audio",
    "--audio-format", "mp3",
    "--output", f"{BASE_FILENAME}.%(ext)s", # yt-dlp will name it track.mp3
    "--embed-thumbnail",       # NEW: Embeds the cover art into the MP3
    "--write-info-json",       # NEW: Creates a file with the track's metadata
    "--playlist-end", "1",
    SOUNDCLOUD_USER_URL
]

# Clean up any old files before running
if os.path.exists(TRACK_FILE):
    os.remove(TRACK_FILE)
if os.path.exists(INFO_FILE):
    os.remove(INFO_FILE)

# Run the download command
try:
    print("Downloading latest track and metadata from SoundCloud...")
    subprocess.run(command, check=True)
    print("Download complete.")
except subprocess.CalledProcessError as e:
    print(f"Error downloading track: {e}")
    exit()

# 2. Prepare to send the audio file to Telegram
if os.path.exists(TRACK_FILE) and os.path.exists(INFO_FILE):
    # NEW: Read the metadata from the .info.json file
    with open(INFO_FILE, 'r') as f:
        track_info = json.load(f)
    
    # Extract the title and artist. Use 'N/A' as a fallback.
    track_title = track_info.get('title', 'N/A')
    track_artist = track_info.get('uploader', 'N/A')
    
    print(f"Track found: '{track_title}' by '{track_artist}'")
    print("Sending audio to Telegram...")
    
    # Set up the API call with metadata
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
    files = {'audio': open(TRACK_FILE, 'rb')}
    data = {
        'chat_id': CHAT_ID,
        'caption': 'Here is the latest track!',
        'title': track_title,   # NEW: Set the track title
        'performer': track_artist # NEW: Set the artist name
    }

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("Audio sent successfully!")
    else:
        print(f"Failed to send audio. Response: {response.text}")

    # 3. Clean up all downloaded files
    os.remove(TRACK_FILE)
    os.remove(INFO_FILE)
    print("Cleaned up audio and info files.")
else:
    print("Could not find downloaded track or info file.")
