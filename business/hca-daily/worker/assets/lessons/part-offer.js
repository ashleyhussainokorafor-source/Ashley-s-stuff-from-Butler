/* HCA Daily — Drill Units D: Offer & Negotiation (part-offer.js)
 * Units u15–u17. Voices: warm, sharp, market-data-driven (MGMA/BLS). Never entitled.
 * Item types: flash (comp lever / anchor), bullet (market-anchored script pick), speak (verbatim line + 4-check rubric).
 */
window.HCA_UNITS_D = [
  {
    id: "u15",
    title: "Total Comp Anatomy",
    dim: "offer",
    level: 1,
    items: [
      {
        type: "flash",
        prompt: "The practice names a lump-sum dollar amount at the bottom of the offer to offset what you give up by leaving your current employer. Which comp lever is this?",
        options: [
          { text: "Sign-on bonus", correct: true },
          { text: "Base salary", correct: false },
          { text: "Retirement match", correct: false },
          { text: "Incentive percentage", correct: false }
        ],
        why: "Lever: sign-on bonus. It is a one-time cash payment that buys the offer a market-competitive first-year total rather than inflating the recurring base."
      },
      {
        type: "flash",
        prompt: "Which comp lever hits your paycheck every single pay period and is the anchor every other lever is negotiated off of?",
        options: [
          { text: "Base salary", correct: true },
          { text: "Relocation allowance", correct: false },
          { text: "PTO", correct: false },
          { text: "Sign-on bonus", correct: false }
        ],
        why: "Lever: base salary. It is the recurring anchor of your total compensation; every bonus, incentive, and match is expressed as a percentage or layer on top of it."
      },
      {
        type: "flash",
        prompt: "The practice will reimburse your move-in expenses and flights to the new market. Which comp lever is being extended?",
        options: [
          { text: "Relocation allowance", correct: true },
          { text: "CME stipend", correct: false },
          { text: "Incentive percentage", correct: false },
          { text: "Vesting schedule", correct: false }
        ],
        why: "Lever: relocation allowance. It covers one-time move costs (movers, flights, temporary housing) so the move does not quietly eat away the value of the base."
      },
      {
        type: "flash",
        prompt: "A percentage of your total comp is tied to hitting clinic performance targets each quarter. Which lever is this?",
        options: [
          { text: "Incentive percentage", correct: true },
          { text: "Sign-on bonus", correct: false },
          { text: "PTO", correct: false },
          { text: "Retirement match", correct: false }
        ],
        why: "Lever: incentive percentage. It converts performance into variable pay — commonly 10-30% of total comp in ambulatory and executive roles — so know the target hurdle before you sign."
      },
      {
        type: "flash",
        prompt: "Two non-cash levers add quiet value on top of the base: one guarantees paid time away, the other funds your ongoing education. Which pair are they?",
        options: [
          { text: "PTO and CME stipend", correct: true },
          { text: "Sign-on and relocation", correct: false },
          { text: "Base and incentive", correct: false },
          { text: "Vesting and match", correct: false }
        ],
        why: "Levers: PTO and CME. Paid time off protects your bandwidth (weeks, not days) and a CME stipend keeps your credentials current — both should appear on your anatomy before you sign, not after."
      }
    ]
  },
  {
    id: "u16",
    title: "The Counter-Offer Scripts",
    dim: "offer",
    level: 2,
    items: [
      {
        type: "bullet",
        prompt: "The base offer lands at $92k. The MGMA range for your role, region, and years is $96k-$102k. Which counter anchors to that market data without sounding entitled?",
        options: [
          { text: '"I want $105k, honestly my rent has gone up a lot."', correct: false },
          { text: '"Thank you, I appreciate it. Balancing the offer against the MGMA range for clinic managers with my years in the Southeast, I ask we land closer to the $96k-$102k band — and I am flexible on how we get there."', correct: true },
          { text: '"I cannot sign for anything under $100k, take it or leave it."', correct: false },
          { text: '"My last role paid me more, so match it or I walk."', correct: false }
        ],
        why: "Lever: base salary anchor. This script cites a published band and invites a problem-solving tone instead of a demand, so the counter is data-backed rather than entitled."
      },
      {
        type: "bullet",
        prompt: "The base is fair, but the offer has no sign-on. Which response ties a modest sign-on to market convention without sounding grabby?",
        options: [
          { text: '"I expect a sign-on or this is a no from me."', correct: false },
          { text: '"Sign-ons are standard, everybody gets one, so add $20k."', correct: false },
          { text: '"For me to leave an existing role cleanly, I would ask the first-year total to carry a modest sign-on, in line with what independent practices in this market commonly pair with the base."', correct: true },
          { text: '"Just bump the base up instead, forget the sign-on entirely."', correct: false }
        ],
        why: "Lever: sign-on bonus. It frames the ask as closing a first-year total-comp gap caused by leaving an employer — a market-based reason, not a personal appetite."
      },
      {
        type: "bullet",
        prompt: "The recruiter says the base is at its ceiling and cannot move. Which counter pivots to another lever instead of digging in on the base?",
        options: [
          { text: '"Then we are done here, the base is everything."', correct: false },
          { text: '"Fine, lower it then, I do not care anymore."', correct: false },
          { text: '"If the base is at its ceiling, I would invite the incentive percentage or a relocation allowance to close the gap to market — one-time or performance dollars preserve your recurring budget."', correct: true },
          { text: '"I only negotiate base salary, nothing else counts."', correct: false }
        ],
        why: "Levers: incentive percentage and relocation. A trade-creating counter keeps total comp competitive on levers that do not strain the recurring base — distinct from conceding."
      },
      {
        type: "bullet",
        prompt: "The offer has a 2% retirement match and you know the market norm is 3-5%. Which script asks for the match within the band, anchored and not entitled?",
        options: [
          { text: '"My friend gets 6% at her clinic, so I want that too."', correct: false },
          { text: '"The 2% match sits below the 3-5% common in this market; I would ask the match to land at the low-to-middle of that band, which keeps your cost modest and shows commitment on both sides."', correct: true },
          { text: '"I will only accept a 10% match, no exceptions."', correct: false },
          { text: '"Retirement is not that important, keep it at 2%."', correct: false }
        ],
        why: "Lever: retirement match. It benchmarks to the prevailing market band and asks for the middle, not the top, of the range — a warm, reasonable anchor that preserves leverage."
      },
      {
        type: "speak",
        prompt: "Your base offer is $90k with 2 weeks PTO; the market median PTO in your segment is 3 weeks. Write ONE sentence that anchors to that market norm, states your specific ask, and offers a trade — no entitlement.",
        rubric: [
          "Anchors to the market norm (3 weeks / published PTO median)",
          "States a specific ask (the 3rd week of PTO)",
          "Offers a trade or shows flexibility on how it is delivered",
          "Stays warm, collaborative, and free of entitlement or ultimatum"
        ]
      }
    ]
  },
  {
    id: "u17",
    title: "Lowball & Best-Final Defense",
    dim: "offer",
    level: 3,
    items: [
      {
        type: "flash",
        prompt: "A $75k offer lands when the market band is $85k-$95k. The lowball itself is which negotiation tactic?",
        options: [
          { text: "Anchoring — opening low to drag the settlement toward the floor", correct: true },
          { text: "Best-and-final deadline pressure", correct: false },
          { text: "Silence to make you fill the gap", correct: false },
          { text: "A good-faith market-calibrated offer", correct: false }
        ],
        why: "Lever: anchor. The lowball sets a low opening anchor to pull your counter and the final number toward the bottom of the band — name it, then re-anchor to market data."
      },
      {
        type: "flash",
        prompt: "The recruiter says the base is truly best and final. Which lever still grows your FIRST-YEAR total comp without touching the recurring base?",
        options: [
          { text: "Sign-on bonus", correct: true },
          { text: "Base salary", correct: false },
          { text: "PTO days", correct: false },
          { text: "Vesting schedule", correct: false }
        ],
        why: "Lever: sign-on bonus. When the base is locked, a one-time sign-on lifts first-year total comp to market without reopening the recurring budget — a clean final move."
      },
      {
        type: "bullet",
        prompt: "You receive a lowball of $75k against an $85k-$95k band. Which response defends with market data, is not entitled, and leaves the door open?",
        options: [
          { text: '"I will accept $75k since I do not want to be difficult."', correct: false },
          { text: '"That is insulting, counter it with $95k or I walk today."', correct: false },
          { text: '"I understand that is the budgeted figure. From my side, the published range for this role in this market is $85k-$95k, so I would like to understand how we bridge that — can you share what makes the current number work?"', correct: true },
          { text: '"I only talk to someone who can match my number immediately."', correct: false }
        ],
        why: "Lever: base anchor. It names a published band and asks a genuine question about the gap — firm on market data, curious instead of entitled, and it keeps the negotiation alive."
      },
      {
        type: "bullet",
        prompt: "On a best-and-final call, the recruiter insists this is the last ask. Which response respects the deadline while defending your value?",
        options: [
          { text: '"Fine, I will take whatever you decide."', correct: false },
          { text: '"I respect the timeline, so here is my single final number: $94k base, and I would stretch a little on incentive for the team. Can we confirm the base before we close?"', correct: true },
          { text: '"Best and final is a trick, so I will counter three more times tonight."', correct: false },
          { text: '"I refuse to give a number until you give me a better one."', correct: false }
        ],
        why: "Lever: base anchor with an incentive trade. It gives one crisp, data-calibrated number, offers a flexibility trade on incentive percentage, and verifies alignment — closing with grace."
      },
      {
        type: "speak",
        prompt: "On a best-and-final call the recruiter asks you to commit to $88k when the market median for your role is $94k — no more moves after this. Write ONE line that defends your value, is specific, and keeps the relationship warm.",
        rubric: [
          "Anchors to the market median ($94k)",
          "States one specific final number or trade",
          "Closes professionally, without a threat or ultimatum",
          "Keeps a warm, collaborative tone that preserves the relationship"
        ]
      }
    ]
  }
];