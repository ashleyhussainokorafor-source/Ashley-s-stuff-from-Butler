import subprocess
import os
import json
import qrcode

os.makedirs("/data/whatsapp/session", exist_ok=True)
env = os.environ.copy()
env["SESSION_DIR"] = "/data/whatsapp/session"
env["WHATSAPP_MODE"] = "self-chat"
env["ALLOWED_USERS"] = "19514455799"

print("Starting WhatsApp QR listener...", flush=True)
proc = subprocess.Popen(
    ["/usr/local/bin/node", "/opt/hermes-agent/scripts/whatsapp-bridge/bridge.js", "--pair", "--pair-json"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

for line in iter(proc.stdout.readline, ''):
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        ev = data.get("event")
        if ev == "qr":
            qr_str = data["qr"]
            img = qrcode.make(qr_str)
            img.save("/data/whatsapp_pairing_qr.png")
            with open("/data/whatsapp_pairing_qr.txt", "w") as f:
                f.write(qr_str)
            print(f"[QR_READY] /data/whatsapp_pairing_qr.png", flush=True)
        elif ev in ("connected", "open"):
            print("[PAIRED] success", flush=True)
        elif ev == "disconnected":
            print(f"[DISCONNECTED] reason={data.get('reason')}", flush=True)
        elif ev == "error":
            print(f"[ERROR] {data.get('error')} reason={data.get('reason')}", flush=True)
    except Exception:
        pass
