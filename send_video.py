import requests
import subprocess
import os
import json
import time

# --- CONSTANTS AND SECRETS ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
STATE_FILE = "sent_tracks.json"

# --- PASTE YOUR LIST OF LINKS HERE ---
SOUNDCLOUD_URLS = [
    "https://soundcloud.com/nasa",
    "https://soundcloud.com/xosri",
    # Add your links here...
]

# --- SCRIPT LOGIC ---

# Load the memory of sent tracks from the state file
try:
    with open(STATE_FILE, 'r') as f:
        sent_tracks = json.load(f)
    print("Successfully loaded the sent tracks log.")
except (FileNotFoundError, json.JSONDecodeError):
    sent_tracks = {}
    print("Could not find or read the log file. Starting with an empty memory.")

# Loop through each URL
for i, user_url in enumerate(SOUNDCLOUD_URLS):
    print("-" * 40)
    print(f"Processing link {i+1}/{len(SOUNDCLOUD_URLS)}: {user_url}")

    try:
        # First, just get the ID of the latest track without downloading
        print("Checking for the latest track's ID...")
        result = subprocess.run(
            ['yt-dlp', '--print', 'id', '--playlist-end', '1', user_url],
            capture_output=True, text=True, check=True
        )
        latest_track_id = result.stdout.strip()

        if not latest_track_id:
            print("Could not retrieve track ID. Skipping.")
            continue

        print(f"Latest track ID is: {latest_track_id}")

        # Check if we've already sent this track for this artist
        if sent_tracks.get(user_url) == latest_track_id:
            print("-> No new tracks found for this artist. Skipping.")
            continue

        # If we're here, it's a new track! Download it.
        print("-> New track found! Proceeding with download...")
        BASE_FILENAME = "track"
        TRACK_FILE = f"{BASE_FILENAME}.mp3"
        INFO_FILE = f"{BASE_FILENAME}.info.json"

        # Clean up old files before the new download
        if os.path.exists(TRACK_FILE): os.remove(TRACK_FILE)
        if os.path.exists(INFO_FILE): os.remove(INFO_FILE)

        # The full download command
        download_command = [
            "yt-dlp", "--quiet", "--no-warnings", "-f", "bestaudio",
            "--extract-audio", "--audio-format", "mp3",
            "--output", f"{BASE_FILENAME}.%(ext)s",
            "--embed-thumbnail", "--write-info-json",
            # Important: Use the specific track URL to ensure we get the right one
            f"https://soundcloud.com/none/s-{latest_track_id}"
        ]
        subprocess.run(download_command, check=True)
        print("Download complete.")

        # Send to Telegram
        if os.path.exists(TRACK_FILE) and os.path.exists(INFO_FILE):
            with open(INFO_FILE, 'r') as f:
                track_info = json.load(f)

            track_title = track_info.get('title', 'N/A')
            track_artist = track_info.get('uploader', 'N/A')

            print(f"Sending '{track_title}' by '{track_artist}' to Telegram...")
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
            files = {'audio': open(TRACK_FILE, 'rb')}
            data = {'chat_id': CHAT_ID, 'caption': f"From: {track_artist}",
                    'title': track_title, 'performer': track_artist}
            response = requests.post(url, files=files, data=data)

            if response.status_code == 200:
                print("Audio sent successfully! Updating memory...")
                # Update the memory with the new track ID for this user
                sent_tracks[user_url] = latest_track_id
            else:
                print(f"Failed to send audio. Not updating memory. Response: {response.text}")

        # Clean up downloaded files
        if os.path.exists(TRACK_FILE): os.remove(TRACK_FILE)
        if os.path.exists(INFO_FILE): os.remove(INFO_FILE)

    except subprocess.CalledProcessError as e:
        print(f"-> Error processing {user_url}. Moving to the next link.")
        continue

    print("Waiting 5 seconds...")
    time.sleep(5)

# After checking all links, save the updated memory back to the file
with open(STATE_FILE, 'w') as f:
    json.dump(sent_tracks, f, indent=4)
print("-" * 40)
print("Process finished. Sent tracks log has been updated.")
