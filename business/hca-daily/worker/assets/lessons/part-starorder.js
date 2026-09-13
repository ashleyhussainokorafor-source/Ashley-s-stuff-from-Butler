/* Supplemental star-ORDER items — options are listed in correct order (S→T→A→R);
   the player shuffles them and the learner taps them back into sequence. */
window.HCA_STAR_ORDER = {
  u9: [
    { type:"star-order",
      prompt:"Put this answer's STAR back in order.",
      context:"\"Denials were 14%, so I rebuilt the prior-auth workflow, trained 8 staff, and cut denials to 6% — recovering $310K.\"",
      options:[
        {text:"S — denials running 14% of claims"},
        {text:"T — fix the broken prior-auth workflow"},
        {text:"A — rebuilt the checklist + trained 8 staff"},
        {text:"R — denials 14% → 6%, $310K recovered"}
      ],
      why:"STAR forces metric → action → result. Panels listen for the numbers, not the adjectives." }
  ],
  u10: [
    { type:"star-order",
      prompt:"Order this leadership story.",
      context:"\"Turnover was 34%. I found onboarding was the leak, redesigned it with a 90-day buddy program, and got retention to 82%.\"",
      options:[
        {text:"S — nurse turnover at 34%, bleeding margin"},
        {text:"T — fix the onboarding leak"},
        {text:"A — rebuilt onboarding + 90-day buddy program"},
        {text:"R — retention up to 82% in two quarters"}
      ],
      why:"A leadership answer lives or dies on a clean S→T→A→R spine." }
  ],
  u12: [
    { type:"star-order",
      prompt:"Sequence this revenue-cycle answer.",
      context:"\"Clean claims were 88%. I found eligibility errors upstream, added a real-time check, and pushed clean claims to 97%.\"",
      options:[
        {text:"S — clean claim rate stuck at 88%"},
        {text:"T — close the eligibility loophole"},
        {text:"A — added a real-time eligibility check"},
        {text:"R — clean claims 88% → 97%"}
      ],
      why:"In revenue-cycle answers, the 'A' must be a mechanism with a measurable 'R'." }
  ],
  u11: [
    { type:"star-order",
      prompt:"Order this operational answer.",
      context:"\"No-shows hit 19%. I reworked the reminder cadence, and they fell to 11% in a quarter.\"",
      options:[
        {text:"S — no-show rate at 19%"},
        {text:"T — find the scheduling/communication gap"},
        {text:"A — reworked the reminder cadence"},
        {text:"R — no-shows 19% → 11% in one quarter"}
      ],
      why:"Operations answers win when the action is specific and the result is time-bound." }
  ]
};