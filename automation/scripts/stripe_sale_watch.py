#!/usr/bin/env python3
"""First-sale / new-payment watchdog for The HCA Daily.

Checks Stripe for charges newer than the last one we reported. Prints a short
plain-English alert ONLY when a new payment has landed — otherwise prints
nothing, so the cron watchdog pattern holds (empty stdout = no message).

Also warns once if the "open checkout but never paid" count jumps, which is the
signature of a broken checkout rather than a traffic problem.

State: /data/automation/state/stripe_watch_state.json
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ENV = "/data/.stripe.env"
STATE = "/data/automation/state/stripe_watch_state.json"


def key():
    with open(ENV) as f:
        for line in f:
            if line.startswith("STRIPE_RESTRICTED_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("STRIPE_RESTRICTED_KEY not found")


def get(path, k):
    req = urllib.request.Request("https://api.stripe.com/v1/" + path)
    req.add_header("Authorization", "Bearer " + k)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"reported_charges": [], "open_sessions": None}


def main():
    k = key()
    state = load_state()
    try:
        charges = get("charges?limit=100", k)["data"]
        sessions = get("checkout/sessions?limit=100", k)["data"]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        # Transient network/auth trouble — stay quiet, retry next tick.
        print(f"stripe watch could not reach Stripe (will retry): {str(e)[:120]}", file=sys.stderr)
        return 0

    seen = set(state.get("reported_charges", []))
    paid = [c for c in charges if c.get("status") == "succeeded" and c["id"] not in seen]
    open_now = sum(1 for s in sessions if s["status"] == "open")

    lines = []
    if paid:
        for c in sorted(paid, key=lambda z: z["created"]):
            when = datetime.fromtimestamp(c["created"], timezone.utc).strftime("%b %d, %H:%M UTC")
            amount = c["amount"] / 100
            who = (c.get("billing_details") or {}).get("email") or c.get("receipt_email") or "no email captured"
            desc = c.get("description") or "(no description)"
            lines.append(f"💰 NEW PAYMENT — ${amount:,.2f} on {when}\n   {who}\n   {desc}")
        state["reported_charges"] = sorted(seen | {c["id"] for c in paid})

    # A jump in open-but-unpaid checkouts means people are trying to buy and
    # failing — that is a bug, not a marketing problem.
    prev_open = state.get("open_sessions")
    if prev_open is not None and open_now - prev_open >= 3:
        lines.append(
            f"⚠️ {open_now} checkouts are open and unpaid (was {prev_open}). "
            "People may be trying to buy and failing — worth checking the checkout."
        )
    state["open_sessions"] = open_now

    json.dump(state, open(STATE, "w"), indent=2)

    if lines:
        print("\n\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())