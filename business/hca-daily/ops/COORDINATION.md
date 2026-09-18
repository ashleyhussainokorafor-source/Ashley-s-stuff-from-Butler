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

# How we work together

Two agents share this project: **Butler** (platform lead) and the **hcadaily bot** (growth
lead). The split exists because our failure mode is not incompetence — it is two agents
independently doing the same work, or one silently undoing the other's.

## Roles

**Butler — Platform Lead.** Everything that ships and takes money:
worker code (`worker/src/index.ts`, `wrangler.jsonc`), site UI/assets, Stripe,
deploys, cron infrastructure, and cross-project repo concerns.
*Butler owns the blast radius.*

**hcadaily bot — Growth Lead.** Everything that brings people in:
audience research, content and script packs, the Shorts pipeline, YouTube comment
replies and descriptions, outreach, and landing-page copy.
*Growth owns the volume.*

## The seam, and how to cross it

Growth work must never edit worker code directly, and platform work must not rewrite
content. When you need the other side:

- **Growth needs a site/product change** → write it in the Queue below as
  `[platform]` and tell Ashley. Butler implements it.
- **Platform needs copy or content** → write it as `[growth]`. Do not write the copy
  yourself as a side quest.
- **Genuinely shared file** → take the mechanical lock (see below), change it, verify,
  release. Never both at once.

## The rhythm

1. **Claim** your lane *and* your queue item before starting.
2. **Do** the work — smallest correct change.
3. **Verify** against the live system, never against your own script's log.
4. **Publish** (`scripts/publish_to_github.sh`) so the other agent can see it.
   Unpushed work is invisible and is the root cause of duplicated work.
5. **Release** your lane and mark the queue item done.

## Definition of done

A task is done when the live system proves it, and this file says so. Not when the
script printed success. Not when the commit landed. **Verified, published, and written
down** — all three.

## Escalation — ask Ashley, do not guess

- Another agent holds your lock or lane and is active.
- The change would spend money, change a price, or alter what a customer receives.
- You disagree with the other agent's approach.
- You are about to overwrite someone's uncommitted work.

A blocked agent that explains itself beats two agents overwriting each other.

---

## Work queue — claim before you start, one owner per line

**Ashley's asks in flight.** Pull from here; do not invent parallel work.

| # | Item | Owner | Status |
|---|---|---|---|
| 1 | Reply to every YouTube comment with a relevance-matched link | growth | IN PROGRESS — engine live; 15/run every 2h (Ashley's pacing call), daily cap 120 |
| 2 | No-experience offers (products for people with zero healthcare background) | growth | **DONE** — $147 Résumé Translation live: /resume, Stripe product + link, gated intake form, order-alert cron every 30m |
| 3 | Re-engagement video for the 6,190 dormant subs | growth | NOT STARTED |
| 4 | Write the 7 research-backed Shorts scripts (pack runs dry Sept 22) | growth | **DONE** — pack extended to Sept 29; trimmed to the 20-25s retention window |
| 5 | Reach BOTH audiences: clinical (nurses/radiology/MD) and non-clinical | growth | NOT STARTED |
| 6 | Direct outreach to HCA programs/universities (this-month revenue) | growth | IN PROGRESS — **pilot 10 sent + verified** 23:12; 91 verified targets; crons live (12/day at 14:00, reply watch 4h). See `outreach/OUTREACH_PLAN.md` |
| 7 | Push to GitHub regularly; teach the house rule to all bots | both | IN PROGRESS |
| 8 | Finish the remaining ~54 video CTA upgrades | platform | AUTOMATED — runs 3am daily |
| 9 | Scorecard must offer at peak intent (it collected the email, diagnosed the gap, then sold nothing) | platform (Butler) | **DONE** — contextual offer card on `worker/assets/scorecard.html`, targets the lead's own weakest dimension, gold CTA → $27 Vault + $297 Accelerator. Verified live, deployed `2c49f4c3` |
| 10 | Drip copy + logic bugs (`email/drip.py`) | platform (Butler) | **DONE** — Email 6 corrupted sentence restored; score-of-0 no longer mistaken for "no score". Uncommitted at time of writing |
| 11 | `[platform]` **Modernise the site UI/UX for a younger audience** — real student photography on every page, rewrite the jargon hero, settle on ONE palette, real mobile nav + sticky mobile CTA, shared stylesheet. Audit + spec: `design/UI_UX_AUDIT.md` (current score **5.3/10**). Licensed image library + `CREDITS.md` land in `worker/assets/img/`. | platform | QUEUED — spec delivered 2026-09-18 |

**Blocked on Ashley:** none.

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
| 3 (Content) | hcadaily bot | 2026-09-18 19:30 | Comment-reply engine, no-experience offers, re-engagement video | ACTIVE |
| 4 (Shorts) | hcadaily bot | 2026-09-18 19:30 | Comment replies (YouTube API) + script pack expansion | ACTIVE |

**Lanes 1 (worker), 2 (UI) and 5 (payments) are FREE.** If you need them, claim them above.

**2026-09-18 23:20 UTC — Lane 2 (Site UI) worked by Butler, now RELEASED.** Changed
`worker/assets/scorecard.html` (peak-intent offer card) and deployed worker version
`2c49f4c3`. Also touched `email/drip.py` (not in the lane table — flagging rather than
assuming it's mine). Both are recorded in the queue as items #9 and #10 and in
`ops/OPS_LOG.md`. Lane 2 is free again.

**2026-09-18 23:40 UTC — Lane 2 (Site UI) CLAIMED by Butler.** Ashley asked for a
visual UI/UX audit + modernisation of the site for a younger (college / early-career)
audience, with real imagery. Scope: `worker/assets/*.html` and new image assets.
Findings so far: the site has **zero images** on any page, and the deployed CSS uses
coral `#ff5749` + amber `#f59e0b` for CTAs while the brand guide's gold `#c9a227` is
**entirely absent** (navy/teal are correct). Mobile header wraps/breaks at 390px.
Work in progress — do not edit `worker/assets/*.html` until this line says RELEASED.

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

---

## Mechanical lock (use it for production changes)

The lane table above is honour-system. For anything that ships or spends money, also take
the real lock so two agents physically cannot deploy at once:

```bash
bash /data/scripts/deploy_lock.sh acquire <scope> <your-agent-name>
bash /data/scripts/deploy_lock.sh status
bash /data/scripts/deploy_lock.sh release <scope> <your-agent-name>
```

Suggested scopes: `worker/src/index.ts`, `stripe`, `kv`, `youtube`, `cron`.

- `acquire` **exits 1** if another agent holds the scope and claimed it under 60 minutes ago.
  If that happens: stop and ask Ashley who should proceed. Do not overwrite.
- A lock older than 60 minutes is treated as abandoned (owner died) — `acquire` will warn
  and take it over. Say so out loud so the previous owner isn't surprised.
- `release` refuses if you aren't the holder.
- Locks live in `ops/locks/` and are gitignored-local; they are not a source of truth for
  anything except "someone is mid-flight right now."

**Hold the lock only for the duration of the change.** Acquire → change → verify → release.
A lock left held blocks every other agent on that scope.