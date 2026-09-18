# HCA Daily — Ops: how we find and fix problems fast

Everything here is automated. You should never have to go looking for a problem —
the system tells you. This file is the map for when it does.

## What runs on its own

| Every | What | Where the evidence lives |
|---|---|---|
| 30 min | **Ops watchdog** — site up, paid files still locked, both Stripe links still active, drip alive, lead count | `ops/OPS_LOG.md`, snapshot in `ops/status.json` |
| 2 h | **Email drip** — Day 0/1/3/5/7/9 follow-ups to every scorecard lead | `email/drip_state.json` |
| 3 h | **Stripe sale watcher** — alerts the second a payment lands | `automation/state/stripe_watch_state.json` |
| 3 AM daily | **YouTube CTA finish** — remaining video descriptions (quota-capped at ~180/day) | `automation/scripts/yt_cta_upgrade_state.json` |
| 6 h | **Shorts publisher** — uploads whatever is due from `shorts/queue.json` (unlisted until you approve) | `shorts/queue.json` |

## How to read the log

`ops/OPS_LOG.md`, newest entries at the bottom, one line per run:

```
- 2026-09-18 17:56 UTC | OK | pages=12/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
```

- **OK** — everything measured fine. No message is sent for these.
- **FAIL** — something that costs money is broken. You get a Telegram alert.
- **UNKNOWN** — a check couldn't reach its target. Not the same as OK, and not
  silently ignored. If Stripe or Cloudflare is down, the log says so.

## The failure modes that matter, in order of how much money they cost

**1. Paywall leak — paid files downloadable by anyone**
Log says `locked /vault.pdf FAIL HTTP 200 — LEAKED`.
This means the $27 and $297 products are being given away. Fix: the HMAC gate in
`worker/src/index.ts` (`ENTITLED_PRICES`, `DOWNLOAD_SECRET`) — redeploy the worker.
Alert severity: 🔴 immediate.

**2. Checkout dead — nobody can pay**
Log says `checkout Interview Answer Vault FAIL inactive/deactivated`.
Fix: the Stripe payment link was deactivated or the price changed. Verify against
the live Stripe API, create a replacement link, then update every place the old URL
appears: `worker/assets/vault.html`, `accelerator.html`, `pricing.html`, and the
YouTube descriptions. Alert severity: 🔴 immediate.

**3. Site down or a page 404s**
Fix: `cd business/hca-daily/worker && npx wrangler deploy` (creds in `.cloudflare.env`).
Then re-run the watchdog and confirm the page count is back to 12/12.

**4. Drip stopped — leads get no follow-up**
Log says `drip FAIL state not written in 3Xh`.
Fix: run `/opt/venv/bin/python3 business/hca-daily/email/drip.py`. It needs
`/opt/venv/bin/python3`, not the system python — the system one has no google-api
libraries and dies with ModuleNotFoundError.

**5. Traffic with no leads**
Not a bug — a content problem. Check `status.json` for lead count, and
`/admin/traffic` on the site for pageviews by day. If pageviews rise but leads
don't, the free offer isn't being seen (check that the CTA is still on line 1 of
each video description).

## Ground rules

- **A check that can't measure reports UNKNOWN, never OK.** "I couldn't look" and
  "it's fine" must never be the same line in the log.
- **Alerts are rate-limited** to once per 6 hours per problem, so a standing issue
  can't flood the chat. It re-alerts only if it clears and comes back.
- **Nothing gets published publicly without an explicit go-ahead.** Shorts upload
  unlisted; `queue.json`'s `auto_publish` is `false` and stays false until Ashley
  says otherwise.
- **Verify against the live source before claiming a fix.** A green check inside a
  script is the script's opinion; re-read the live page, the live Stripe object, or
  the live video and confirm.
