# HCA Daily — Ops Log

Automated health checks every 30 min, newest entries at the bottom.
Format: `UTC time | verdict | what was measured`
FAIL = something that costs money is broken. UNKNOWN = could not measure.

- **2026-09-18 17:56 UTC** | `OK` | pages=12/12 paywall=4/4 leads=2 sales=0 revenue=$0.00

## Changes log (human entries)

- **2026-09-18 18:00 UTC** — Ops watchdog built and armed (every 30 min). Watches:
  site pages (12), paywall integrity (4 paid files must be 403), both Stripe payment
  links still active, KV lead count, drip freshness, Stripe sales. Logs every run to
  this file; alerts only on a problem, a recovery, a new lead or a sale. Baseline at
  first run: `OK | pages=12/12 paywall=4/4 leads=2 sales=0 revenue=$0.00`.
- **2026-09-18 18:00 UTC** — Incident playbook written: `ops/INCIDENT_PLAYBOOK.md`
  (what breaks, what it costs, how it gets fixed).
- **2026-09-18 18:00 UTC** — Shorts pipeline built: `shorts/queue.json` is the state,
  `automation/scripts/hca_short_publish.py` uploads due posts, cron every 6 h.
  Safety: uploads UNLISTED while `auto_publish` is false; requires an explicit
  'publish <id>' to go live. Verified: dry-run on an empty queue is a silent no-op.
- **2026-09-18 18:00 UTC** — Lead audit: both leads in KV are self-tests
  (`ashleyhussainokorafor@gmail.com` and `ashley+audittest@thehcadaily.com`, source
  `audit-test`, ua `cli`). There are still **0 real leads**. Pageviews 2026-09-18: 38
  homepage hits, nearly all from us, not organic. The bottleneck remains reach.

- **2026-09-18 18:05 UTC** | `UPLOADED` | Short #001 "MHA or MBA? You're Asking the Wrong Question"
  → https://www.youtube.com/shorts/HHAiukzmPs8 (privacyStatus=**unlisted**, awaiting Ashley's go-ahead).
  Verified independently of the builder: ffprobe 1080x1920 h264 yuv420p 30fps, 37.18s; YouTube reports
  PT38S, category 27, uploadStatus=processed, description line 1 = free scorecard CTA with UTM
  `utm_campaign=short001`. Safe-zone gate re-run by hand: 13/13 frames inside y476-1344 (band 380-1450), ALL PASS.
  NOTE: vision tooling is not configured on this host, so the visual gate is a pixel bounding-box check
  plus a human look from Ashley. Queued in `shorts/queue.json` as `awaiting_approval`.
- **2026-09-18 18:19 UTC** | `PUBLISHED` | Short 'MHA or MBA? You're Asking the Wrong Question #Shorts' (youtube.com/shorts/HHAiukzmPs8) went public; YouTube now reports unlisted
- **2026-09-18 18:22 UTC** | `SHORT-BUILD` | short002: synthesizing voiceover (78 words)
- **2026-09-18 18:22 UTC** | `SHORT-BUILD` | short002: audio=32.14s  wps=0.4120
- **2026-09-18 18:22 UTC** | `SHORT-BUILD` | short002: built 16 frames -> 32.14s  787KB
- **2026-09-18 18:22 UTC** | `SHORT-BUILD` | short002: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:23 UTC** | `SHORT-BUILD` | short002: synthesizing voiceover (78 words)
- **2026-09-18 18:24 UTC** | `SHORT-BUILD` | short002: audio=32.14s  wps=0.4120
- **2026-09-18 18:24 UTC** | `SHORT-BUILD` | short002: built 16 frames -> 32.14s  754KB
- **2026-09-18 18:24 UTC** | `SHORT-BUILD` | short002: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:24 UTC** | `UPLOADED` | Short 'Do You Actually Need a Clinical Background? #Shorts' → youtube.com/shorts/1Z7nOlwj0QA (privacyStatus=public)
- **2026-09-18 18:25 UTC** | `SHORT-BUILD` | short003: synthesizing voiceover (51 words)
- **2026-09-18 18:25 UTC** | `SHORT-BUILD` | short003: audio=22.32s  wps=0.4376
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short003: built 13 frames -> 22.32s  510KB
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short003: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short004: synthesizing voiceover (53 words)
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short004: audio=28.87s  wps=0.5448
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short004: built 16 frames -> 28.87s  653KB
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short004: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short005: synthesizing voiceover (60 words)
- **2026-09-18 18:26 UTC** | `SHORT-BUILD` | short005: audio=24.74s  wps=0.4124
- **2026-09-18 18:26 UTC** | `OK` | pages=12/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
- **2026-09-18 18:27 UTC** | `SHORT-BUILD` | short005: built 19 frames -> 24.74s  571KB
- **2026-09-18 18:27 UTC** | `SHORT-BUILD` | short005: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:35 UTC** | `SHORT-BUILD` | short006: synthesizing voiceover (66 words)
- **2026-09-18 18:35 UTC** | `SHORT-BUILD` | short006: audio=29.42s  wps=0.4458
- **2026-09-18 18:35 UTC** | `SHORT-BUILD` | short006: built 19 frames -> 29.42s  713KB
- **2026-09-18 18:35 UTC** | `SHORT-BUILD` | short006: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 18:57 UTC** | `OK` | pages=12/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
- **2026-09-18 19:28 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=1 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 19:59 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=1 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 20:30 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=1 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 20:46 UTC** | `COMMENT-REPLY` | replied to 6 (failed 0); types {'story': 1, 'opinion': 5}
- **2026-09-18 20:56 UTC** | `SHORT-BUILD` | short007: synthesizing voiceover (74 words)
- **2026-09-18 20:56 UTC** | `SHORT-BUILD` | short007: audio=34.70s  wps=0.4690
- **2026-09-18 20:57 UTC** | `SHORT-BUILD` | short007: built 19 frames -> 34.70s  838KB
- **2026-09-18 20:57 UTC** | `SHORT-BUILD` | short007: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 20:57 UTC** | `SHORT-BUILD` | short007: synthesizing voiceover (39 words)
- **2026-09-18 20:58 UTC** | `SHORT-BUILD` | short007: audio=20.66s  wps=0.5298
- **2026-09-18 20:58 UTC** | `SHORT-BUILD` | short007: built 12 frames -> 20.66s  473KB
- **2026-09-18 20:58 UTC** | `SHORT-BUILD` | short007: queued as ready (auto_publish=True) -> https://youtube.com/shorts/... after publish
- **2026-09-18 21:01 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 21:32 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 22:03 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
- **2026-09-18 22:34 UTC** | `FAIL` | pages=10/12 paywall=4/4 leads=2 sales=0 revenue=$0.00
    - FAIL · page /navigator · HTTP 402, 1594b
    - FAIL · page /coach · HTTP 402, 1554b
