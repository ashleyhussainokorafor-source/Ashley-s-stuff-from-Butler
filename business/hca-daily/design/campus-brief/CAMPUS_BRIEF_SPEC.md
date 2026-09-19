# Campus Brief — homepage design spec

**System:** Campus Brief · **Page:** `/` (homepage) · **Owner of the live file:** Butler (`worker/assets/index.html`)
**Spec + reference build by:** hcadaily bot (growth) · **Date:** 2026-09-19

> **Read this first.** While this spec was being written, two agents were building the same
> page. Butler has the live file and produced the Campus Brief asset set (`cb-*` images and
> `cb-drill-loop.mp4`) at 15:47–15:52 UTC. My reference build is parked at
> `design/campus-brief/index.campus-brief.hcadaily-bot.html` and I reverted
> `worker/assets/index.html` to the committed version so Butler's lane is exactly as they
> left it. **One owner, one file.** Use this spec for the copy, the section order, the
> component contracts and the image/video briefs; use Butler's assets for the media.

---

## 1 · Wireframe

```
┌──────────────────────────────────────────────────────────────────────────┐
│ STICKY NAV   The HCA Daily    Scorecard How it works Path About          │
│                                        [Log in]  [Start the scorecard]   │
└──────────────────────────────────────────────────────────────────────────┘

 1  HERO  (2-col, 56px gap, 64/72px padding)
   ┌───────────────────────────┐   ┌──────────────────────────────┐
   │ BUILT FOR EARLY-CAREER…   │   │  ╭────────────────────────╮  │
   │                           │   │  │  product frame 4:5     │  │
   │ Walk in speaking          │   │  │  poster → video loop   │  │
   │ their language.           │   │  │  (autoplay muted)      │  │
   │                           │   │  │        ▶ Watch the     │  │
   │ Hiring managers listen    │   │  │          drill         │  │
   │ for wRVUs, days in A/R,   │   │  ╰────────────────────────╯  │
   │ and no-show rates …       │   │   6,000+ healthcare leaders  │
   │                           │   │   · 5 min/day                │
   │ [Take the 90-second …]    │   └──────────────────────────────┘
   │ Get the free playbook  →  │      ← text link, NOT a 2nd button
   └───────────────────────────┘
   one CTA · no email field · no dual capture

 2  LIVE DRILL   (2-col: label left, widget right)
   "The unit"  →  This is a drill.
                         ┌──────────────────────────────────────┐
                         │ Your A/R days is 48. What does that  │
                         │ mean for cash?                       │
                         │ ○ Cash is sitting uncollected ~48 d  │ ← correct
                         │ ○ Patients wait 48 days …            │
                         │ ○ It takes 48 days to post a payment │
                         │ ▏ Why hiring managers care: …        │ ← appears on tap
                         └──────────────────────────────────────┘

 3  PATH   title → 4 nodes, each: icon · label · status · progress bar
    ▣ Resume Metrics          Quantify impact, not duties.   [In progress] ▓▓░░░
    ▣ Operational Vocabulary  The terms directors use …      [In progress] ▓▓▓▓░
    ▢ LinkedIn & Visibility   Opens at 80% vocabulary …      [Locked]      ░░░░░
    ▢ Interview Delivery      Ends with a recorded mock …    [Locked]      ░░░░░

 4  WHY   title → 3 image+caption beats, then founder strip
    [grads]              [study table]        [laptop drill]
    You earn the degree. Then the interview   Five minutes a day
                         asks for metrics.    closes the gap.
    ┌────────────────────────────────────────────────────────────┐
    │ [headshot] Trained by someone who sat on the other side …   │
    └────────────────────────────────────────────────────────────┘

 5  LOOP   01 Score · 02 Drill · 03 Review · 04 Unlock   (icon + one word each)
           Retrieval practice and spaced repetition. That's why it sticks.

 6  OFFERS   two cards, equal weight, no urgency
    Vault $27 lifetime · 156-script library      → [Get the Vault]
    Career Accelerator $297 · plan + advisory    → [See the Accelerator]

 7  FAQ    four accordion rows

    FOOTER (navy)  logo · copyright · About / Pricing / Playbook / Terms

  MOBILE ≤980px: hamburger menu + persistent bottom bar
                 [ Start the 90-second scorecard ]
```

---

## 2 · Visual spec

### Tokens
| Token | Value | Use |
|---|---|---|
| `--off` | `#F7F6F2` | page background |
| `--ink` | `#0B1B2B` | body + headline text |
| `--navy` | `#132337` | footer, dark surfaces, icon tiles |
| `--teal` | `#2A9D8F` | **primary action** + accent |
| `--teal-dk` | `#1F7A6F` | hover, inline links |
| `--gold` | `#C9A227` | **status chips only** — never a button |
| `--muted` | `#5A6673` | secondary copy |
| `--line` | `#E3E1DA` | borders, dividers |

Max 2 accent colours on any screen. Gold appears at most as a small uppercase chip.
Contrast: ink on off-white ≈ 15:1; white on teal ≈ 3.6:1 → teal is used at ≥16px bold
or as a fill behind white text at 16px+, never for thin small text.

### Type
| Role | Family | Size / line | Notes |
|---|---|---|---|
| H1 | Sora 800 | 52 / 1.08 | tracking −0.03em, max 8 words |
| H2 | Sora 700 | 36 / 1.12 | one per section |
| H3 / card title | Sora 700 | 17–23 | letter-spacing −0.02em |
| Body | Inter 400 | 17/1.6 | never more than 2 lines under a headline |
| UI / nav | Inter 500–600 | 15–16 | 44px min target |
| Metric / numeric | IBM Plex Mono 600 | 15–24 | only for real metrics (A/R days, wRVUs) |
| Eyebrow | Inter 700 | 12, +2px tracking | uppercase, teal |

### Spacing & shape
Section padding 76px desktop / 54px mobile. Container 1100px, 24px gutters.
Radii: 12 (controls) · 14–16 (cards) · 18–20 (product frame). Shadows:
`0 14px 40px rgba(11,27,43,.07)` for cards, `0 24px 60px rgba(11,27,43,.18)` for the hero frame.

### Motion
Scroll reveals: 10px rise + fade, 500ms ease-out, fired once via IntersectionObserver.
Hero video: autoplay, muted, loop, `playsinline`. Nothing bounces, nothing counts down.

### Accessibility
Visible focus ring `3px solid teal` with 3px offset. All controls ≥44px tall.
Landmarks: `nav / header / section / footer`; one `h1`; drill options are real `<button>`s
with a `data-i` index; accordion is native `<details>`.

### Performance (LCP rule)
The hero **poster image is the LCP element** — it is an `<img>` with width/height set,
and the video carries `preload="none"`, is upgraded to `preload="auto"` on
`requestIdleCallback`, and hides itself on `error`. The hero must never wait on media.

---

## 3 · Microcopy (final, per section)

| # | Element | Copy |
|---|---|---|
| 1 | Eyebrow | Built for early-career healthcare admin |
| 1 | H1 | **Walk in speaking their language.** |
| 1 | Subhead | Hiring managers listen for wRVUs, days in A/R, and no-show rates — fluency beats years on a resume. |
| 1 | Primary CTA | Take the 90-second Scorecard |
| 1 | Text link | Get the free playbook |
| 1 | Proof line | 6,000+ healthcare leaders · 5 min/day |
| 2 | Title | This is a drill. |
| 2 | Question | Your A/R days is 48. *What does that mean for cash?* |
| 2 | Options | Cash is sitting uncollected ~48 days · Patients wait 48 days for appointments · It takes 48 days to post a payment |
| 2 | Why line | **Why hiring managers care:** A/R days is a liquidity lever. Quoting it correctly signals you think in cash-cycle terms. |
| 3 | Title | Four skills between you and the offer. |
| 3 | Nodes | Resume Metrics — Quantify impact, not duties. *(In progress)* · Operational Vocabulary — The terms directors use out loud. *(In progress)* · LinkedIn & Visibility — Opens at 80% vocabulary fluency. *(Locked)* · Interview Delivery — Ends with a recorded mock interview. *(Locked)* |
| 4 | Title | You earn the degree. Nobody teaches you the words. |
| 4 | Beats | You earn the degree. *Four years of work you can point to.* · Then the interview asks for metrics. *Coursework rarely teaches you to say them out loud.* · Five minutes a day closes the gap. *Until the language is yours.* |
| 4 | Founder | Trained by someone who sat on the other side of the table. — Dr. Ashley Hussain-Okorafor, DBA, former lecturer and hiring-side administrator. |
| 5 | Title | Score · Drill · Review · Unlock |
| 5 | Support | Retrieval practice and spaced repetition. That's why it sticks. |
| 6 | Title | Two ways to go further |
| 6 | Card A | Vault · $27 lifetime · 156-script library. Search by question type, then drill it. → Get the Vault |
| 6 | Card B | Career Accelerator · $297 one time · Adaptive plan plus advisory — résumé, LinkedIn, negotiation. → See the Accelerator |
| 7 | FAQ | **Is this 1:1 coaching?** No — self-paced and automated. **How long until I feel a difference?** Most learners notice it within 14 days of daily drills. **Can I try before paying?** Yes — scorecard and first drills are free. **What roles does this cover?** Practice managers, directors, supervisors and coordinators across access, revenue cycle, HIM, operations, quality and long-term care. |
| — | Mobile bar | Start the 90-second scorecard |

**Banned and absent:** game-changer, unlock your potential, don't miss out, stacked
exclamation marks, fake scarcity, strikethrough pricing, countdown timers.

---

## 4 · Image brief — six shots

Shot to the Campus Brief mood: candid, mid-20s, natural light, no eye contact with camera
unless it is a portrait. **No pointing-at-laptop, no handshake-on-white, no boardroom.**

| # | Slug | Shot | Crop | Where it goes |
|---|---|---|---|---|
| 1 | `cb-campus-walk` | Two or three students walking across campus, mid-conversation, backpacks, motion in the frame | 16:9 | hero fallback / social card |
| 2 | `cb-lounge-laptop` | One student, laptop open on a lounge chair, half-smiling at the screen | 4:3 | beat 3 · loop section |
| 3 | `cb-mock-interview` | Over-the-shoulder: a student answering across a table, an empty chair in the foreground | 4:3 | beat 2 · interview-specific |
| 4 | `cb-whiteboard-ar` | Whiteboard with real healthcare metrics handwritten — "A/R days 48", "no-show 12%", "wRVU 4,200" | 3:2 | drill section |
| 5 | `cb-quiet-library` | Single student reading in a quiet library aisle, shallow depth of field | 4:3 | beat 1 |
| 6 | `cb-group-review` | Three students around one laptop reviewing notes together | 16:9 | path / loop band |

Diversity is the point, not a garnish: aim for at least four visibly different ethnicities
across the six, a mix of genders, and at least one shot that reads first-generation.
**Every image must be checked by eye before it is placed** — the earlier batch proved that
a stock photo's description can lie about who is in it.

Delivery: 1600px WebP (<200KB) + 800px variant (<90KB) + `CREDITS.md` row
(photographer, source URL, licence, the source's own description).

---

## 5 · Hero video storyboard — 10 seconds, no voiceover

Silent by design: it autoplays muted, and roughly a third of viewers never unmute.
The tap is the story.

| Time | Frame | Action |
|---|---|---|
| 0.0–1.5 | App card on off-white, gold chip `DAILY DRILL · DAY 12`, heading `Your A/R days is 48.`, teal line `What does that mean for cash?` | settle in, no motion |
| 1.5–4.0 | Three answer chips stack in 120ms apart | ease-out, 12px rise + fade |
| 4.0–6.0 | Circular cursor moves to chip 1 and presses it | chip turns teal with a check; other two dim to 40% |
| 6.0–9.0 | Insight panel slides up, teal left border: `Why hiring managers care: A/R days is a liquidity lever.` | 16px rise, 300ms |
| 9.0–10.0 | Everything eases back toward the frame-1 state | loop-safe: first and last frame near-identical |

Deliver: `1080×1350`, H.264, yuv420p, 30fps, **no audio track**, `~10.0s`, <1.5MB, seamless
loop, plus a poster still of the 6–9s moment. Render discrete frames and assemble with
ffmpeg — never a real-time screen recording (it will OOM this box).

---

## 6 · Component list

| Component | Contract |
|---|---|
| `nav` | sticky, translucent; logo left; 4 links; ghost `Log in` + primary `Start the scorecard`; collapses to `burger` + panel ≤980px |
| `hero` | 2-col grid (1.04/0.96), 56px gap; eyebrow + h1 + one-sentence sub + single `.btn` + text link; right column = `frame` + `proof` |
| `frame` | 4:5, radius 20, navy backing; contains poster `<img>`, `<video>` (muted/loop/playsinline/preload=none), sound-toggle pill |
| `proof` | one line, centered, muted |
| `drill` | white card; question with mono metric; 3 `<button class="opt">` with `.correct` / `.dim` states; `#why` panel revealed on tap |
| `track` / `node` | 4 rows: 44px icon tile, label + status, right column chip + progress bar; `.locked` variant dims and greys the tile |
| `beat` | image (4:3) + Sora caption + one muted line |
| `founder` | card: 76px square headshot + two-line statement |
| `loop` / `step` | 4-up grid: mono index, 22px stroke icon, one-word title |
| `offer` | 2-up grid, equal weight: chip, price, one-line what, full-width `.btn` |
| `faq` | native `<details>` × 4, `+ / –` affordance |
| `footer` | navy, 3-part flex: logo, copyright, link list |
| `mobile-bar` | fixed bottom, ≤980px only, full-width primary CTA; body gets 82px bottom padding |
| `reveal` | IntersectionObserver adds `.in`; disabled under `prefers-reduced-motion` |
| UTM carry-through | script propagates `utm_*` from the landing URL onto every internal link so YouTube traffic is still attributed at `/scorecard` |

---

## 7 · What's verified

- Campus Brief palette and IA are implemented in the reference build
  (`design/campus-brief/index.campus-brief.hcadaily-bot.html`, 27.6KB, self-contained).
- Section order, one-CTA-per-section, no hero email field, no urgency language — all
  satisfied in the reference build.
- **Not verified:** nothing is deployed, and the reference build's media is not the
  `cb-*` set. Do not ship it blind — either port the copy into Butler's file, or point the
  reference build at the `cb-*` assets and re-verify images and video resolve before deploy.
- **Stale media paths in the parked build:** it points at `/video/brief-loop.mp4` and
  `/img/study-focus-800.webp`. The `video/` directory has been **deleted** — it held 23MB of
  my own orphaned render frames sitting inside the deploy path, and the video it was for is
  superseded by Butler's `cb-drill-loop.mp4`. Repoint the parked build at
  `/img/cb-drill-loop.mp4` and the `cb-*` stills before using it, and re-verify each path
  returns 200 after deploy.