# The HCA Daily — Monetization & Payment Infrastructure Specification

**Approved Products & Pricing Structure:**
1. **HCA Career Navigator Monthly:** $29.00 / month (Recurring Subscription)
2. **HCA Career Navigator Annual:** $199.00 / year (Recurring Subscription — 43% savings)
3. **HCA Interview Coach Single Session:** $19.00 (One-time payment)
4. **HCA Interview Coach 3-Pack:** $49.00 (One-time payment)

---

## 1. Zero-Code Fast-Track: Stripe Payment Links (Recommended)

To collect payments immediately without building a backend:
1. Log into your **Stripe Dashboard** ([dashboard.stripe.com](https://dashboard.stripe.com/)).
2. Go to **More** → **Payment Links** → **New**.
3. Create 4 Payment Links matching our exact approved pricing:
   - **Product 1:** `HCA Career Navigator (Monthly)` — $29/month recurring.
   - **Product 2:** `HCA Career Navigator (Annual)` — $199/year recurring.
   - **Product 3:** `HCA Interview Coach (Single Mock Session)` — $19 one-time.
   - **Product 4:** `HCA Interview Coach (3-Session Prep Pack)` — $49 one-time.
4. **After Payment Redirect (Success URL):**
   - For Navigator: Redirect to member onboarding / welcome page.
   - For Interview Coach: Redirect to mock interview scheduling / intake form.

---

## 2. Platform Alternative: Beehiiv / Substack Paid Tier
If delivering The HCA Daily via Beehiiv or Substack:
- Set **Monthly Subscription:** $29/mo
- Set **Annual Subscription:** $199/yr
- Benefit: Built-in paywalling for exclusive Tuesday premium editions, member-only discussion threads, and direct Stripe Connect integration.

---

## 3. Webhook & Access Automation (When Ready)
When Stripe is configured, the following environment variables enable automated fulfillment:
- `STRIPE_SECRET_KEY`: `sk_live_...`
- `STRIPE_WEBHOOK_SECRET`: `whsec_...`
- `STRIPE_PRICE_NAVIGATOR_MONTHLY`: `price_...`
- `STRIPE_PRICE_NAVIGATOR_ANNUAL`: `price_...`
