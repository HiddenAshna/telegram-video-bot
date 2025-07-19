import requests
import subprocess
import os
import json
import time # Import the time module to add delays

# --- GET DETAILS FROM GITHUB SECRETS ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- PASTE YOUR LIST OF LINKS HERE ---
# Add all your SoundCloud user links inside the square brackets, separated by commas.
# Make sure each link is in "quotes".
SOUNDCLOUD_URLS = [
    "https://soundcloud.com/winterwidoww",
    "https://soundcloud.com/xosri",
    # Add up to 50 links here...
    # "https://soundcloud.com/another-artist",
    # "https://soundcloud.com/a-third-artist",
]

# --- SCRIPT LOGIC (No need to edit below this line) ---

print(f"Starting process for {len(SOUNDCLOUD_URLS)} SoundCloud links.")

# Loop through each URL in your list
for i, user_url in enumerate(SOUNDCLOUD_URLS):
    # The 'enumerate' function gives us a counter (i) for our logs
    print("-" * 40)
    print(f"Processing link {i+1}/{len(SOUNDCLOUD_URLS)}: {user_url}")

    BASE_FILENAME = "track"
    TRACK_FILE = f"{BASE_FILENAME}.mp3"
    INFO_FILE = f"{BASE_FILENAME}.info.json"
    
    # Define the download command
    command = [
        "yt-dlp", "--quiet", "--no-warnings", "-f", "bestaudio",
        "--extract-audio", "--audio-format", "mp3",
        "--output", f"{BASE_FILENAME}.%(ext)s",
        "--embed-thumbnail", "--write-info-json",
        "--playlist-end", "1", user_url
    ]

    # This 'try...except' block will handle errors for a single link
    try:
        # Clean up files from the previous loop iteration
        if os.path.exists(TRACK_FILE): os.remove(TRACK_FILE)
        if os.path.exists(INFO_FILE): os.remove(INFO_FILE)

        print("Downloading latest track...")
        subprocess.run(command, check=True)
        print("Download complete.")

        # Send the track to Telegram if the download was successful
        if os.path.exists(TRACK_FILE) and os.path.exists(INFO_FILE):
            with open(INFO_FILE, 'r') as f:
                track_info = json.load(f)

            track_title = track_info.get('title', 'N/A')
            track_artist = track_info.get('uploader', 'N/A')

            print(f"Sending '{track_title}' by '{track_artist}' to Telegram...")
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
            files = {'audio': open(TRACK_FILE, 'rb')}
            data = {
                'chat_id': CHAT_ID, 'caption': f"From: {track_artist}",
                'title': track_title, 'performer': track_artist
            }

            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print("Audio sent successfully!")
            else:
                print(f"Failed to send audio. Response: {response.text}")
        else:
            print("Could not find downloaded file.")

    except subprocess.CalledProcessError as e:
        # If a download fails, print an error and continue to the next link
        print(f"-> Could not process {user_url}. Moving to the next link.")
        continue # This tells the loop to go to the next URL
    
    # Wait for 5 seconds before starting the next download to be respectful to SoundCloud's servers
    print("Waiting 5 seconds...")
    time.sleep(5)

print("-" * 40)
print("Process finished for all links.")
