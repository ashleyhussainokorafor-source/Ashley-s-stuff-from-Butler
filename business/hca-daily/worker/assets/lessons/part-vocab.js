// HCA Daily — Vocabulary Drill Units (Part B: Units 3–6)
// Each unit is a vocabulary drill. Item keys per schema:
//   type: 'flash' | 'bullet' | 'star' | 'linkedin' | 'speak'
//   prompt (may include <b> or <span class="mono">), context (optional),
//   options:[{text,correct}] for non-speak, why (one-sentence, names the metric),
//   rubric:[4 checks] for 'speak' only.
(function () {
  window.HCA_UNITS_B = [
    {
      id: 'u3',
      title: 'Revenue Cycle in 6 Numbers',
      dim: 'vocabulary',
      level: 1,
      items: [
        {
          type: 'flash',
          prompt: 'A claim goes out on day 5 and gets paid on day 42. A manager reads the <span class="mono">Days in A/R</span> gauge as 42. What does a rising number on this gauge signal?',
          context: 'Interview prompt: "Your days in A/R jumped eight days quarter over quarter."',
          options: [
            { text: 'Cash is coming in more slowly — a revenue-cycle red flag', correct: true },
            { text: 'The billing team is submitting claims faster', correct: false },
            { text: 'Denial rates are going down', correct: false },
            { text: 'Contractual adjustments are shrinking', correct: false }
          ],
          why: 'Days in A/R is the classic cash-flow metric — when it climbs, money is aging on the books and the revenue cycle is backing up.'
        },
        {
          type: 'flash',
          prompt: 'Your team submits 1,000 claims this month and 140 come back needing rework or denial. What is the <span class="mono">denial rate</span>?',
          options: [
            { text: '14%', correct: true },
            { text: '1.4%', correct: false },
            { text: '140%', correct: false },
            { text: '0.14%', correct: false }
          ],
          why: 'Denial rate (140 ÷ 1,000) is the revenue-leak metric every finance leader quotes before anything else.'
        },
        {
          type: 'flash',
          prompt: 'Which single metric best tells you whether your front-end registration and eligibility work is getting claims accepted <b>the first time</b>?',
          context: 'Benchmark pressure: a payer just flagged your registration quality.',
          options: [
            { text: 'Clean claim rate', correct: true },
            { text: 'Gross collection rate', correct: false },
            { text: 'Cost-to-collect', correct: false },
            { text: 'Days in A/R', correct: false }
          ],
          why: 'Clean claim rate measures first-pass acceptance, so it isolates capture and eligibility problems before they ever become denials.'
        },
        {
          type: 'flash',
          prompt: 'A smaller practice spends $45,000 on billing staff and collections for a quarter and brings in $900,000 of collected revenue. What is its <span class="mono">cost-to-collect</span>?',
          options: [
            { text: '5%', correct: true },
            { text: '0.5%', correct: false },
            { text: '50%', correct: false },
            { text: '20%', correct: false }
          ],
          why: 'Cost-to-collect (45,000 ÷ 900,000) is the efficiency metric that shows how much of every dollar you burn to bring a dollar in.'
        },
        {
          type: 'bullet',
          prompt: 'You are briefing leadership on the revenue cycle. Which number do you lead with to show <b>how much of allowed reimbursement you actually kept</b>?',
          context: 'Leadership wants one number that captures write-offs, denials, and bad debt together.',
          options: [
            { text: 'Net collection rate', correct: true },
            { text: 'Face-value gross charges', correct: false },
            { text: 'Total encounters', correct: false },
            { text: 'Average co-pay collected', correct: false }
          ],
          why: 'Net collection rate measures allowed revenue actually captured, so it rolls denials, write-offs, and bad debt into a single number.'
        },
        {
          type: 'flash',
          prompt: 'Your billing team now submits claims within <b>two business days</b> of service instead of ten. Which downstream metric should improve as a direct result?',
          options: [
            { text: 'Days in A/R', correct: true },
            { text: 'Cost-to-collect', correct: false },
            { text: 'Net collection rate', correct: false },
            { text: 'Clean claim rate', correct: false }
          ],
          why: 'Faster <span class="mono">days-to-bill</span> shortens Days in A/R because the clock starts earlier on every claim.'
        }
      ]
    },
    {
      id: 'u4',
      title: 'Clinical Ops Fluency',
      dim: 'vocabulary',
      level: 2,
      items: [
        {
          type: 'flash',
          prompt: 'A clinic books 200 appointments this week and 32 patients never show and never cancel. What is the <span class="mono">no-show</span> rate?',
          options: [
            { text: '16%', correct: true },
            { text: '1.6%', correct: false },
            { text: '32%', correct: false },
            { text: '6.4%', correct: false }
          ],
          why: 'No-show rate (32 ÷ 200) is the scheduling metric that directly caps how much physician and staff capacity actually gets used.'
        },
        {
          type: 'flash',
          prompt: 'One physician produces work valued at $3,000 in <span class="mono">wRVU</span> this week. What is that $3,000 actually measuring?',
          context: 'A recruiter asks you to compare two physicians\u2019 productivity.',
          options: [
            { text: 'The complexity-weighted volume of work the physician performed', correct: true },
            { text: 'The dollar amount the practice collected', correct: false },
            { text: 'The number of patients seen', correct: false },
            { text: 'The physician\u2019s salary', correct: false }
          ],
          why: 'wRVU (work relative value units) is the productivity metric that weights clinical work by complexity, so it compares physicians fairly regardless of payer mix.'
        },
        {
          type: 'flash',
          prompt: 'Your plan calls for 40.0 FTE of nursing staff but the schedule actually consumes 43.4 FTE. What metric describes this gap?',
          options: [
            { text: 'FTE variance', correct: true },
            { text: 'No-show rate', correct: false },
            { text: 'Contribution margin', correct: false },
            { text: 'ALOS', correct: false }
          ],
          why: 'FTE variance (43.4 vs 40.0) is the staffing metric that flags budget overruns before they hit labor cost per unit of service.'
        },
        {
          type: 'flash',
          prompt: 'Inpatient admits this month total 1,500 patient-days across 120 admissions. What is the average length of stay (<span class="mono">ALOS</span>)?',
          options: [
            { text: '12.5 days', correct: true },
            { text: '8 days', correct: false },
            { text: '0.08 days', correct: false },
            { text: '1,625 days', correct: false }
          ],
          why: 'ALOS (1,500 ÷ 120) is the utilization metric that ties throughput to bed capacity and the cost of each admission.'
        },
        {
          type: 'flash',
          prompt: 'An ED is full but patients are leaving before treatment. Which metric captures these patients and matters most to hospital leaders and the board?',
          context: 'ED leadership asks you to explain why wait times are misrepresenting demand.',
          options: [
            { text: 'LWBS (left without being seen)', correct: true },
            { text: 'No-show rate', correct: false },
            { text: 'FTE variance', correct: false },
            { text: 'Clean claim rate', correct: false }
          ],
          why: 'LWBS is the ED access metric that signals capacity failure and lost revenue, and it is a safety and survey risk for the hospital.'
        },
        {
          type: 'speak',
          prompt: 'Say the sentence a hiring manager wants to hear when you explain why you track <b>contribution margin</b> for a service line: what it measures, what a low or negative margin tells you, and the one number you pull to fix it.',
          rubric: [
            'Defines contribution margin as revenue left after direct variable costs (not total profit, not raw charges)',
            'States that a low or negative margin means the service line loses money or barely breaks even on direct costs',
            'Names which number (wRVU, encounters, cases, or revenue) they would track to diagnose the driver',
            'Speaks in sharp, metric-literate language with no filler'
          ]
        }
      ]
    },
    {
      id: 'u5',
      title: 'Quality & Compliance Speak',
      dim: 'vocabulary',
      level: 2,
      items: [
        {
          type: 'flash',
          prompt: 'Your hospital\u2019s overall <span class="mono">HCAHPS</span> results show a strong composite score. What is that score summarizing?',
          context: 'The board wants one number that reflects the patient experience story.',
          options: [
            { text: 'The patient\u2019s experience of care, including communication and nursing, rolled into one composite', correct: true },
            { text: 'The hospital\u2019s infection rate', correct: false },
            { text: 'The accuracy of billing', correct: false },
            { text: 'The physician\u2019s clinical complexity load', correct: false }
          ],
          why: 'The HCAHPS composite is the patient-experience metric that feeds Star ratings and reimbursement incentives.'
        },
        {
          type: 'flash',
          prompt: 'Of 400 Medicare patients discharged in Q1, 56 are readmitted within 30 days for any cause. What is the <span class="mono">30-day readmission</span> rate?',
          options: [
            { text: '14%', correct: true },
            { text: '1.4%', correct: false },
            { text: '56%', correct: false },
            { text: '7%', correct: false }
          ],
          why: 'Readmission rate (56 ÷ 400) is the quality and penalty metric that directly drives Medicare reimbursement and hospital reputation.'
        },
        {
          type: 'flash',
          prompt: 'CMS publishes a public rating that patients and payers see first to judge a facility\u2019s quality. Which measure is that?',
          context: 'Care coordination interviews ask you to talk quality signals an outsider can verify.',
          options: [
            { text: 'CMS Star rating', correct: true },
            { text: 'HEDIS measure', correct: false },
            { text: 'Cost-to-collect', correct: false },
            { text: 'FTE variance', correct: false }
          ],
          why: 'The CMS Star rating is the public quality metric that compresses clinical, safety, and experience data into a 1–5 score patients and payers trust.'
        },
        {
          type: 'bullet',
          prompt: 'You oversee a Medicare Advantage plan\u2019s performance. Which set of measures would you pull to show members, regulators, and the plan how well it is actually delivering quality?',
          options: [
            { text: 'HEDIS measures', correct: true },
            { text: 'Days in A/R', correct: false },
            { text: 'Cost-to-collect', correct: false },
            { text: 'FTE variance', correct: false }
          ],
          why: 'HEDIS is the standardized quality-measure set that payers and NCQA use to benchmark and contract performance across care delivery.'
        },
        {
          type: 'flash',
          prompt: 'A payer is deciding whether to renew a network contract. Which <b>patient-reported</b> survey metric best complements your HEDIS clinical data for that conversation?',
          options: [
            { text: 'CAHPS survey results', correct: true },
            { text: 'Clean claim rate', correct: false },
            { text: 'wRVU totals', correct: false },
            { text: 'Days in A/R', correct: false }
          ],
          why: 'CAHPS is the patient-experience survey metric that pairs with HEDIS clinical measures to give a complete quality picture.'
        },
        {
          type: 'speak',
          prompt: 'In one breath, tell a compliance committee how you would keep a quality program <b>audit-ready</b>: the documentation you maintain, how you prove your measures are current, and the metric that would raise a red flag if it slipped.',
          rubric: [
            'Names concrete retained artifacts (policies, training logs, measure documentation, audit trails)',
            'Explains how the program proves measures reflect the current reporting period and rules',
            'Identifies a specific red-flag metric (HCAHPS composite, readmission rate, HEDIS, or Star rating)',
            'Answers in sharp, compliance-literate language that lands in under a minute'
          ]
        }
      ]
    },
    {
      id: 'u6',
      title: 'LTC & Post-Acute Metrics',
      dim: 'vocabulary',
      level: 3,
      items: [
        {
          type: 'flash',
          prompt: 'A 120-bed skilled nursing facility averages 108 occupied beds this month. What is its <span class="mono">occupancy</span> rate?',
          options: [
            { text: '90%', correct: true },
            { text: '1.1%', correct: false },
            { text: '108%', correct: false },
            { text: '11%', correct: false }
          ],
          why: 'Occupancy (108 ÷ 120) is the core LTC revenue and census metric every operator quotes because it drives the bulk of facility revenue.'
        },
        {
          type: 'flash',
          prompt: 'A facility\u2019s residents require heavier nursing and therapy, and its payer thinks it is caring for a lighter, cheaper mix. What metric shows the true acuity of the census?',
          context: 'A rate-negotiation conversation is stalling on acuity disagreement.',
          options: [
            { text: 'Case-mix index', correct: true },
            { text: 'Occupancy', correct: false },
            { text: 'Cost-to-collect', correct: false },
            { text: 'No-show rate', correct: false }
          ],
          why: 'Case-mix index quantifies resident acuity and supports rate and staffing negotiations when the census is heavier than the payer believes.'
        },
        {
          type: 'star',
          prompt: 'Medicare is restructuring how facilities are paid for Part A skilled-nursing stays, shifting from a therapy-minute system to a patient-driven model. What acronym should you cite when discussing this transition?',
          options: [
            { text: 'PDPM', correct: true },
            { text: 'HEDIS', correct: false },
            { text: 'wRVU', correct: false },
            { text: 'CAHPS', correct: false }
          ],
          why: 'PDPM (Patient-Driven Payment Model) is the Medicare payment reform metric-adjacent policy that removed the therapy-time incentive and reshaped SNF reimbursement.'
        },
        {
          type: 'bullet',
          prompt: 'A regional director reviews facilities and wants to know which one is strongest on publicly reported quality. Which source do you point them to first for <b>skilled nursing</b>?',
          options: [
            { text: 'CMS Nursing Home (Five-Star) ratings', correct: true },
            { text: 'Clean claim rate', correct: false },
            { text: 'FTE variance', correct: false },
            { text: 'wRVU totals', correct: false }
          ],
          why: 'The CMS Five-Star rating is the public quality metric families, payers, and regulators use to judge a nursing home, so it also becomes a marketing and contract tool.'
        },
        {
          type: 'flash',
          prompt: 'A post-acute unit reports 60 resident-days delivered across 5 rehab admissions. What length-of-stay signal does this give the operator?',
          options: [
            { text: 'Average length of stay of 12 days — helpful for staffing and readmission planning', correct: true },
            { text: 'Occupancy of 12%', correct: false },
            { text: 'A 5-star rating', correct: false },
            { text: 'A case-mix index of 60', correct: false }
          ],
          why: 'ALOS (60 ÷ 5) in post-acute tints staffing ratios, reimbursement timing, and readmission risk across the care continuum.'
        },
        {
          type: 'speak',
          prompt: 'Persuade an operator in 40 seconds to track both <b>occupancy</b> and <b>case-mix index</b>: what each one captures, why tracking them together beats tracking revenue alone, and which one is more likely to move before a payer re-rates the contract.',
          rubric: [
            'Defines occupancy as beds filled and case-mix index as resident acuity, distinguishing revenue volume from revenue quality',
            'Explains that together they separate \u201chow full\u201d from \u201chow heavy\u201d to diagnose whether rate or census is the weak lever',
            'Notes case-mix index is the metric a payer re-rates on when acuity or documentation shifts',
            'Delivers a persuasive, metric-literate pitch in under 40 seconds'
          ]
        }
      ]
    }
  ];
})();