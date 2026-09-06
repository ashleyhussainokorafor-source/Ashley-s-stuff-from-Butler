"""
The HCA Daily — Interactive Career Navigator Prototype Server
Provides API endpoints & web chat interface for the Career Navigator LLM.
"""

import os
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_NAME = "deepseek/deepseek-v4-pro-0813"

# Load the verified HCA Navigator System Prompt
PROMPT_PATH = "/data/business/hca-daily/career_navigator_prompt.md"
SYSTEM_PROMPT = ""
if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()

NAVIGATOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HCA Career Navigator — AI Advisor Demo</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 flex flex-col h-screen">

  <!-- HEADER -->
  <header class="p-4 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <span class="w-8 h-8 rounded-lg bg-teal-500 flex items-center justify-center font-extrabold text-slate-950 text-sm">H</span>
      <div>
        <h1 class="font-bold text-sm leading-tight text-white">HCA Career Navigator</h1>
        <p class="text-xs text-teal-400">Executive Advisory AI • Powered by The HCA Daily</p>
      </div>
    </div>
    <a href="https://buy.stripe.com/test_5kQ8wQacT4qM4QlfnEgMw00" target="_blank" class="px-3 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs">
      Unlock Full Access ($29/mo)
    </a>
  </header>

  <!-- CHAT WINDOW -->
  <main id="chat-box" class="flex-1 overflow-y-auto p-4 space-y-4 max-w-3xl w-full mx-auto">
    <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-sm text-slate-300">
      <p class="font-bold text-teal-400 mb-1">Welcome to the HCA Career Navigator.</p>
      <p>I am your specialized healthcare operations and executive career advisor. How can I help you today?</p>
      <div class="mt-3 flex flex-wrap gap-2 text-xs">
        <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">"Audit my resume for Clinic Manager roles"</button>
        <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">"How do I explain my RN experience on an admin CV?"</button>
        <button onclick="sendPrompt(this.innerText)" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">"What is the MGMA median salary for Ops Directors?"</button>
      </div>
    </div>
  </main>

  <!-- INPUT BAR -->
  <footer class="p-4 border-t border-slate-800 bg-slate-900/50">
    <div class="max-w-3xl mx-auto flex gap-2">
      <input id="user-input" type="text" placeholder="Ask about compensation, resume makeovers, or operational metrics..." class="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-teal-500">
      <button onclick="handleSend()" class="px-6 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm transition-all">Send</button>
    </div>
  </footer>

  <script>
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const history = [];

    userInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSend();
    });

    function sendPrompt(text) {
      userInput.value = text;
      handleSend();
    }

    async function handleSend() {
      const text = userInput.value.trim();
      if (!text) return;
      userInput.value = '';

      // Append User message
      chatBox.innerHTML += `<div class="flex justify-end"><div class="max-w-[80%] p-3.5 rounded-2xl bg-teal-600 text-white text-sm font-medium">${text}</div></div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      history.push({ role: 'user', content: text });

      // Loading bubble
      const loadingId = 'loading-' + Date.now();
      chatBox.innerHTML += `<div id="${loadingId}" class="flex justify-start"><div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400 text-sm animate-pulse">Consulting executive knowledge base...</div></div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: history })
        });
        const data = await resp.json();
        document.getElementById(loadingId).remove();
        
        const reply = data.reply || "Error connecting to advisor.";
        history.push({ role: 'assistant', content: reply });

        chatBox.innerHTML += `<div class="flex justify-start"><div class="max-w-[85%] p-4 rounded-2xl bg-slate-900 border border-slate-800 text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">${reply}</div></div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
      } catch (err) {
        document.getElementById(loadingId).remove();
        chatBox.innerHTML += `<div class="text-xs text-red-400 p-2 text-center">Connection error. Please try again.</div>`;
      }
    }
  </script>
</body>
</html>
"""

class NavigatorRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html", "/landing"):
            landing_path = "/data/business/hca-daily/web/index.html"
            if os.path.exists(landing_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(landing_path, "rb") as f:
                    self.wfile.write(f.read())
                return
        elif self.path in ("/app", "/navigator", "/chat"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(NAVIGATOR_HTML.encode("utf-8"))
            return
        
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body)
            messages = payload.get("messages", [])

            # Inject HCA Navigator system prompt
            full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

            # Call OpenRouter API with DeepSeek model
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            req_data = json.dumps({
                "model": MODEL_NAME,
                "messages": full_messages,
                "temperature": 0.4
            }).encode("utf-8")

            req = urllib.request.Request(api_url, data=req_data, headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            })

            try:
                with urllib.request.urlopen(req) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    reply_text = res_json["choices"][0]["message"]["content"]
            except Exception as e:
                reply_text = f"HCA Navigator Advisor Offline: {str(e)}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply_text}).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

if __name__ == "__main__":
    port = 8085
    server = HTTPServer(("0.0.0.0", port), NavigatorRequestHandler)
    print(f"HCA Daily Platform Server running on port {port}...")
    server.serve_forever()
