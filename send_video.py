import requests
import subprocess
import os

# --- GET DETAILS FROM GITHUB SECRETS ---
BOT_TOKEN = os.environ.get("7592519816:AAG8_NU1A8cUw6jf0YuWnjReSRag08rpdJc")
CHAT_ID = os.environ.get("1566333943")
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@catchthedit/shorts" # Change this to your desired channel

# --- SCRIPT LOGIC (No need to edit below this line) ---

# 1. Download the latest video using yt-dlp
# The command finds the latest video from the channel's "shorts" page and downloads it.
# It saves the video with the name "video.mp4".
command = [
    "yt-dlp",
    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "--quiet",
    "--no-warnings",
    "-f", "best[ext=mp4]", # Download best quality MP4
    "--output", "video.mp4", # Save as video.mp4
    "--match-filter", "!is_live", # Ignore live streams
    "--playlist-end", "1", # Only download the very first video on the page (the latest)
    YOUTUBE_CHANNEL_URL
]

# Run the download command
try:
    # Ensure any old video is deleted first
    if os.path.exists("video.mp4"):
        os.remove("video.mp4")
    
    print("Downloading latest short video...")
    subprocess.run(command, check=True)
    print("Download complete.")
except subprocess.CalledProcessError as e:
    print(f"Error downloading video: {e}")
    exit() # Stop the script if download fails

# 2. Send the video to Telegram
if os.path.exists("video.mp4"):
    print("Sending video to Telegram...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    files = {'video': open('video.mp4', 'rb')}
    data = {'chat_id': CHAT_ID, 'caption': 'Here is your daily video!'}
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        print("Video sent successfully!")
    else:
        print(f"Failed to send video. Response: {response.text}")
        
    # 3. Clean up the downloaded file
    os.remove("video.mp4")
    print("Cleaned up video file.")
else:
    print("No video file found to send.")
