# Workspace Progress Tracker

**Last Updated:** September 18, 2026
**Status:** HCA Daily is the active priority
**Repo:** Ashley's Workspace (`ashleyhussainokorafor-source/Ashley-s-stuff-from-Butler`)

---

## ⚠️ READ FIRST: multiple agents work this workspace at the same time

Several agents run on this machine and share the same `/data` filesystem. On 2026-09-18
two of them edited the same HCA Daily files within seconds of each other. It merged, but
by luck rather than design — one bad write takes down a live paid product.

**Three rules, no exceptions:**

1. **Before editing anything under `business/hca-daily/`, read
   `business/hca-daily/ops/COORDINATION.md` and claim a lane.** One lane, one owner.
   If your lane is claimed by someone active, stop and tell the user instead of racing.
2. **Verify against the live system, never a script's own log.** A script once printed
   both "✅ PUBLISHED" and `privacyStatus=unlisted` about the same video.
3. **Push your work, or no other agent can see it.** Unpushed local work is invisible.
   The old local `main` cannot be pushed (it contains an OpenRouter key at
   `profiles/bolt/state.db` in commit `7de1bbd`; push protection refuses it). Rebuild on
   `origin/main` using the worktree recipe in `COORDINATION.md`.

---

## Current focus: HCA Daily (revenue first)

Healthcare-administration career products by Dr. Ashley Hussain-Okorafor, DBA.
Goal: **profitability this month.** Fully automated, minimal owner intervention.

**Product:** a daily-practice app at `thehcadaily.com` (scorecard → 17-unit path →
drills → league → AI Navigator / Coach).

**Tiers (verified live in Stripe):**
- Free — scorecard + playbook (lead magnets)
- Interview Answer Vault — **$27 one-time**
- Career Accelerator — **$297 one-time**
- Career Navigator — **$29/mo or $199/yr (recurring subscription)**
- Interview Coach — $19 single / $49 3-pack

**Traffic asset:** YouTube `@professorashley` — 6,190 subs, 250 videos, 644,539 lifetime
views, but dormant (3 uploads since Aug 1). Shorts are the only working discovery engine.

**Verified working as of 2026-09-18 19:15 UTC:**
- Free pages all 200; paid PDFs gated (raw paths 403)
- Navigator + Coach gated; all 8 entry paths return 402
- Shorts auto-publish ON — `business/hca-daily/shorts/queue.json` (`auto_publish: true` is
  Ashley's **standing approval** for faceless automated Shorts)

---

## Other projects

### Personal: China Relocation, Health & Community
- **Relocation (deadline Jan 1):** Batches 1 & 2 transmitted (8 coastal universities).
- **Vital Health:** tracker at `personal/health-vital/health_tracker.md`.
- **Relationships:** `personal/relationships/relationship_map.md`.

### Business: Freedom Soapbox Records (FS Records)
Logged, not started. Artist account: NVA FRQCY.

### Personal Social Media
Placeholder.

---

## Infrastructure

- **3 Gmail accounts** connected (main, family, business)
- **Cloudflare R2** — `hca-daily-assets`, `fs-records`; `storage_guard.py` active
- **Cloudflare Worker** `hca-daily` serves the site (deploy from `business/hca-daily/worker`)
- **Model routing** — DeepSeek primary, Gemini Flash auxiliary vision
- **Cron** — drip engine, YouTube CTA upgrade, first-sale alert, ops watchdog,
  Shorts publisher (2h), Shorts factory (daily 2pm)

---

## Blocked / waiting on owner

- API keys for additional tools (when needed)
- Content topics for the Shorts engine once the current pack runs dry

---

## Notes

- One repo holds all projects (personal + business).
- Execution requires explicit CEO approval before starting.
- Goal: maximum automation with minimal owner intervention.
- **HCA Daily work belongs in the HCA Daily chat.** That is where the owner coordinates it.