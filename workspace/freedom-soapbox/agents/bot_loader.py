#!/usr/bin/env python3
"""
Shared bot loader for Ashley's multi-agent setup.
Each side hustle / agent has its own .env file in /data/workspace/bots/

Usage:
    from agents.bot_loader import load_bot

    env = load_bot("bolt")           # loads bots/bolt.env
    env = load_bot("hca_daily")      # loads bots/hca_daily.env
    env = load_bot("freedom_soapbox")

    token = env["TELEGRAM_BOT_TOKEN"]
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BOTS_DIR = Path("/data/workspace/bots")


def load_bot(agent_name: str) -> dict:
    """
    Load environment variables for a specific agent/bot.

    Returns a dict of the loaded variables (also sets os.environ).
    """
    env_file = BOTS_DIR / f"{agent_name}.env"

    if not env_file.exists():
        raise FileNotFoundError(f"Bot env file not found: {env_file}")

    # Load into a clean dict without polluting global env too much
    load_dotenv(env_file, override=True)

    # Return the relevant keys
    keys = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_BOT_USERNAME",
        "AGENT_NAME",
        "AGENT_ROLE",
        "OWNER",
    ]
    return {k: os.getenv(k) for k in keys if os.getenv(k)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agents/bot_loader.py <agent_name>")
        print("Available agents: bolt, hca_daily, freedom_soapbox")
        sys.exit(1)

    agent = sys.argv[1]
    try:
        env = load_bot(agent)
        print(f"✅ Loaded bot for: {agent}")
        for k, v in env.items():
            if "TOKEN" in k:
                print(f"   {k}: {v[:12]}... (hidden)")
            else:
                print(f"   {k}: {v}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
