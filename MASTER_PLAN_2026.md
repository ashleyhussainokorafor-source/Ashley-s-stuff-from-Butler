# HCA Daily — Master Plan
**Drafted:** September 10, 2026
**Status:** AWAITING APPROVAL — no execution until approved
**Owner:** Dr. Ashley Hussain-Okorafor

---

## The Goal

Turn HCA Daily from *documents and a good-looking website* into a **business that takes money**, without risking what already works.

Two independent businesses, side by side:

| Business | State | Real asset |
|---|---|---|
| **HCA Daily** | Site live on Wix, 4 Stripe links live, 6.17K YouTube subs | Career/education audience + academic credibility |
| **FS Records** | Afroviolin music pipeline exists (agent scripts, 18-track plan) | Production tooling for faceless music videos |

FS Records needs its **own** planning session — it has tooling but no strategy. Deliberately out of scope for this plan.

---

## What The Research Established

**The gap:** Nobody sells an AI career product that speaks healthcare administration. Generic AI tools charge **$25–90/month** (Final Round AI, Teal, Big Interview) with zero HCA content — no MHA advice, no fellowship coaching, no ACHE/FACHE context. Healthcare creators in the niche sell only cheap guides, or nothing.

**The proven pricing bands:**
- $9–39/month + $99–299 annual/lifetime → consumer AI subscriptions
- $50–450 per item, $100–450/hour → professional services
- **$1,000–11,000** → premium outcomes

| Proof point | Price | Audience |
|---|---|---|
| ACHE Career Launch Program | **$1,099** | MHA students — *our exact audience* |
| Accepted.com grad packages | **$4,365+** | MHA applicants (treated generically) |
| Big Interview Pro | $299 lifetime | Generic job seekers |
| Final Round AI | $25–90/mo | Generic job seekers |

**Ashley's current pricing ($29/mo, $199/yr, $19, $49) sits correctly in band 1 — but the ceiling is $49 while the market has proven buyers at $1,099 and $4,365.**

**Best-converting free offer:** the **free expert critique** (resume/LinkedIn review, or recorded mock interview with specific feedback). Universal across every winner studied — it demonstrates the quality gap *and* pulls the user into the product. For high-ticket, a **free 30-minute strategy call** is the standard converter.

**The domain is locked by Wix:** Wix does not permit nameserver changes on Wix-registered domains. Full migration requires transferring the registration away first (5–7 days, with real risk to email/DNSSEC if done carelessly). A **subdomain bypasses this entirely** and needs no transfer.

---

## Phase 1 — Ship The Product Publicly
**Goal:** The AI tools become reachable and payable by real customers.
**Why first:** Everything else (SEO, Telegram, email) points at a product. Without a live product there is nothing to point at.

- Rebuild the AI Navigator + Coach to run on Cloudflare (the current Python cannot — Workers need a different runtime). ~1 day for a straight port; 2–3 days including payments + logins.
- Serve at **`app.thehcadaily.com`** — one DNS record added in Wix's panel. **The existing Wix site keeps running untouched.**
- Wire the 4 live Stripe links into the product with real subscriber gating.
- Fix the naming mismatch: the site says "Roadmap Audit," Stripe says "Career Navigator" — a visitor cannot connect them.

**Risk:** Low. Nothing existing changes or goes dark.
**Cost:** $5/month.
**Needs from Ashley:** Cloudflare login (one time).

---

## Phase 2 — The Revenue Pipeline
**Goal:** A visitor can go from stranger → email → paying customer.

### The front door: The HCA Career Readiness Scorecard

**Correction to earlier advice:** I previously said the "free expert critique" was the best front door. Research refined this. The critique converts strongly *downstream* but only captures 5–15% of visitors. The **interactive diagnostic** captures **30–40%**. The winning combination:

- **The promise** = a free expert critique (what the niche expects)
- **The mechanism** = a 90-second interactive scorecard (what actually captures emails)
- **The delivery** = a one-page checklist (highest raw opt-in format, 23–42%)

The current ebook is the **worst** performing format in every dataset (0.9–8% conversion; 60–70% never opened). Retire it as the primary opt-in.

**The scorecard:** 8–10 questions, email gate *before* the result is revealed (the reveal is where capture happens). Output: a 0–100 score across 4 dimensions — Resume Metrics, Operational Vocabulary, LinkedIn/Visibility, Interview Readiness — plus a peer benchmark, the candidate's top-3 fixes, and a downloadable PDF.

**Why this is the right build:** the scorecard is a stripped-down version of the Navigator, so the free→paid jump is one click and the lead magnet doubles as a product demo. It can reuse the Navigator backend already built in Phase 1.

**Then:** a 6-email sequence (Day 0, 1, 3, 5, 7, 9) that segments by the lowest-scoring dimension and converts to the Navigator trial on Day 7.

### The offer ladder — REBUILT FOR ZERO LIVE TIME

**Design constraint (Ashley, Sept 10):** maximum automation, maximum income, no 1:1 customer calls — a 5-year-old and a 1-year-old at home. The earlier $1,995 done-with-you package required 8–10 hours of live time *per client* and is **disqualified**.

**The finding that matters:** the automated version doesn't just fit her life — **it earns more.** The 1:1 package at 6 clients grosses ~$12,000 for 55+ hours of her calendar. The same content, sold self-paced to ~95 buyers, grosses **$19,000–28,000 and keeps selling every month after**, with zero marginal time. *Low price × high volume × zero marginal time beats high price × low volume × her personal calendar.*

| Rung | Price | What it is | Zero-live? |
|---|---|---|---|
| Free Starter Kit | $0 | Lead magnet → email list | ✅ |
| **HCA Interview Answer Vault** | **$27** | 150 role-specific questions + STAR scripts + salary scripts | ✅ |
| **HCA Career Accelerator** | **$297** | 6-module self-paced course + template vault | ✅ |
| **HCA Application Accelerator** | **$497** | *Replaces the $1,995 package* — course + vault + AI Navigator + AI Coach + template pack | ✅ |
| HCA Daily Insider membership | $39/mo · $347/yr | Ongoing access, monthly drops, **pre-recorded** Q&A | ✅ |
| HCA Executive Director Track | $997 | Premium program, async AI-scored simulations | ✅ |

**Year-1 realistic: ~$50,000** (slow $24,000 · base ~$52,000 · strong ~$86,000) — all delivered by software, Stripe, and email sequences.

### Build order — and the first money is small on purpose

**Build the $27 Interview Answer Vault FIRST** (~20 hours). It sells from the first welcome email, brings cash within **2–3 weeks**, and proves the funnel before anything bigger is built. Then ship the **$297 course 30–45 days later** — that's the real revenue line (~$19,000/yr, launched 3× a year).

**Why the $497 bundle matters:** it's the productized form of the $1,995 offer. Same outcome path — resume rebuilt, application targeted, interviews scored, salary scripted — at one-quarter the price, to unlimited buyers, with no calendar slot. Offered as a one-click upgrade at checkout (order bumps convert 35–40% of the time).

### Phase 2b — Institutional licensing (capped side channel, NOT primary)

Verdict: **conditionally viable, deliberately capped.** The revenue-per-transaction is the best available — one $27,000 career-center license equals **136 annual subscribers**; 2–4 deals a year roughly doubles a several-hundred-subscriber business. Ashley is unusually well-positioned: DBA, former CSUSB lecturer, warm California higher-ed relationships, prior institutional outreach.

**The honest caveat:** this is *not* low-touch in the near term. The binding constraint is a **12–18 month approval cycle** (champion → buyer → IT security → accessibility → procurement → legal) plus FERPA/WCAG compliance gates. No automation fixes that timeline.

**How to run it as close to hands-off as possible:**
- **Best first target:** one California CAHME-accredited MHA/MPH program already in her CSUSB network.
- **Lead with a free 90-day pilot, never a demo.** Pilots with measured outcomes convert to full purchase 2.5–3× more often.
- **Engineer pricing under procurement thresholds** — $4,500–7,500 for a program, $10,000–27,000 for a career center. Crossing $25,000 triggers competitive bid, and incumbents (VMock, Handshake, Symplicity) get invited to undercut.
- **Close with an auto-generated outcome report**, not a meeting. Send report + price sheet + self-serve checkout link.
- **Cap live calls at 3–4 per year**, batched into one two-week window, signature-stage only — or hire a fractional rep at 15–20% commission.
- **The only genuinely low-touch version:** association white-label. NCAF (109 member organizations), CAHME, and state ACHE chapters earn 70–85% margins on education and are actively hunting non-dues revenue — they supply the sales team, member list, and billing.

**Stop-loss:** if no paying institution has signed within 12 months of the first pilot, or servicing exceeds 5 hours/month, exit the channel.

**The rule for this whole phase:** the bottleneck is no longer her calendar — it is **traffic**. Income = traffic × conversion × price, with no ceiling. Which is why Phase 3 stops being "marketing" and becomes the actual revenue engine.

### What to avoid
- Unlimited free 1:1 resume reviews or mock interviews — they consume the one resource that cannot scale: her time. Do it as a **monthly group session** instead (doubles as a content asset).
- Ungated "free downloads" with no email capture at the reveal.
- Discounts as the magnet — attracts deal-seekers, not buyers.

**Needs from Ashley:** nothing — decided. Launch order is set from evidence.

---

## Phase 3 — The SEO Engine
**Goal:** Own the searches your audience actually types.

Certification content is the unguarded door — current top results are thin affiliate clones with no credentials behind them. A DBA outranks them on authority alone.

**Quick wins:** CPPS (near-zero competition) · CPHQ · "is FACHE worth it" (ROI math) · MHA vs MBA (proven undecided demand).

A full 90-day, week-by-week roadmap already exists in the research (`seo_keyword_plan_report.md`).

**Tactics:** every post links up to a hub and down to a product page; mine YouTube comments weekly — every recurring "how do I become X" becomes the next post.

---

## Phase 4 — Audience & Community
**Goal:** Keep people, not just acquire them.

- **Telegram student group** + HCA Daily bot for students/customers (the bot scaffolding already exists with placeholder tokens — the bot itself was never created).
- **WhatsApp** connection (currently deferred).
- **YouTube → site → email** conversion. 6.17K subscribers is the most underused asset in this whole plan.
- Bolt stays personal; FS Records gets its own bot later.

---

## Phase 5 — Domain Migration & FS Records
**Goal:** The clean setup, once revenue justifies the risk.

- Move `thehcadaily.com` off Wix (transfer registration → Cloudflare). **Never step one** — skip a step and email or the whole domain dies.
- FS Records planning session — the Afroviolin pipeline is real and now properly housed; it needs a strategy, not just tooling.

---

## Standing Rules

1. **Verify, don't assume.** After any push, confirm against GitHub rather than trusting a green check. This rule exists because a backup silently drifted 4 days.
2. **Nothing goes dark.** Existing site stays up until a replacement is proven.
3. **Secrets never get committed.** `.gitignore` hardened; re-verified after every commit.
4. **No action without explicit approval**, phase by phase.

---

## Decisions — Resolved

- [x] **Phase 1 approved** — subdomain first, rather than full Wix replacement
- [x] **Front door decided** — interactive scorecard (with the critique as the promise), replacing the generic ebook
- [x] **High-ticket tier approved, and both offers confirmed** — A (done-with-you, $1,995) first, B (group cohort, $997) second
- [ ] **Cloudflare access** — the one remaining blocker for going live
