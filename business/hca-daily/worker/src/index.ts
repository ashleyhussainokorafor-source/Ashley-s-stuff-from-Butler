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
      return json({ error: "Not found" }, 404);
    }

    if (request.method !== "GET" && request.method !== "HEAD") {
      return json({ error: "Method not allowed" }, 405);
    }

    if (url.pathname === "/admin/leads") return handleListLeads(request, env);

    if (url.pathname === "/admin/traffic") return handleTraffic(request, env);

    if (url.pathname === "/api/user") return handleGetUser(request, env);

    if (url.pathname === "/api/league") return handleLeague(request, env);

    if (url.pathname === "/vault/download") {
      const pdfReq = new Request(new URL("/vault.pdf", request.url).toString(), request);
      const asset = await env.ASSETS.fetch(pdfReq);
      if (asset.status === 404) return json({ error: "Not found" }, 404);
      const headers = new Headers(asset.headers);
      headers.set("Content-Type", "application/pdf");
      headers.set("Content-Disposition", 'attachment; filename="HCA-Interview-Answer-Vault.pdf"');
      return new Response(asset.body, { status: 200, headers });
    }

    if (url.pathname === "/accelerator/download") {
      const pdfReq = new Request(new URL("/accelerator.pdf", request.url).toString(), request);
      const asset = await env.ASSETS.fetch(pdfReq);
      if (asset.status === 404) return json({ error: "Not found" }, 404);
      const headers = new Headers(asset.headers);
      headers.set("Content-Type", "application/pdf");
      headers.set("Content-Disposition", 'attachment; filename="HCA-Career-Accelerator.pdf"');
      return new Response(asset.body, { status: 200, headers });
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
