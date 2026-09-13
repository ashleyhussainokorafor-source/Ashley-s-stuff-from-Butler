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

  const record = { ...lead, email, receivedAt: new Date().toISOString() };

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

/** Record a completed drill; increment streak on a new day (humane pacing). */
async function handleDrill(request: Request, env: Env): Promise<Response> {
  let body: Record<string, unknown> = {};
  try { body = (await request.json()) as Record<string, unknown>; } catch { return json({ ok: false, error: "invalid json" }, 400); }
  const userId = String(body.userId ?? "").trim();
  if (!userId) return json({ ok: false, error: "missing userId" }, 400);

  const raw = await env.LEADS.get(`user:${userId}`);
  let user: Record<string, unknown> = raw
    ? (JSON.parse(raw) as Record<string, unknown>)
    : { userId, streak: 0, lastDrillDay: null, dimensions: {}, overall: 0, path: {} };

  const today = todayStr();
  if (user.lastDrillDay === today) {
    return json({ ok: true, streak: user.streak as number, already: true, user });
  }
  user.streak = (user.lastDrillDay === yesterdayStr()) ? ((user.streak as number) || 0) + 1 : 1;
  user.lastDrillDay = today;
  await env.LEADS.put(`user:${userId}`, JSON.stringify(user));
  return json({ ok: true, streak: user.streak as number, user });
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

/** Fetch the asset behind a rewritten path. */
function serveAsset(request: Request, env: Env, pathname: string): Promise<Response> {
  const url = new URL(request.url);
  url.pathname = pathname;
  return env.ASSETS.fetch(new Request(url.toString(), request));
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
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

    if (url.pathname === "/api/user") return handleGetUser(request, env);

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
    if (rewrite) return serveAsset(request, env, rewrite);

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
