#!/usr/bin/env python3
"""
my_G Conversational DEBUG — Verbose version to find why messages are silent
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
CHAT_HISTORY_DIR = PROJECT_ROOT / "logs" / "my_g_chats"
LOG_DIR = PROJECT_ROOT / "logs"
CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("MY_G_MODEL", "x-ai/grok-4")

DEBUG_LOG = LOG_DIR / "my_g_debug.log"

def dlog(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_keys():
    dlog("Loading keys...")
    # Try afroviolin/.env first (has both tokens)
    env1 = PROJECT_ROOT / "afroviolin" / ".env"
    if env1.exists():
        load_dotenv(env1)
        dlog(f"Loaded from {env1}")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    or_key = os.getenv("OPENROUTER_API_KEY")
    dlog(f"TELEGRAM_BOT_TOKEN present: {bool(tg_token)}")
    dlog(f"OPENROUTER_API_KEY present: {bool(or_key)}")
    return tg_token, or_key

def get_system_context():
    ctx = []
    try:
        import shutil
        total, used, free = shutil.disk_usage("/data")
        disk_pct = round((used / total) * 100, 1)
        ctx.append(f"Disk: {disk_pct}% used")
    except Exception as e:
        ctx.append(f"Disk error: {e}")
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                st = json.load(f)
            ctx.append(f"Load state: {'OVERLOADED' if st.get('overloaded') else 'OK'}")
    except Exception as e:
        ctx.append(f"State error: {e}")
    ctx.append(f"Time: {datetime.now().strftime('%H:%M UTC')}")
    return "\n".join(ctx)

def load_history(chat_id):
    hist_file = CHAT_HISTORY_DIR / f"{chat_id}.jsonl"
    if not hist_file.exists():
        return []
    msgs = []
    with open(hist_file) as f:
        for line in f:
            try:
                msgs.append(json.loads(line))
            except Exception:
                pass
    return msgs[-10:]

def save_turn(chat_id, role, content):
    hist_file = CHAT_HISTORY_DIR / f"{chat_id}.jsonl"
    with open(hist_file, "a") as f:
        f.write(json.dumps({"role": role, "content": content, "ts": datetime.now().isoformat()}) + "\n")

def call_llm(openrouter_key, messages):
    dlog("Calling OpenRouter...")
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 800,
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=45)
        dlog(f"OpenRouter status: {r.status_code}")
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            dlog(f"LLM reply length: {len(reply)}")
            return reply
        else:
            err = f"[LLM {r.status_code}] {r.text[:300]}"
            dlog(err)
            return err
    except Exception as e:
        dlog(f"LLM exception: {e}")
        return f"[LLM exception] {e}"

def send_telegram(token, chat_id, text):
    dlog(f"Sending to chat {chat_id}...")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
        dlog(f"Telegram send status: {r.status_code}")
        if r.status_code != 200:
            dlog(f"Telegram error body: {r.text[:200]}")
    except Exception as e:
        dlog(f"send_telegram exception: {e}")

def handle_message(token, or_key, chat_id, user_text):
    dlog(f"Handling message from {chat_id}: {user_text[:50]}...")
    system_prompt = f"""You are Hermes, the user's intelligent agent.
Current context:
{get_system_context()}"""
    history = load_history(chat_id)
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_text})

    reply = call_llm(or_key, messages)
    save_turn(chat_id, "user", user_text)
    save_turn(chat_id, "assistant", reply)
    send_telegram(token, chat_id, reply)
    dlog("Message handled.")

def main():
    tg_token, or_key = load_keys()
    if not tg_token or not or_key:
        dlog("FATAL: Missing tokens")
        return

    dlog("my_G DEBUG listener started")
    offset = None

    while True:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/getUpdates?timeout=25"
            if offset:
                url += f"&offset={offset}"
            r = requests.get(url, timeout=30)
            data = r.json()
            if data.get("ok"):
                updates = data.get("result", [])
                if updates:
                    dlog(f"Received {len(updates)} update(s)")
                for update in updates:
                    offset = update["update_id"] + 1
                    msg = update.get("message") or update.get("edited_message")
                    if msg:
                        chat_id = msg.get("chat", {}).get("id")
                        text = msg.get("text", "")
                        if chat_id and text:
                            handle_message(tg_token, or_key, chat_id, text)
        except Exception as e:
            dlog(f"Loop error: {e}")
            time.sleep(3)
        time.sleep(1)

if __name__ == "__main__":
    main()
