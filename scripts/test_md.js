// Isolated check of the md.js renderer: does it format markdown, and does it
// neutralise injected HTML? Run: node /data/scripts/test_md.js
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('/data/business/hca-daily/worker/assets/md.js', 'utf8'));

const sample = `### Key Drivers

| Group size | Independent | Health-system |
|---|---|---|
| Small (6-20) | $110K - $135K | $125K - $160K |
| Large (20+) | $130K - $160K | $150K - $190K |

- **Specialty mix:** surgical pays more
- Geography: Northeast +10-20%

1. Anchor on total package
2. Ask about CME

Plain paragraph with \`inline code\` and a [link](https://thehcadaily.com).`;

const xss = `Hello <img src=x onerror=alert(1)> <script>alert('xss')</script> **bold**`;

const out = window.renderMarkdown(sample);
const vuln = window.renderMarkdown(xss);

const checks = [
  ['renders <table>',            out.includes('<table')],
  ['no raw pipe rows left',      !/\|\s*\$110K\s*\|/.test(out)],
  ['table header styled',        out.includes('<th')],
  ['bold -> <strong>',           out.includes('<strong')],
  ['no raw ** left',             !out.includes('**')],
  ['heading -> div',             out.includes('Key Drivers') && !out.includes('###')],
  ['unordered list',             out.includes('<ul')],
  ['ordered list',               out.includes('<ol')],
  ['inline code',                out.includes('<code')],
  ['link rendered',              out.includes('<a href="https://thehcadaily.com"')],
  ['XSS img defused',            !vuln.includes('<img')],
  ['XSS script defused',         !vuln.includes('<script')],
  ['XSS escaped as text',        vuln.includes('&lt;script&gt;')],
  ['bold still works w/ XSS',    vuln.includes('<strong')],
];

let bad = 0;
for (const [name, ok] of checks) {
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) bad++;
}
console.log(`\n${bad === 0 ? 'ALL PASS' : bad + ' FAILURES'}`);
console.log('\n--- rendered table excerpt ---');
console.log(out.slice(out.indexOf('<table'), out.indexOf('</table>') + 8).slice(0, 400));
console.log('\n--- XSS input rendered ---');
console.log(vuln);
process.exit(bad === 0 ? 0 : 1);