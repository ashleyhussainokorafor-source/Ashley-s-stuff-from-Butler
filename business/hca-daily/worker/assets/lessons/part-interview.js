// HCA Daily — Interview Delivery drill units (part C).
// Each unit holds 5 recall items mixing 'star' (fill the missing metric/number
// in a STAR result), 'speak' (real interview question with a 4-check rubric),
// and 'bullet' (pick the line a hiring manager actually believes).
// DR. ASHLEY HUSSAIN-OKAFORA, DBA · HCA Daily
window.HCA_UNITS_C = [
  {
    id: "u9",
    title: "Behavioral STAR Foundations",
    dim: "interview",
    level: 1,
    items: [
      {
        type: "star",
        prompt: "Finish the result in this STAR: \u201cI launched an SMS reminder workflow for the front desk, and within one quarter our <b>no-show rate</b> dropped from 18% to\u2026\u201d",
        context: "No-show rate = patients who miss an appointment without canceling. A 3-point drop at a 900-appointments-per-week clinic is roughly 27 fewer empty slots weekly.",
        options: [
          { text: "11%", correct: true },
          { text: "17%", correct: false },
          { text: "15%", correct: false },
          { text: "8%", correct: false }
        ],
        why: "Hiring managers read the number literally: a specific, measurable no-show drop proves the workflow changed behavior, not that you \u201chelped a bit.\u201d"
      },
      {
        type: "bullet",
        prompt: "Which STAR result line would a hiring manager actually trust in your interview story?",
        context: "You are describing a patient-access improvement you owned.",
        options: [
          { text: "\u201cCut average wait time from 24 minutes to 11 minutes across three clinics by rebalancing check-in.\u201d", correct: true },
          { text: "\u201cWorked with the front desk to make check-in faster for more patients.\u201d", correct: false },
          { text: "\u201cReduced wait times somewhat after changing some processes.\u201d", correct: false },
          { text: "\u201cHelped the team feel better about patient flow.\u201d", correct: false }
        ],
        why: "Specific before/after numbers on a named metric let the interviewer hold your story, replay it, and verify impact \u2014 vague opens do not survive the room."
      },
      {
        type: "speak",
        prompt: "\u201cTell me about a time you failed.\u201d",
        context: "Answer in under 90 seconds with a real story, not a disguised win.",
        rubric: [
          "Named a hard metric you were chasing (goal, target, or baseline)",
          "Included a concrete number that shows the miss (e.g., missed target by X)",
          "Owned the action \u2014 used \u2018I decided,\u2019 not \u2018we were told\u2019",
          "Tied the lesson to margin or operations (cost, patients, revenue, flow)"
        ]
      },
      {
        type: "star",
        prompt: "Complete the STAR outcome: \u201cAfter scripting front-desk check-in and adding pre-visit calls, our <b>patient satisfaction</b> (top-box on surveys) went from 71% to\u2026\u201d",
        context: "Top-box = 9–10 on the survey scale, the slice most leaders track.",
        options: [
          { text: "84%", correct: true },
          { text: "72%", correct: false },
          { text: "75%", correct: false },
          { text: "71%", correct: false }
        ],
        why: "Patient satisfaction is the operating metric behind HCAHPS-style scores; a clean 13-point jump reads as real process change, not a rounding artifact."
      },
      {
        type: "bullet",
        prompt: "Pick the STAR line that proves <b>you</b> caused the result, not your team by accident.",
        options: [
          { text: "\u201cI built the tracker, set the weekly cadence, and personally reconciled every discrepancy each Friday.\u201d", correct: true },
          { text: "\u201cThe team did a great job tracking denials better.\u201d", correct: false },
          { text: "\u201cDenial rate improved during my time there.\u201d", correct: false },
          { text: "\u201cWe sort of got faster at reconciliation over time.\u201d", correct: false }
        ],
        why: "The \u2018A\u2019 in STAR is your action \u2014 an active verb tied to a metric shows ownership, which is the difference between a candidate and a bystander."
      }
    ]
  },
  {
    id: "u10",
    title: "Leadership Stories",
    dim: "interview",
    level: 2,
    items: [
      {
        type: "star",
        prompt: "Fill the missing number: \u201cI introduced manager check-ins and a real promotion path, and our annual <b>staff turnover</b> fell from 32% to\u2026\u201d",
        context: "Turnover = staff who leave in a year ÷ average headcount. At 40 FTE, every 5 points is about 2 fewer people walking out the door per year.",
        options: [
          { text: "19%", correct: true },
          { text: "30%", correct: false },
          { text: "33%", correct: false },
          { text: "25%", correct: false }
        ],
        why: "Turnover reduction is the leadership margin story \u2014 every retained employee avoids recruiting, onboarding, and overtime cost, so leaders quote it cold."
      },
      {
        type: "speak",
        prompt: "\u201cDescribe a time you led a team through change.\u201d",
        context: "Use STAR. Focus on the decision you made and how you carried people with you.",
        rubric: [
          "Named the metric the change moved (retention, engagement, wait time, cost)",
          "Included a number that anchors the before-and-after (e.g., from 21 to 9 weeks)",
          "Owned the action \u2014 \u2018I set the plan,\u2019 \u2018I made the call\u2019",
          "Tied the outcome to margin or operations (overtime, lost revenue, patient flow)"
        ]
      },
      {
        type: "bullet",
        prompt: "Which leadership-impact bullet do interviews believe without a second read?",
        options: [
          { text: "\u201cImproved team engagement score from 3.1 to 4.4 of 5 by restructuring huddles and recognition.\u201d", correct: true },
          { text: "\u201cKept the team happy and motivated.\u201d", correct: false },
          { text: "\u201cGenerally boosted morale around the office.\u201d", correct: false },
          { text: "\u201cPeople seemed more engaged after I got there.\u201d", correct: false }
        ],
        why: "Engagement scores are a tracked HR metric; a before/after delta proves the leadership skill, whereas \u2018happy team\u2019 is an opinion with no evidence."
      },
      {
        type: "star",
        prompt: "Complete the leadership result: \u201cI sponsored a cross-department huddle and clarified roles, and <b>staff engagement survey participation</b> climbed from 54% to\u2026\u201d",
        context: "Participation rate = how many eligible staff actually answered the survey.",
        options: [
          { text: "88%", correct: true },
          { text: "55%", correct: false },
          { text: "60%", correct: false },
          { text: "51%", correct: false }
        ],
        why: "High participation is what makes an engagement survey trustworthy; leaders track it closely, and a 30+ point jump signals real buy-in, not a rubber-stamp."
      },
      {
        type: "bullet",
        prompt: "Choose the response that shows leadership ownership (the \u2018A\u2019 of STAR) over a metric problem.",
        options: [
          { text: "\u201cI stopped the blame game, audited the overtime pattern myself, and reset the staffing grid.\u201d", correct: true },
          { text: "\u201cOvertime went down because the schedule was better.\u201d", correct: false },
          { text: "\u201cNobody really planned it; it just improved.\u201d", correct: false },
          { text: "\u201cMy director suggested the schedule change.\u201d", correct: false }
        ],
        why: "Leaders are hired to own problems, not describe them; a first-person active verb on a real cost \u2014 overtime \u2014 is what separates a manager from a narrator."
      }
    ]
  },
  {
    id: "u11",
    title: "Operational Interview Answers",
    dim: "interview",
    level: 2,
    items: [
      {
        type: "star",
        prompt: "Fill the missing metric: \u201cBy front-loading orders and cueing registration, we cut our average <b>discharge cycle time</b> from 3.2 hours to\u2026\u201d",
        context: "Discharge cycle time = hours from the discharge order to a cleaned bed ready for the next patient.",
        options: [
          { text: "1.4 hours", correct: true },
          { text: "3.0 hours", correct: false },
          { text: "2.9 hours", correct: false },
          { text: "3.1 hours", correct: false }
        ],
        why: "Faster discharge cycle time frees beds and ED capacity \u2014 an operations leader names it in hours because it maps directly to throughput and capacity."
      },
      {
        type: "speak",
        prompt: "\u201cWalk me through a process you improved.\u201d",
        context: "STAR, operational flavor. Name the constraint, your fix, and the measured result.",
        rubric: [
          "Named the process metric (cycle time, wait time, turnaround, cost per case)",
          "Included a number that anchors the improvement (e.g., from 40 to 22 minutes)",
          "Owned the action \u2014 \u2018I ran the pilot,\u2019 \u2018I designed the flow\u2019",
          "Tied the result to margin or operations (throughput, overtime, waste, revenue)"
        ]
      },
      {
        type: "bullet",
        prompt: "Which operational-answer line makes an interviewer mentally nod?",
        options: [
          { text: "\u201cLeaner scheduling cut clinic no-show rate from 16% to 9% and added 5 net new patient slots a day.\u201d", correct: true },
          { text: "\u201cScheduling got a lot better for the clinic.\u201d", correct: false },
          { text: "\u201cWe improved the schedule somewhat.\u201d", correct: false },
          { text: "\u201cDoctors liked the new schedule.\u201d", correct: false }
        ],
        why: "Pairing a metric (no-show rate) with a capacity payoff (net new slots) shows you think in operations, not just activity \u2014 exactly what ops leaders screen for."
      },
      {
        type: "star",
        prompt: "Complete the ops result: \u201cAfter standardizing supply ordering and par levels, our <b>supply cost per case</b> dropped from $312 to\u2026\u201d",
        context: "Supply cost per case = total supplies used ÷ number of procedures in the period.",
        options: [
          { text: "$264", correct: true },
          { text: "$305", correct: false },
          { text: "$311", correct: false },
          { text: "$318", correct: false }
        ],
        why: "Per-case supply cost is the purest ops-cost-per-unit metric; a $48 swing at scale compounds into real margin, so experts quote it in dollars, not percentages."
      },
      {
        type: "bullet",
        prompt: "Pick the operating-room answer that names a metric the CFO parses.",
        options: [
          { text: "\u201cRaised on-time first-case starts from 61% to 92% by freezing block time.\u201d", correct: true },
          { text: "\u201cMade the OR start closer to on time.\u201d", correct: false },
          { text: "\u201cSurgeons were happier with the schedule.\u201d", correct: false },
          { text: "\u201cFirst-case starts were better in general.\u201d", correct: false }
        ],
        why: "First-case on-time start is a regulated, benchmarked OR metric tied to staff overtime and room utilization \u2014 the exact lens a CFO and CNO share."
      }
    ]
  },
  {
    id: "u12",
    title: "Revenue Cycle Answers",
    dim: "interview",
    level: 2,
    items: [
      {
        type: "star",
        prompt: "Fill the missing number: \u201cBy scripting registration and catching errors at the front desk, we cut <b>days in A/R</b> from 52 to\u2026\u201d",
        context: "Days in A/R = average days between charge and payment/denial; the higher it climbs, the more cash is stuck and at risk.",
        options: [
          { text: "38", correct: true },
          { text: "51", correct: false },
          { text: "50", correct: false },
          { text: "53", correct: false }
        ],
        why: "Days in A/R is the single number revenue-cycle leads watch \u2014 a 14-day pull shortens cash conversion and lowers bad-debt exposure, which is real money."
      },
      {
        type: "speak",
        prompt: "\u201cHow would you reduce denials?\u201d",
        context: "Give a process answer, not a slogan. Name a metric, a number, and the fix.",
        rubric: [
          "Named the metric (denial rate, first-pass claim acceptance, clean claim rate)",
          "Included a number (e.g., target <5% denial rate or cut denials by 30%)",
          "Owned the action \u2014 \u2018I would audit,\u2019 \u2018I would train,\u2019 \u2018I would fix the root cause\u2019",
          "Tied it to margin or operations (cash recovery, rework cost, write-offs)"
        ]
      },
      {
        type: "bullet",
        prompt: "Which revenue-cycle answer shows you understand front-end cash control?",
        options: [
          { text: "\u201cVerified eligibility at check-in and cut the clean claim rate from 74% to 91%.\u201d", correct: true },
          { text: "\u201cClaims got more accurate after a while.\u201d", correct: false },
          { text: "\u201cWe tried to bill things more correctly.\u201d", correct: false },
          { text: "\u201cPayer issues caused most of the denials.\u201d", correct: false }
        ],
        why: "Clean claim rate is the front-end health gauge \u2014 raising it upstream keeps claims out of the denial queue before they ever become rework cost."
      },
      {
        type: "star",
        prompt: "Complete the result: \u201cAfter retraining the team on auth and coding checks, our <b>denial rate</b> fell from 11% to\u2026\u201d",
        context: "Denial rate = claims rejected by payers ÷ total claims submitted.",
        options: [
          { text: "4%", correct: true },
          { text: "10%", correct: false },
          { text: "12%", correct: false },
          { text: "9%", correct: false }
        ],
        why: "Denial rate under 5% is the benchmark leaders quote; a 7-point drop is a cash-preserving headline, and the denominator tells them how much is at stake."
      },
      {
        type: "bullet",
        prompt: "Choose the answer that links revenue-cycle work to bottom-line margin, not just volume.",
        options: [
          { text: "\u201cRaised net collection rate from 47% to 59%, adding roughly $1.2M in collected cash annually.\u201d", correct: true },
          { text: "\u201cProcessed a lot more claims every month.\u201d", correct: false },
          { text: "\u201cBilling volume went up nicely.\u201d", correct: false },
          { text: "\u201cHandled more accounts than before.\u201d", correct: false }
        ],
        why: "Net collection rate converts activity into actual cash captured; naming the dollar impact is what makes a revenue-cycle candidate land the offer."
      }
    ]
  },
  {
    id: "u13",
    title: "Clinical Ops & Quality Answers",
    dim: "interview",
    level: 3,
    items: [
      {
        type: "star",
        prompt: "Fill the missing number: \u201cBy hardening discharge teaching and follow-up calls, we cut the 30-day <b>readmission rate</b> from 14% to\u2026\u201d",
        context: "Readmission rate = patients who return within 30 days ÷ discharges; each readmission costs revenue dollars and quality standing.",
        options: [
          { text: "8%", correct: true },
          { text: "13%", correct: false },
          { text: "15%", correct: false },
          { text: "12%", correct: false }
        ],
        why: "Readmission rate is a CMS-starred quality metric tied to penalties and reimbursement; a 6-point cut is both a patient-safety and a financial story."
      },
      {
        type: "speak",
        prompt: "\u201cHow do you drive quality improvement?\u201d",
        context: "Answer with a real initiative, a metric, and a number. Show you know quality is data, not vibes.",
        rubric: [
          "Named the metric (HCAHPS, CLABSI, CAUTI, readmission rate, patient harm)",
          "Included a number that anchors the effort (baseline and target)",
          "Owned the action \u2014 \u2018I led the workgroup,\u2019 \u2018I ran the PDSA\u2019",
          "Tied it to margin or operations (penalty avoidance, LOS, cost, reimbursement)"
        ]
      },
      {
        type: "bullet",
        prompt: "Which quality answer proves you track outcomes that regulators and payers weight?",
        options: [
          { text: "\u201cDrove HCAHPS top-box from 68% to 81% by scripted rounding and leader follow-up.\u201d", correct: true },
          { text: "\u201cPatients seemed much happier with their care.\u201d", correct: false },
          { text: "\u201cQuality got better overall during my tenure.\u201d", correct: false },
          { text: "\u201cEveryone was working harder on satisfaction.\u201d", correct: false }
        ],
        why: "HCAHPS is the federally scored patient-experience survey tied to reimbursement; naming it with a top-box delta proves you work on regulated, benchmarked measures."
      },
      {
        type: "star",
        prompt: "Complete the clinical-ops result: \u201cAfter standardizing line-maintenance rounds, our <b>CLABSI rate</b> per 1,000 line-days dropped from 1.8 to\u2026\u201d",
        context: "CLABSI = central line-associated bloodstream infection, counted per 1,000 central line-days.",
        options: [
          { text: "0.5", correct: true },
          { text: "1.7", correct: false },
          { text: "1.9", correct: false },
          { text: "1.6", correct: false }
        ],
        why: "Infection rates are the metrics payers and regulators penalize; a sub-1.0 CLABSI rate is the credibility number clinical-ops leaders hold in their head."
      },
      {
        type: "bullet",
        prompt: "Select the answer that connects quality directly to the operating margin.",
        options: [
          { text: "\u201cAvoided roughly $800K in readmission-penalty exposure by sustaining an 8% readmission rate.\u201d", correct: true },
          { text: "\u201cKept readmissions from being too high.\u201d", correct: false },
          { text: "\u201cPatients stopped coming back as often.\u201d", correct: false },
          { text: "\u201cQuality work went reasonably well.\u201d", correct: false }
        ],
        why: "Quality roles live or die on whether you can translate a metric into penalty avoidance and reimbursement \u2014 the language CFOs and CNOs actually negotiate in."
      }
    ]
  },
  {
    id: "u14",
    title: "HIM & LTC Answers",
    dim: "interview",
    level: 3,
    items: [
      {
        type: "star",
        prompt: "Fill the missing number: \u201cBy adding query tracking and faster physician turnaround, we cut <b>average documentation-to-closure days</b> from 12 to\u2026\u201d",
        context: "Documentation-to-closure days = days from service until the record is complete and billable.",
        options: [
          { text: "5", correct: true },
          { text: "11", correct: false },
          { text: "13", correct: false },
          { text: "10", correct: false }
        ],
        why: "Faster record closure speeds claim submission and cash \u2014 an HIM answer that names turnaround days shows you connect documentation to revenue, not just files."
      },
      {
        type: "speak",
        prompt: "\u201cExplain how accurate coding affects revenue.\u201d",
        context: "Bridge HIM compliance and revenue. Use a metric and a number, and own the process.",
        rubric: [
          "Named the metric (query rate, coder productivity, claim lag, denial rate)",
          "Included a number (e.g., 98% correct coding or a day-count target)",
          "Owned the action \u2014 \u2018I built the query log,\u2019 \u2018I trained coders\u2019",
          "Tied it to margin or operations (clean claims, cash lag, compliance risk, reimbursement)"
        ]
      },
      {
        type: "bullet",
        prompt: "Which HIM answer shows you treat documentation as a revenue driver?",
        options: [
          { text: "\u201cRaised coder query capture from 2% to 7% of records, recovering $340K in uncaptured charges.\u201d", correct: true },
          { text: "\u201cCoding got a little more accurate over time.\u201d", correct: false },
          { text: "\u201cQuery rates moved in the right direction.\u201d", correct: false },
          { text: "\u201cCoders tried harder on their reviews.\u201d", correct: false }
        ],
        why: "Query rate is the HIM metric that flags missed documentation; pairing a rise in it with recovered dollars proves you know coding directly prints revenue."
      },
      {
        type: "star",
        prompt: "Complete the LTC result: \u201cBy stabilizing admissions and improving census management, our average <b>occupancy</b> climbed from 81% to\u2026\u201d",
        context: "Occupancy = filled beds ÷ total beds; it is the top-line lever for a facility's margin.",
        options: [
          { text: "93%", correct: true },
          { text: "82%", correct: false },
          { text: "80%", correct: false },
          { text: "85%", correct: false }
        ],
        why: "In LTC, occupancy is nearly everything \u2014 every percentage point is recurring per-diem revenue, so leaders want to hear you manage census, not just care."
      },
      {
        type: "bullet",
        prompt: "Pick the LTC answer that connects care quality to reimbursement you actually want to defend.",
        options: [
          { text: "\u201cImproved our CMS Five-Star overall rating from 2 to 4 by cleaning MDS accuracy and staffing data.\u201d", correct: true },
          { text: "\u201cMade the facility feel like a better place.\u201d", correct: false },
          { text: "\u201cRatings improved some.\u201d", correct: false },
          { text: "\u201cFamily surveys were nicer to read.\u201d", correct: false }
        ],
        why: "The CMS Five-Star rating is public and feeds referrals and payor preference; moving it two stars is a measurable, market-facing quality-and-revenue win."
      }
    ]
  }
];