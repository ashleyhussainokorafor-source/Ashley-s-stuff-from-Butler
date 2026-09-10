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

### The offer ladder (both offers confirmed — phased)

| Offer | Price | Live by | Year-1 revenue |
|---|---|---|---|
| **A — Done-With-You Application Package** (1:1) | $1,995 (founding $1,495) | **1–2 weeks** | ~$19,950 |
| **B — 8-Week Group "Career Launch" Cohort** | $997 (early-bird $797) | Jan 2027 | ~$34,895 |
| **C — Employer/University Sponsored Cohort** (B2B) | $4,000–5,000 | Month 9+ | ~$4,500 |

**Base case: ~$59,345 over 12 months** on top of existing subscriptions. Conservative $26,925 · Optimistic $81,795.

**Launch order — A first, B second (≈90 days later), C last:**

- **A goes first because it costs almost nothing to build** — it repackages the resume playbook and interview coach that already exist. Highest revenue per hour (~$200–250/hr of Ashley's time).
- **The timing is a buying window:** MHA/MPH applications are due Dec–Feb; administrative fellowships recruit Sep–Nov. Right now.
- **Critically, A produces the student success stories she currently lacks** — and those testimonials are exactly what make a $997 cohort sell out and a $5,000 sponsorship credible.
- **B is the strategic flagship, not the opener** — it's the only offer that scales beyond her calendar (one-to-many, ~2.5 hrs/seat), and ACHE selling out a $1,099 equivalent proves this buyer pays $1,000+. But it needs 40–60 hours of construction, so rushing it risks an empty first cohort.

Pricing benchmarks: ACHE $1,099/$1,249 · Accepted.com $3,400–$4,500 packages and $407–420/hr · BeMo $3,997–$11,097. The $1,995 price is a deliberate value wedge *under* Accepted, not a premium.

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
