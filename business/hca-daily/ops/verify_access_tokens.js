// Standalone verification of the HMAC access-token mechanism used by the worker.
// Mirrors mintDownloadToken / tokenUnlocks from src/index.ts exactly, then
// exercises the accept/reject cases that matter. No network, no secrets.
const crypto = require("crypto");

const TTL = 1000 * 60 * 60 * 24 * 30;
const SECRET = "test-secret-not-the-real-one";

function b64urlFromBytes(buf) {
  return buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function bytesFromB64url(value) {
  const b64 = value.replace(/-/g, "+").replace(/_/g, "/");
  return Buffer.from(b64 + "=".repeat((4 - (b64.length % 4)) % 4), "base64");
}
function hmacSign(secret, message) {
  return b64urlFromBytes(crypto.createHmac("sha256", secret).update(message).digest());
}
function mintDownloadToken(product, nowMs = Date.now()) {
  const payload = `${product}.${nowMs + TTL}`;
  return `${b64urlFromBytes(Buffer.from(payload))}.${hmacSign(SECRET, payload)}`;
}
function tokenUnlocks(token, product, nowMs = Date.now()) {
  try {
    if (!SECRET || !token) return false;
    const dot = token.lastIndexOf(".");
    if (dot < 1) return false;
    const payload = bytesFromB64url(token.slice(0, dot)).toString();
    const [prod, expiryRaw] = payload.split(".");
    if (prod !== product) return false;
    if (!(Number(expiryRaw) > nowMs)) return false;
    const expected = hmacSign(SECRET, payload);
    const given = token.slice(dot + 1);
    if (given.length !== expected.length) return false;
    let diff = 0;
    for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ given.charCodeAt(i);
    return diff === 0;
  } catch {
    return false;
  }
}

const results = [];
function check(name, actual, expected) {
  const ok = actual === expected;
  results.push(ok);
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${name}  (got ${actual}, want ${expected})`);
}

console.log("=== access-token mechanism verification ===\n");

// 1. happy path, both app products
for (const p of ["navigator", "coach", "vault", "accelerator"]) {
  const t = mintDownloadToken(p);
  check(`valid token accepted for ${p}`, tokenUnlocks(t, p), true);
}

// 2. cross-product rejection — a coach token must not open the navigator
const coachToken = mintDownloadToken("coach");
check("coach token rejected for navigator", tokenUnlocks(coachToken, "navigator"), false);

// 3. tampered signature
const navToken = mintDownloadToken("navigator");
const tampered = navToken.slice(0, -2) + (navToken.endsWith("AA") ? "BB" : "AA");
check("tampered signature rejected", tokenUnlocks(tampered, "navigator"), false);

// 4. tampered payload (swap product inside the signed body)
const [body, sig] = navToken.split(".");
const forgedBody = b64urlFromBytes(Buffer.from(`coach.${Date.now() + TTL}`));
check("forged payload rejected", tokenUnlocks(`${forgedBody}.${sig}`, "coach"), false);

// 5. expired token
const old = mintDownloadToken("navigator", Date.now() - TTL * 2);
check("expired token rejected", tokenUnlocks(old, "navigator"), false);

// 6. junk input
for (const junk of ["", "abc", ".", "a.b", "..", "not-a-token"]) {
  check(`junk rejected: ${JSON.stringify(junk)}`, tokenUnlocks(junk, "navigator"), false);
}

// 7. wrong secret cannot mint a valid token
const foreign = `${b64urlFromBytes(Buffer.from(`navigator.${Date.now() + TTL}`))}.${b64urlFromBytes(
  crypto.createHmac("sha256", "attacker-secret").update(`navigator.${Date.now() + TTL}`).digest(),
)}`;
check("foreign-signed token rejected", tokenUnlocks(foreign, "navigator"), false);

const passed = results.filter(Boolean).length;
console.log(`\n${passed}/${results.length} passed`);
process.exit(passed === results.length ? 0 : 1);
