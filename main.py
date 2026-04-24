import requests
import time
import urllib3
from datetime import datetime, UTC

# ===================== CONFIGURATION =====================
BOT_TOKEN = "your_bot_token"
CHANNEL_ID = "your_channel_id"

POLL_INTERVAL = 60  # seconds

STATUS_URL = "https://status.epicgames.com/api/v2/summary.json"

# Custom images
IMAGE_UP   = "https://pbs.twimg.com/media/Gr128MzWMAASYNe?format=jpg&name=large"
IMAGE_DOWN = "https://pbs.twimg.com/media/Gr128MzWUAAHyGe?format=jpg&name=large"

# Headers
HEADERS = {
    "Authorization": f"Bot {BOT_TOKEN}",
    "User-Agent": "Fortnite-Status-Bot/1.0",
    "Content-Type": "application/json"
}

# Suppress only the InsecureRequestWarning (safe for public status page)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# =========================================================

def get_fortnite_status():
    """Fetch Fortnite status from Epic Games"""
    try:
        r = requests.get(
            STATUS_URL,
            headers={'User-Agent': 'Fortnite-Status-Bot/1.0'},
            timeout=10,
            verify=False   # Required on your system due to cert issue
        )
        r.raise_for_status()
        data = r.json()

        for component in data.get('components', []):
            if component.get('name') == 'Fortnite':
                return component.get('status', 'unknown').lower()
        return "unknown"
    except Exception as e:
        print(f"[ERROR] Failed to fetch status: {e}")
        return "error"


def send_discord_message(title, description, color, image_url):
    """Send message to Discord"""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "image": {"url": image_url},
        "timestamp": datetime.now(UTC).isoformat(),   # Fixed deprecation warning
        "footer": {"text": "Froster Bot"}
    }

    payload = {
        "username": "Sever Status Bot",
        "avatar_url": "https://www.image2url.com/r2/default/images/1776456056362-7953d0c8-0c56-43be-93aa-983e7e77ae78.png",
        "embeds": [embed]
    }

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ Message sent successfully")
        else:
            print(f"[DISCORD ERROR] {resp.status_code} - {resp.text}")
            if resp.status_code == 429:
                time.sleep(5)
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")


# ===================== MAIN LOOP =====================
print("Fortnite Server Monitor started")
print(f"Polling every {POLL_INTERVAL}s | Channel ID: {CHANNEL_ID}")

previous_status = None

while True:
    current = get_fortnite_status()

    if previous_status is None:
        # First run - initial message
        if current == "operational":
            send_discord_message(
                "Fortnite Monitor Online",
                "**Servers are currently UP** \nMonitoring started.",
                0x2ecc71,
                IMAGE_UP
            )
        else:
            send_discord_message(
                "Fortnite Monitor Online",
                f"**Current status: {current.replace('_', ' ').title()}**",
                0xe67e22,
                IMAGE_DOWN
            )
        print(f"Initial status sent: {current}")

    elif current != previous_status:
        if current == "operational":
            send_discord_message(
                "FORTNITE IS BACK ONLINE!",
                "Servers recovered",
                0x2ecc71,
                IMAGE_UP
            )
            print("UP notification sent")
        else:
            send_discord_message(
                "FORTNITE SERVERS ARE DOWN",
                f"Status → **{current.replace('_', ' ').title()}**\n\nhttps://status.epicgames.com/",
                0xe74c3c,
                IMAGE_DOWN
            )
            print(f"DOWN notification sent ({current})")

    previous_status = current
    time.sleep(POLL_INTERVAL)