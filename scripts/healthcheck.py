#!/usr/bin/env python3
"""HCA Daily / Hermes one-shot health check.

Prints a single PASS/FAIL table so a breakage is obvious at a glance.
Usage:  python3 /data/scripts/healthcheck.py
"""
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request

results = []


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((name, ok, detail))


def env_val(path, key):
    if not os.path.exists(path):
        return None
    for line in open(path):
        line = line.strip()
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def http(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


# --- gateway ---------------------------------------------------------------
def gateway():
    out = subprocess.run(["pgrep", "-af", "hermes gateway run"],
                         capture_output=True, text=True).stdout.strip()
    pids = [l.split()[0] for l in out.splitlines() if l.strip()]
    return bool(pids), f"PID {','.join(pids) or 'NONE'}"


# --- website ---------------------------------------------------------------
def website():
    st, body = http("https://thehcadaily.com", 15)
    return st == 200, f"HTTP {st}, {len(body):,} bytes"


# --- site pricing sanity ---------------------------------------------------
def pricing():
    _, body = http("https://thehcadaily.com/accelerator.html", 15)
    txt = body.decode("utf-8", "ignore")
    has297 = "$297" in txt
    has279 = "279" in txt
    return (has297 and not has279), f"$297={has297} stale279={has279}"


# --- stripe links live -----------------------------------------------------
def stripe_links():
    st, _ = http("https://buy.stripe.com/9B63cwdp53mIdmR8ZggMw06", 15)  # $297 accelerator
    return st == 200, f"accelerator link HTTP {st}"


# --- stripe catalog price --------------------------------------------------
def stripe_price():
    key = env_val("/data/.stripe.env", "STRIPE_RESTRICTED_KEY")
    if not key:
        return False, "no STRIPE_RESTRICTED_KEY"
    req = urllib.request.Request(
        "https://api.stripe.com/v1/payment_links?limit=20&expand[]=data.line_items",
        headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    for l in d.get("data", []):
        li = l.get("line_items", {})
        for i in (li.get("data", []) if isinstance(li, dict) else []):
            p = i.get("price")
            if isinstance(p, dict) and "Accelerator" in (i.get("description") or ""):
                if p["unit_amount"] == 29700 and l.get("url", "").endswith("9B63cwdp53mIdmR8ZggMw06"):
                    return True, "accelerator = $297.00 USD"
    return False, "no active $297 accelerator link found"


# --- openrouter credits ----------------------------------------------------
def credits():
    key = env_val("/data/.env", "OPENROUTER_API_KEY")
    if not key:
        return False, "no OPENROUTER_API_KEY"
    req = urllib.request.Request("https://openrouter.ai/api/v1/credits",
                                 headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)["data"]
    rem = d["total_credits"] - d["total_usage"]
    return rem > 5, f"${rem:.2f} remaining"


# --- youtube token ---------------------------------------------------------
def youtube():
    tok = json.load(open("/data/youtube_token.json"))
    import urllib.parse
    data = urllib.parse.urlencode({
        "client_id": tok["client_id"], "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen(urllib.request.Request(
            "https://oauth2.googleapis.com/token", data=data), timeout=20) as r:
        access = json.load(r)["access_token"]
    req = urllib.request.Request(
        "https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true",
        headers={"Authorization": f"Bearer {access}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        s = json.load(r)["items"][0]["statistics"]
    return True, f"{int(s['subscriberCount']):,} subs / {int(s['videoCount'])} videos"


# --- browser binary --------------------------------------------------------
def browser():
    binp = "/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
    if not os.path.exists(binp):
        return False, "chromium binary missing"
    with open(binp, "rb") as f:
        head = f.read(2)
    wrapped = head == b"#!"
    if not wrapped:
        return False, "NOT wrapped (run wrap_chromium.sh)"
    out = subprocess.run([binp, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=6000", "--dump-dom", "https://example.com"],
                         capture_output=True, text=True, timeout=120)
    return "Example Domain" in out.stdout, "launches + fetches OK" if "Example Domain" in out.stdout else "launch failed"


# --- cron ------------------------------------------------------------------
def cronjobs():
    out = subprocess.run(["/opt/venv/bin/hermes", "cron", "list"],
                         capture_output=True, text=True, timeout=60).stdout
    names = re.findall(r"Name:\s+(.+)", out)
    return len(names) > 0, f"{len(names)} jobs: {', '.join(n.strip() for n in names[:4])}"


check("Gateway process", gateway)
check("Website live", website)
check("Site pricing ($297, no stale $279)", pricing)
check("Stripe checkout reachable", stripe_links)
check("Stripe price correct", stripe_price)
check("OpenRouter credits > $5", credits)
check("YouTube API + channel", youtube)
check("Browser binary wrapped + runs", browser)
check("Cron jobs registered", cronjobs)

print("\n  HCA DAILY / HERMES HEALTH CHECK")
print("  " + "─" * 62)
fails = 0
for name, ok, detail in results:
    mark = "✅ PASS" if ok else "❌ FAIL"
    if not ok:
        fails += 1
    print(f"  {mark}  {name:<38} {detail}")
print("  " + "─" * 62)
print(f"  {len(results) - fails}/{len(results)} passing"
      + ("" if not fails else f"   <-- {fails} NEEDS ATTENTION"))
print(f"  see /data/OPS_LOG.md for fixes\n")
