#!/usr/bin/env python3
"""
notify_telegram.py — Send alerts via Telegram bot.

Usage:
    python agents/notify_telegram.py "message text here"

Bot token is read from:
- bots/my_g.env (preferred for Afroviolin/storage alerts)
- or afroviolin/.env as fallback
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path("/data/workspace")

def load_token():
    # Try my_g.env first (new personal bot)
    env_file = PROJECT_ROOT / "bots" / "my_g.env"
    if env_file.exists():
        load_dotenv(env_file)
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            return token

    # Fallback to afroviolin/.env
    env_file = PROJECT_ROOT / "afroviolin" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            return token

    return None


def send_message(text: str, chat_id: str = None):
    token = load_token()
    if not token:
        print("ERROR: No TELEGRAM_BOT_TOKEN found in bots/my_g.env or afroviolin/.env")
        return False

    # Default to the bot owner (you) — replace with your chat_id if needed
    if chat_id is None:
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("Telegram message sent")
            return True
        else:
            print(f"Telegram error: {r.text}")
            return False
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: notify_telegram.py 'message text'")
        sys.exit(1)
    send_message(" ".join(sys.argv[1:]))
