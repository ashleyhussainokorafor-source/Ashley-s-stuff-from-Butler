/* The HCA Daily — shared lesson library.
   Load AFTER the 4 part-*.js files (which define HCA_UNITS_A..D). */
window.HCA_DIMENSIONS = [
  { id:"resume",     label:"Resume Metrics",        icon:"📊", color:"var(--coral)" },
  { id:"vocabulary", label:"Operational Vocabulary", icon:"🗣️", color:"var(--amber)" },
  { id:"linkedin",   label:"LinkedIn & Visibility", icon:"🔗", color:"#0d9488" },
  { id:"interview",  label:"Interview Delivery",     icon:"🎤", color:"#0b2545" },
  { id:"offer",      label:"Offer & Negotiation",   icon:"💰", color:"#7c3aed" },
];
window.HCA_UNIT_ORDER = ["u1","u2","u3","u4","u5","u6","u7","u8","u9","u10","u11","u12","u13","u14","u15","u16","u17"];

window.HCA_UNITS = [].concat(
  window.HCA_UNITS_A || [], window.HCA_UNITS_B || [],
  window.HCA_UNITS_C || [], window.HCA_UNITS_D || []
);
window.HCA_UNITS_BY_ID = {};
window.HCA_UNITS.forEach(u => { window.HCA_UNITS_BY_ID[u.id] = u; });
window.HCA_UNITS = window.HCA_UNIT_ORDER.map(id => window.HCA_UNITS_BY_ID[id]).filter(Boolean);

/* inject star-ORDER extras into matching units */
if (window.HCA_STAR_ORDER) {
  Object.keys(window.HCA_STAR_ORDER).forEach(uid => {
    const u = window.HCA_UNITS_BY_ID[uid];
    if (u) u.items = (u.items || []).concat(window.HCA_STAR_ORDER[uid]);
  });
}

/* label for a dimension id */
window.HCA_DIM_LABEL = id => (window.HCA_DIMENSIONS.find(d => d.id === id) || {}).label || id;