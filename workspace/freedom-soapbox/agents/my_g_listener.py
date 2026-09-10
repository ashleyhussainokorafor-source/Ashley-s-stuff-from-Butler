#!/usr/bin/env python3
"""
my_G Listener — Lightweight Telegram bot listener for @my_G_agentbot

Features:
- Long-polling for commands
- /start, /status, /backup, /help
- Respects system overload state
- Can trigger storage backups on demand
- Stores chat_id for proactive notifications

Run:
    PYTHONPATH=/data/workspace python agents/my_g_listener.py

Or in background:
    nohup python agents/my_g_listener.py > logs/my_g_listener.log 2>&1 &
"""

import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = Path("/data/workspace")
STATE_FILE = PROJECT_ROOT / "system_state.json"
CHAT_ID_FILE = PROJECT_ROOT / "logs" / "my_g_chat_id.json"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def load_token():
    env_file = PROJECT_ROOT / "bots" / "my_g.env"
    if env_file.exists():
        load_dotenv(env_file)
        return os.getenv("TELEGRAM_BOT_TOKEN")
    return None

def get_chat_id():
    if CHAT_ID_FILE.exists():
        try:
            with open(CHAT_ID_FILE) as f:
                return json.load(f).get("chat_id")
        except Exception:
            pass
    return None

def save_chat_id(chat_id):
    CHAT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_ID_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "saved_at": datetime.now().isoformat()}, f)

def is_overloaded():
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f).get("overloaded", False)
    except Exception:
        pass
    return False

def get_disk_usage():
    try:
        import shutil
        total, used, free = shutil.disk_usage("/data")
        return round((used / total) * 100, 1)
    except Exception:
        return 0.0

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception:
        pass

def handle_update(token, update):
    msg = update.get("message", {})
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    text = msg.get("text", "").strip().lower()

    if not chat_id or not text:
        return

    # Save chat_id on first message
    if get_chat_id() != chat_id:
        save_chat_id(chat_id)

    if text.startswith("/start"):
        send_message(token, chat_id, "✅ my_G is now connected.\n\nCommands:\n/status - system health\n/backup - trigger cloud backup\n/help - this message")

    elif text.startswith("/status"):
        load = "OVERLOADED" if is_overloaded() else "OK"
        disk = get_disk_usage()
        send_message(token, chat_id, f"📊 Status\nDisk: {disk}%\nLoad: {load}\nTime: {datetime.now().strftime('%H:%M')}")

    elif text.startswith("/backup"):
        if is_overloaded():
            send_message(token, chat_id, "⛔ System overloaded — backup skipped")
        else:
            send_message(token, chat_id, "☁️ Starting backup to Google Drive...")
            # Trigger backup script (dry-run first for safety)
            import subprocess
            result = subprocess.run(
                ["python", str(PROJECT_ROOT / "agents" / "backup_to_cloud.py"), "--dry-run"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                send_message(token, chat_id, "✅ Dry-run complete. Run without --dry-run to upload.")
            else:
                send_message(token, chat_id, f"❌ Backup error: {result.stderr[:200]}")

    elif text.startswith("/help"):
        send_message(token, chat_id, "Commands:\n/status\n/backup\n/help")

def main():
    token = load_token()
    if not token:
        print("ERROR: No token in bots/my_g.env")
        return

    print("my_G listener started")
    offset = None

    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"

            r = requests.get(url, timeout=35)
            data = r.json()

            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    handle_update(token, update)

        except Exception as e:
            print(f"Listener error: {e}")
            time.sleep(5)

        time.sleep(1)

if __name__ == "__main__":
    main()
