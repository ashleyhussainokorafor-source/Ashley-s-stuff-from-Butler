"""
The HCA Daily — Inbound Lead Webhook Listener for Content 360
Listens on port 8086 for inbound leads (Instagram/Facebook chatbot opt-ins)
and logs/processes them for automated onboarding.
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

LEADS_FILE = "/data/business/hca-daily/inbound_leads.json"

class LeadWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path in ("/webhook/content360", "/api/leads"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                lead_data = json.loads(body)
            except Exception:
                lead_data = {"raw": body}

            lead_data["received_at"] = datetime.utcnow().isoformat()

            # Append to leads log
            leads = []
            if os.path.exists(LEADS_FILE):
                try:
                    with open(LEADS_FILE, "r") as f:
                        leads = json.load(f)
                except Exception:
                    leads = []

            leads.append(lead_data)
            with open(LEADS_FILE, "w") as f:
                json.dump(leads, f, indent=2)

            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] New lead captured from Content 360!")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Lead ingested by Hermes"}).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

    def do_GET(self):
        if self.path in ("/webhook/content360", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "active", "service": "Hermes Content 360 Lead Listener"}).encode("utf-8"))
            return
        self.send_error(404)

if __name__ == "__main__":
    port = 8086
    server = HTTPServer(("0.0.0.0", port), LeadWebhookHandler)
    print(f"Content 360 Lead Webhook Listener running on port {port}...")
    server.serve_forever()
