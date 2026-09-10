# Ashley's Multi-Agent Telegram Bot Setup

Ashley owns this workspace. Her personal agent is **Bolt** (CEO).  
She runs multiple side hustles, each needing its own dedicated Telegram bot.

## Current Bots

| Agent / Side Hustle          | Env File                  | Bot Username       | Role                              | Status      |
|-----------------------------|---------------------------|--------------------|-----------------------------------|-------------|
| Bolt (Personal CEO)         | `bots/bolt.env`           | @Agent_boltbot     | Personal life + side hustle oversight | ✅ Active   |
| HCA Daily                   | `bots/hca_daily.env`      | (to be created)    | Health Admin Career Education     | ⏳ Pending  |
| Freedom Soapbox Records     | `bots/freedom_soapbox.env`| (to be created)    | Music Production & Releases       | ⏳ Pending  |

## How to Add a New Bot

1. Create a new bot with [@BotFather](https://t.me/botfather)
2. Copy the token
3. Create `/data/workspace/bots/<name>.env` using the template below
4. Fill in the token and details
5. Use `agents/bot_loader.py` in your scripts

### Template for new `.env`

```env
TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
TELEGRAM_BOT_USERNAME=@YourBotUsername
AGENT_NAME=Your Agent Name
AGENT_ROLE=What this agent does
OWNER=Ashley
```

## Usage in Code

```python
from agents.bot_loader import load_bot

env = load_bot("bolt")                    # or "hca_daily", "freedom_soapbox"
token = env["TELEGRAM_BOT_TOKEN"]
bot_username = env["TELEGRAM_BOT_USERNAME"]
```

## Security Notes

- All `.env` files are gitignored
- Never commit real tokens
- Each agent should only have the tokens it needs
- Use the shared `load_guard.py` to prevent system overload when bots trigger heavy work

## Next Steps

1. Create new Telegram bots for HCA Daily and Freedom Soapbox
2. Add their tokens to the respective `.env` files
3. Wire the bots into their project scripts using `bot_loader.py`
4. Optionally add notification hooks from `load_guard.py` to Bolt's bot for system health alerts
