# The HCA Daily — 2026 Cloudflare Hosting Architecture Decision Record

**Date:** September 9, 2026
**Constraint that drives everything:** the origin container's public egress IP rotates on every request (6 IPs in 6 checks). No stable A record is possible. Also: no systemd, no cron, no sudo.
**Domain:** `thehcadaily.com`, currently registered at **Wix**.
**Current app:** `/data/business/hca-daily/web/server.py` — 128 lines, stdlib `http.server`, 3 static HTML pages (`index.html`, `navigator.html`, `coach.html`), 2 JSON POST endpoints (`/api/chat`, `/api/coach`) calling OpenRouter `deepseek/deepseek-v4-pro-0813`. Prompts read from two local `.md` files. No DB, no build step.

---

## 1. Verdict

**Deploy a single Cloudflare Worker with static assets. Do not tunnel back to this container. Do not use an external host. Do not start a new Pages project.**

```
Browser
  │
  ├── GET /  /navigator  /coach  → Worker static assets (free, unlimited, cached at edge)
  │
  └── POST /api/chat  /api/coach → Worker (TypeScript)
                                    ├── session cookie check (HMAC, WebCrypto)
                                    ├── D1: subscribers / leads
                                    ├── Durable Object (SQLite): one per chat session
                                    └── fetch → AI Gateway → OpenRouter (DeepSeek)
      POST /api/stripe/webhook   → Worker (HMAC-SHA256 signature verify) → D1
```

The rotating egress IP becomes irrelevant because **nothing inbound ever touches this container**. The container is only a build/deploy box: `wrangler deploy` is an outbound HTTPS call, which works fine from a rotating IP.

Cloudflare's own docs now say to start new projects on Workers, not Pages: "Workers supports most Pages use cases and offers a broader feature set. It is Cloudflare's primary platform for building applications. Start new projects with Workers." — https://developers.cloudflare.com/pages/

---

## 2. Option comparison

| Option | Solves rotating IP? | Cost at low traffic | What breaks |
|---|---|---|---|
| **(b) Workers + static assets** ✅ recommended | Yes — no origin at all | $0 (free tier) or $5/mo Workers Paid | Python must be rewritten in TS/JS; 10 ms CPU cap on free plan; hard 429 stop at 100k req/day |
| (a) Pages + Pages Functions | Yes — same reason | $0; identical Workers quota | Same rewrite; Cloudflare steers new projects to Workers; 500 builds/mo; git-integration or Direct Upload adds a step you don't need |
| (c) Cloudflare Tunnel to this container | Yes — `cloudflared` makes outbound-only connections | Tunnel + Cloudflare One free plan = $0 (≤50 users) | Fragile here: no systemd/cron means nothing restarts `cloudflared` or `server.py`; container restart = site down; single point of presence, no edge caching of dynamic routes; still need D1/KV/Stripe work anyway |
| (d) Render / Railway / Fly + Cloudflare DNS | Yes — provider gives a stable hostname | Render Free web service $0 but sleeps; Render Starter $7/mo; Railway Hobby $5/mo + usage; Fly usage-based (~$2–5/mo for a shared-cpu-1x/256MB machine) | Cold starts (Render free sleeps → 30–60 s first request on an AI landing page); a second bill and a second deploy pipeline; you still need somewhere for state; Python survives unchanged (the only real upside) |

---

## 3. Port to JavaScript, don't keep Python

Python Workers are real and first-class (https://developers.cloudflare.com/workers/languages/python/), but every line of `server.py` that matters is unusable there anyway:

- `http.server` / `HTTPServer` — irrelevant; Workers use a `fetch` handler.
- `urllib.request.urlopen` — **no network** in Pyodide; outbound calls must go through JS `fetch` via the FFI.
- `threading` / `multiprocessing` — importable but non-functional (https://developers.cloudflare.com/workers/languages/python/stdlib/).
- `open()` on `/data/.../career_navigator_prompt.md` — the Python Worker filesystem is ephemeral and in-memory; prompts must become bundled constants, static assets, or KV values.

So Python buys nothing and costs Pyodide bundle/cold-start overhead, plus Stripe/Durable-Object/streaming examples are all JS-first.

**Effort:** straight port ≈ 250–350 lines TS, **4–8 hours**. Full product (Stripe webhook + cookie sessions + DO chat state + SSE streaming + email capture) ≈ **2–3 working days**.

---

## 4. State storage

| Store | Fit | Free-tier limits |
|---|---|---|
| **Durable Objects (SQLite)** — chat sessions ✅ | One DO per conversation. Strongly consistent, single-threaded, `sql.exec()` for turn history, WebSocket Hibernation for live chat without paying duration while idle. | 100,000 requests/day; 13,000 GB-s/day; 1 GB storage per DO on Free (10 GB Paid); SQLite backend only on Free; 100 DO classes. https://developers.cloudflare.com/durable-objects/platform/limits/ |
| **D1** — subscribers, leads, Stripe records ✅ | Relational, indexable, `WHERE email = ?`, joins for tier/status. Exactly the shape of a subscriber table. | 5 M rows read/day; 100,000 rows written/day; 5 GB total storage; 500 MB max per DB on Free; **50 queries per Worker invocation on Free**; 10 DBs on Free. https://developers.cloudflare.com/d1/platform/limits/ · https://developers.cloudflare.com/d1/platform/pricing/ |
| Workers KV — hot cache only ⚠️ | Fine for a 5-minute "is this cookie still entitled" cache or feature flags. **Wrong for chat turns**: only **1,000 writes/day** free and eventually consistent (a Stripe webhook write may not be readable for up to ~60 s). | 100,000 reads/day; 1,000 writes/day to different keys; 1 write/sec to same key; 1 GB storage; 25 MiB value. https://developers.cloudflare.com/kv/platform/limits/ |
| R2 — transcript archives, lead magnets/PDFs ✅ (secondary) | Object storage, free egress. Not a session store. | 10 GB-month; 1 M Class A ops/mo; 10 M Class B ops/mo; egress free. https://developers.cloudflare.com/r2/pricing/ |

**Decision: Durable Objects (SQLite) for conversation state + D1 for subscribers/leads + KV only as a short-TTL entitlement cache + R2 for downloadable assets.**

---

## 5. Stripe paid gating flow

1. Keep the 4 live Payment Links. For each, set the post-payment redirect to `https://thehcadaily.com/welcome?session_id={CHECKOUT_SESSION_ID}` and enable "prefill email".
2. `wrangler secret put STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` and `SESSION_SECRET` (never in `wrangler.jsonc`).
3. Stripe Dashboard → Webhooks → endpoint `https://thehcadaily.com/api/stripe/webhook`, events: `checkout.session.completed`, `customer.subscription.created|updated|deleted`, `invoice.payment_failed`.
4. In the Worker: `const raw = await request.text()` **before** any JSON parse. Parse the `Stripe-Signature` header into `t` and `v1`. HMAC-SHA256 `${t}.${raw}` with the signing secret using WebCrypto (`crypto.subtle.importKey`/`sign`), constant-time compare against `v1`, reject if `Math.abs(now - t) > 300`. No Stripe SDK required.
5. On `checkout.session.completed`: `INSERT ... ON CONFLICT(email) DO UPDATE` into D1 `subscribers(email, stripe_customer_id, stripe_subscription_id, tier, status, current_period_end, rev, created_at)`. Return `200` immediately; push anything slow into `ctx.waitUntil()`.
6. Grant access two ways: (a) `/welcome` handler calls `GET /v1/checkout/sessions/{id}` server-side, confirms `payment_status === "paid"`, and mints the cookie on the spot; (b) magic link — random 32 bytes, store only the SHA-256 hash in D1 with a 15-minute expiry, email via Resend/Cloudflare Email Routing, `/auth/verify?token=` swaps it for a cookie and deletes the row.
7. Session token: HMAC-signed compact JWT in an `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000` cookie carrying `sub` (email), `tier`, `rev`, `exp`. Verified with WebCrypto on every request — no DB hit for a normal page view.
8. Gate `/api/chat`, `/api/coach`, `/premium/*`: verify cookie → check D1 for `status IN ('active','trialing') AND current_period_end > now` → cache that answer in KV for 5 minutes keyed by email. `customer.subscription.deleted` / `invoice.payment_failed` sets `status='canceled'` and bumps `rev`, which invalidates outstanding cookies.
9. Free tier email capture: `POST /api/subscribe` → D1 `leads` + double opt-in token → serve the lead magnet from R2.
10. Rate-limit anonymous/free chat by IP (KV counter or a Cloudflare Rate Limiting rule) so non-subscribers can't run up the OpenRouter bill.

---

## 6. Wix → Cloudflare migration (the hard part)

**The blocker, stated plainly:** Wix does not allow editing nameservers for a Wix-registered domain. Wix's own article: "Currently, it's not possible to change name servers (edit NS records) for a Wix domain… To change the name servers, you'll need to transfer your domain away from Wix." (https://support.wix.com/en/article/request-changing-name-server-ns-records-for-a-wix-domain)

And Cloudflare Registrar cannot be the first hop, because Cloudflare refuses the auth code until the zone is already **Active** on Cloudflare nameservers: "Cloudflare does not allow you to submit an authorization code upfront… You must first add your domain to Cloudflare, update your nameservers, and wait for the zone to show Active status." (https://developers.cloudflare.com/registrar/troubleshooting/)

That is a genuine chicken-and-egg. Two ways out:

**Path A — zero-downtime interim, no transfer needed (do this first, today).**
Deploy the Worker, then in **Wix DNS** add `CNAME app.thehcadaily.com → <worker/pages hostname>`. Cloudflare issues the certificate; a custom **subdomain** does not require the zone to be on Cloudflare nameservers ("If you are deploying to a subdomain, it is not necessary for your site to be a Cloudflare zone" — https://developers.cloudflare.com/pages/configuration/custom-domains/). The apex keeps serving the Wix site, nothing goes dark, and you can sell from `app.thehcadaily.com` immediately. Apex on Cloudflare still requires a nameserver change.

**Path B — full migration (apex on Cloudflare).**
1. ICANN Lookup (https://lookup.icann.org/) to confirm registrar and that the domain is >60 days old with no registrant-contact change in 60 days.
2. Export/screenshot **every** existing DNS record in Wix: apex A, `www`, MX (email!), SPF/DKIM/DMARC TXT, Google/Microsoft verification TXT, any CAA.
3. Disable DNSSEC at Wix and wait ≥24 h — active DNSSEC causes NXDOMAIN after the NS flip and blocks transfers (https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/#disable-dnssec).
4. In Wix: unlock the domain, turn off domain privacy, request the EPP/auth code (Wix emails it).
5. Transfer to an **interim registrar that permits NS edits** (Porkbun, Namecheap, Dynadot). Cloudflare's own guidance for restricted-nameserver providers: "Transfer your domain to a registrar that allows nameserver management" (https://developers.cloudflare.com/dns/nameservers/update-nameservers/#restricted-nameserver-management). Allow up to 5–7 days.
6. Add `thehcadaily.com` to Cloudflare (Free plan) — https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/. Let the quick scan run, then **manually re-enter every record from step 2**. Keep the current Wix A/CNAME values in place, DNS-only (grey cloud), so the live site keeps working through propagation.
7. At the interim registrar, set the two Cloudflare nameservers. Zone goes `Pending Nameserver Update` → `Active`; Cloudflare rechecks after 60 s then at increasing intervals, up to ~24 h; you can force an activation check from the Overview page (https://developers.cloudflare.com/dns/zone-setups/reference/domain-status/).
8. Once **Active**: confirm Universal SSL is issued, set SSL/TLS to Full (strict), enable Always Use HTTPS.
9. Cut over: attach `thehcadaily.com` and `www` as Worker **Custom Domains** (https://developers.cloudflare.com/workers/configuration/routing/custom-domains/) — Cloudflare writes the DNS records and manages the cert. Delete the old Wix A/CNAME records.
10. Send a test email to a domain mailbox; re-verify SPF/DKIM/DMARC. Then re-enable DNSSEC in Cloudflare and publish the DS record at the registrar.
11. Only after the apex serves correctly, cancel the Wix Premium plan (the domain is often bundled with it).
12. Optional, after the ICANN 60-day post-transfer lock: transfer the registration into Cloudflare Registrar (at-cost, no markup) — https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/.

**What breaks if you skip steps:** missing MX = email silently dies; missing verification TXT = Google/Stripe/Search Console re-verification; live DNSSEC = total NXDOMAIN outage; a CAA record that excludes Cloudflare = the cert never issues and the site serves TLS errors (https://developers.cloudflare.com/pages/configuration/custom-domains/#caa-records); the Wix auth code can expire while you wait for the zone to go Active.

---

## 7. Free-tier limits that will actually bite

Sources: https://developers.cloudflare.com/workers/platform/limits/ · https://developers.cloudflare.com/workers/platform/pricing/ · https://developers.cloudflare.com/pages/platform/limits/

- **Workers Free: 100,000 requests/day**, account-wide, shared with Pages Functions. **Requests to static assets are free and unlimited** (https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/), so page views don't count — only `/api/*` does. At 10,000 monthly visitors this is ~3–5% of quota. Not a risk.
- **Workers Free: 10 ms CPU per request.** Waiting on `fetch()` does **not** count as CPU — the OpenRouter round trip is free. But JSON-parsing large payloads and re-encoding SSE chunks can, and the failure mode is Error 1102 / `exceededCpu`. Workers Paid raises this to 30 s (up to 5 min).
- **Free plan hard-stops with no overage.** Blow the daily request quota and API calls return **429** while static pages keep serving — a half-broken site on your best traffic day. `$5/mo` Workers Paid removes the cliff.
- **KV: 1,000 writes/day free.** Writing a KV record per chat turn is the classic mistake — 10,000 visitors with any real chat usage exceeds this. Also 1 write/sec per key, and eventual consistency (up to ~60 s) means a Stripe webhook write can be invisible to the very next gating check.
- **D1 Free: 100,000 rows written/day, 5 M rows read/day, 500 MB/DB, 5 GB account, 50 queries per invocation.** Unindexed `SELECT *` bills the full table scan as rows read, so index `email` and `stripe_customer_id`.
- **Durable Objects Free: SQLite backend only, 100,000 requests/day, 13,000 GB-s/day, 1 GB per object.** WebSocket messages and alarms each count as requests — use Hibernation so idle chats cost nothing.
- **Pages (if used anyway): 500 builds/month, 1 concurrent build, 20-minute build timeout, 20,000 files.**
- **Subrequests: 50 per request on Free** (10,000 on Paid).
- **Workers AI Free: 10,000 Neurons/day, total.** That is tiny — see §8.
- **AI Gateway Free: 100,000 persistent logs total across all gateways**; Logpush is Paid-only (https://developers.cloudflare.com/ai-gateway/reference/pricing/).
- **R2 Free: 10 GB-month, 1 M Class A, 10 M Class B ops/month, free egress.**
- **Cloudflare One / Tunnel: free for ≤50 users** (https://www.cloudflare.com/plans/) — relevant only if you keep Path (c) as a fallback.

---

## 8. Workers AI vs AI Gateway vs OpenRouter direct

Concrete, same-model comparison for the model this app already uses (`deepseek-v4-pro-0813`):

| Route | Input /M tokens | Output /M tokens |
|---|---|---|
| OpenRouter `deepseek/deepseek-v4-pro-0813` (live API pricing) | **$0.66** | **$1.98** |
| Workers AI `@cf/deepseek-ai/deepseek-v4-pro-0813` | **$1.32** | **$3.96** |

**Workers AI is exactly 2× the price for the identical model.** Its free allocation — 10,000 Neurons/day at $0.011/1,000 Neurons (https://developers.cloudflare.com/workers-ai/platform/pricing/) — buys about **83,000 input tokens/day** on that model (120,000 Neurons per M input tokens), i.e. roughly a dozen coaching turns. Cheaper models stretch further (`@cf/meta/llama-3.3-70b-instruct-fp8-fast` at 26,668 Neurons/M input ≈ 375,000 input tokens/day free), and text generation is rate-limited to 300 req/min. Also note some frontier models on Workers AI **require** a paid billing method.

**Recommendation: keep OpenRouter, and put AI Gateway in front of it.** AI Gateway is free on all plans and is one line of code (swap the base URL): you get analytics, cost-per-request tracking, persistent logs, response caching, rate limiting, retries and model fallback. Caching alone pays for itself on repeated Career-Navigator openers. Keep Workers AI in reserve for cheap side jobs (embeddings at ~$0.012–0.02/M tokens, Whisper transcription at $0.0005/audio-minute) where the free Neuron allocation is genuinely useful.

Cost lever worth taking: `deepseek-v4-flash-0731` on OpenRouter is $0.065/M in, $0.18/M out — ~10× cheaper than `v4-pro` — plenty for the Interview Coach's turn-taking, with `v4-pro` reserved for final scored evaluations.

---

## 9. Money

| Line item | 1,000 visitors/mo | 10,000 visitors/mo |
|---|---|---|
| Cloudflare Workers + static assets + D1 + DO + KV + R2 | **$0** (free tier), or $5/mo Workers Paid for headroom | **$5/mo** (Workers Paid strongly advised) |
| AI Gateway | $0 | $0 |
| OpenRouter, `v4-pro` throughout (~8-turn sessions, ~3k in / 500 out per turn, 15% of visitors chatting) | ~$3–6 | ~$30–40 |
| OpenRouter, `v4-flash` for turns + `v4-pro` for scoring | ~$1 | ~$4–8 |
| Domain (`.com` at Cloudflare Registrar, at cost, no markup) | ~$10–12/yr | ~$10–12/yr |
| Stripe | 2.9% + $0.30 per charge | 2.9% + $0.30 per charge |
| **Realistic total** | **~$1–6/mo + ~$1/mo domain** | **~$9–45/mo depending on model choice** |

The variable cost is inference, not hosting. Hosting is effectively free at this scale; the model mix is the only decision that moves the bill.
