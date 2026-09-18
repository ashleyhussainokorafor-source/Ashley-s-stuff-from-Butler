#!/usr/bin/env python3
"""OpenRouter credit-balance watchdog for Hermes cron (no_agent).

Loads OPENROUTER_API_KEY from /data/.env, hits the /credits endpoint,
and prints a human alert ONLY when remaining balance drops below a
threshold. Healthy balance -> empty stdout -> cron sends nothing
(watchdog pattern). This monitor consumes zero LLM tokens.
"""
import json
import os
import urllib.request

ENV_PATH = "/data/.env"
WARN = 10.0   # first heads-up
CRIT = 5.0    # urgent
EMPTY = 2.0   # effectively out, fallback imminent


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> None:
    key = load_key()
    if not key:
        print("⚠️ OpenRouter monitor: OPENROUTER_API_KEY not found in /data/.env")
        return
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)["data"]
    except Exception as e:
        print(f"⚠️ OpenRouter credit check failed: {e}")
        return

    total = float(data.get("total_credits", 0))
    used = float(data.get("total_usage", 0))
    remaining = total - used

    if remaining <= EMPTY:
        print(
            f"🚨 CRITICAL — OpenRouter credits essentially out: ${remaining:.2f} left "
            f"(used ${used:.2f} of ${total:.2f}). "
            f"Hermes will switch to the free fallback model (gemma-4-31b-it:free). "
            f"Top up NOW to stay on DeepSeek V4.1.\n"
            f"→ openrouter.ai/settings/credits"
        )
    elif remaining <= CRIT:
        print(
            f"🚨 URGENT — OpenRouter credits running low: ${remaining:.2f} left "
            f"(used ${used:.2f} of ${total:.2f}). "
            f"Top up soon or you'll drop to the free fallback.\n"
            f"→ openrouter.ai/settings/credits"
        )
    elif remaining <= WARN:
        print(
            f"⚠️ OpenRouter balance low: ${remaining:.2f} left "
            f"(used ${used:.2f} of ${total:.2f}). "
            f"Consider topping up.\n→ openrouter.ai/settings/credits"
        )
    # else: healthy, print nothing (watchdog)


if __name__ == "__main__":
    main()