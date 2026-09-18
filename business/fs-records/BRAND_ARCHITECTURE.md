# FS Records — Brand Architecture v1

> **Status: DRAFT — awaiting approval by Dr. Ashley Hussain-Okorafor.**
> Nothing in here is built until approved. Supersedes nothing; extends the existing artist brand bibles.
> Created: 2026-09-16

---

## 0. The model in one sentence

**One family universe, many stages. The characters are the asset — the songs are the output.**

Everything below is just plumbing for that idea.

---

## 1. The four layers

### Layer 1 — Freedom Soapbox *(parent brand)*
The real family story. Real vlogs + the "special songs." Documentary of a family in motion.
- **Not** the monetization engine. This is brand equity and the emotional core.
- Everything else in FS Records is downstream of this.

### Layer 2 — The Universe *(shared animated characters)*
One locked character bible. Every account draws from the same world.
- This is the flywheel. A kid who watches the kids' channel recognizes the mom and dad characters when they appear on an artist channel.
- Without this, you have six unrelated YouTube channels. With it, you have a franchise.

### Layer 3 — Stage accounts *(each persona gets a lead)*

| Account | Lead identity | Role |
|---|---|---|
| **NVA FRQCY** | Ashley's artist identity | Adult R&B / fusion / memory-music |
| **APX Shft** | Nnamdi's artist identity | Braggadocio hype / family-loyalty anthem lane |
| **Afro Violin** | Instrumental (visual DNA `afroviolin_v1` locked) | Afrobeat violin instrumentals |
| **Divine Freedom Soapbox** | Reflective / faith | Yin-yang, wu wei, inner-strength lane |
| **Peoploids** | Cosmic multi-species collective | Sci-fi satire / bucket-hats merch lane |
| **Freedom Soapbox Collective** | Overflow / catch-all | Good tracks that fit nowhere else |

### Layer 4 — The Kids Spin-off *(new)*
The family characters **as kids' avatars**. Kids take the lead. Gracie's Corner model.
- Sits **under** Freedom Soapbox as a branded spin-off — parent-branded, separately distributed.

---

## 2. Character universe spec (v0)

### Hard rules
1. **No real names. Ever.** Public personas use stage names only.
2. **The animated kids are distinct characters inspired by, not portraits of, the real children.** Different names, meaningfully different hair/face/proportions. Nobody should be able to reverse-link the cartoon to a real minor.
3. **No real voice recordings of the children. No voice cloning of the children.** Adult characters may use the adults' own recorded voices (their consent, their choice).
4. **One locked character sheet per character** — turnaround, palette hexes, proportions, expression set. Treated like `afroviolin_v1`: locked, versioned, single source of truth.
5. **Cross-show rule:** a character appears in another account's content only if it's in the bible.

### Proposed roster *(names are placeholders — you name them)*
- **Mom character** ← NVA FRQCY identity
- **Dad character** ← APX Shft identity
- **Older sister character** (~5, the diplomat)
- **Younger sister character** (toddler, the menace)
- *(optional)* Grandparent / extended-family characters for the vlog layer

### Why the kids' characters should NOT be 1:1
The real girls' identities are already partially public on the family vlog. Cartoon versions with different names and slightly altered designs give you a clean separation: the cartoon can go anywhere (brand deals, merch, licensing, overseas distribution) without exposing the actual children. That flexibility is worth more than visual accuracy.

---

## 3. Kids spin-off spec

- **Branding:** "[Name TBD] — a Freedom Soapbox family production"
- **Format:** 2–4 minute songs. Sing-along, call-and-response, repetition. Letters, numbers, manners, confidence, movement.
- **Lane:** Gracie's Corner / Ms Rachel territory — but the differentiator is the **three-continent Venn**: South Asian + Nigerian + American kid life, and *frugal-first* family values. Nobody owns that lane.
- **Distribution:** **separate YouTube channel** (kid audience profile ≠ adult music audience profile — sharing one channel hurts both), plus YouTube Kids, Spotify/Apple Kids, merch.
- **Cadence target:** 1 upload/week once the pipeline is proven.
- **Same footage, two purposes:** kid-channel shoots and relocation/vlog content come from the same sessions.

---

## 4. Revenue reality (honest version)

**Kid content is not a fast ad-revenue play.** YouTube "made for kids" (COPPA) removes personalized ads, comments, and notifications. Per-view RPM is lower than adult music.

But the ceiling is real: Gracie's Corner sits at roughly **6.5M subscribers / 6.4B lifetime views**, and its money comes substantially from **licensing, merch, and brand partnerships** — not raw ad revenue. Kids catalogs are evergreen: a good song earns for a decade.

**Where FS Records actually makes money, ordered by speed:**
1. **Artist account catalog** (streams + sync/licensing) — exists today, compounding
2. **Merch** (Peoploids bucket hats is already the flagged first signal) — highest margin
3. **Kids spin-off** — slow build, then evergreen + licensing
4. **Freedom Soapbox** — brand equity, not revenue

So: **kid channel = audience and brand. Artist accounts = catalog. Merch = the profit center that compounds.**

---

## 5. The animation stack decision — the real gate

Current state: **no video-generation keys in `.env`.** The old afroviolin Runway/Kling/Seedance agents are in the repo but dead. `playwright` module missing. So this is a from-scratch decision.

There is a real fork here, and it's about **what you're making**, not about budget:

- **Music videos / shorts** need *beauty and novelty per shot*. Generative video wins.
- **A recurring kids' series** needs the *same character looking identical in episode 40 as in episode 1*, with lip-sync to your audio. Generative video is still bad at this. Rigged 2D animation is good at it.

### Path A — Rigged 2D animation *(recommended for the kids' series)*
**Reallusion Cartoon Animator 5** — perpetual license **US$149**, 30-day full-feature free trial, commercial use permitted under EULA, Windows/Mac.
- Auto-rigs characters from Photoshop/vector art, AI lip-sync generated from your audio track, reusable rigs across episodes, 1700+ embedded assets.
- One character built once = identical in every episode, forever.
- Occasional 50%-off bundle promos run (2 items to the basket).
- **Cost: $149 one-time.** Learning curve: moderate.
- Honest downside: it's a desktop app, not autonomous — it will not run unattended in an agent pipeline.

### Path B — Generative video subscription *(recommended for artist music videos)*
- **Vidu Q3** — best-in-class character consistency via reference images; free plan with unlimited off-peak generation. Cheapest credible entry.
- **Kling 3.0** — ~$6.99/mo entry, 66 free credits/day, 4-image Elements system to lock a character. Longest clips. Failed generations still burn credits.
- **Seedance 2.0/2.5** (ByteDance) — native multi-shot storytelling with character continuity; best for narrative.
- **Cost: roughly $0–30/month.** Great for Afroviolin / NVA FRQCY / APX Shft music videos. Not reliable for a 40-episode kids' series.

### Path C — Rebuild the API agent pipeline *(later, at volume)*
Reuse the existing `afroviolin/agents/` architecture with a live video API — Seedance 2.0 Mini at ~**$0.04/second** at 480p is the cheapest documented rate, Veo 3.1 Lite ~$0.05/sec at 720p.
- Fully autonomous: no human hands, matches the "systems run in the background" thesis.
- **Cost scales per second of output.** Not the right first move — it's how you industrialize *after* the format works.

### Recommendation
**Hybrid.** Path A for the kids' series (identity lock is non-negotiable there). Path B for artist music videos (Vidu free tier to validate, Kling if you need more). Path C once there's a proven format and real volume.

**Cheapest possible validation, this month:** one character sheet + one 60-second test episode, made in the CA5 free trial. Under $200 and no commitment tells you whether the format works.

### Suno — CONFIRMED: Pro ($10/mo)

**Verdict: Pro is the correct plan.** Commercial rights confirmed. But three things changed in September 2026 that directly constrain this rollout. All verified against Suno's own help center.

**1. Commercial rights — confirmed, with a catch on *when* they attach**
> "For any song that you **download from the platform as a paying subscriber**, you have the commercial rights."

- Rights are tied to the **download**, not the generation. A track generated on Pro but never downloaded is not cleared.
- **Not retroactive.** Free-tier tracks are Suno's property, licensed to you for personal use only. Upgrading does not clear them. Any released FS Records track that originated on the free tier is an open exposure and must be regenerated on Pro.
- Rights are perpetual — cancel later, you keep what you made while subscribed.

**2. 🚩 The real constraint: download caps (effective Sept 3, 2026)**
- **Pro = 20 downloads/month.** Premier = 60/month. Free = 7 lifetime.
- One song = one download regardless of format. Re-downloading is free. Stems count as part of that song's download.
- **Caps are retroactive to your entire existing library.** Any old song never downloaded before now counts against the current 20/month.
- No rollover — unused downloads are lost on the billing date.
- **Suno Studio workflows are exempt** (Premier only) — that's the paid escape hatch.

*Implication:* 20/month is comfortable for one kids' channel at 1 upload/week (4–5/mo). It is **not** comfortable if NVA FRQCY, APX Shft, the kids' channel, and Afroviolin are all pulling from the same 20. Running multiple brands at once argues for Premier ($30/mo) or doing all downloads in one Studio session.

**3. 🚩 All pre-v6 models retired September 9, 2026**
- v4, v4.5, v5, v5.5 — all retired. v6 family only (v6, v6-wild, v6-mini).
- Existing songs are safe, playable, and shareable in the library. But **extensions, remixes, and covers now run on v6**, so they will sound different from the originals. There is no rollback.
- **Consequence for FS Records:** any locked sonic identity from v5.5 cannot be continued. New material will have a v6 character.

**Upside:** this is a clean slate that lines up exactly with the new brand architecture. Generate the kids' catalog on v6 from the start rather than trying to match old v5.5 sessions.

**Actions:**
1. Audit the existing catalog — which released tracks were generated on the free tier? Those need regenerating on Pro.
2. Decide whether 20 downloads/month covers the rollout, or whether Premier's 60 is needed once multiple brands are live.
3. Confirm whether the **Voices** feature (consistent vocal identity across tracks — critical for a kids' character voice) is available on your Pro tier. Sources conflict; check for the Voices tab in your account and treat this as the deciding factor on Premier.

---

## 6. Rollout

- **Phase 0 — Lock (this week):** character names, character bible v1 (4 sheets), Suno plan confirmed, animation path chosen.
- **Phase 1 — Pilot (weeks 2–3):** one 60–90s kids song, fully animated, one character only. Prove the pipeline end to end.
- **Phase 2 — Buffer + launch (weeks 4–6):** 4-episode bank, channel setup and art, launch, weekly cadence.
- **Phase 3 — Universe bleed:** artist-account music videos drawn from the same character world (APX Shft and NVA FRQCY first — they already have brand bibles).
- **Phase 4 — Merch + licensing:** bucket hats, kids' merch, licensing conversations.

---

## 7. Open decisions for Ashley

1. **Character names** — 4 leads need names (the girls' stage names are already an open task in `freedom-soapbox.md`).
2. **Kids' channel name.**
3. **Animation path** — A, B, or hybrid (recommended).
4. **Suno plan** — which tier, and are there free-tier tracks that need regenerating?
5. **Who operates the animation tool** — you, Nnamdi, or does it get pushed toward an automated Path C pipeline later?