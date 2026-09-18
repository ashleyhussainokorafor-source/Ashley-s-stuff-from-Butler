/* HCA Daily — shared safe markdown renderer.
 *
 * Why this exists: the Navigator and Interview Coach both ask the model for
 * structured answers (tables, bold headers, lists). Injecting that reply into
 * innerHTML rendered it as raw text — literal "| $110K | $135K |" pipes and
 * "**bold**" asterisks — which makes a paid product look broken.
 *
 * SECURITY: everything is HTML-escaped BEFORE any formatting is applied, so a
 * visitor cannot inject markup through the chat box or trick the model into
 * emitting a script tag. Never reorder those two steps.
 */
(function (global) {
  "use strict";

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  /* Inline formatting. Input is ALREADY escaped. */
  function inline(s) {
    s = s.replace(/`([^`]+)`/g, '<code class="bg-slate-800 px-1.5 py-0.5 rounded text-teal-300 text-[0.85em]">$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-white">$1</strong>');
    s = s.replace(/(^|[^*\w])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-teal-400 underline">$1</a>');
    // bare URLs
    s = s.replace(/(^|[\s(])((?:https?:\/\/)[^\s<)]+)/g,
      '$1<a href="$2" target="_blank" rel="noopener noreferrer" class="text-teal-400 underline">$2</a>');
    return s;
  }

  function splitRow(line) {
    var t = line.trim();
    if (t.startsWith("|")) t = t.slice(1);
    if (t.endsWith("|")) t = t.slice(0, -1);
    return t.split("|").map(function (c) { return c.trim(); });
  }

  function isSepRow(line) {
    return /^\s*\|?[\s:-]*-[\s:|-]*\|?\s*$/.test(line) && line.indexOf("-") !== -1;
  }

  function render(src) {
    if (!src) return "";
    var lines = escapeHtml(src).replace(/\r\n/g, "\n").split("\n");
    var out = [];
    var i = 0;

    while (i < lines.length) {
      var line = lines[i];

      // blank
      if (!line.trim()) { i++; continue; }

      // table: header row followed by a separator row
      if (line.indexOf("|") !== -1 && i + 1 < lines.length && isSepRow(lines[i + 1])) {
        var head = splitRow(line);
        i += 2;
        var rows = [];
        while (i < lines.length && lines[i].indexOf("|") !== -1 && lines[i].trim()) {
          rows.push(splitRow(lines[i]));
          i++;
        }
        var html = '<div class="overflow-x-auto my-3"><table class="w-full text-[0.8em] border-collapse">';
        html += "<thead><tr>";
        head.forEach(function (h) {
          html += '<th class="text-left p-2 border-b border-slate-600 text-teal-300 font-semibold align-top">'
            + inline(h) + "</th>";
        });
        html += "</tr></thead><tbody>";
        rows.forEach(function (r) {
          html += "<tr>";
          for (var c = 0; c < head.length; c++) {
            html += '<td class="p-2 border-b border-slate-800 align-top">'
              + inline(r[c] === undefined ? "" : r[c]) + "</td>";
          }
          html += "</tr>";
        });
        html += "</tbody></table></div>";
        out.push(html);
        continue;
      }

      // heading
      var h = line.match(/^\s{0,3}(#{1,6})\s+(.*)$/);
      if (h) {
        var lvl = h[1].length;
        var cls = lvl <= 2
          ? "text-base font-bold text-white mt-4 mb-2"
          : "text-sm font-bold text-teal-300 mt-4 mb-1.5 uppercase tracking-wide";
        out.push("<div class=\"" + cls + "\">" + inline(h[2]) + "</div>");
        i++;
        continue;
      }

      // horizontal rule
      if (/^\s*([-*_])\s*\1\s*\1[\s\S]*$/.test(line) && line.replace(/[\s\-*_]/g, "") === "") {
        out.push('<hr class="border-slate-700 my-3">');
        i++;
        continue;
      }

      // unordered list
      if (/^\s*[-*+]\s+/.test(line)) {
        var ul = '<ul class="list-disc ml-5 my-2 space-y-1">';
        while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
          ul += "<li>" + inline(lines[i].replace(/^\s*[-*+]\s+/, "")) + "</li>";
          i++;
        }
        out.push(ul + "</ul>");
        continue;
      }

      // ordered list
      if (/^\s*\d+[.)]\s+/.test(line)) {
        var ol = '<ol class="list-decimal ml-5 my-2 space-y-1">';
        while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
          ol += "<li>" + inline(lines[i].replace(/^\s*\d+[.)]\s+/, "")) + "</li>";
          i++;
        }
        out.push(ol + "</ol>");
        continue;
      }

      // paragraph (consume until a blank line or a block starter)
      var para = [];
      while (i < lines.length && lines[i].trim() &&
             !/^\s{0,3}#{1,6}\s/.test(lines[i]) &&
             !/^\s*[-*+]\s+/.test(lines[i]) &&
             !/^\s*\d+[.)]\s+/.test(lines[i]) &&
             !(lines[i].indexOf("|") !== -1 && i + 1 < lines.length && isSepRow(lines[i + 1]))) {
        para.push(inline(lines[i]));
        i++;
      }
      out.push('<p class="my-2">' + para.join("<br>") + "</p>");
    }
    return out.join("");
  }

  global.renderMarkdown = render;
  global.escapeHtml = escapeHtml;
})(window);
