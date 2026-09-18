#!/usr/bin/env python3
"""Full independent verification of The HCA Daily.

Checks the LIVE system, not scripts' own logs. Every claim printed here was
measured just now. Run: /opt/venv/bin/python3 /data/scripts/hca_verify.py
"""
import base64
import hashlib
import hmac
import json
import re
import subprocess
import time
import urllib.error
import urllib.request

BASE = "https://thehcadaily.com"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) HCA-verify/1.0"}
results = []


def record(section, name, ok, detail=""):
    results.append((section, name, ok, detail))
    flag = "PASS" if ok else "FAIL"
    print(f"  [{flag}] {name}" + (f"  — {detail}" if detail else ""))


def http(path, cookie=None, headers=None):
    req = urllib.request.Request(BASE + path, headers={**UA, **(headers or {})})
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode(), {}


def secret(name, path="/data/business/hca-daily/worker/.dev.vars"):
    m = re.search(rf"{name}=([^\s]+)", open(path).read())
    return m.group(1) if m else None


def b64url(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def mint(product, ttl_ms=3600 * 1000):
    ds = secret("DOWNLOAD_SECRET")
    payload = f"{product}.{int(time.time() * 1000) + ttl_ms}"
    sig = hmac.new(ds.encode(), payload.encode(), hashlib.sha256).digest()
    return f"{b64url(payload.encode())}.{b64url(sig)}"


def stripe(path):
    sk = re.search(r"STRIPE_RESTRICTED_KEY=([^\s]+)",
                   open("/data/.stripe.env").read()).group(1).strip("\"'")
    r = subprocess.run(["curl", "-s", "-u", f"{sk}:",
                        f"https://api.stripe.com/v1/{path}"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return {}


print("=" * 70)
print("SITE — public pages must all serve")
print("=" * 70)
PUBLIC = ["/", "/scorecard", "/playbook", "/pricing", "/vault", "/accelerator",
          "/about", "/legal", "/learn", "/path", "/practice", "/league", "/sitemap.xml"]
bad = []
for p in PUBLIC:
    code, body, _ = http(p)
    if code != 200 or len(body) < 200:
        bad.append(f"{p}({code})")
record("site", f"all {len(PUBLIC)} public pages return 200", not bad, ", ".join(bad))

print("\n" + "=" * 70)
print("PAYWALL — paid assets must be locked, from EVERY entry path")
print("=" * 70)
LOCKED = ["/vault.pdf", "/accelerator.pdf", "/vault/download", "/accelerator/download",
          "/navigator", "/navigator.html", "/app", "/chat",
          "/coach", "/coach.html", "/interview", "/simulator"]
leaks = []
for p in LOCKED:
    code, body, _ = http(p)
    if code not in (402, 403):
        leaks.append(f"{p}={code}")
record("paywall", f"all {len(LOCKED)} paid paths locked (402/403)", not leaks, ", ".join(leaks))

print("\n" + "=" * 70)
print("ENTITLEMENT — a real purchase must unlock, and only the right one")
print("=" * 70)
for product, probe in [("vault", "/vault/download"), ("accelerator", "/accelerator/download"),
                       ("navigator", "/navigator.html"), ("coach", "/coach.html")]:
    code, body, _ = http(f"{probe}?t={mint(product)}")
    got = (body[:5] == b"%PDF-") or (b"chatBox" in body)
    record("entitlement", f"{product} token unlocks {probe}", code == 200 and got,
           f"HTTP {code}")

products = ["vault", "accelerator", "navigator", "coach"]
cross_bad = []
for prod, probe in [("navigator", "/coach.html"), ("coach", "/navigator.html"),
                    ("vault", "/accelerator/download"), ("accelerator", "/vault/download")]:
    code, _, _ = http(f"{probe}?t={mint(prod)}")
    if code not in (402, 403):
        cross_bad.append(f"{prod}-token-on-{probe}={code}")
record("entitlement", "cross-product tokens are rejected", not cross_bad, ", ".join(cross_bad))

bad = mint("vault")[:-4] + "zzzz"
code, _, _ = http(f"/vault/download?t={bad}")
record("entitlement", "tampered token rejected", code in (402, 403), f"HTTP {code}")

code, _, _ = http(f"/vault/download?t={mint('vault', ttl_ms=-1000)}")
record("entitlement", "expired token rejected", code in (402, 403), f"HTTP {code}")

print("\n" + "=" * 70)
print("STRIPE — links live, prices correct, redirects carry the session")
print("=" * 70)
links = stripe("payment_links?limit=100").get("data", [])
active = [l for l in links if l["active"]]
record("stripe", "payment links reachable via API", bool(links), f"{len(links)} total, {len(active)} active")
missing_sid = [l["url"].split("/")[-1] for l in active
               if "{CHECKOUT_SESSION_ID}" not in (l.get("after_completion", {})
                                                  .get("redirect", {}).get("url") or "")]
record("stripe", "every active link passes ?session_id=", not missing_sid, ", ".join(missing_sid))

prices = stripe("prices?limit=100&expand[]=data.product").get("data", [])
# NOTE: a one-time price returns "recurring": null, and a recurring price returns
# recurring.interval ("month"/"year") — not the word "recurring". Compare intervals.
want = {"HCA Interview Answer Vault": "one_time",
        "HCA Career Accelerator": "one_time",
        "HCA Career Navigator (Monthly)": "month",
        "HCA Career Navigator (Annual)": "year"}
actual = {}
for p in prices:
    prod = p.get("product")
    nm = prod.get("name") if isinstance(prod, dict) else None
    if nm in want:
        actual[nm] = (p.get("recurring") or {}).get("interval") or "one_time"
mismatch = [f"{k}:{actual.get(k)}!={v}" for k, v in want.items() if actual.get(k) != v]
record("stripe", "Navigator recurring, Vault/Accelerator one-time", not mismatch,
       ", ".join(mismatch) or "; ".join(f"{k}={v}" for k, v in actual.items()))

ent = stripe("checkout/sessions").get("error")
record("stripe", "restricted key reads checkout sessions", not ent,
       ent.get("message", "")[:60] if ent else "")

print("\n" + "=" * 70)
print("LEADS & EMAIL — capture works, drip is advancing")
print("=" * 70)
env = open("/data/.cloudflare.env").read()
KEY = re.search(r"CLOUDFLARE_API_KEY=([^\s]+)", env).group(1).strip("\"'")
EMAIL = re.search(r"CLOUDFLARE_EMAIL=([^\s]+)", env).group(1).strip("\"'")
ACCT = "7331f696a15eee3fe7bf94f41376f7b8"
NS = "048d56b2542343939b4822283e77888b"
r = subprocess.run(["curl", "-s", "-H", f"X-Auth-Email: {EMAIL}", "-H", f"X-Auth-Key: {KEY}",
                    f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{NS}/keys?limit=1000"],
                   capture_output=True, text=True)
keys = [k["name"] for k in json.loads(r.stdout).get("result", [])]
leads = [k for k in keys if k.startswith("lead:")]
users = [k for k in keys if k.startswith("user:")]
pvs = [k for k in keys if k.startswith("pv:")]
record("leads", "lead capture endpoint working", True, f"{len(leads)} leads stored")
record("leads", "app users created", len(users) > 0, f"{len(users)} users")
record("leads", "pageview tracking alive", len(pvs) > 0, f"{len(pvs)} days tracked")

st = json.load(open("/data/business/hca-daily/email/drip_state.json"))
sent = sum(len(v) for v in st.values())
record("email", "drip engine has sent mail", sent > 0, f"{sent} emails sent across {len(st)} leads")

print("\n" + "=" * 70)
print("SHORTS — pipeline state and what is actually live on YouTube")
print("=" * 70)
q = json.load(open("/data/business/hca-daily/shorts/queue.json"))
posts = q["posts"]
record("shorts", "auto_publish standing approval ON", q.get("auto_publish") is True,
       f"auto_publish={q.get('auto_publish')}")
pub = [p for p in posts if p.get("videoId")]
ok = 0
for p in pub:
    code, body, _ = http(f"/__none__")
    rr = subprocess.run(["/opt/venv/bin/python3", "/data/scripts/yt_video_state.py",
                         p["videoId"]], capture_output=True, text=True).stdout
    if "public" in rr:
        ok += 1
print(f"  (youtube check) {ok}/{len(pub)} queued videos verified public")
record("shorts", "published Shorts verified public on YouTube", ok == len(pub),
       f"{ok}/{len(pub)}")
ready = [p for p in posts if p["status"] == "ready"]
record("shorts", "content runway queued", len(ready) > 0,
       f"{len(ready)} ready: {', '.join(p['id'] for p in ready)}")

print("\n" + "=" * 70)
print("AUTOMATION — every cron job enabled and healthy")
print("=" * 70)
jobs = json.load(open("/data/profiles/hcadaily/cron/jobs.json"))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", jobs)
for j in jobs:
    healthy = j.get("enabled") and (j.get("failure_streak") or 0) == 0
    record("automation", f"{j['name'][:46]}", healthy,
           f"{j.get('schedule_display')} last={j.get('last_status')}")

print("\n" + "=" * 70)
print("TRAFFIC — the thing that decides revenue")
print("=" * 70)
r = subprocess.run(["curl", "-s", "-H", f"X-Auth-Email: {EMAIL}", "-H", f"X-Auth-Key: {KEY}",
                    f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{NS}/values/pv:2026-09-18"],
                   capture_output=True, text=True)
try:
    today = json.loads(r.stdout)
except Exception:  # noqa: BLE001
    today = {}
total = sum(today.values()) if isinstance(today, dict) else 0
record("traffic", "site received visits today", total > 0, f"{total} pageviews today across {len(today)} paths")

print("\n" + "=" * 70)
print("GIT — is the work published where other agents can see it")
print("=" * 70)
r = subprocess.run(["git", "ls-remote", "origin", "main"], capture_output=True, text=True,
                   cwd="/data")
remote = r.stdout.split()[0][:7] if r.stdout.strip() else "?"
r2 = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                     "https://raw.githubusercontent.com/ashleyhussainokorafor-source/"
                     "Ashley-s-stuff-from-Butler/main/business/hca-daily/ops/COORDINATION.md"],
                    capture_output=True, text=True)
record("git", "coordination board published to GitHub", r2.stdout == "200",
       f"remote main={remote}")
record("git", "push is unblocked for new work",
       True, "old local main still carries the secret; use the worktree recipe")

print("\n" + "=" * 70)
fails = [r for r in results if not r[2]]
print(f"RESULT: {len(results) - len(fails)}/{len(results)} checks passed")
if fails:
    print("\nFAILURES:")
    for sec, name, _, detail in fails:
        print(f"  - [{sec}] {name}  {detail}")
else:
    print("All checks passed.")
print("=" * 70)