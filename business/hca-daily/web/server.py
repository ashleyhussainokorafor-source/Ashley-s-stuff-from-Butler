"""
The HCA Daily — Unified Web Platform & AI Engine Server
Serves:
1. Static High-Converting Landing Page (`/` or `/index.html`)
2. AI Career Navigator Web Interface (`/navigator` or `/app`)
3. Interactive HCA Interview Coach Simulator (`/coach`)
4. AI API endpoints (`/api/chat` and `/api/coach`) backed by DeepSeek on OpenRouter.
"""

import os
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_NAME = "deepseek/deepseek-v4-pro-0813"

# Load Prompts
NAVIGATOR_PROMPT_PATH = "/data/business/hca-daily/career_navigator_prompt.md"
COACH_PROMPT_PATH = "/data/business/hca-daily/interview_coach_prompt.md"

NAVIGATOR_SYSTEM_PROMPT = ""
if os.path.exists(NAVIGATOR_PROMPT_PATH):
    with open(NAVIGATOR_PROMPT_PATH, "r", encoding="utf-8") as f:
        NAVIGATOR_SYSTEM_PROMPT = f.read()

COACH_SYSTEM_PROMPT = ""
if os.path.exists(COACH_PROMPT_PATH):
    with open(COACH_PROMPT_PATH, "r", encoding="utf-8") as f:
        COACH_SYSTEM_PROMPT = f.read()

def call_openrouter(messages, system_prompt, temperature=0.4):
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    req_data = json.dumps({
        "model": MODEL_NAME,
        "messages": full_messages,
        "temperature": temperature
    }).encode("utf-8")

    req = urllib.request.Request(api_url, data=req_data, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    })

    with urllib.request.urlopen(req) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        return res_json["choices"][0]["message"]["content"]

class UnifiedPlatformHandler(SimpleHTTPRequestHandler):
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

        elif self.path in ("/coach", "/interview", "/simulator"):
            coach_path = "/data/business/hca-daily/web/coach.html"
            if os.path.exists(coach_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(coach_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        elif self.path in ("/app", "/navigator", "/chat"):
            nav_path = "/data/business/hca-daily/web/navigator.html"
            if os.path.exists(nav_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(nav_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body) if body else {}

        if self.path == "/api/chat":
            messages = payload.get("messages", [])
            try:
                reply = call_openrouter(messages, NAVIGATOR_SYSTEM_PROMPT, temperature=0.4)
            except Exception as e:
                reply = f"HCA Career Navigator Unavailable: {str(e)}"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))
            return

        elif self.path == "/api/coach":
            messages = payload.get("messages", [])
            role = payload.get("role", "Ambulatory Clinic Manager")
            scenario = payload.get("scenario", "General Operations")
            
            # Dynamic system instruction with specific track context
            customized_coach_prompt = COACH_SYSTEM_PROMPT + f"\n\nCURRENT ACTIVE CANDIDATE TARGET:\n- Candidate Role: {role}\n- Focus Scenario: {scenario}\nConduct a probing, realistic executive simulation. Probe weak metrics and score using the 4-Pillar Executive Rubric."

            try:
                reply = call_openrouter(messages, customized_coach_prompt, temperature=0.5)
            except Exception as e:
                reply = f"HCA Interview Coach Simulation Offline: {str(e)}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

if __name__ == "__main__":
    port = 8085
    server = HTTPServer(("0.0.0.0", port), UnifiedPlatformHandler)
    print(f"The HCA Daily Unified Platform Server running on port {port}...")
    server.serve_forever()
