# HCA Daily — Agent Coordination Board

**READ THIS BEFORE YOU EDIT ANYTHING UNDER `business/hca-daily/`.**

Multiple agents work this project on the same filesystem. On 2026-09-18 two agents
edited `worker/src/index.ts`, `navigator.html` and `coach.html` within seconds of each
other. It happened to merge cleanly — that was luck. One bad write and a paid product
goes down.

---

## The rule

**One lane, one owner, at a time.** Before you touch a file: check the table, claim your
lane by writing a row, do the work, then release it. If your lane is claimed by someone
active (claimed within the last 60 minutes), **stop and tell the user** — do not edit.

---

## Lanes

| # | Lane | Files you own in this lane |
|---|---|---|
| 1 | **Worker / backend** | `worker/src/index.ts`, `worker/wrangler.jsonc`, anything you then `wrangler deploy` |
| 2 | **Site UI / assets** | `worker/assets/*.html`, `worker/assets/md.js`, CSS |
| 3 | **Content** | `content/**`, `research/**` |
| 4 | **Shorts pipeline** | `automation/scripts/hca_short_*.py`, `shorts/queue.json`, `content/shorts_scripts.json` |
| 5 | **Payments / Stripe** | Stripe API changes, `live_stripe_production_links.json` |
| 6 | **Ops / cron** | `profiles/hcadaily/scripts/**`, cron job registration |

Lane 4 reads `content/shorts_scripts.json` (lane 3) — that is a **read**, not an edit.
Adding a script to the pack is lane 3. Building/queueing the video is lane 4.

---

## Active claims

*(Format: lane | agent | claimed at UTC | what you are doing | status)*

| Lane | Agent | Claimed (UTC) | Doing | Status |
|---|---|---|---|---|
| — | — | — | *nothing currently claimed* | — |

---

## Live state (keep this current — it is what other agents trust)

**Last verified:** 2026-09-18 19:15 UTC by the hcadaily chat session

**Live and verified working:**
- Site `thehcadaily.com` — all free pages 200
- Paid PDFs gated by HMAC token; raw paths `/vault.pdf`, `/accelerator.pdf` → 403
- Navigator + Coach gated behind a 30-day access cookie; **all 8 entry paths → 402**
  (`/navigator`, `/navigator.html`, `/app`, `/chat`, `/coach`, `/coach.html`,
  `/interview`, `/simulator`)
- Navigator is a **recurring subscription** in Stripe ($29/mo, $199/yr)
- Shorts auto-publish is ON (`shorts/queue.json` → `auto_publish: true`, Ashley's
  standing approval for faceless Shorts). short001/002 live; 003–006 scheduled daily.

**Known-good facts worth not rediscovering:**
- Stripe restricted key is **valid** (`/data/.stripe.env`), live mode, no `balance_read`.
- `ENTITLED_PRICES` in `worker/src/index.ts` maps product → allowed Stripe price ids.
  A product **missing from that map can never be purchased-and-unlocked**.
- Payment links must redirect with `?session_id={CHECKOUT_SESSION_ID}`.
- YouTube `videos().list` is **eventually consistent** after an update — poll, never
  trust the first read (it once made a publisher report "unlisted" for a live video).

---

## Hard rules learned the expensive way

1. **Gate the raw path, not just the friendly URL.** `/coach` was gated but
   `/coach.html` served the whole paid app for free. Same mistake as `/vault.pdf`.
2. **Escape before you format.** Navigator/Coach injected chat into `innerHTML`
   unescaped — an XSS hole on a site taking payments.
3. **Verify against the live system, never the script's own log.** "✅ PUBLISHED" and
   `privacyStatus=unlisted` were printed by the same script about the same video.
4. **Push your work.** Unpushed local work is invisible to every other agent. See the
   Git section below.

---

## Git: how work becomes shared

Repo: `ashleyhussainokorafor-source/Ashley-s-stuff-from-Butler` (PUBLIC).

**The old local `main` is un-pushable.** Commit `7de1bbd` contains a live OpenRouter API
key at `profiles/bolt/state.db:11698`, and GitHub push protection correctly refuses the
whole ref. Do not try to push that history, and do not "unblock" the secret.

To publish work, rebuild it on top of `origin/main`:

```bash
cd /data
git config credential.helper "store --file=/data/.git-credentials"
git fetch origin
git worktree add /tmp/wt origin/main
cd /tmp/wt
git checkout <your-commit> -- .gitignore automation business scripts
git add -A && git commit -m "..."
git push origin HEAD:main
```

`profiles/` is gitignored on purpose — **never publish agent profile data.** It carries
secrets and state that belong to one bot only.

---

## If you find another agent mid-edit

Do not race it. Either switch to a lane nobody holds, or write your finding to this file
and tell the user. A blocked agent that explains itself is worth far more than two agents
overwriting each other's work.