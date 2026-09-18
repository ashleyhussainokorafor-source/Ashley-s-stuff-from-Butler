# FS Records / HCA Daily — Multi-Bot Architecture

Each project runs as its own **Hermes profile** = its own Telegram bot, memory, skills, sessions, and cron. Fully compartmentalized.

| Bot | Username | Profile | Purpose | Gateway |
|---|---|---|---|---|
| **Butler** | @Thaadeus_bot | `default` | Master / CEO — situation room, cross-project | running (PID 35) |
| **HCA Daily** | @The_HCA_daily_bot | `hcadaily` | Career business (product, funnel, revenue, YouTube) | running |
| **FS Records** | @FD_RECORDS_bot | `fsrecords` | Music + content empire (7 artist brands) | running |
| **Family** | @FS_FAMILY_MANAGER_bot | `family` | Personal CRM, health, household, relocation | running |
| **Book** | @GHOSTWRITERFORASHLEY_bot | `book` | The writing / publishing project | running |

## How it works
- Profiles live at `/data/profiles/<name>/` (own `.env`, `config.yaml`, `skills/`, `memories/`, `cron/`).
- Each profile's `.env` holds its own `TELEGRAM_BOT_TOKEN`.
- Each profile runs its own gateway process: `hermes --profile <name> gateway run`.
- Created with `hermes profile create <name> --clone` (inherits model + skills from default).

## To add a new project bot
1. @BotFather → `/newbot` → name + username → copy token
2. `hermes profile create <name> --clone --description "..."`
3. Put the token in `/data/profiles/<name>/.env` as `TELEGRAM_BOT_TOKEN`
4. `hermes --profile <name> gateway run` (background)
5. Open the bot in Telegram and say hi (registers the chat)

## Notes
- Stray profiles `bolt`, `bruh` (created earlier) — to clean up.
- Models: all profiles cloned to deepseek-v4.1-flash via OpenRouter with fallbacks.

## Durability (IMPORTANT)
Profile gateways launched as children of an agent session **die when the gateway restarts**. They are kept alive by:
- `/data/scripts/gateway_supervisor.sh` — discovers every profile with a `TELEGRAM_BOT_TOKEN`, restarts any whose gateway is missing (uses `setsid` so the process detaches and survives).
- Cron job `61b4f2584d65` — runs the supervisor every 3 minutes. Silent when healthy (watchdog pattern); prints only when it restarts something.

If a bot goes silent, run `bash /data/scripts/gateway_supervisor.sh` and check that profile's `logs/gateway.log`.
