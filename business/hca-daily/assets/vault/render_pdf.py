#!/usr/bin/env python3
"""Render the assembled HCA Interview Answer Vault to a styled HTML file
(which Chrome then prints to PDF).

Handles the markdown subset actually used in the vault: headings, bold, italic,
bullet lists (incl. nesting), ordered lists, blockquotes, horizontal rules,
and paragraphs.
"""
import html
import re
from pathlib import Path

VAULT = Path("/data/business/hca-daily/assets/vault")
SRC = VAULT / "HCA-Interview-Answer-Vault-COMPLETE.md"
OUT = VAULT / "vault-print.html"


def inline(text: str) -> str:
    """Escape HTML, then apply inline markdown."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def convert(md: str) -> str:
    out = []
    lines = md.split("\n")
    i = 0
    list_stack = []  # stack of "ul" / "ol"

    def close_lists(to_depth=0):
        while len(list_stack) > to_depth:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # blank line
        if not stripped:
            close_lists()
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}", stripped):
            close_lists()
            out.append('<hr class="rule">')
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            close_lists()
            content = stripped.lstrip("> ").strip()
            out.append(f'<blockquote>{inline(content)}</blockquote>')
            i += 1
            continue

        # bullet list (supports one level of nesting via 2-space indent)
        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            depth = 2 if indent >= 2 else 1
            while len(list_stack) < depth:
                out.append("<ul>")
                list_stack.append("ul")
            while len(list_stack) > depth:
                out.append(f"</{list_stack.pop()}>")
            out.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue

        # ordered list
        m = re.match(r"^(\s*)\d+[\.\)]\s+(.*)$", line)
        if m:
            if not list_stack or list_stack[-1] != "ol":
                close_lists()
                out.append("<ol>")
                list_stack.append("ol")
            out.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue

        # paragraph
        close_lists()
        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    close_lists()
    return "\n".join(out)


body = convert(SRC.read_text(encoding="utf-8"))

CSS = """
@page { size: Letter; margin: 20mm 18mm; }
* { box-sizing: border-box; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 11.2pt; line-height: 1.62; color: #14181f; margin: 0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1 {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 25pt; color: #0b2545; margin: 0 0 14pt;
  page-break-before: always; page-break-after: avoid;
  border-bottom: 2.5pt solid #0d9488; padding-bottom: 8pt;
}
h1:first-of-type { page-break-before: avoid; font-size: 34pt; border-bottom: none; }
h2 {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 16pt; color: #0b2545; margin: 22pt 0 8pt; page-break-after: avoid;
}
h3 {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 12.6pt; color: #0f766e; margin: 17pt 0 6pt;
  page-break-after: avoid; page-break-inside: avoid;
}
h4 { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11pt; color: #0b2545; }
p { margin: 0 0 7pt; }
strong { color: #0b2545; }
em { color: #334155; }
ul, ol { margin: 0 0 9pt 0; padding-left: 17pt; }
li { margin-bottom: 3.5pt; page-break-inside: avoid; }
ul ul { margin-top: 3.5pt; margin-bottom: 0; }
blockquote {
  margin: 8pt 0; padding: 9pt 13pt; background: #f1f5f9;
  border-left: 3.5pt solid #0d9488; font-style: italic; color: #1e293b;
  page-break-inside: avoid;
}
hr.rule { border: none; border-top: 1pt solid #cbd5e1; margin: 15pt 0; page-break-after: avoid; }
"""

HTML = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>The HCA Interview Answer Vault</title>
<style>{CSS}</style></head>
<body>{body}</body></html>"""

OUT.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT}  ({OUT.stat().st_size:,} bytes)")
print(f"Headings: {body.count('<h3')} question blocks, {body.count('<h1')} parts")
