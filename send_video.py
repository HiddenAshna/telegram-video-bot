import requests
import subprocess
import os

# --- GET DETAILS FROM GITHUB SECRETS ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- PASTE YOUR DETAILS HERE ---
SOUNDCLOUD_USER_URL = "https://soundcloud.com/xosri" # Replace with the target SoundCloud user's URL

# --- SCRIPT LOGIC (No need to edit below this line) ---

FILENAME = "track.mp3"

# 1. Download the latest track using yt-dlp
command = [
    "yt-dlp",
    "--quiet",
    "--no-warnings",
    "-f", "bestaudio",      # Download the best quality audio
    "--extract-audio",      # Ensure we get an audio file
    "--audio-format", "mp3",# Convert the audio to MP3
    "--output", FILENAME,   # Save the file as track.mp3
    "--playlist-end", "1",  # Only download the latest track
    SOUNDCLOUD_USER_URL
]

# Run the download command
try:
    if os.path.exists(FILENAME):
        os.remove(FILENAME)

    print("Downloading latest track from SoundCloud...")
    subprocess.run(command, check=True)
    print("Download complete.")
except subprocess.CalledProcessError as e:
    print(f"Error downloading track: {e}")
    exit()

# 2. Send the audio file to Telegram
if os.path.exists(FILENAME):
    print("Sending audio to Telegram...")
    # Use the sendAudio method for music files
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
    files = {'audio': open(FILENAME, 'rb')}
    data = {'chat_id': CHAT_ID, 'caption': 'Here is the latest track!'}

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("Audio sent successfully!")
    else:
        print(f"Failed to send audio. Response: {response.text}")

    # 3. Clean up the downloaded file
    os.remove(FILENAME)
    print("Cleaned up audio file.")
else:
    print("No audio file found to send.")
