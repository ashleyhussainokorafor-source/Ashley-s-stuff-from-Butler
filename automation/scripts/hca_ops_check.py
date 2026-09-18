#!/usr/bin/env python3
"""HCA Daily ops watchdog + log.

Runs every 30 minutes from cron. Three jobs in one pass:

  1. CHECK the money path is intact (site up, paid files still locked,
     checkout links still active, drip still running).
  2. LOG every run, healthy or not, to ops/OPS_LOG.md so a failure has a
     timeline we can read back later.
  3. ALERT on Telegram (via cron stdout) ONLY when something is wrong, when
     it recovers, or when a new lead lands. Healthy runs print nothing.

Design rules:
  - Read-only against the outside world. The only things it writes are its own
    log, its own state, and a status.json snapshot.
  - Never alert twice for the same standing problem: re-alerts are rate-limited
    to once per 6 hours until it clears.
  - A check that cannot reach its target is reported as UNKNOWN, never as OK.
    "Could not measure" must not look like "fine".

State: /data/automation/state/hca_ops_state.json
Log:   /data/business/hca-daily/ops/OPS_LOG.md
Snapshot: /data/business/hca-daily/ops/status.json
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

SITE = "https://thehcadaily.com"
CF_ENV = "/data/.cloudflare.env"
STRIPE_ENV = "/data/.stripe.env"
STATE = "/data/automation/state/hca_ops_state.json"
OPS_DIR = "/data/business/hca-daily/ops"
LOG = os.path.join(OPS_DIR, "OPS_LOG.md")
SNAPSHOT = os.path.join(OPS_DIR, "status.json")
DRIP_STATE = "/data/business/hca-daily/email/drip_state.json"
REALERT_AFTER = 6 * 3600

KV_NS = "048d56b2542343939b4822283e77888b"
ACCOUNT = "7331f696a15eee3fe7bf94f41376f7b8"

# Payment links that must stay ACTIVE (id -> human label, price).
PAYMENT_LINKS = {
    "plink_1UEI8yLxRw5x7PaclgmBGlpq": ("Interview Answer Vault", "$27"),
    "plink_1UGQBNLxRw5x7PacpnekEYiy": ("Career Accelerator", "$297"),
}

# Public pages that must render with real content.
PAGES = {
    "/": 8000,
    "/scorecard": 8000,
    "/pricing": 4000,
    "/vault": 4000,
    "/accelerator": 4000,
    "/playbook": 8000,
    "/learn": 8000,
    "/path": 3000,
    "/practice": 3000,
    "/league": 2000,
    "/resume": 3000,
}

# Gated app entry points. These are PAID (Navigator/Coach sit behind a 30-day
# access cookie), so 402 IS the correct answer and 200 is a LEAK — the exact
# mistake that once served the whole paid app for free at /coach.html.
GATED = ["/app", "/navigator", "/navigator.html", "/coach", "/coach.html",
         "/interview", "/simulator", "/chat"]

# Paid artifacts that must stay locked.
LOCKED = ["/vault.pdf", "/accelerator.pdf", "/vault/download", "/accelerator/download"]
# Free lead magnet that must stay open.
FREE = ["/playbook.pdf"]


def now():
    return datetime.now(timezone.utc)


def read_env(path, name):
    try:
        with open(path) as f:
            for line in f:
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def curl_code(url, timeout=25):
    """Return (http_code, bytes) or (None, 0) if unreachable."""
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{size_download}",
             "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 10,
        ).stdout.split()
        return int(out[0]), int(out[1])
    except Exception:
        return None, 0


def http_json(url, headers):
    req = urllib.request.Request(url)
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def cf_list(prefix):
    key = read_env(CF_ENV, "CLOUDFLARE_API_KEY")
    email = read_env(CF_ENV, "CLOUDFLARE_EMAIL")
    if not key or not email:
        return None
    url = (f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}"
           f"/storage/kv/namespaces/{KV_NS}/keys?prefix={prefix}&limit=1000")
    try:
        d = http_json(url, {"X-Auth-Email": email, "X-Auth-Key": key,
                            "Content-Type": "application/json"})
        if not d.get("success"):
            return None
        return d["result"]
    except Exception:
        return None


def stripe_get(path):
    k = read_env(STRIPE_ENV, "STRIPE_RESTRICTED_KEY")
    if not k:
        return None
    try:
        return http_json("https://api.stripe.com/v1/" + path, {"Authorization": "Bearer " + k})
    except Exception:
        return None


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"failing": {}, "last_alert": {}, "leads": None, "run": 0}


def main():
    t0 = now()
    st = load_state()
    st["run"] = st.get("run", 0) + 1
    checks = []          # (name, status, detail)  status: OK / FAIL / UNKNOWN
    alerts = []

    # --- 1. public pages -------------------------------------------------
    bad_pages = []
    for path, floor in PAGES.items():
        code, size = curl_code(SITE + path)
        if code is None:
            checks.append((f"page {path}", "UNKNOWN", "unreachable"))
            bad_pages.append(f"{path} (unreachable)")
        elif code != 200 or size < floor:
            checks.append((f"page {path}", "FAIL", f"HTTP {code}, {size}b"))
            bad_pages.append(f"{path} (HTTP {code}, {size}b)")
        else:
            checks.append((f"page {path}", "OK", f"HTTP 200 {size}b"))
    if bad_pages:
        alerts.append("🔴 SITE BROKEN — " + "; ".join(bad_pages[:6]))

    # --- 1b. gated app entry points (200 here = paid app given away) -----
    open_gates = []
    for path in GATED:
        code, _ = curl_code(SITE + path)
        if code is None:
            checks.append((f"gate {path}", "UNKNOWN", "unreachable"))
        elif code == 200:
            checks.append((f"gate {path}", "FAIL", "HTTP 200 — OPEN, paid app leaks"))
            open_gates.append(path)
        elif code == 402:
            checks.append((f"gate {path}", "OK", "402 gated"))
        else:
            checks.append((f"gate {path}", "UNKNOWN", f"HTTP {code}"))
    if open_gates:
        alerts.append("🔴 PAID APP OPEN — these entry points are serving the paid "
                      "Navigator/Coach for free: " + ", ".join(open_gates))

    # --- 2. paywall integrity (a leak here is lost revenue) --------------
    leaked = []
    for path in LOCKED:
        code, _ = curl_code(SITE + path)
        if code is None:
            checks.append((f"locked {path}", "UNKNOWN", "unreachable"))
        elif code == 200:
            checks.append((f"locked {path}", "FAIL", "HTTP 200 — LEAKED"))
            leaked.append(path)
        elif code == 403:
            checks.append((f"locked {path}", "OK", "403"))
        else:
            checks.append((f"locked {path}", "UNKNOWN", f"HTTP {code}"))
    if leaked:
        alerts.append("🔴 PAYWALL DOWN — these paid files are downloadable by anyone: "
                      + ", ".join(leaked))
    for path in FREE:
        code, size = curl_code(SITE + path)
        if code != 200 or size < 10000:
            checks.append((f"free {path}", "FAIL", f"HTTP {code}, {size}b"))
            alerts.append(f"🟠 Free lead magnet {path} is not being served (HTTP {code}).")

    # --- 3. checkout links still accepting money -------------------------
    for plink, (label, price) in PAYMENT_LINKS.items():
        d = stripe_get(f"payment_links/{plink}")
        if d is None:
            checks.append((f"checkout {label}", "UNKNOWN", "Stripe unreachable"))
            continue
        if d.get("active") and not d.get("deactivated_at"):
            checks.append((f"checkout {label}", "OK", f"active {price}"))
        else:
            checks.append((f"checkout {label}", "FAIL", "inactive/deactivated"))
            alerts.append(f"🔴 CHECKOUT DEAD — the {label} ({price}) payment link is not active. "
                          "Nobody can buy that product right now.")

    # --- 4. leads + traffic ---------------------------------------------
    keys = cf_list("lead:")
    leads = None
    if keys is None:
        checks.append(("leads", "UNKNOWN", "KV unreachable"))
    else:
        leads = len(keys)
        checks.append(("leads", "OK", f"{leads} total"))
        if st.get("leads") is not None and leads > st["leads"]:
            new = sorted(k["name"] for k in keys)[-max(0, leads - st["leads"]):]
            for n in new:
                stamp = n.split(":")[1] if ":" in n else "?"
                alerts.append(f"🟢 NEW LEAD — captured {stamp}")
            st["lead_alerted"] = True
        st["leads"] = leads

    # --- 5. email drip still alive --------------------------------------
    try:
        age = time.time() - os.path.getmtime(DRIP_STATE)
        if age > 36 * 3600:
            checks.append(("drip", "FAIL", f"state not written in {age/3600:.1f}h"))
            alerts.append("🟠 The email drip has not run in over 36 hours — new leads "
                          "are not getting their follow-up emails.")
        else:
            checks.append(("drip", "OK", f"last write {age/3600:.1f}h ago"))
    except OSError:
        checks.append(("drip", "UNKNOWN", "no state file"))

    # --- 6. new payments (logged here, alerted by the sale watcher) ------
    charges = stripe_get("charges?limit=100")
    sales_line = ""
    if charges is not None:
        seen = set(st.get("charges", []))
        paid = [c for c in charges["data"] if c.get("status") == "succeeded"]
        new_paid = [c for c in paid if c["id"] not in seen]
        st["charges"] = sorted(seen | {c["id"] for c in paid})
        st["lifetime_cents"] = sum(c["amount"] for c in paid)
        st["sales_count"] = len(paid)
        sales_line = f"sales={len(paid)} revenue=${st['lifetime_cents']/100:,.2f}"
        if new_paid:
            alerts.append(f"💰 NEW SALE — {len(new_paid)} new payment(s), "
                          f"${sum(c['amount'] for c in new_paid)/100:,.2f}")
        checks.append(("stripe charges", "OK", sales_line))
    else:
        checks.append(("stripe charges", "UNKNOWN", "unreachable"))

    # --- alert rate-limiting -------------------------------------------
    failing = [n for n, s, _ in checks if s == "FAIL"]
    loud = []
    for a in alerts:
        # Key on the alert's headline only — the detail (byte counts, page lists)
        # changes between runs and must not defeat the rate-limit.
        key = a.split("—")[0].strip()[:48]
        last = st.setdefault("last_alert", {}).get(key, 0)
        recovered = failing == [] and key not in st.get("failing_keys", [])
        if key.startswith("🟢") or key.startswith("💰") or recovered or time.time() - last > REALERT_AFTER:
            loud.append(a)
            st["last_alert"][key] = time.time()
    st["failing_keys"] = [c for c in (a.split("—")[0].strip()[:48] for a in alerts)
                          if c.startswith("🔴") or c.startswith("🟠")]

    # --- log -------------------------------------------------------------
    os.makedirs(OPS_DIR, exist_ok=True)
    fails = [c for c in checks if c[1] == "FAIL"]
    unknowns = [c for c in checks if c[1] == "UNKNOWN"]
    verdict = "OK" if not fails and not unknowns else ("FAIL" if fails else "PARTIAL")
    pages_ok = len([c for c in checks if c[0].startswith("page ") and c[1] == "OK"])
    gates_ok = len([c for c in checks if c[0].startswith("gate ") and c[1] == "OK"])
    summary = (f"pages={pages_ok}/{len(PAGES)} gates={gates_ok}/{len(GATED)}"
               f" paywall={len(LOCKED)-len(leaked)}/{len(LOCKED)}"
               f" leads={leads if leads is not None else '?'}"
               f" {sales_line or 'sales=?'}")
    with open(LOG, "a") as f:
        if not os.path.exists(LOG) or os.path.getsize(LOG) == 0:
            f.write("# HCA Daily — Ops Log\n\n"
                    "Automated health checks every 30 min, newest entries at the bottom.\n"
                    "Format: `UTC time | verdict | what was measured`\n"
                    "FAIL = something that costs money is broken. UNKNOWN = could not measure.\n\n")
        f.write(f"- **{t0.strftime('%Y-%m-%d %H:%M')} UTC** | `{verdict}` | {summary}\n")
        for n, s, d in fails + unknowns:
            f.write(f"    - {s} · {n} · {d}\n")
        if st.get("sales_count"):
            f.write(f"    - lifetime: {st['sales_count']} sales, "
                    f"${st['lifetime_cents']/100:,.2f}\n")

    json.dump({
        "checked_at": t0.isoformat(),
        "verdict": verdict,
        "run": st["run"],
        "leads": leads,
        "sales_count": st.get("sales_count"),
        "revenue_usd": round(st.get("lifetime_cents", 0) / 100, 2),
        "failing": [{"check": n, "detail": d} for n, s, d in fails],
        "unknown": [{"check": n, "detail": d} for n, s, d in unknowns],
        "checks": [{"name": n, "status": s, "detail": d} for n, s, d in checks],
    }, open(SNAPSHOT, "w"), indent=2)

    json.dump(st, open(STATE, "w"), indent=2)

    if loud:
        print("\n".join(loud + [f"({len(fails)} failing check(s) — full log: ops/OPS_LOG.md)"] if fails else loud))
    return 0


if __name__ == "__main__":
    sys.exit(main())
