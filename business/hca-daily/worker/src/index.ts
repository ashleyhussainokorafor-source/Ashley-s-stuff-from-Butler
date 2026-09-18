/**
 * The HCA Daily — Cloudflare Worker
 *
 * Port of the original Python stdlib server (web/server.py) to Workers.
 *
 * Serves:
 *   1. Landing page            /            (and /landing)
 *   2. AI Career Navigator     /navigator   (and /app, /chat)
 *   3. Interview Coach         /coach       (and /interview, /simulator)
 *   4. AI endpoints            POST /api/chat   POST /api/coach
 *
 * Why the rewrite: Workers cannot run http.server, urllib, or read local
 * files. Static pages ship as Worker assets; the OpenRouter call becomes
 * fetch(); the prompts are bundled at build time via the Text rule.
 */

import navigatorPrompt from "../prompts/career_navigator_prompt.md";
import coachPrompt from "../prompts/interview_coach_prompt.md";

interface Env {
  ASSETS: Fetcher;
  OPENROUTER_API_KEY: string;
  AI_MODEL?: string;
  /** Optional email-platform endpoint (ConvertKit/MailerLite/etc). When unset, leads are logged. */
  LEAD_WEBHOOK?: string;
  /** KV namespace for storing scorecard leads. */
  LEADS: KVNamespace;
  /** Shared secret guarding the /admin/leads read endpoint. */
  ADMIN_TOKEN?: string;
  /** Restricted Stripe key (Checkout Sessions: read). Used to verify a buyer. */
  STRIPE_SECRET_KEY?: string;
  /** HMAC secret used to sign paid-download links. */
  DOWNLOAD_SECRET?: string;
}

/* -------------------------------------------------------------------------
 * Paid-download entitlements
 * -------------------------------------------------------------------------
 * Stripe payment links send the buyer to /vault/thanks?session_id=... or
 * /accelerator/thanks?session_id=... . We re-check that session against the
 * Stripe API (genuinely paid AND bought the matching price), then mint a
 * short-lived HMAC token that unlocks the PDF.
 *
 * Without a valid token the PDFs are unreachable — including the raw asset
 * paths, which are explicitly blocked below. Never widen this.
 * ---------------------------------------------------------------------- */

/** Price ids that entitle a buyer to each product. */
const ENTITLED_PRICES: Record<string, string[]> = {
  vault: ["price_1UEI8QLxRw5x7PacFp8oN38A"], // $27 Interview Answer Vault
  accelerator: ["price_1UGQBNLxRw5x7PacwEEkmwKy"], // $297 Career Accelerator
  // $29/mo + $199/yr Career Navigator
  navigator: ["price_1UCmwALxRw5x7PacwMCWqOYF", "price_1UCmwBLxRw5x7Pac7UPmWiJn"],
  // $19 single session + $49 3-session prep pack Interview Coach
  coach: ["price_1UCmwCLxRw5x7PacgMiFzkdY", "price_1UCmwELxRw5x7PacgkVSxvI7"],
  // $147 done-for-you résumé translation
  resume: ["price_1UHAWBLxRw5x7PaccZEaL50i"],
};

/** Products that unlock a live app rather than a file download. */
const APP_FOR_PRODUCT: Record<string, { asset: string; cookie: string; label: string }> = {
  navigator: { asset: "/navigator.html", cookie: "hca_navigator", label: "Career Navigator" },
  coach: { asset: "/coach.html", cookie: "hca_coach", label: "Interview Coach" },
};

/** URL paths that resolve to a gated app. */
const APP_PRODUCT_FOR_PATH: Record<string, string> = {
  "/app": "navigator",
  "/navigator": "navigator",
  "/chat": "navigator",
  // Raw asset paths. The friendly routes below are gated, but without these
  // entries the paywall is bypassed completely by adding ".html" to the URL —
  // the same mistake as serving the paid PDFs at /vault.pdf.
  "/navigator.html": "navigator",
  "/coach": "coach",
  "/interview": "coach",
  "/simulator": "coach",
  "/coach.html": "coach",
};

/** Thank-you pages for the app products. */
const ACCESS_PAGE_FOR_PRODUCT: Record<string, string> = {
  navigator: "/navigator-thanks.html",
  coach: "/coach-thanks.html",
};

/** Public Stripe payment links, used by the paywall CTAs. */
const PAYMENT_LINK_FOR_PRODUCT: Record<string, string> = {
  navigator: "https://buy.stripe.com/5kQ8wQacT4qM4QlfnEgMw00",
  coach: "https://buy.stripe.com/9B66oI98PbTeaaF8ZggMw02",
};

/** 30-day access cookie lifetime, in seconds (matches DOWNLOAD_TOKEN_TTL_MS). */
const ACCESS_COOKIE_MAX_AGE = 60 * 60 * 24 * 30;

function readCookie(request: Request, name: string): string {
  const header = request.headers.get("Cookie") ?? "";
  for (const part of header.split(";")) {
    const eq = part.indexOf("=");
    if (eq < 0) continue;
    if (part.slice(0, eq).trim() === name) return decodeURIComponent(part.slice(eq + 1).trim());
  }
  return "";
}

function accessCookie(product: string, token: string): string {
  const spec = APP_FOR_PRODUCT[product];
  const name = spec ? spec.cookie : `hca_${product}`;
  return `${name}=${encodeURIComponent(token)}; Path=/; Max-Age=${ACCESS_COOKIE_MAX_AGE}; HttpOnly; Secure; SameSite=Lax`;
}

/** Paywall shown to anyone without a valid access cookie. */
function paywallPage(product: string, reason: string): string {
  const spec = APP_FOR_PRODUCT[product] ?? { label: product, asset: "/" };
  const link = PAYMENT_LINK_FOR_PRODUCT[product] ?? "/pricing";
  const blurb =
    product === "navigator"
      ? "The Career Navigator is the AI advisor that turns your scorecard into a week-by-week move plan — resume rewrites, target roles, and the exact language hiring managers respond to."
      : "The Interview Coach runs a live executive mock interview, scores your answers against the HCA competency framework, and hands you the rewrites.";
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${spec.label} — The HCA Daily</title>
<style>
 body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
      background:#0b1120;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:24px}
 .card{max-width:560px;background:#111c33;border:1px solid #1e293b;border-radius:20px;padding:40px;text-align:center}
 .lock{font-size:40px;margin-bottom:8px}
 h1{font-size:26px;margin:0 0 12px;color:#fff}
 p{color:#94a3b8;line-height:1.6;margin:0 0 24px}
 .cta{display:inline-block;background:#14b8a6;color:#04231f;font-weight:700;text-decoration:none;
      padding:16px 32px;border-radius:14px;font-size:16px}
 .cta:hover{background:#2dd4bf}
 .alt{display:block;margin-top:16px;color:#64748b;font-size:13px;text-decoration:none}
 .why{margin-top:24px;padding-top:20px;border-top:1px solid #1e293b;color:#64748b;font-size:13px}
</style></head><body><div class="card">
<div class="lock">🔒</div>
<h1>${spec.label} is a paid product</h1>
<p>${blurb}</p>
<a class="cta" href="${link}">Get ${spec.label} →</a>
<a class="alt" href="/scorecard">Or take the free scorecard first</a>
<div class="why">${reason}</div>
</div></body></html>`;
}

/** Replace the access placeholder in a thanks page with the real outcome. */
function renderThanks(html: string, product: string, granted: boolean): string {
  const spec = APP_FOR_PRODUCT[product] ?? { label: product, asset: "/" };
  const block = granted
    ? `<div class="granted"><p><strong>Payment confirmed.</strong> You're in.</p>
       <a class="cta" href="${spec.asset}">Open the ${spec.label} →</a>
       <p class="hint">Access is saved to this browser for 30 days. Bookmark this page if you switch devices.</p></div>`
    : `<div class="failed"><p><strong>We couldn't verify that purchase yet.</strong></p>
       <p class="hint">If you just paid, wait a few seconds and reload. If it still fails, email
       <a href="mailto:ashleyhussainokorafor@gmail.com">ashleyhussainokorafor@gmail.com</a> with your receipt and we'll unlock you manually.</p>
       <a class="cta" href="${PAYMENT_LINK_FOR_PRODUCT[product] ?? "/pricing"}">Get ${spec.label} →</a></div>`;
  return html.replace("<!--ACCESS-->", block);
}

/** /navigator/thanks and /coach/thanks — verify the purchase, then set the access cookie. */
async function handleAccessThanks(request: Request, env: Env, product: string): Promise<Response> {
  const url = new URL(request.url);
  const sessionId = url.searchParams.get("session_id") ?? "";
  const provided = url.searchParams.get("t") ?? "";

  let token: string | null = null;
  if (await tokenUnlocks(env, provided, product)) {
    token = provided;
  } else if (await sessionEntitles(env, sessionId, product)) {
    token = await mintDownloadToken(env, product);
  }

  const page = ACCESS_PAGE_FOR_PRODUCT[product] ?? "/thankyou.html";
  const asset = await serveAsset(request, env, page);
  const html = await asset.text();

  const headers: Record<string, string> = {
    "content-type": "text/html; charset=utf-8",
    "cache-control": "no-store",
  };
  if (token) headers["Set-Cookie"] = accessCookie(product, token);

  return new Response(renderThanks(html, product, Boolean(token)), { status: 200, headers });
}

/** Intake form shown to a verified résumé-translation buyer. */
const RESUME_INTAKE_FORM = `
<form id="intakeForm">
  <label for="f_name">Your name</label>
  <input id="f_name" autocomplete="name" required>
  <label for="f_email">Email I should reply to</label>
  <input id="f_email" type="email" autocomplete="email" required>
  <label for="f_role">The role you're targeting</label>
  <input id="f_role" placeholder="e.g. Ambulatory Clinic Manager">
  <label for="f_resume">Paste your current résumé</label>
  <textarea id="f_resume" required placeholder="Paste the whole thing — formatting doesn't matter, I'll rebuild it."></textarea>
  <p class="hint">Paste it as text. If you only have a PDF or Word file, email it to
  ashleyhussainokorafor@gmail.com and mention this order.</p>
  <label for="f_notes">Anything else I should know?</label>
  <textarea id="f_notes" style="min-height:90px" placeholder="Target salary, geography, a specific posting you're going after, a gap you're worried about…"></textarea>
  <button type="submit">Send my résumé →</button>
</form>
<div class="ok" id="okBox"><strong>Got it.</strong> Your rewrite comes back to you by email within 3 business days.</div>`;

/** /resume/thanks — verify the purchase, then hand over the intake form. */
async function handleResumeThanks(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const sessionId = url.searchParams.get("session_id") ?? "";
  const granted = await sessionEntitles(env, sessionId, "resume");

  const asset = await serveAsset(request, env, "/resume-thanks.html");
  const html = await asset.text();
  const block = granted
    ? RESUME_INTAKE_FORM
    : `<div class="warn">We couldn't verify that purchase yet. If you just paid, wait a
       few seconds and reload — Stripe occasionally takes a moment to confirm. If it still
       fails, email <a href="mailto:ashleyhussainokorafor@gmail.com">ashleyhussainokorafor@gmail.com</a>
       with your receipt and I'll sort it directly.</div>`;

  return new Response(html.replace("<!--ACCESS-->", block), {
    status: 200,
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
  });
}

/**
 * POST /api/resume-intake — store a buyer's résumé for Ashley to rewrite.
 * Never loses work: writes to KV first, and only reports success once it lands.
 */
async function handleResumeIntake(request: Request, env: Env): Promise<Response> {
  let body: Record<string, unknown> = {};
  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch {
    /* fall through to validation */
  }

  const email = String(body.email ?? "").trim();
  const resumeText = String(body.resumeText ?? "").trim();
  if (!email.includes("@") || resumeText.length < 40) {
    return json({ ok: false, error: "a valid email and the résumé text are required" }, 400);
  }

  const record = {
    name: String(body.name ?? "").trim(),
    email,
    targetRole: String(body.targetRole ?? "").trim(),
    notes: String(body.notes ?? "").trim(),
    resumeText,
    receivedAt: new Date().toISOString(),
  };

  try {
    await env.LEADS.put(`resume:${record.receivedAt}:${crypto.randomUUID()}`,
                        JSON.stringify(record));
  } catch (error) {
    console.error("resume intake write failed", String(error));
    return json({ ok: false, error: "could not save your résumé" }, 500);
  }
  return json({ ok: true });
}

/** Gate /app and /coach behind the access cookie (or a ?t= token that sets it). */
async function handleGatedApp(request: Request, env: Env, product: string): Promise<Response> {
  const spec = APP_FOR_PRODUCT[product];
  if (!spec) return json({ error: "unknown product" }, 404);

  const url = new URL(request.url);
  const urlToken = url.searchParams.get("t") ?? "";
  const cookieToken = readCookie(request, spec.cookie);

  let valid = false;
  let tokenToSet = "";
  if (urlToken && (await tokenUnlocks(env, urlToken, product))) {
    valid = true;
    tokenToSet = urlToken;
  } else if (cookieToken && (await tokenUnlocks(env, cookieToken, product))) {
    valid = true;
  }

  if (!valid) {
    return new Response(paywallPage(product, "You're seeing this because this page requires a purchase."), {
      status: 402,
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
    });
  }

  const asset = await serveAsset(request, env, spec.asset);
  const html = await asset.text();
  const headers: Record<string, string> = {
    "content-type": "text/html; charset=utf-8",
    "cache-control": "no-store",
  };
  if (tokenToSet) headers["Set-Cookie"] = accessCookie(product, tokenToSet);
  return new Response(html, { status: 200, headers });
}

const PDF_FOR_PRODUCT: Record<string, { asset: string; filename: string }> = {
  vault: { asset: "/vault.pdf", filename: "HCA-Interview-Answer-Vault.pdf" },
  accelerator: { asset: "/accelerator.pdf", filename: "HCA-Career-Accelerator.pdf" },
};

const THANKS_PAGE_FOR_PRODUCT: Record<string, string> = {
  vault: "/thankyou.html",
  accelerator: "/accelerator-thanks.html",
};

/** Raw asset paths that must never be served directly. */
const PROTECTED_ASSET_PATHS = new Set(["/vault.pdf", "/accelerator.pdf"]);

/** How long a minted download link stays valid. */
const DOWNLOAD_TOKEN_TTL_MS = 1000 * 60 * 60 * 24 * 30; // 30 days

function b64urlFromBytes(bytes: Uint8Array): string {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function bytesFromB64url(value: string): Uint8Array {
  const b64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const bin = atob(b64 + "=".repeat((4 - (b64.length % 4)) % 4));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function hmacSign(secret: string, message: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return b64urlFromBytes(new Uint8Array(sig));
}

async function mintDownloadToken(env: Env, product: string): Promise<string | null> {
  if (!env.DOWNLOAD_SECRET) return null;
  const payload = `${product}.${Date.now() + DOWNLOAD_TOKEN_TTL_MS}`;
  const sig = await hmacSign(env.DOWNLOAD_SECRET, payload);
  return `${b64urlFromBytes(new TextEncoder().encode(payload))}.${sig}`;
}

async function tokenUnlocks(env: Env, token: string, product: string): Promise<boolean> {
  try {
    const secret = env.DOWNLOAD_SECRET;
    if (!secret || !token) return false;
    const dot = token.lastIndexOf(".");
    if (dot < 1) return false;
    const payload = new TextDecoder().decode(bytesFromB64url(token.slice(0, dot)));
    const [prod, expiryRaw] = payload.split(".");
    if (prod !== product) return false;
    if (!(Number(expiryRaw) > Date.now())) return false;
    const expected = await hmacSign(secret, payload);
    const given = token.slice(dot + 1);
    if (given.length !== expected.length) return false;
    let diff = 0;
    for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ given.charCodeAt(i);
    return diff === 0;
  } catch {
    return false;
  }
}

/** True only when the Stripe session is paid AND bought the expected product. */
async function sessionEntitles(env: Env, sessionId: string, product: string): Promise<boolean> {
  const key = env.STRIPE_SECRET_KEY;
  if (!key || !sessionId) return false;
  try {
    const res = await fetch(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}?expand[]=line_items`,
      { headers: { Authorization: `Bearer ${key}` } },
    );
    if (!res.ok) return false;
    const session = (await res.json()) as {
      payment_status?: string;
      line_items?: { data?: { price?: { id?: string } }[] };
    };
    // "no_payment_required" is what Stripe returns for a session that was fully
    // discounted (100%-off promo code) or otherwise $0. Those buyers are entitled
    // too — the line-item price check below is what actually proves the product.
    if (session.payment_status !== "paid" && session.payment_status !== "no_payment_required") {
      return false;
    }
    const allowed = ENTITLED_PRICES[product] ?? [];
    return (session.line_items?.data ?? []).some((item) =>
      allowed.includes(item.price?.id ?? ""),
    );
  } catch {
    return false;
  }
}

/** Human page shown when someone lands on a paid file without a valid link. */
function lockedPage(product: string): string {
  const label = product === "vault" ? "Interview Answer Vault" : "Career Accelerator";
  return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Download link needed</title>
<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#f7f9fb;color:#14181f;display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0;padding:24px}
.c{background:#fff;border:1px solid #e4e9f0;border-radius:18px;padding:40px 32px;max-width:520px;text-align:center;box-shadow:0 20px 60px rgba(11,37,69,.08)}
h1{color:#0b2545;font-size:25px;margin:0 0 12px}p{color:#5b6572;line-height:1.6;margin:0 0 16px}
a{display:inline-block;background:#c9a227;color:#1a1400;font-weight:800;padding:14px 30px;border-radius:11px;text-decoration:none}</style>
</head><body><div class="c">
<h1>This link needs to come from your receipt</h1>
<p>The ${label} is a paid download, so this page needs the link from your purchase confirmation.</p>
<p>Open the confirmation email for your order, or the “thank you” page Stripe sent you after checkout — the download button there works.</p>
<a href="https://thehcadaily.com/pricing">See the ${label}</a>
</div></body></html>`;
}

const DEFAULT_MODEL = "deepseek/deepseek-v4-pro-0813";
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";

/** Friendly URLs -> the asset file that actually backs them. */
const ROUTE_REWRITES: Record<string, string> = {
  "/": "/index.html",
  "/landing": "/index.html",
  "/app": "/navigator.html",
  "/navigator": "/navigator.html",
  "/chat": "/navigator.html",
  "/coach": "/coach.html",
  "/interview": "/coach.html",
  "/simulator": "/coach.html",
  "/scorecard": "/scorecard.html",
  "/readiness": "/scorecard.html",
  "/quiz": "/scorecard.html",
  "/learn": "/learn.html",
  "/today": "/learn.html",
  "/path": "/path.html",
  "/practice": "/practice.html",
  "/league": "/league.html",
  "/vault": "/vault.html",
  "/sales": "/vault.html",
  "/store": "/vault.html",
  "/vault/thanks": "/thankyou.html",
  "/thank-you": "/thankyou.html",
  "/thanks": "/thankyou.html",
  "/resume": "/resume.html",
  "/resume-translation": "/resume.html",
  "/resume-rewrite": "/resume.html",
  "/accelerator": "/accelerator.html",
  "/accelerator/thanks": "/accelerator-thanks.html",
  "/admin": "/admin.html",
  "/leads": "/admin.html",
  "/playbook": "/playbook.html",
  "/resume-playbook": "/playbook.html",
  "/free": "/playbook.html",
  "/pricing": "/pricing.html",
  "/plans": "/pricing.html",
  "/about": "/about.html",
  "/legal": "/legal.html",
  "/terms": "/legal.html",
  "/privacy": "/legal.html",
};

interface ChatMessage {
  role: string;
  content: string;
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** Single place that talks to OpenRouter. Mirrors call_openrouter() from the Python. */
async function callOpenRouter(
  env: Env,
  messages: ChatMessage[],
  systemPrompt: string,
  temperature: number,
): Promise<string> {
  if (!env.OPENROUTER_API_KEY) {
    throw new Error("OPENROUTER_API_KEY is not configured on this Worker");
  }

  const response = await fetch(OPENROUTER_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
      // OpenRouter attribution headers (optional, but good practice)
      "HTTP-Referer": "https://thehcadaily.com",
      "X-Title": "The HCA Daily",
    },
    body: JSON.stringify({
      model: env.AI_MODEL || DEFAULT_MODEL,
      messages: [{ role: "system", content: systemPrompt }, ...messages],
      temperature,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`OpenRouter ${response.status}: ${detail.slice(0, 200)}`);
  }

  const data = (await response.json()) as {
    choices?: Array<{ message?: { content?: string } }>;
  };
  return data.choices?.[0]?.message?.content ?? "";
}

async function readMessages(request: Request): Promise<ChatMessage[]> {
  try {
    const body = (await request.json()) as { messages?: ChatMessage[] };
    return Array.isArray(body?.messages) ? body.messages : [];
  } catch {
    return [];
  }
}

async function handleChat(request: Request, env: Env): Promise<Response> {
  const messages = await readMessages(request);
  try {
    const reply = await callOpenRouter(env, messages, navigatorPrompt, 0.4);
    return json({ reply });
  } catch (error) {
    return json({ reply: `HCA Career Navigator Unavailable: ${String(error)}` });
  }
}

async function handleCoach(request: Request, env: Env): Promise<Response> {
  let payload: { messages?: ChatMessage[]; role?: string; scenario?: string } = {};
  try {
    payload = await request.json();
  } catch {
    payload = {};
  }

  const messages = Array.isArray(payload.messages) ? payload.messages : [];
  const role = payload.role || "Ambulatory Clinic Manager";
  const scenario = payload.scenario || "General Operations";

  const contextualPrompt =
    `${coachPrompt}\n\nCURRENT ACTIVE CANDIDATE TARGET:\n` +
    `- Candidate Role: ${role}\n- Focus Scenario: ${scenario}\n` +
    `Conduct a probing, realistic executive simulation. ` +
    `Probe weak metrics and score using the 4-Pillar Executive Rubric.`;

  try {
    const reply = await callOpenRouter(env, messages, contextualPrompt, 0.5);
    return json({ reply });
  } catch (error) {
    return json({ reply: `HCA Interview Coach Simulation Offline: ${String(error)}` });
  }
}

/** Bot-ish user agents — never let scanners inflate our own traffic numbers. */
const BOT_UA =
  /bot|crawler|spider|crawl|slurp|curl|wget|python-|httpclient|scanner|nmap|masscan|zgrab|censys|expanse|semrush|ahrefs|mj12|dotbot|petalbot|bytespider|monitor|headless|lighthouse|go-http|okhttp|java\/|libwww|facebookexternalhit|preview/i;

function isLikelyBot(request: Request): boolean {
  const ua = request.headers.get("user-agent") || "";
  return !ua || BOT_UA.test(ua);
}

/**
 * Where a visitor actually came from.
 *
 * Prefers UTMs sent in the request body; falls back to the page URL in the
 * Referer header (a same-origin fetch sends the full URL, query string and all),
 * which is how the scorecard page hands us the campaign that brought them in.
 */
function attribution(request: Request, body: Record<string, unknown> = {}): Record<string, string> {
  let params: URLSearchParams | null = null;
  let referrer = "";
  try {
    const ref = request.headers.get("referer") || request.headers.get("referrer") || "";
    if (ref) {
      const u = new URL(ref);
      params = u.searchParams;
      referrer = u.origin;
    }
  } catch {
    params = null;
    referrer = "";
  }

  const pick = (k: string): string => {
    const fromBody = body[k];
    if (typeof fromBody === "string" && fromBody) return fromBody;
    return params?.get(k) ?? "";
  };

  const cf = (request as unknown as { cf?: { country?: string; city?: string } }).cf;

  return {
    utmSource: pick("utm_source"),
    utmMedium: pick("utm_medium"),
    utmCampaign: pick("utm_campaign"),
    utmContent: pick("utm_content"),
    referrer,
    country: cf?.country ?? "",
  };
}

/** Persist one pageview into a per-day counter, so we can see real humans. */
async function recordPageview(env: Env, request: Request, path: string): Promise<void> {
  if (isLikelyBot(request)) return;
  const day = new Date().toISOString().slice(0, 10);
  const key = `pv:${day}`;
  try {
    const raw = await env.LEADS.get(key);
    const counts: Record<string, number> = raw ? JSON.parse(raw) : {};
    counts[path] = (counts[path] || 0) + 1;
    await env.LEADS.put(key, JSON.stringify(counts));
  } catch (error) {
    console.error("pageview write failed", String(error));
  }
}

/** Human traffic + lead sources (admin). Guarded by ADMIN_TOKEN. */
async function handleTraffic(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") ?? request.headers.get("X-Admin-Token") ?? "";
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return json({ error: "unauthorized" }, 401);
  }

  const days: Record<string, Record<string, number>> = {};
  const pvList = await env.LEADS.list({ prefix: "pv:" });
  for (const k of pvList.keys) {
    const raw = await env.LEADS.get(k.name);
    if (!raw) continue;
    try { days[k.name.slice(3)] = JSON.parse(raw); } catch { /* skip */ }
  }

  const leadList = await env.LEADS.list({ prefix: "lead:" });
  const leadsBySource: Record<string, number> = {};
  const recent: Record<string, unknown>[] = [];
  for (const k of leadList.keys) {
    const raw = await env.LEADS.get(k.name);
    if (!raw) continue;
    try {
      const l = JSON.parse(raw) as Record<string, string>;
      const src = l.utmSource || l.referrer || "(direct)";
      leadsBySource[src] = (leadsBySource[src] || 0) + 1;
      recent.push({
        email: l.email, source: src, campaign: l.utmCampaign || "",
        overall: l.overall, receivedAt: l.receivedAt, country: l.country,
      });
    } catch { /* skip malformed */ }
  }

  const userList = await env.LEADS.list({ prefix: "user:" });

  return json({
    counts: { leads: leadList.keys.length, users: userList.keys.length, daysTracked: pvList.keys.length },
    leadsBySource,
    days,
    recentLeads: recent.slice(-50),
  });
}

/** Scorecard lead capture. Never fails the visitor — always returns ok on valid input. */
async function handleScorecard(request: Request, env: Env): Promise<Response> {
  let lead: Record<string, unknown> = {};
  try {
    lead = (await request.json()) as Record<string, unknown>;
  } catch {
    return json({ ok: false, error: "invalid json" }, 400);
  }

  const email = String(lead.email ?? "").trim();
  if (!email || !email.includes("@")) {
    return json({ ok: false, error: "a valid email is required" }, 400);
  }

  const record = {
    ...lead,
    email,
    ...attribution(request, lead),
    receivedAt: new Date().toISOString(),
  };

  // 1) Always persist to KV so a lead is never lost.
  try {
    const key = `lead:${record.receivedAt}:${crypto.randomUUID()}`;
    await env.LEADS.put(key, JSON.stringify(record));
  } catch (error) {
    console.error("lead kv write failed", String(error));
  }

  // 2) Optionally forward to an email platform.
  if (env.LEAD_WEBHOOK) {
    try {
      await fetch(env.LEAD_WEBHOOK, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(record),
      });
    } catch (error) {
      // A broken email platform must not stop the visitor seeing their score.
      console.error("lead webhook failed", String(error));
    }
  } else {
    console.log("SCORECARD_LEAD", JSON.stringify(record));
  }

  return json({ ok: true });
}

/** List stored leads (admin). Guarded by ADMIN_TOKEN. */
async function handleListLeads(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") ?? request.headers.get("X-Admin-Token") ?? "";

  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return json({ error: "unauthorized" }, 401);
  }

  const list = await env.LEADS.list({ prefix: "lead:" });
  const leads: Record<string, unknown>[] = [];
  for (const key of list.keys) {
    const raw = await env.LEADS.get(key.name);
    if (raw) {
      try { leads.push({ ...JSON.parse(raw), _key: key.name }); } catch { /* skip malformed */ }
    }
  }
  leads.sort((a, b) => String(a.receivedAt ?? "").localeCompare(String(b.receivedAt ?? "")));
  return json({ count: leads.length, leads });
}

function todayStr(): string { return new Date().toISOString().slice(0, 10); }
function yesterdayStr(): string { return new Date(Date.now() - 86400000).toISOString().slice(0, 10); }
function mondayStr(d = new Date()): string {
  const day = d.getUTCDay();
  const diff = day === 0 ? 6 : day - 1;
  const m = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - diff));
  return m.toISOString().slice(0, 10);
}
function daysBetween(a: string, b: string): number {
  return Math.round((new Date(b + "T00:00:00Z").getTime() - new Date(a + "T00:00:00Z").getTime()) / 86400000);
}

/** Create/upsert a learner from the scorecard. Never loses prior state. */
async function handleCreateUser(request: Request, env: Env): Promise<Response> {
  let body: Record<string, unknown> = {};
  try { body = (await request.json()) as Record<string, unknown>; } catch { return json({ ok: false, error: "invalid json" }, 400); }

  const userId = String(body.userId ?? "").trim() || crypto.randomUUID();
  const raw = await env.LEADS.get(`user:${userId}`);
  let existing: Record<string, unknown> = {};
  if (raw) { try { existing = JSON.parse(raw) as Record<string, unknown>; } catch { /* ignore */ } }

  const prevDims = (existing.dimensions ?? {}) as Record<string, number>;
  const user = {
    userId,
    email: String(body.email ?? existing.email ?? "").trim(),
    name: String(body.name ?? existing.name ?? "").trim(),
    overall: (body.overall ?? existing.overall) as number,
    dimensions: { ...prevDims, ...((body.dimensions ?? {}) as Record<string, number>) },
    createdAt: (existing.createdAt ?? new Date().toISOString()) as string,
    streak: (existing.streak ?? 0) as number,
    lastDrillDay: (existing.lastDrillDay ?? null) as string | null,
    freezes: (existing.freezes ?? 1) as number,
    freezeAwarded: (existing.freezeAwarded ?? false) as boolean,
    xp: (existing.xp ?? 0) as number,
    xpWeek: (existing.xpWeek ?? 0) as number,
    weekStart: (existing.weekStart ?? null) as string | null,
    path: (existing.path ?? {}) as Record<string, unknown>,
  };
  await env.LEADS.put(`user:${userId}`, JSON.stringify(user));
  return json({ ok: true, userId, user });
}

async function handleGetUser(request: Request, env: Env): Promise<Response> {
  const id = new URL(request.url).searchParams.get("id") ?? "";
  if (!id) return json({ user: null });
  const raw = await env.LEADS.get(`user:${id}`);
  return raw ? json({ user: JSON.parse(raw) }) : json({ user: null });
}

/** Record a completed drill: XP + streak (with freeze) + weekly XP. Humane pacing. */
async function handleDrill(request: Request, env: Env): Promise<Response> {
  let body: Record<string, unknown> = {};
  try { body = (await request.json()) as Record<string, unknown>; } catch { return json({ ok: false, error: "invalid json" }, 400); }
  const userId = String(body.userId ?? "").trim();
  if (!userId) return json({ ok: false, error: "missing userId" }, 400);
  const xpEarned = Math.max(0, Number(body.xpEarned) || 10);

  const raw = await env.LEADS.get(`user:${userId}`);
  let user: Record<string, unknown> = raw
    ? (JSON.parse(raw) as Record<string, unknown>)
    : { userId, streak: 0, lastDrillDay: null, freezes: 1, xp: 0, xpWeek: 0, weekStart: null, dimensions: {}, overall: 0, path: {} };

  // weekly XP rollover
  const wm = mondayStr();
  if ((user.weekStart ?? "") !== wm) { user.xpWeek = 0; user.weekStart = wm; }
  user.xp = ((user.xp as number) || 0) + xpEarned;
  user.xpWeek = ((user.xpWeek as number) || 0) + xpEarned;

  const today = todayStr();
  let already = false, froze = false;
  if (user.lastDrillDay === today) {
    already = true;
  } else if (user.lastDrillDay === yesterdayStr()) {
    user.streak = ((user.streak as number) || 0) + 1;
  } else if (user.lastDrillDay) {
    const gap = daysBetween(user.lastDrillDay as string, today);
    if (gap === 2 && (user.freezes as number) > 0) {
      user.freezes = (user.freezes as number) - 1;
      user.streak = ((user.streak as number) || 0) + 1;
      froze = true;
    } else {
      user.streak = 1;
    }
  } else {
    user.streak = 1;
  }
  user.lastDrillDay = today;

  // award a freeze at a 7-day streak (once)
  if (!user.freezeAwarded && ((user.streak as number) || 0) >= 7) {
    user.freezeAwarded = true;
    user.freezes = Math.min(2, ((user.freezes as number) || 0) + 1);
  }

  await env.LEADS.put(`user:${userId}`, JSON.stringify(user));
  return json({ ok: true, streak: user.streak as number, xp: user.xp, xpWeek: user.xpWeek, freezes: user.freezes, froze, already, user });
}

/** Mark a unit mastered on the skill path. */
async function handleProgress(request: Request, env: Env): Promise<Response> {
  let body: Record<string, unknown> = {};
  try { body = (await request.json()) as Record<string, unknown>; } catch { return json({ ok: false, error: "invalid json" }, 400); }
  const userId = String(body.userId ?? "").trim();
  const unitId = String(body.unitId ?? "").trim();
  if (!userId || !unitId) return json({ ok: false, error: "userId + unitId required" }, 400);

  const raw = await env.LEADS.get(`user:${userId}`);
  let user: Record<string, unknown> = raw
    ? (JSON.parse(raw) as Record<string, unknown>)
    : { userId, streak: 0, lastDrillDay: null, dimensions: {}, overall: 0, path: {} };

  const path = (user.path ?? {}) as Record<string, unknown>;
  path[unitId] = { mastered: true, at: new Date().toISOString() };
  user.path = path;
  await env.LEADS.put(`user:${userId}`, JSON.stringify(user));
  return json({ ok: true, path: user.path });
}

/** Weekly XP leaderboard (small cohort, opt-in, no public humiliation — top 10 + requester rank). */
async function handleLeague(request: Request, env: Env): Promise<Response> {
  const uid = new URL(request.url).searchParams.get("id") ?? "";
  const list = await env.LEADS.list({ prefix: "user:" });
  const rows: Array<{ userId: string; name: string; xpWeek: number }> = [];
  for (const k of list.keys) {
    const raw = await env.LEADS.get(k.name);
    if (!raw) continue;
    try {
      const u = JSON.parse(raw) as Record<string, unknown>;
      const xp = (u.xpWeek as number) || 0;
      if (xp > 0) rows.push({ userId: (u.userId as string) || "", name: (u.name as string) || "Anonymous", xpWeek: xp });
    } catch { /* skip malformed */ }
  }
  rows.sort((a, b) => b.xpWeek - a.xpWeek);
  const idx = uid ? rows.findIndex(r => r.userId === uid) : -1;
  return json({
    top: rows.slice(0, 10).map((r, i) => ({ rank: i + 1, ...r })),
    myRank: idx >= 0 ? idx + 1 : null,
    myXp: idx >= 0 ? rows[idx].xpWeek : 0,
  });
}

/** Fetch the asset behind a rewritten path. */
function serveAsset(request: Request, env: Env, pathname: string): Promise<Response> {
  const url = new URL(request.url);
  url.pathname = pathname;
  return env.ASSETS.fetch(new Request(url.toString(), request));
}

/** Swap the download button on a thank-you page for a working (or honest) link. */
function withDownloadLink(html: string, product: string, token: string | null): string {
  const anchor = new RegExp(`<a\\b[^>]*href="/${product}/download"[^>]*>(.*?)</a>`, "is");
  const match = html.match(anchor);
  if (!match) return html;
  const inner = match[1] ?? "Download";
  if (token) {
    return html.replace(
      anchor,
      () => `<a href="/${product}/download?t=${token}" class="cta">${inner}</a>`,
    );
  }
  return html.replace(
    anchor,
    () =>
      `<p style="color:#5b6572;font-size:15px;background:#fff7e6;border:1px solid #f0dca8;border-radius:10px;padding:14px 18px;margin:0;text-align:left">This page is missing its purchase link. Open the confirmation email for your order and use the download button there — or reply to that email and I'll re-send your file.</p>`,
  );
}

/**
 * Paid download. Requires an unexpired HMAC token minted for this product.
 * Anyone arriving without one gets the locked page instead of the PDF.
 */
async function handleDownload(request: Request, env: Env, product: string): Promise<Response> {
  const url = new URL(request.url);
  const token = url.searchParams.get("t") ?? "";

  if (!(await tokenUnlocks(env, token, product))) {
    return new Response(lockedPage(product), {
      status: 403,
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
    });
  }

  const spec = PDF_FOR_PRODUCT[product];
  const asset = await env.ASSETS.fetch(
    new Request(new URL(spec.asset, request.url).toString(), request),
  );
  if (asset.status === 404) return json({ error: "Not found" }, 404);

  const headers = new Headers(asset.headers);
  headers.set("Content-Type", "application/pdf");
  headers.set("Content-Disposition", `attachment; filename="${spec.filename}"`);
  headers.set("Cache-Control", "no-store");
  return new Response(asset.body, { status: 200, headers });
}

/**
 * Post-purchase landing page. Verifies the Stripe checkout session, then hands
 * the buyer a signed download link. Repeat visits work as long as the buyer
 * keeps the ?session_id=... URL or the token.
 */
async function handleThanks(request: Request, env: Env, product: string): Promise<Response> {
  const url = new URL(request.url);
  const sessionId = url.searchParams.get("session_id") ?? "";
  const provided = url.searchParams.get("t") ?? "";

  let token: string | null = null;
  if (await tokenUnlocks(env, provided, product)) {
    token = provided;
  } else if (await sessionEntitles(env, sessionId, product)) {
    token = await mintDownloadToken(env, product);
  }

  const asset = await serveAsset(request, env, THANKS_PAGE_FOR_PRODUCT[product]);
  const html = await asset.text();
  return new Response(withDownloadLink(html, product, token), {
    status: 200,
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
  });
}

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: { waitUntil(promise: Promise<unknown>): void },
  ): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "POST") {
      if (url.pathname === "/api/chat") return handleChat(request, env);
      if (url.pathname === "/api/coach") return handleCoach(request, env);
      if (url.pathname === "/api/scorecard") return handleScorecard(request, env);
      if (url.pathname === "/api/user") return handleCreateUser(request, env);
      if (url.pathname === "/api/drill") return handleDrill(request, env);
      if (url.pathname === "/api/progress") return handleProgress(request, env);
      if (url.pathname === "/api/resume-intake") return handleResumeIntake(request, env);
      return json({ error: "Not found" }, 404);
    }

    if (request.method !== "GET" && request.method !== "HEAD") {
      return json({ error: "Method not allowed" }, 405);
    }

    if (url.pathname === "/admin/leads") return handleListLeads(request, env);

    if (url.pathname === "/admin/traffic") return handleTraffic(request, env);

    if (url.pathname === "/api/user") return handleGetUser(request, env);

    if (url.pathname === "/api/league") return handleLeague(request, env);

    if (url.pathname === "/vault/download") return handleDownload(request, env, "vault");

    if (url.pathname === "/accelerator/download")
      return handleDownload(request, env, "accelerator");

    if (url.pathname === "/vault/thanks") return handleThanks(request, env, "vault");

    if (url.pathname === "/accelerator/thanks")
      return handleThanks(request, env, "accelerator");

    if (url.pathname === "/navigator/thanks")
      return handleAccessThanks(request, env, "navigator");

    if (url.pathname === "/coach/thanks") return handleAccessThanks(request, env, "coach");

    if (url.pathname === "/resume/thanks") return handleResumeThanks(request, env);

    // The live apps are paid products — gate them before the rewrite map runs.
    const gatedProduct = APP_PRODUCT_FOR_PATH[url.pathname];
    if (gatedProduct) return handleGatedApp(request, env, gatedProduct);

    // The raw PDFs back the paid downloads — never serve them directly.
    if (PROTECTED_ASSET_PATHS.has(url.pathname)) {
      return new Response(lockedPage(url.pathname.includes("accelerator") ? "accelerator" : "vault"), {
        status: 403,
        headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
      });
    }

    const rewrite = ROUTE_REWRITES[url.pathname];
    if (rewrite) {
      ctx.waitUntil(recordPageview(env, request, url.pathname));
      return serveAsset(request, env, rewrite);
    }

    const asset = await env.ASSETS.fetch(request);
    if (asset.status === 404) {
      // Serve the landing page for unknown URLs, but keep the 404 status so
      // search engines don't index dead links as real pages (soft-404).
      const fallback = await serveAsset(request, env, "/index.html");
      return new Response(fallback.body, {
        status: 404,
        headers: fallback.headers,
      });
    }
    return asset;
  },
};
