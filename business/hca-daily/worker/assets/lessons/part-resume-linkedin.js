// HCA Daily — Skill Path: Resume & LinkedIn (Units A)
// 4 units: Numbers Beat Nouns, Bulletproof Bullets, Headline Hooks, Profile That Recruits
window.HCA_UNITS_A = [

  {
    id: 'u1',
    title: 'Numbers Beat Nouns',
    dim: 'resume',
    level: 1,
    blurb: 'Nouns describe you. Numbers sell you.',
    items: [
      {
        type: 'flash',
        prompt: 'A payer cuts reimbursement by <b>$35/wRVU</b> on a practice producing <b>8,000 wRVUs a year</b>. What is the real annual hit?',
        options: [
          { text: '$28,000', correct: false },
          { text: '$280,000', correct: true },
          { text: '$2.8M', correct: false }
        ],
        why: '8,000 × $35 = $280,000 — recruiters want the admin who translates a rate slice into annual dollars, because $280K is a decision-size number, not a vibe.'
      },
      {
        type: 'bullet',
        prompt: 'Hiring managers scan a resume in ~6 seconds. Pick the line that survives that scan.',
        context: 'Revenue-cycle administrator resume',
        options: [
          { text: 'Responsible for billing operations and payer relations.', correct: false },
          { text: 'Lifted clean claim rate from 89% to 96% in two quarters.', correct: true },
          { text: 'Worked in revenue cycle management for several years.', correct: false }
        ],
        why: 'A before-to-after clean claim rate is a provable 7-point gain a director can build a story on, where a responsibility list only proves you held the seat.'
      },
      {
        type: 'star',
        prompt: 'Your practice runs 10,000 annual visits. A <b>3% no-show rate</b> costs you <span class="mono">___</span> visits.',
        options: [
          { text: '300', correct: true },
          { text: '30', correct: false },
          { text: '3,000', correct: false }
        ],
        why: '10,000 × 0.03 = 300 lost visits — and because those visits are billable encounters, the number is the difference between a line item and a business case.'
      },
      {
        type: 'flash',
        prompt: 'Your site hits the <b>92nd percentile</b> on HCAHPS for "likelihood to recommend." What does that signal to a hiring manager?',
        context: 'Ambulatory network with 4 clinics',
        options: [
          { text: 'You run a hospital, not a clinic.', correct: false },
          { text: 'Patients measure you better than 91% of peers — your patient-experience operations work.', correct: true },
          { text: 'Your compensation is above market.', correct: false }
        ],
        why: 'A 92nd-percentile HCAHPS score is a defensible, peer-ranked outcome that signals real patient-experience operations, and percentile rank is what executive recruiters benchmark against.'
      },
      {
        type: 'bullet',
        prompt: 'Which staffing line should a surgical practice administrator lead with?',
        options: [
          { text: 'Managed 14 providers and 40 staff across two sites.', correct: true },
          { text: 'Supervised a large clinical and non-clinical team.', correct: false },
          { text: 'Helped out with scheduling and staffing when needed.', correct: false }
        ],
        why: '"14 providers and 40 staff across two sites" gives span-of-control and scale — the two numbers that let a CEO size up your management footprint instantly.'
      },
      {
        type: 'speak',
        prompt: 'In 30 seconds, say out loud why your "responsibilities" should become a numbers-first resume. Name one number you would add and what it proves.',
        rubric: [
          'Named at least one concrete metric (e.g., days in A/R, clean claim rate, no-show rate)',
          'Tied that number to a business impact, not just activity',
          'Spoke in under 30 seconds without rambling',
          'Closed with what the number proves to a hiring manager'
        ]
      }
    ]
  },

  {
    id: 'u2',
    title: 'Bulletproof Bullets',
    dim: 'resume',
    level: 2,
    blurb: 'Thin verbs, fat numbers — bullets that survive a 6-second scan.',
    items: [
      {
        type: 'star',
        prompt: 'Denials run <b>18%</b>. A best-in-class peer operates at 7%. Your target for the next fiscal year should be <span class="mono">___%</span>.',
        options: [
          { text: '10', correct: false },
          { text: '7', correct: true },
          { text: '15', correct: false }
        ],
        why: 'Hiring managers test whether your improvement targets are benchmarked (MGMA peer median ~7%) rather than invented — a target with an external anchor shows operational literacy.'
      },
      {
        type: 'bullet',
        prompt: 'Pick the bullet that passes the "so what?" test.',
        context: 'Ambulatory practice administrator',
        options: [
          { text: 'Reduced days in A/R from 48 to 32 by reworking the front-end authorization queue.', correct: true },
          { text: 'Worked on reducing days in A/R.', correct: false },
          { text: 'Responsible for A/R and denials.', correct: false }
        ],
        why: 'A 16-day A/R improvement with a named mechanism (front-end authorization) is both a result and a proof of method — the two things a director reads for in a single line.'
      },
      {
        type: 'flash',
        prompt: 'A clinic cuts left-without-being-seen (LWBS) from 4.5% to 1.2%. What is the billing-side implication a recruiter will probe you on?',
        options: [
          { text: 'Patient satisfaction improved but revenue is unaffected.', correct: false },
          { text: 'Recaptured billable visits that previously produced zero revenue and still cost staff time.', correct: true },
          { text: 'LWBS only matters to the ED, not to clinics.', correct: false }
        ],
        why: 'Every kept visit is a billable encounter, so a 3.3-point LWBS gain reclaims revenue AND amortizes fixed staff cost — a combined impact probe that separates operators from title-holders.'
      },
      {
        type: 'bullet',
        prompt: 'Which closing bullet earns the right to say "at my previous org"?',
        options: [
          { text: 'Achieved <b>94% clean claim rate</b> for 4 consecutive quarters, beating the MGMA median for community practices.', correct: true },
          { text: 'Was named employee of the month twice.', correct: false },
          { text: 'Worked hard on claims and denials every day.', correct: false }
        ],
        why: 'A sustained 94% clean claim rate benchmarked to the MGMA median is a durability claim (4 quarters) plus an external standard — precisely the evidence a skeptic recruiter looks for.'
      },
      {
        type: 'flash',
        prompt: 'A staffing model runs 12% FTE variance against predicted volume. What does the pattern reveal you should fix?',
        options: [
          { text: 'Scheduling is matched to forecast, keeping utilization optimal.', correct: false },
          { text: 'Workforce is not flexing with volume, so you overpay some shifts and understaff others.', correct: true },
          { text: 'FTEs are too low overall and the model is broken.', correct: false }
        ],
        why: 'FTE variance vs. volume is the signature of a schedule not flexing with demand — it misprices labor both directions, and naming the mechanism makes you a cost analyst, not a scheduler.'
      },
      {
        type: 'speak',
        prompt: 'In 30 seconds, sell one bullet you would put at the top of YOUR resume. Make it start with a number, state the mechanism, and end with the business result it produced.',
        rubric: [
          'Led with a specific number, not an adjective',
          'Named the mechanism that drove the result',
          'Connected the result to revenue, cost, or patient flow',
          'Finished cleanly within 30 seconds with a strong closing line'
        ]
      }
    ]
  },

  {
    id: 'u7',
    title: 'Headline Hooks',
    dim: 'linkedin',
    level: 1,
    blurb: 'Your headline is the 60 characters recruiters read first.',
    items: [
      {
        type: 'linkedin',
        prompt: 'A recruiter searches "healthcare administrator" + your city. Which headline gets found AND read?',
        context: '40-MPH pacing, ambulatory background',
        options: [
          { text: 'Healthcare Administrator | Ambulatory Ops | Revenue Cycle', correct: true },
          { text: 'I love making healthcare work better for everyone', correct: false },
          { text: 'Administrator', correct: false }
        ],
        why: 'Stacking keyword + domain + specialty means LinkedIn\'s search returns you for the exact terms a recruiter types, while a slogan or a single word costs you both the search rank and the scan.'
      },
      {
        type: 'flash',
        prompt: 'Your headline contains "Revenue Cycle." A recruiter\'s LinkedIn search uses the term <b>"clean claim rate."</b> What happens?',
        options: [
          { text: 'You match, because recruiters always use generic broad terms.', correct: false },
          { text: 'You may not surface — search matches headline keywords, so mirror recruiters\' exact terms.', correct: true },
          { text: 'Headlines do not affect recruiter search at all.', correct: false }
        ],
        why: 'LinkedIn recruiter search is keyword-matching, so if your headline and first 40 words do not echo the recruiter\'s exact boolean terms, you rank below a peer who does.'
      },
      {
        type: 'bullet',
        prompt: 'Which headline wins the 2-second glance on a mobile feed?',
        options: [
          { text: 'Healthcare Administrator | Reducing Denials Since 2021', correct: true },
          { text: 'Passionate, driven, results-focused professional', correct: false },
          { text: 'Looking for my next opportunity in healthcare', correct: false }
        ],
        why: '"Reducing Denials Since 2021" packs a specialty plus a proof of time-in-role, where vague filler and job-seeking language read as noise a busy recruiter scrolls past.'
      },
      {
        type: 'star',
        prompt: 'Recruiters on LinkedIn have about <span class="mono">___ seconds</span> to decide whether to click your profile from a search result.',
        options: [
          { text: '15', correct: false },
          { text: '5', correct: true },
          { text: '90', correct: false }
        ],
        why: 'Recruiter scan time is measured in seconds, so your headline has to deliver the value proposition before they scroll — that is why keyword density beats prose.'
      },
      {
        type: 'linkedin',
        prompt: 'You run a 6-chair outpatient dialysis center. Which headline makes recruiters slow down?',
        options: [
          { text: 'Dialysis Center Administrator | CMS Star Rating 4 | 6 Chairs | Community-Based Care', correct: true },
          { text: 'Operations Manager at a Healthcare Facility', correct: false },
          { text: 'Administrator', correct: false }
        ],
        why: 'CMS star rating plus chair count is a concrete, searchable differentiator that answers "what is this person good at" in under seven words — specificity drives the click.'
      },
      {
        type: 'speak',
        prompt: 'In 30 seconds, pitch a recruiter three headline options for a mid-career ambulatory administrator — a keyword-stacked one, a metric-led one, and one to avoid. End by recommending one and why.',
        rubric: [
          'Delivered three distinct headline options, not variations of one',
          'Included at least one searchable metric or specialty keyword',
          'Named the one headline to avoid and a reason',
          'Made a confident recommendation within 30 seconds'
        ]
      }
    ]
  },

  {
    id: 'u8',
    title: 'Profile That Recruits',
    dim: 'linkedin',
    level: 2,
    blurb: 'Turn your profile into a searchable asset that attracts, not just describes.',
    items: [
      {
        type: 'linkedin',
        prompt: 'Pick the headline that signals "operator," not "aspirant" — recruiters keyword-match these terms.',
        options: [
          { text: 'Ambulatory Operations Leader | wRVU Contracts · Days in A/R · Denials', correct: true },
          { text: 'Healthcare Professional Seeking Opportunities', correct: false },
          { text: 'Life-long learner and team player', correct: false }
        ],
        why: 'Naming wRVU contracts and days in A/R as headline keywords marks you as someone who owns the money metrics, so recruiters filtering by those terms surface you and stay.'
      },
      {
        type: 'bullet',
        prompt: 'Which "About" opening hooks a recruiter deciding whether to read on?',
        options: [
          { text: 'I run ambulatory revenue operations and took clean claim rate from 88% to 95% in one fiscal year.', correct: true },
          { text: 'I am a hardworking healthcare professional who loves helping patients.', correct: false },
          { text: 'My name is Alex and I have worked in healthcare for a while.', correct: false }
        ],
        why: 'An About section that opens with a specific, quantified feat gives the recruiter an immediate reason to keep reading — an outcome beats a value statement every time.'
      },
      {
        type: 'flash',
        prompt: 'Your profile "skills" list ends with <b>"Microsoft Excel."</b> A recruiter searches the skill <b>"Power BI building."</b> What does your profile lose?',
        options: [
          { text: 'Nothing — skills are not searchable.', correct: false },
          { text: 'Ranked visibility on that exact skill, because search matches the skill taxonomy, not close synonyms.', correct: true },
          { text: 'Only your recommendations section is affected.', correct: false }
        ],
        why: 'LinkedIn skill search matches against its skill taxonomy, so a near-miss skill term gets you skipped while a peer carrying the exact skill name ranks — keyword precision is what makes you recruiter-found.'
      },
      {
        type: 'star',
        prompt: 'LinkedIn shows about the first <span class="mono">___</span> lines of your About section before "see more" hides the rest.',
        options: [
          { text: '8', correct: false },
          { text: '3', correct: true },
          { text: '20', correct: false }
        ],
        why: 'Only the first ~3 visible lines earn the click to expand, so your hook has to land a quantified claim immediately or the rest of your story never gets read.'
      },
      {
        type: 'linkedin',
        prompt: 'Which headline converts an inbound recruiter into a "message you" action?',
        context: 'Practice manager targeting $120K–$160K roles',
        options: [
          { text: 'Practice Administrator | 22 Providers · 94% Clean Claims · MS in HCA', correct: true },
          { text: 'Manager at Medical Group', correct: false },
          { text: 'Open to new challenges and growth opportunities', correct: false }
        ],
        why: 'Scale (22 providers), a top-quartile outcome (94% clean claims), and credential (MS) together give a recruiter the exact data needed to qualify you in one glance and take the next step.'
      },
      {
        type: 'speak',
        prompt: 'In 30 seconds, walk a mentor through the one change you would make to your LinkedIn profile THIS week to raise your recruiter-search rank. Name the section, the exact term you would add, and the metric you would use as proof.',
        rubric: [
          'Named one specific profile section to change',
          'Chose an exact, recruiter-searchable term (not a generic quality)',
          'Included a concrete metric as supporting proof',
          'Stated the expected effect on search visibility in 30 seconds'
        ]
      }
    ]
  }
];