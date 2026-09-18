# thehcadaily.com — UI/UX audit + modernisation spec

**Date:** 2026-09-18 · **Audited by:** hcadaily bot (growth) · **Lane:** audit is growth; implementation is `[platform]` (Butler owns `worker/assets`)

---

## Score: **5.3 / 10**

Solid, honest, well-built — and aimed at the wrong audience. It reads like a
professional tool for people already in healthcare administration. It does not
read like something a 21-year-old student feels invited into.

| # | Dimension | Weight | Score | Why |
|---|---|---|---|---|
| 1 | First impression / visual appeal | 15% | 6.5 | Clean, confident, generous whitespace. Flat: text and CSS only. |
| 2 | Clarity of the offer | 15% | 6.0 | Hero headline is director-level jargon (see below). |
| 3 | Photography / human warmth | 10% | **1.0** | **Zero images on the entire site.** |
| 4 | Social proof & trust | 10% | 3.0 | Numbers yes, faces no. No testimonials. |
| 5 | Navigation & IA | 10% | 6.5 | Four items, logical. "Start" is ambiguous. |
| 6 | Mobile experience | 10% | 5.5 | Two breakpoints, no mobile nav pattern. |
| 7 | Conversion path & CTA clarity | 15% | 7.5 | Best thing on the site. Free tool + email capture above the fold. |
| 8 | Design-system consistency | 10% | 4.0 | No shared CSS; 8 different border-radii; palette contradicts the brand guide. |
| 9 | Accessibility & performance | 5% | 6.0 | Viewport set; but render-blocking font import, no image discipline yet. |

---

## Evidence (measured, not impressions)

- **`<img>` tags across all 13 pages: 0. `<svg>`: 0. `alt` attributes: 0.**
  Every page — including the scorecard and both product pages — is pure text + CSS.
  Even the instructor block uses a lettered circle instead of her face.
- **Fonts:** Sora (display), Inter (body), IBM Plex Mono (accents) — genuinely
  modern choices. Loaded from Google Fonts (render-blocking).
- **Palette in use:** navy `#0b2545`/`#13315c` + **coral `#ff5749`** + **mint `#8fd3c9`** + **amber `#f59e0b`**.
- **⚠️ The site's palette contradicts the brand guide.** The brand guide specifies
  navy + **teal `#0d9488`** + **gold `#c9a227`**, and explicitly names coral, mint
  and amber as *not* brand colours (that is exactly why the first promo Short was
  rejected). Right now the website and the YouTube channel are two different brands.
  This needs one decision, made once.
- **Responsive:** only two media queries (`max-width:820px`, `max-width:480px`).
  **No hamburger / mobile-nav toggle exists** anywhere in the markup.
- **CSS:** one inline `<style>` block per page, no shared stylesheet. Eight distinct
  `border-radius` values (6, 10, 12, 13, 14, 16, 18, 20). Every page is edited
  independently, which is how pages drift apart.
- **Section order on the home page:** hero → live drill demo → four scored skills →
  instructor blurb → Score/Drill/Review/Unlock → two product cards → FAQ → footer.
- **Proof present:** "6,000+ healthcare leaders", "4 scored dimensions", "5 min a day".
- **Proof absent:** testimonials, student faces, outcomes, before/after, any human
  photograph at all.

### The headline is the single biggest miss for a younger audience

> "Get interview-fluent in the metrics hiring execs actually use — 5 minutes a day."

A 22-year-old two weeks from graduating does not know what "interview-fluent"
means, and does not yet believe they belong in a room with "hiring execs". The
line is written for someone already in the industry. Same with the demo drill
("Cash is sitting uncollected ~48 days") — expert-level, brilliant for a
manager, opaque to a student.

---

## What to change, in priority order

### 1. Put people on every page (the whole point of this brief)

| Where | What goes there |
|---|---|
| Hero | One real photo — a confident young woman with a laptop, off-centre, text on the clean side. Immediate signal: *this is for someone like me.* |
| "Who this is for" band (new) | 3-up grid of student portraits: clinical, non-clinical, career-changer. |
| Testimonial strip (new) | 3 short quotes **with faces**. Real quotes only — no invented students. If none exist yet, use her face + the 6,000+ and YouTube numbers until real ones arrive. |
| Drill / skills section | Keep the interactive demo; add a small photo of students working together to warm the section. |
| Products | Small "what you get" photo thumbnails. |
| Footer | Nothing. Leave it clean. |

Discipline: **WebP, lazy-loaded, explicit width/height, 800px mobile / 1600px
desktop variants.** Never ship a 3MB JPEG into a mobile hero.

### 2. Rewrite the hero for the person who is actually arriving

Working direction (keep her voice, drop the jargon):

> **Headline:** Go from new grad to the one they hire.
> **Sub:** Five minutes a day on the exact numbers — A/R days, wRVUs, no-show rate —
> that decide who gets the director's office. Free to start.
> **CTA:** Take the 90-second Scorecard *(unchanged — this is working)*

The metrics stay; they move from the headline into the proof. Same authority,
no membership test.

### 3. One palette, decided once

Recommendation: **navy base + coral primary + gold accent**, and retire mint and
amber. Coral is the youth-facing energy the brief asks for; navy + gold carry the
authority her channel is built on. Then update the brand guide **and the Shorts**
so the site and YouTube finally match. (Alternative: adopt the guide's teal/gold
exactly and drop coral. Either is defensible — but only one.)

### 4. Mobile-first, properly

- Real mobile nav (hamburger that actually opens).
- Sticky bottom CTA bar on mobile: *Take the scorecard* — always one tap away.
- 44px minimum tap targets.
- Test at 390px, not just at "max-width:820px".

### 5. Shared stylesheet + design tokens

One `styles.css` with CSS custom properties (`--navy`, `--coral`, `--gold`, `--r-card`,
`--r-pill`, spacing scale). Collapses 8 radii to 2–3, kills per-page drift, and makes
the next redesign cheap instead of a 13-file rewrite.

### 6. Motion, sparingly

Scroll-in reveals on section bands, the drill demo already animates (good), and a
completion beat on the scorecard. Enough to feel alive; not a screensaver.

---

## Handoff

Site UI is `[platform]` (Butler) per `ops/COORDINATION.md` — growth does not edit
`worker/assets`. This document is the spec. The image library lands in
`worker/assets/img/` with `CREDITS.md` + `manifest.json`, so the platform owner can
drop images in without sourcing anything.

Queued in `COORDINATION.md` as `[platform]`.