#!/usr/bin/env python3
"""
Phi Alpha — Conversational Hermes via Telegram (@phi_alpha_bot)

Full natural language access to the workspace.
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
CHAT_HISTORY_DIR = PROJECT_ROOT / "logs" / "phi_alpha_chats"
CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "x-ai/grok-4"

def load_keys():
    load_dotenv(PROJECT_ROOT / "bots" / "phi_alpha.env")
    return os.getenv("TELEGRAM_BOT_TOKEN")

def get_context():
    ctx = []
    try:
        import shutil
        total, used, _ = shutil.disk_usage("/data")
        ctx.append(f"Disk: {round((used/total)*100,1)}% used")
    except Exception:
        pass
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                st = json.load(f)
            ctx.append(f"Load: {'OVERLOADED' if st.get('overloaded') else 'OK'}")
    except Exception:
        pass
    ctx.append(f"Time: {datetime.now().strftime('%H:%M UTC')}")
    return "\n".join(ctx)

def load_history(chat_id):
    f = CHAT_HISTORY_DIR / f"{chat_id}.jsonl"
    if not f.exists():
        return []
    msgs = []
    with open(f) as fh:
        for line in fh:
            try:
                msgs.append(json.loads(line))
            except Exception:
                pass
    return msgs[-12:]

def save_turn(chat_id, role, content):
    f = CHAT_HISTORY_DIR / f"{chat_id}.jsonl"
    with open(f, "a") as fh:
        fh.write(json.dumps({"role": role, "content": content, "ts": datetime.now().isoformat()}) + "\n")

def call_llm(key, messages):
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 900}
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=50)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"[LLM error {r.status_code}]"
    except Exception as e:
        return f"[LLM exception] {e}"

def send_msg(token, chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": text}, timeout=15)
    except Exception:
        pass

def handle(token, or_key, chat_id, text):
    system = f"You are Hermes. Context:\n{get_context()}"
    history = load_history(chat_id)
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": text})

    reply = call_llm(or_key, msgs)
    save_turn(chat_id, "user", text)
    save_turn(chat_id, "assistant", reply)
    send_msg(token, chat_id, reply)

def main():
    tg_token = load_keys()
    load_dotenv(PROJECT_ROOT / "afroviolin" / ".env")
    or_key = os.getenv("OPENROUTER_API_KEY")

    if not tg_token or not or_key:
        print("Missing tokens")
        return

    print("Phi Alpha bot started (@phi_alpha_bot)")
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            r = requests.get(url, timeout=35)
            data = r.json()
            if data.get("ok"):
                for u in data.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    if chat_id and text:
                        handle(tg_token, or_key, chat_id, text)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(3)
        time.sleep(1)

if __name__ == "__main__":
    main()
