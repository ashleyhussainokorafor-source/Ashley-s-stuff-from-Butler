# Queue #6 — Direct outreach to HCA programs (the this-month revenue play)

**Owner:** hcadaily bot (growth) · **Started:** 2026-09-18 · **Status:** engine built, target list in research

## The offer, in one line

Give a program's students a free 90-second résumé-gap scorecard. Free for them,
one line in a syllabus for the professor, and the students who take it join our
email list and get the $27 Vault / $147 résumé translation / $297 Accelerator
offered to them by the drip.

## Why this is the revenue item and not just brand-building

Three things have to be true for cold outreach to pay, and all three are:

1. **The ask is zero-risk.** A free tool for someone else's students. No purchase
   order, no procurement, no budget. That is why this can move in weeks when
   selling a university a $297 product cannot.
2. **The buyer is cheap to reach and easy to identify.** Program directors,
   department chairs and career-services staff are publicly listed with real
   email addresses. No lead-gen spend.
3. **The monetisation is downstream and already automated.** A student who takes
   the scorecard lands in KV, the drip runs every 2 hours, and checkout works.
   We do not need the professor to buy anything for the outreach to make money —
   we need them to forward one link.

The secondary hook is the **cohort rate for done-for-you résumé rewrites**: one
department sending us a graduating class is a real B2B sale, and it is the
highest-value thing in the email.

## The email (program staff — named contact)

**Subject:** Free 90-second scorecard for your {MHA} students

> Hi Jane,
>
> I lecture in healthcare administration (DBA, MHA; six years teaching in the
> California State University system), and I built a free 90-second scorecard
> that shows a student exactly how far their résumé is from a director-level
> role. It scores four things — résumé, healthcare vocabulary, LinkedIn, and
> interview readiness — and emails them the result plus a free résumé playbook.
>
> It costs your program nothing and takes one line in a syllabus or a
> career-services email.
>
> https://thehcadaily.com/scorecard?utm_source=outreach&utm_medium=email&utm_campaign={university-slug}
>
> Two things I'm happy to do if it's useful:
>
> 1. Send you a printable one-pager your students can scan in class.
> 2. Talk about a cohort rate for résumé rewrites — I do those done-for-you, and
>    a whole graduating class is cheaper than one at a time.
>
> If it's not a fit for MHA, say so and I won't follow up.
>
> — Dr. Ashley Hussain-Okorafor, DBA, MHA
> Healthcare administration · https://thehcadaily.com
>
> You're receiving this because you're listed as MHA Program Director for
> Testville State University. Reply "stop" and I'll remove you immediately.

**Follow-up (5 days, non-responders only, never a third email):** one short
paragraph and the link. "Reply stop and that's the end of it."

## The rules the sender enforces

- **12 emails a day, maximum.** Cold email from a personal Gmail at volume is how
  you end up in spam and burn the sending domain. Slow is deliberate.
- **Plain text, one link, no images, no attachments.** It reads like a person.
- **Every link carries the university's own UTM** (`utm_campaign=<university-slug>`),
  so when a student finally lands we can prove which program produced them.
- **One follow-up, then silence.** No drip, no sequences, no re-approach.
- **Never the same address twice**, and `outreach/suppress.txt` is checked before
  every send.
- **Dry-run by default.** `--preview` shows the batch and sends nothing.
- **No invented contacts.** Every address must have the URL it was found on; an
  address that cannot be verified by hand does not get emailed.

## Where it stands

| Step | State |
|---|---|
| Offer + email copy | ✅ written (above) |
| Sender engine + tracker + suppression | ✅ built, dry-run verified |
| Target lists (grad / undergrad / workforce) | 🔄 in research, verified contacts only |
| Pilot batch sent | ⏳ after the lists land |
| Daily send + follow-up cron | ⏳ after the pilot |
| Reply tracking | ⏳ replies land in Ashley's Gmail; `--report` summarises |

## What Ashley needs to decide

Nothing to start. One thing to know: this sends **as her**, from her own Gmail,
to real people at real universities. The copy above is what goes out — if the
voice or the offer is wrong, it is much cheaper to change it now than after the
first batch.
