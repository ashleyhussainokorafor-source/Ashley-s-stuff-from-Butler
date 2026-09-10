#!/usr/bin/env python3
"""
my_G Conversational — Full natural language Hermes agent via Telegram

Replaces the command-only listener with a real LLM-powered conversation.

- Uses OPENROUTER_API_KEY from afroviolin/.env
- Maintains per-chat history in logs/my_g_chats/
- Injects Hermes context (workspace state, guards, Afroviolin project, user prefs)
- Supports fluid back-and-forth like this webui chat
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
MODEL = os.environ.get("MY_G_MODEL", "x-ai/grok-4")  # or gemini-flash, etc.

def load_keys():
    load_dotenv(PROJECT_ROOT / "afroviolin" / ".env")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    or_key = os.getenv("OPENROUTER_API_KEY")
    return tg_token, or_key

def get_system_context():
    ctx = []
    # Disk + load
    try:
        import shutil
        total, used, free = shutil.disk_usage("/data")
        disk_pct = round((used / total) * 100, 1)
        ctx.append(f"Disk: {disk_pct}% used on /data")
    except Exception:
        pass

    # Overload state
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                st = json.load(f)
            ctx.append(f"System load state: {'OVERLOADED' if st.get('overloaded') else 'OK'}")
    except Exception:
        pass

    # Afroviolin quick status
    try:
        state_path = PROJECT_ROOT / "afroviolin" / "artifacts" / "afroviolin_state.json"
        if state_path.exists():
            with open(state_path) as f:
                af = json.load(f)
            total = af.get("pipeline_stats", {}).get("total_tracks", 18)
            published = af.get("pipeline_stats", {}).get("published", 0)
            ctx.append(f"Afroviolin: {published}/{total} tracks published")
    except Exception:
        pass

    # User identity
    ctx.append("User: Ashley (Creative Director, Afroviolin project owner)")
    ctx.append("Current date: " + datetime.now().strftime("%Y-%m-%d %H:%M UTC"))

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
    return msgs[-20:]  # last 20 turns for context

def save_turn(chat_id, role, content):
    hist_file = CHAT_HISTORY_DIR / f"{chat_id}.jsonl"
    with open(hist_file, "a") as f:
        f.write(json.dumps({"role": role, "content": content, "ts": datetime.now().isoformat()}) + "\n")

def call_llm(openrouter_key, messages):
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes-agent.nousresearch.com",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1200,
        "temperature": 0.7,
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"[LLM error {r.status_code}] {r.text[:200]}"
    except Exception as e:
        return f"[LLM exception] {e}"

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=15)
    except Exception:
        pass

def handle_message(token, or_key, chat_id, user_text):
    # Build messages
    system_prompt = f"""You are Hermes, the user's intelligent agent running on a Linux workspace.
You have full access to the workspace, Afroviolin project, storage guards, and can reason about the system state.

Current context:
{get_system_context()}

Respond naturally and helpfully. Be concise when possible. If the user asks for actions (backup, status, code changes), describe what you would do or confirm before executing heavy operations."""

    history = load_history(chat_id)
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_text})

    # Call LLM
    reply = call_llm(or_key, messages)

    # Save turns
    save_turn(chat_id, "user", user_text)
    save_turn(chat_id, "assistant", reply)

    # Send back
    send_telegram(token, chat_id, reply)

def main():
    tg_token, or_key = load_keys()
    if not tg_token or not or_key:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or OPENROUTER_API_KEY")
        return

    print("my_G conversational listener started (natural language mode)")
    offset = None

    while True:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/getUpdates?timeout=40"
            if offset:
                url += f"&offset={offset}"
            r = requests.get(url, timeout=45)
            data = r.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    if chat_id and text:
                        handle_message(tg_token, or_key, chat_id, text)
        except Exception as e:
            print(f"Listener error: {e}")
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    main()
