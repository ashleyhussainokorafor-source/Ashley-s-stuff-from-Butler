#!/usr/bin/env python3
"""FS Records Personal CRM — daily nudge. Tells Ashley who to reach out to TODAY.
Usage:
  python3 crm_nudge.py            -> list who's due today
  python3 crm_nudge.py --mark NAME -> record that she contacted someone (resets their clock)
"""
import json, os, sys, datetime

BASE = "/data/personal/relationships"
STATE = os.path.join(BASE, "crm_state.json")
today = datetime.date.today()

def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}

# mark a contact as contacted
if len(sys.argv) > 1 and sys.argv[1] == "--mark":
    name = " ".join(sys.argv[2:])
    if not name:
        print("usage: crm_nudge.py --mark \"Name\"")
        sys.exit(1)
    state = load_state()
    state[name] = today.isoformat()
    json.dump(state, open(STATE, "w"), indent=2)
    print(f"✅ {name} marked contacted ({today})")
    sys.exit()

contacts = json.load(open(os.path.join(BASE, "crm.json")))["contacts"]
state = load_state()

def days_ago(d):
    return (today - datetime.date.fromisoformat(d)).days

due = []
for c in contacts:
    last = state.get(c["name"])
    od = last is None or days_ago(last) >= c["cadence_days"]
    if od:
        due.append((c, last))

# milestone/urgent first, then highest health-score bonds
def urgent(c):
    return any(("PREGNANT" in m) or ("NEW" in m) for m in c["milestones"])
due.sort(key=lambda x: (0 if urgent(x[0]) else 1, -(x[0]["health"])))

if not due:
    # silent when nothing due -> cron delivers nothing that day
    sys.exit()
else:
    print("👋 PERSONAL CRM — who to reach out to today\n")
    for c, last in due:
        mil = ("  · " + " / ".join(c["milestones"])) if c["milestones"] else ""
        note = f" — {c['notes']}" if c["notes"] else ""
        status = "never logged" if last is None else f"last {last} ({days_ago(last)}d ago)"
        print(f"• {c['name']} [{c['relation']}] via {c['channel']}")
        print(f"    {status} | due {c['cadence_days']}d{mil}{note}\n")
    print("Mark done: python3 crm_nudge.py --mark \"Name\"")