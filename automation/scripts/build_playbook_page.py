#!/usr/bin/env python3
"""Build /playbook — the free lead magnet page — from the playbook markdown.

Also renders a print version and turns it into playbook.pdf with headless Chrome,
so the YouTube CTA ("free download") actually hands the visitor a file.

Run from anywhere:  /opt/venv/bin/python3 automation/scripts/build_playbook_page.py
"""
import html
import re
import subprocess
import sys

import markdown

SRC = "/data/business/hca-daily/assets/hca_resume_playbook.md"
OUT_HTML = "/data/business/hca-daily/worker/assets/playbook.html"
OUT_PDF = "/data/business/hca-daily/worker/assets/playbook.pdf"
CHROME = "/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free: The HCA Metric-Driven Résumé Playbook — The HCA Daily</title>
<meta name="description" content="Free playbook: the 3-part formula that turns duty-list résumé bullets into quantified executive achievements, plus the 20 KPIs healthcare leaders hire on.">
<meta name="theme-color" content="#0b2545">
<link rel="canonical" href="https://thehcadaily.com/playbook">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@600;700&display=swap" rel="stylesheet">
<style>
  :root{ --navy:#0b2545; --navy2:#13315c; --coral:#ff5749; --amber:#f59e0b; --teal:#0d9488;
    --green:#16a34a; --slate:#94a3b8; --off:#faf9f6; --ink:#14181f; --muted:#5b6572; --line:#e6e3dd }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Inter',system-ui,-apple-system,sans-serif;color:var(--ink);background:var(--off);line-height:1.65;-webkit-font-smoothing:antialiased}
  h1,h2,h3,h4{font-family:'Sora',sans-serif;color:var(--navy);line-height:1.2}
  .container{max-width:760px;margin:0 auto;padding:0 22px}
  nav{background:var(--navy);padding:14px 22px}
  .logo{font-family:'Sora',sans-serif;font-weight:800;color:#fff;font-size:17px;text-decoration:none}
  .logo span{color:var(--coral)}
  header{background:linear-gradient(168deg,#0b2545,#13315c 65%,#0e3a5c);color:#fff;padding:52px 0 44px}
  header h1{color:#fff;font-size:34px;letter-spacing:-.6px;margin-bottom:14px}
  header p{color:#c2cfe0;font-size:17px;max-width:600px}
  .eyebrow{letter-spacing:2.5px;text-transform:uppercase;font-size:12px;font-weight:700;color:#8fd3c9;margin-bottom:14px}
  .gate{background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;margin:-30px auto 0;max-width:760px;box-shadow:0 14px 34px rgba(11,37,69,.10);position:relative}
  .gate h2{font-size:20px;margin-bottom:6px}
  .gate p{color:var(--muted);font-size:14.5px;margin-bottom:14px}
  .row{display:flex;gap:10px;flex-wrap:wrap}
  input[type=email]{flex:1;min-width:220px;border:2px solid var(--line);border-radius:12px;padding:14px 16px;font-size:15px;font-family:inherit}
  input[type=email]:focus{outline:none;border-color:var(--coral)}
  .btn{display:inline-block;background:var(--coral);color:#fff;border:0;font-weight:700;font-size:15.5px;padding:15px 28px;border-radius:12px;text-decoration:none;cursor:pointer;font-family:inherit;box-shadow:0 10px 24px rgba(255,87,73,.26)}
  .btn.ghost{background:transparent;color:var(--navy);box-shadow:none;border:2px solid var(--line)}
  .msg{margin-top:12px;font-size:14px;font-weight:600;color:var(--green);display:none}
  main{padding:44px 0 20px}
  article h2{font-size:23px;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--line)}
  article h3{font-size:18px;margin:22px 0 8px}
  article h4{font-size:16px;margin:18px 0 6px;color:var(--navy2)}
  article p{margin:10px 0}
  article ul,article ol{margin:10px 0 10px 22px}
  article li{margin:6px 0}
  article strong{color:var(--navy)}
  article code{background:#eef1f5;padding:2px 6px;border-radius:5px;font-size:14px}
  article hr{border:0;border-top:1px solid var(--line);margin:26px 0}
  article table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14.5px}
  article th,article td{border:1px solid var(--line);padding:9px 11px;text-align:left}
  article th{background:#f1f5f9;color:var(--navy)}
  .cta{margin:36px 0 0;background:var(--navy);color:#fff;border-radius:18px;padding:30px;text-align:center}
  .cta h3{color:#fff;font-size:21px;margin-bottom:8px}
  .cta p{color:#c2cfe0;font-size:15px;margin-bottom:16px}
  footer{background:var(--navy);color:#8ca2bd;padding:34px 0;font-size:13.5px;margin-top:44px}
  footer a{color:#c2cfe0;text-decoration:none}
  @media print{ nav,.gate,.cta,footer{display:none} header{background:#fff;color:#000} header h1,header p{color:#000} body{background:#fff} }
</style>
</head>
<body>
<nav><div class="container"><a class="logo" href="/">The HCA <span>Daily</span></a></div></nav>
<header>
  <div class="container">
    <p class="eyebrow">Free playbook</p>
    <h1>The Metric-Driven Résumé &amp; Executive Career Playbook</h1>
    <p>Why duty-list résumés get archived — and the 3-part formula that makes a hiring executive stop scrolling. Read it right here, or take the PDF.</p>
  </div>
</header>

<div class="gate">
  <h2>Get the PDF + your daily drill</h2>
  <p>Enter your email and I'll also send you the free 90-second scorecard and a 5-minute drill each day. No spam, unsubscribe anytime.</p>
  <form id="gateForm" class="row">
    <input id="emailInput" type="email" required placeholder="you@email.com">
    <button class="btn" type="submit">Send me the PDF</button>
  </form>
  <div class="msg" id="msg">✅ Sent. <a href="/playbook.pdf" style="color:var(--teal);font-weight:700">Download the PDF now →</a></div>
</div>

<main>
  <div class="container">
    <article>
"""

TAIL = """    </article>

    <div class="cta">
      <h3>How far is your résumé from the director role?</h3>
      <p>The free 90-second scorecard scores you across the 4 dimensions healthcare leaders actually hire on — and shows your top 3 fixes.</p>
      <a class="btn" href="/scorecard">Take the free scorecard →</a>
      <p style="margin-top:16px;font-size:13.5px">Ready for the depth? <a href="/vault" style="color:#8fd3c9">Interview Answer Vault · $27</a> &nbsp;·&nbsp; <a href="/accelerator" style="color:#8fd3c9">Career Accelerator · $297</a></p>
    </div>
  </div>
</main>

<footer>
  <div class="container">
    <a class="logo" href="/" style="font-family:'Sora',sans-serif;font-weight:800">The HCA <span style="color:var(--coral)">Daily</span></a>
    <p style="margin-top:10px">Dr. Ashley Hussain-Okorafor, DBA · <a href="/about">About</a> · <a href="/pricing">Pricing</a> · <a href="/legal">Terms</a></p>
  </div>
</footer>

<script>
  var form = document.getElementById("gateForm");
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var email = document.getElementById("emailInput").value.trim();
    if (!email) return;
    var params = new URLSearchParams(location.search);
    try {
      await fetch("/api/scorecard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          source: "playbook",
          utm_source: params.get("utm_source") || "",
          utm_medium: params.get("utm_medium") || "",
          utm_campaign: params.get("utm_campaign") || "",
          utm_content: params.get("utm_content") || ""
        })
      });
    } catch (err) { /* never block the download */ }
    document.getElementById("msg").style.display = "block";
    window.location.href = "/playbook.pdf";
  });
</script>
</body>
</html>
"""


def main():
    raw = open(SRC).read()
    # strip the internal front-matter lines meant for our own records
    raw = re.sub(r"^\*\*Status:\*\*.*$", "", raw, flags=re.M)
    raw = re.sub(r"^\*\*Distribution:\*\*.*$", "", raw, flags=re.M)
    # Drop the H1 — the page header already carries the title.
    raw = re.sub(r"^#\s+.*$", "", raw, count=1, flags=re.M)
    # Python-Markdown needs a blank line before a list that follows a paragraph;
    # the source doesn't always have one, which renders bullets as literal "* ".
    raw = re.sub(r"(?m)^([^\n\s*\-|#>].*)\n(?=[*\-]\s)", r"\1\n\n", raw)
    body = markdown.markdown(raw, extensions=["tables", "sane_lists", "attr_list"])
    open(OUT_HTML, "w").write(HEAD + body + TAIL)
    print(f"wrote {OUT_HTML} ({len(body)} chars of body)")

    # Print-only render (no form / nav) for the PDF.
    print_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>body{{font-family:Helvetica,Arial,sans-serif;line-height:1.55;color:#111;margin:44px;font-size:11.5pt}}
    h1{{color:#0b2545;font-size:22pt;margin-bottom:4px}} h2{{color:#0b2545;font-size:15pt;margin-top:22px;border-top:1px solid #ddd;padding-top:10px}}
    h3{{color:#13315c;font-size:12.5pt}} table{{border-collapse:collapse;width:100%;font-size:10pt}}
    th,td{{border:1px solid #ccc;padding:6px 8px;text-align:left}} th{{background:#f1f5f9}}
    .foot{{margin-top:26px;color:#666;font-size:9.5pt;border-top:1px solid #ddd;padding-top:10px}}</style></head>
    <body><p style="color:#ff5749;font-weight:bold;font-size:9.5pt;letter-spacing:2px">THE HCA DAILY · FREE PLAYBOOK</p>
    {body}
    <div class="foot">The HCA Daily · Dr. Ashley Hussain-Okorafor, DBA · thehcadaily.com/scorecard</div>
    </body></html>"""
    tmp = "/tmp/playbook_print.html"
    open(tmp, "w").write(print_html)
    import os
    env = dict(os.environ)
    libdir = "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu"
    if os.path.isdir(libdir):
        env["LD_LIBRARY_PATH"] = libdir + ":" + env.get("LD_LIBRARY_PATH", "")
    r = subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
         "--print-to-pdf=" + OUT_PDF, "--no-pdf-header-footer", tmp],
        capture_output=True, text=True, timeout=180, env=env)
    if r.returncode != 0:
        print("PDF render failed:", r.stderr[-500:], file=sys.stderr)
        return 1
    import os
    print(f"wrote {OUT_PDF} ({os.path.getsize(OUT_PDF)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())