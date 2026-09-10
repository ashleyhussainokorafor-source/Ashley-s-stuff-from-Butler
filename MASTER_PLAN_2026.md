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

- **Front door:** free expert critique (resume/LinkedIn review or mock interview) — replaces the generic ebook as the lead magnet.
- **Add a high-ticket tier** ($500–1,500 range) — 1:1 coaching or a done-with-you application/fellowship package, sold by a **free 30-minute call**. This is where the real income is; the $49 ceiling is the single biggest revenue constraint today.
- Outcome proof: salary-offer and "got the job" testimonials, which every competitor leans on.
- Risk-reversal guarantee (30-day refund) — the standard trust mechanism in this niche.

**Needs from Ashley:** decision on what the high-ticket offer actually *is*.

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

## Decisions Needed From Ashley

- [ ] Approve Phase 1 (subdomain first, rather than full Wix replacement)
- [ ] Approve free-critique lead magnet (replacing generic ebook)
- [ ] Approve adding a high-ticket tier above $49 — and what it should be
- [ ] Cloudflare login, when Phase 1 begins
