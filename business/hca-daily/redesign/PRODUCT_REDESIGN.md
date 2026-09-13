# The HCA Daily — Product Redesign Spec v1

**From a PDF landing page → a daily-practice learning product.**
Founder: Dr. Ashley Hussain-Okorafor, DBA · @professorashley · thehcadaily.com

---

## 0. First-principles diagnosis: why the current site won't create daily practice

The current site is a *brochure that sells a PDF*. It has a scorecard, a vault sales page, and an accelerator page — but they form a straight line that ends at "buy," not a loop that ends at "come back tomorrow." Diagnosed against the seven constraints:

| Principle | What the site does today | The failure |
|---|---|---|
| **1. JTBD = hired** | Sells "156 scripts" (a *knowledge* artifact) | Sells the output of skill, not the skill of *retrieving under pressure* |
| **2. Skill ≠ knowledge** | 157-page PDF to hoard | Reading a script ≠ producing it cold in a panel |
| **3. Forgetting is default** | One-time download, never revisited | No spaced resurfacing; retention ~0 after 7 days |
| **4. Effort fits gap time** | Scorecard is 90s (good), then dead-ends | Nothing to do in the 3–8 min between meetings |
| **5. Motivation = daily yes/no** | "Director role in 6 months" is the only goal | Too far away; no *today-sized* decision |
| **6. Competence must be visible** | Scorecard is a one-and-done lead magnet | No running score, no streak, no "next unlock" |
| **7. Trust is clinical, not cartoon** | Brochure-y, generic SaaS feel | Doesn't feel like hiring-side authority |

**The core insight:** the scorecard is currently the *end* of the funnel (it tips a lead). It must become the *beginning* of a loop (it places you on a path and opens today's 4-minute rep). The same person who finishes the scorecard should, seven minutes later, have finished their first drill and be looking at a streak of 1.

> **Move:** flip the hero from "buy the vault" to "take the scorecard, then do today's drill." Price *after* the first felt win, never before.

---

## 1. Product north star

**One daily behavior: complete today's HCA drill (≤5 minutes).**
Everything — homepage, scorecard, path, vault, paywall — exists to get a user to finish today's drill and return tomorrow.

**Success metrics (instrument from day one):**
- **Activation** — scorecard completed *and* account created in the first session. Target: ≥40% of scorecard finishers.
- **Habit** — Day-7 streak rate (finish a drill on each of your first 7 days). Target: ≥20%.
- **Learning** — improvement on ≥1 of the 4 scorecard dimensions after 14 days of drills (measured by re-scoring). Target: ≥30% move at least one dimension up a level.
- **Revenue** — conversion from free path → Vault / Navigator *after* demonstrated skill gain (i.e., after ≥3 drills, not before). Target: ≥5% of activated users, and *higher* $/user than the current cold-pitch funnel.

---

## 2. Learning system (build these mechanisms — name them in the IA so engineering can implement)

### A. Bite-sized lessons (atomic unit)
- **4–6 minutes, 8–12 interactions,** mixed formats, never a lecture.
- Six drill formats (all implemented as interactive components):
  1. **Metric flash** — "A/R days is 48. What does that mean for cash?" → tap the correct implication.
  2. **Spot the weak bullet** — three resume lines; pick the one that *proves* impact vs. lists duties.
  3. **Fill the STAR** — a messy story; tap Situation / Task / Action / Result in order, then insert the missing number.
  4. **Speak-aloud** — a real question, 30-sec timer, self-score against a rubric.
  5. **LinkedIn scan** — a headline; mark what's recruiter-searchable.
  6. **Negotiation line** — choose the script that anchors to market data without sounding entitled.
- **Immediate right/wrong** + a one-sentence *"why hiring managers care."*
- **Hearts:** 5 mistakes → short cooldown or practice-only mode (prevents binge-and-forget).

### B. Skill path (not a 156-script dump)
A visible skill tree grouped by hiring dimension, with levels Intro → Fluent → Interview-ready per node. Next node locked until current node passes mastery.
1. **Resume Metrics**
2. **Operational Vocabulary** (wRVU, A/R days, denial rate, occupancy, HEDIS, CMS stars, no-show, contribution margin)
3. **LinkedIn & Visibility**
4. **Interview Delivery** (behavioral + operational + clinical ops + revenue cycle + LTC/quality)
5. **Offer & Negotiation**

### C. Retrieval practice, not rereading
Every lesson is mostly *recall*. Vault scripts are **source material to be drilled, not a PDF to hoard.** No "read this chapter" as a primary interaction.

### D. Spaced repetition
- Resurface a concept at expanding intervals: same day → 1 day → 3 days → 7 days.
- **Strength meter** per skill (bars that decay if unused).
- A **Personalized Practice** session fires when any skill drops below threshold.
- The 4 scorecard dimensions become the **live mastery dashboard**, not a one-time lead magnet.

### E. Zone of proximal development (adaptive)
- 4 correct in a row → next item harder (more numbers, messier scenario, tighter timer).
- 2 misses in a row → drop to a scaffolded version (word bank → free recall).
- Never open with a director-level case on day 1.

### F. Noticing patterns
Show 3 bullets/answers; force the user to notice what the strong ones share (quantified delta, time-bound, executive metric). *Then* name the pattern. No definitions-first lecturing.

### G. Communicative competence
End-state is *interview performance*, not quiz score. Every unit closes with a timed spoken/written answer that survives a panel. **Rubric:** metric named · number present · ownership of action · result tied to operations or margin.

### H. Daily streak + humane pressure
- Streak = consecutive days with ≥1 drill.
- **Streak Freeze** (1–2 misses, earned by consistency or in the paid plan).
- **Daily Quest** — one concrete task ("Drill 5 A/R items" / "Rewrite 1 resume bullet").
- **Weekly League** — opt-in, compete on XP with a small cohort; never public humiliation.
- **XP** for lesson done, perfect lesson, practice review, speak-aloud.
- **Milestone identity:** 7 / 30 / 90-day "Interview-Ready" badges tied to *skills*, not vanity.

### I. Progress always visible (post-login home)
Today's lesson (one tap) · streak + freeze status · path with current node highlighted · 4-dimension bars · next-unlock teaser.

---

## 3. Information architecture (sitemap)

Preserve `/scorecard` and `/vault`. New routes:

| Route | Purpose |
|---|---|
| `/` | Marketing + start (hero → live drill → path preview → daily loop → authority → paywall framing → FAQ) |
| `/scorecard` | 10 questions (unchanged). **Results now place you on the path** and create an account |
| `/learn` (or `/today`) | Authenticated home: streak + today's drill + 4-dimension bars + next unlock |
| `/path` | Full skill tree |
| `/practice` | Spaced-repetition queue + Personalized Practice |
| `/vault` | Searchable script library; each script has a **"Drill this"** button |
| `/interview` | Timed mock interview (speak-aloud panel) |
| `/account` | Streak, freezes, billing |
| `/about` | Ashley bio stays — hiring-side credibility is the differentiator |
| `/legal` | Terms, privacy |

---

## 4. Visual design system

**Look:** premium edtech 2026 — calm clinical authority, not 2014 courseware, not kids'-game cartoon. Mobile-first.

### Color tokens
| Token | Hex | Use |
|---|---|---|
| `--navy-900` | `#0b2545` | Primary surfaces, headings |
| `--navy-700` | `#13315c` | Secondary surfaces, hovers |
| `--coral` | `#ff5749` | High-energy accent — primary CTA, "in-progress," daily quest |
| `--amber` | `#f59e0b` | Streak flame, needs-review state |
| `--green` | `#16a34a` | Mastered / correct |
| `--slate` | `#94a3b8` | Locked / disabled |
| `--off-white` | `#faf9f6` | Background |
| `--ink` | `#14181f` | Body text |

**State encoding (color = status):** locked = slate · in-progress = coral · mastered = green · needs-review = amber.

### Type scale
| Role | Face | Size/weight |
|---|---|---|
| Display (scores, path titles) | **Sora**, 800 | 44 / 32 / 24 |
| Headings | **Sora**, 700 | 28 / 22 / 18 |
| Body | **Inter**, 400/500/600 | 16 / 15 / 14 |
| Numbers / streak / metrics | **IBM Plex Mono**, 600 (tabular) | 20 / 16 |

### Components
Button (primary/secondary/tertiary, ≥48px tap target) · lesson card · stat card · **streak chip** (flame + count + freeze) · **hearts** (5) · **skill node** (4 states) · **score bar** (fill % + delta arrow) · progress dots · XP chip · badge · toast · persistent bottom **Continue** bar · speak-aloud timer modal.

### Motion
Short and satisfying only: progress-bar fill, node unlock, streak increment. No decorative animation that delays the next tap. Confetti *only* at unit-complete and streak milestones.

### Accessibility
WCAG 2.2 AA · captions on any audio · full keyboard support on web · color never the sole signal (pair with icon/label).

### Imagery
Abstract the real healthcare-admin world — dashboards, unit boards, revenue-cycle screens — as subtle background texture. No stock smiling nurses. A sharp, calm guide-mark/wordmark is enough; **no owl.**

---

## 5. Homepage layout (section by section, with copy)

**1. Hero — outcome + time**
- Eyebrow: `THE HCA DAILY · HIRING-SIDE TRAINING`
- Headline: **"Get interview-fluent in the metrics hiring execs actually use — 5 minutes a day."**
- Sub: "Say goodbye to 'I'd improve productivity.' Walk in speaking wRVUs, days in A/R, and no-show rates."
- Primary CTA: **"Take the 90-second Scorecard"** → /scorecard
- Secondary: "See a sample drill ↓"

**2. Live drill demo (interactive, not a screenshot)**
- Headline: **"This is a drill."**
- Sub: "One metric, one tap, one sentence on *why it matters*. That's the whole unit."
- Render a real `Metric flash` item, tappable, with feedback.

**3. The four dimensions as a path preview**
- Headline: **"Four skills stand between you and the offer."**
- Sub: "Not 156 scripts — four scoring dimensions. Master each, watch the director role get closer."
- Four node cards (Resume Metrics · Operational Vocabulary · LinkedIn & Visibility · Interview Delivery), each with a level + "IN PROGRESS" state on the first.

**4. Authority — short and specific**
- Headline: **"Trained by someone who sat on your side of the table."**
- Sub: "Dr. Ashley Hussain-Okorafor, DBA — former university lecturer, hiring-side administrator, and the voice behind @professorashley (6,000+ healthcare leaders)."
- One-line proof, no fake testimonials.

**5. How the daily loop works**
- Headline: **"Score → Drill → Review → Unlock."**
- Four steps with icons: 90s scorecard places you on the path → today's 4-min drill → a review resurfaces what's fading → the next unit unlocks.

**6. Vault & Navigator = the depth layer**
- Headline: **"Already in the path? Go deeper."**
- Vault card: "The full 156-script library — the answer key every drill pulls from. Lifetime."
- Navigator/Accelerator card: "Adaptive plan, JD matching, salary bench, and 24/7 advisory."
- Framed as *depth for people already practicing*, never the hero.

**7. FAQ + guarantee**
- "Is this 1:1 coaching?" / "How long until I'm ready?" / "Can I try before paying?" / "What's the guarantee?"

> **Rule enforced in copy:** never lead with "$97 → $27 PDF." Lead with the habit. Price after one felt win.

---

## 6. Lesson-player layout (mobile-first)

- **Top bar (compact):** exit (←) · unit title · **hearts** (♥♥♥♥♥) · XP chip.
- **Progress dots** across the top: current item highlighted, completed filled.
- **Prompt area:** the item — metric, bullet, STAR, or question — large, readable, one idea at a time.
- **Answer affordances:** tap targets (2–4 options) or the speak-aloud timer.
- **Feedback band:** correct → green check + one-sentence *why hiring managers care*; wrong → coral + the reasoning, then advance.
- **Persistent bottom "Continue" bar** — large, always reachable with the thumb.
- **Unit-complete screen:** confetti, "+XP", node progress fill, streak flame if incremented, next-unit teaser.
- Lesson length always visible ("≈4 min") before start.

---

## 7. Gamification rules (exact triggers + copy)

| Event | Trigger | Reward | Copy |
|---|---|---|---|
| Lesson complete | finish all items | +10 XP | "Drill complete. A/R fluency +12. Streak: 6." |
| Perfect lesson | 0 mistakes | +5 XP | "Flawless drill." |
| Practice review | finish a spaced-review session | +5 XP | "Reviewed. Strength refilled." |
| Speak-aloud done | submit a 30s answer | +10 XP | "Answer recorded. Rubric below." |
| Daily quest | complete today's quest | +15 XP | "Quest complete." |
| Streak increment | ≥1 drill today | flame +1 | "Day 6. And counting." |
| Streak freeze | miss a day with freeze held | streak preserved | "Freeze used — you're back at 6." |
| 7 / 30 / 90-day badge | milestone reached | badge | "Week one down." / "One month fluent." / "Interview-Ready." |
| Hearts depleted | 5th mistake | cooldown / practice-only | "Out of hearts. Recover in 10m — or run a review." |
| Week-league promo | top XP in cohort | tier up | "Top of your league this week." |

---

## 8. Content mapping (the work, done)

### Unit list (17 units across 5 paths)

**Path 1 — Resume Metrics**
1. Numbers Beat Nouns *(metric hooks)*
2. Bulletproof Bullets *(spot strong vs. duty-listing)*

**Path 2 — Operational Vocabulary**
3. Revenue Cycle in 6 Numbers *(A/R days, denial rate, clean claim, cost-to-collect)*
4. Clinical Ops Fluency *(wRVU, FTE, HCAHPS, LOS, readmission, no-show)*
5. Quality & Compliance Speak *(HEDIS, CMS stars, HIM, CDI, accreditations)*
6. LTC & Post-Acute Metrics *(occupancy, case mix, star ratings, PDPM)*

**Path 3 — LinkedIn & Visibility**
7. Headline Hooks
8. Profile That Recruits

**Path 4 — Interview Delivery**
9. Behavioral STAR Foundations
10. Leadership Stories
11. Operational Interview Answers
12. Revenue Cycle Answers
13. Clinical Ops & Quality Answers
14. HIM & LTC Answers

**Path 5 — Offer & Negotiation**
15. Total Comp Anatomy
16. The Counter-Offer Scripts
17. Lowball & Best-Final Defense

### Vault → unit mapping (156 scripts)
- **Vault Part 1 (Behavioral & Leadership, 36)** → Units 9–10
- **Vault Part 2 (Operational & Metrics, 30)** → Units 3–4, 11
- **Vault Part 3 (Revenue Cycle & Patient Access, 30)** → Units 3, 12
- **Vault Part 4 (Clinical Ops, Quality, HIM & LTC, 30)** → Units 5–6, 13–14
- **Vault Part 5 (Salary Negotiation, 36)** → Units 15–17
- *(Units 1–2, 7–8 draw from the Accelerator's Resume Kit + LinkedIn Playbook, already written.)*

### Free vs. paid
- **Free:** full 10-question scorecard + first 3 days of the path (Units 1–3) with full drill mechanics.
- **Vault ($27 · lifetime):** full 156-script text (the answer key drills pull from), and interview-answer Units 9–14.
- **Accelerator / Navigator ($279):** negotiation Unit 15–17, adaptive plan, JD matching, salary bench, 24/7 advisory, auto spaced-review, streak freezes, leagues.

### One complete lesson — Unit 3, "Revenue Cycle in 6 Numbers" (10 items)

1. **Metric flash** — "Your A/R days is 48." Tap the correct implication:
   · ✅ *Cash is sitting uncollected ~48 days — the org is financing operations on credit.* · ✗ "Patients wait 48 days for appointments." · ✗ "It takes 48 days to post a payment."
   *Why hiring managers care:* A/R days is a liquidity lever; quoting it correctly signals you think in cash-cycle terms.

2. **Metric flash** — "Denial rate is 12%." Which move do you flag first?
   · ✅ Investigate top denial reasons before re-billing. · ✗ "Re-file every claim faster." · ✗ "Reduce coding staff."
   *Why:* denial rate is a *root-cause* signal, not a volume problem.

3. **Spot the weak bullet** — pick the line that *proves* impact:
   · "Managed registration for a 42-physician clinic." ✗ · "Oversaw patient access operations." ✗ · ✅ "Cut front-desk no-show rate 22% → 13% in 6 months by reworking the reminder cadence."
   *Why:* only the last has a delta + a number + a mechanism.

4. **Fill the STAR — order it.** Messy story: "Denials were killing us — 14% of claims — so I pulled a report and found most were missing prior authorizations…" Tap in order: **S** (14% denials) → **T** (fix auth workflow) → **A** (built a pre-auth checklist + trained 8 staff) → **R** (denials 14% → 6%, $310K recovered).

5. **Fill the STAR — insert the missing number.** "I reduced clean-claim rejections from ____ to 4%." Options: 2% / **9%** / 30%. *(Missing number = 9%.)*
   *Why:* the number is what makes "I helped" into "I moved a metric."

6. **LinkedIn scan** — which headline is recruiter-searchable? · "Healthcare professional dedicated to excellence" ✗ · ✅ "Revenue Cycle Manager · ↓ denials 14%→6% · A/R 48→31 days"
   *Why:* recruiters search job titles + metrics, not adjectives.

7. **Speak-aloud (30s)** — "Tell me about a time you improved revenue cycle performance."
   Rubric: metric named · number present · ownership · result tied to margin.

8. **Metric flash** — "Clean claim rate is 97%." What's the takeaway? · ✅ 3% of claims need rework — shrinking that is the lever. · ✗ "Billing is done." · ✗ "Coding is perfect."

9. **Negotiation line (intro)** — choose the anchor that uses data without sounding entitled:
   · ✅ "Market data for this role in this region sits at $X base; given my revenue-cycle record, I'd target $X + $Y sign-on." · ✗ "I need more money." · ✗ "A friend got more."

10. **Communicative close (written)** — "Explain days in A/R to a CFO in one sentence."
    Rubric: metric named · number present · cash implication stated.
    *(Model: "Days in A/R is the average time a claim sits unpaid — ours is 48, which means ~$2.1M of revenue is floating in receivables instead of funding operations.")*

### Copy — empty states, risk, milestones
- **Empty path (new user):** "No drills yet. Take the scorecard and we'll place you."
- **Streak at risk (evening, no drill today):** "Your 5-day streak is on the line — one 4-minute drill saves it."
- **Freeze used:** "Freeze used — you're back at 6. Don't lose it tomorrow."
- **Unit complete:** "Unit passed. A/R fluency unlocked. Next: Clinical Ops Fluency."
- **Needs review:** "Two skills are fading. A 3-minute review refills them."

---

## 9. Measurement plan (events to track)

`view_homepage` · `start_scorecard` · `complete_scorecard` · `account_created` · `start_lesson` · `complete_lesson` · `item_correct` / `item_incorrect` · `lesson_perfect` · `hearts_depleted` · `speak_aloud_complete` · `streak_increment` · `freeze_used` · `path_node_unlock` · `dimension_score_updated` · `practice_session` · `vault_search` · `vault_drill` · `paywall_view` · `checkout_start` · `checkout_complete` · `day7_return`

Funnel dashboards keyed off: activation (scorecard→account), habit (day-7 streak), learning (dimension re-score), revenue (post-practice conversion).

---

## 10. What not to do

- ❌ No owl or mascot guilt-tripping — cheapens a professional brand.
- ❌ No infinite-scroll blog as the core.
- ❌ No 40-minute video as onboarding.
- ❌ No paywall before the first felt win.
- ❌ No fake testimonials or invented clinical claims.
- ❌ No Farm-Bill / THCA confusion — this is Healthcare Administration, cleanly labeled.
- ❌ Don't delete `/scorecard` and `/vault` — preserve URLs.

---

## 11. Phased ship plan (solo-founder, iterable)

- **Phase 1 (ship first):** scorecard → account creation → `/learn` home (streak + today's drill) → Units 1–3 with all 6 drill formats → streak + hearts. *(No leagues, no full tree, no paywall logic yet.)*
- **Phase 2:** full path tree + spaced-review queue + `/practice` + Vault "Drill this" wiring + negotiation unit.
- **Phase 3:** weekly leagues, Navigator (JD matching, salary bench, 24/7 advisory), adaptive difficulty.

---

*End of spec. Awaiting CEO approval to build Phase 1.*