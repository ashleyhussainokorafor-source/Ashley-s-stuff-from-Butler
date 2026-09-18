# Agent Operating Strategy — Two Agents, One Workspace

**Author:** Butler (Situation Room)
**Date:** 2026-09-18
**Scope:** how the agents sharing `/data` stop duplicating work

---

## The evidence this is built from

Every rule below exists because it actually happened today, in one afternoon:

| # | What happened | Cost |
|---|---|---|
| 1 | Butler rebuilt the entitlement layer the hcadaily session had already built **and deployed** | A full build thrown away |
| 2 | Both agents wrote `ops/COORDINATION.md` within minutes of each other | Butler's thinner version clobbered theirs |
| 3 | Both agents seeded `nnamdiokorafor@gmail.com` as a lead **73 seconds apart** | Duplicate record → he'd get every drip email twice |
| 4 | Both agents built a comment-reply feature for the same request | Redundant implementation |
| 5 | git: `ahead 14, behind 6` and **growing** — three pushes in one hour | 3 add/add conflicts, none of my work pushed |
| 6 | The health monitor flags `/navigator` 402 as FAIL | A correct change reported as an outage |

**Root cause, in one line:** both agents start from *"what should exist?"* instead of
*"what already exists?"* — in a shared working tree, on a shared branch, with no reservation.

---

## The five rules

### Rule 1 — Split the working trees (this is the big one)

The real race is not decisions, it's **two processes writing the same files at the same moment**.
Today the working tree changed under both of us mid-command.

- **`/data` is the PRIMARY tree. Exactly one agent writes it.**
- Every other agent works in `/data/worktrees/<agent>/` on its own branch.
- Nobody edits a file in a tree they don't own.

This alone removes failures #2 and #5.

### Rule 2 — One integrator, branch discipline

- Agents commit to `agent/<name>` branches. **Never straight to `main`.**
- **One integrator** merges to `main`. For HCA Daily the integrator is **Butler**.
- Integrator merges on a schedule (e.g. every 30 min), not on every commit.

This removes failure #5. A linear free-for-all on `main` cannot be reconciled faster
than two agents can diverge.

### Rule 3 — Hard ownership, not shared ownership

Shared ownership of a file means nobody owns it. Assign every artifact to exactly one agent:

| Artifact | Owner |
|---|---|
| `worker/src/index.ts`, `wrangler.jsonc`, deploys | Butler |
| Stripe config, prices, links, coupons | Butler |
| Cloudflare KV, DNS, secrets | Butler |
| `worker/assets/*.html` | Butler |
| `shorts/**`, `content/**`, Shorts pipeline | hcadaily |
| `automation/scripts/hca_short_*.py` | hcadaily |
| `ops/status.json`, `ops/OPS_LOG.md`, ops monitor | hcadaily |
| `ops/COORDINATION.md` | hcadaily |

**To touch another agent's artifact you must claim it first and get an ack.**
If you disagree with a change in someone's lane, write the finding and tell Ashley —
do not edit it.

### Rule 4 — Read-before-write gate (mandatory, mechanical)

Run this before ANY edit. It is not optional and not a judgement call:

```bash
bash /data/scripts/preflight.sh <path-you-are-about-to-edit> <your-agent-name>
```

It refuses to pass if: the file changed in the last 15 minutes, an unmerged branch
touches it, or someone holds the lock. If it fails, **stop and ask Ashley.**

This single gate prevents failures #1, #2 and #4.

### Rule 5 — The shared state file is a contract

`ops/status.json` is what other agents trust. Two obligations:

- **The writer keeps it current.** A stale status file is worse than none.
- **The checks must assert the right thing.** Today's monitor calls a 402 paywall a
  failure — but 402 is the *correct, intended* response for a gated product. A monitor
  that cries wolf trains everyone to ignore it, which is how a real outage gets missed.

---

## Escalation: the 60-minute rule

- Lock/claim held **under 60 min** → the holder is active. **Stop. Ask Ashley who proceeds.**
- Lock held **over 60 min** → assume the holder died. Say so in the chat, then take it over.
- **Two agents both believe they own a task** → do not race. Post the conflict with evidence
  (timestamps, file mtimes, commit SHAs) and let Ashley decide. That has been faster today
  than every race we ran.

---

## Practical loop for each agent

```
1. preflight.sh <file> <me>        # refuses if someone else is mid-flight
2. deploy_lock.sh acquire <scope> <me>
3. ...do the work...
4. verify against the live system, not the local file
5. deploy_lock.sh release <scope> <me>
6. commit to agent/<me>, push the branch
7. post a one-line status to the chat
```

---

## What this costs and what it buys

The rules add roughly two commands per task.

In exchange, today's six failures become structurally impossible:
two writers cannot share a tree, two agents cannot both merge to `main`,
and no agent can start work without being told someone is already on it.

**The honest alternative** is what we did today: both agents fast, and roughly a third
of the work discarded.