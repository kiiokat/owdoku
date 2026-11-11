// OWdoku guess tracking: records the answers in each finished daily game and returns how
// often each answer was picked, for rarity scores and "most common answer" reveals.
//
//   POST /api/result  {day, client, sig, cells:[name|null x9]}   -> {ok:true}
//   GET  /api/stats?day=YYYY-MM-DD&sig=...                        -> {plays, cells:[{name:count}]}
//
// Stores no personal data: "client" is a random id the game generates per browser.
import { PLAYER_NAMES } from "./players.js";

const ALLOWED_ORIGINS = [
  "https://kiiokat.github.io",
  "http://localhost:8000", "http://127.0.0.1:8000",   // local testing
];
const DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
const CLIENT_RE = /^[a-z0-9-]{8,64}$/i;

function cors(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}
function json(body, status, origin, extra = {}) {
  return new Response(JSON.stringify(body), {
    status, headers: { "Content-Type": "application/json", ...cors(origin), ...extra },
  });
}
// Puzzles are by local date, and time zones span about a day either way of UTC,
// so accept yesterday, today and tomorrow (UTC).
function dayIsCurrent(day) {
  const t = Date.parse(day + "T00:00:00Z");
  if (Number.isNaN(t)) return false;
  const now = Date.now(), d = 864e5;
  return t >= now - 2 * d && t <= now + d;
}
// Each grid has its own signature, so a grid change mid-day starts fresh counts.
const SIG_RE = /^[\p{L}\p{N}:|.\- ]{3,300}$/u;   // category ids, e.g. "t:LDN|h:Lúcio|h:Soldier: 76"
const dayKey = (day, sig) => day + "#" + sig;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });

    try {
      if (url.pathname === "/api/result" && request.method === "POST") {
        const len = Number(request.headers.get("Content-Length") || 0);
        if (len > 4096) return json({ error: "too large" }, 413, origin);
        const body = await request.json().catch(() => null);
        if (!body) return json({ error: "bad json" }, 400, origin);
        const { day, client, sig, cells } = body;
        if (!DAY_RE.test(day || "") || !dayIsCurrent(day)) return json({ error: "bad day" }, 400, origin);
        if (!CLIENT_RE.test(client || "")) return json({ error: "bad client" }, 400, origin);
        if (!SIG_RE.test(sig || "")) return json({ error: "bad sig" }, 400, origin);
        if (!Array.isArray(cells) || cells.length !== 9) return json({ error: "bad cells" }, 400, origin);
        const names = cells.map(n => (n == null ? null : String(n)));
        const seen = new Set();
        for (const n of names) {
          if (n === null) continue;
          if (!PLAYER_NAMES.has(n) || seen.has(n)) return json({ error: "bad answer" }, 400, origin);
          seen.add(n);
        }
        const key = dayKey(day, sig);
        // One result per browser per puzzle.
        const ins = await env.DB.prepare(
          "INSERT OR IGNORE INTO plays (day, client, created) VALUES (?, ?, ?)"
        ).bind(key, client, Math.floor(Date.now() / 1000)).run();
        if (!ins.meta || ins.meta.changes === 0) return json({ ok: true, duplicate: true }, 200, origin);
        const stmts = [];
        names.forEach((n, cell) => {
          if (n === null) return;
          stmts.push(env.DB.prepare(
            "INSERT INTO picks (day, cell, player, count) VALUES (?, ?, ?, 1) " +
            "ON CONFLICT(day, cell, player) DO UPDATE SET count = count + 1"
          ).bind(key, cell, n));
        });
        if (stmts.length) await env.DB.batch(stmts);
        return json({ ok: true }, 200, origin);
      }

      if (url.pathname === "/api/stats" && request.method === "GET") {
        const day = url.searchParams.get("day") || "", sig = url.searchParams.get("sig") || "";
        if (!DAY_RE.test(day) || !SIG_RE.test(sig)) return json({ error: "bad request" }, 400, origin);
        const key = dayKey(day, sig);
        const plays = await env.DB.prepare("SELECT COUNT(*) AS n FROM plays WHERE day = ?").bind(key).first();
        const rows = await env.DB.prepare(
          "SELECT cell, player, count FROM picks WHERE day = ? ORDER BY count DESC LIMIT 900"
        ).bind(key).all();
        const cells = Array.from({ length: 9 }, () => ({}));
        for (const r of rows.results || []) if (r.cell >= 0 && r.cell < 9) cells[r.cell][r.player] = r.count;
        return json({ plays: plays ? plays.n : 0, cells }, 200, origin, { "Cache-Control": "public, max-age=30" });
      }

      return json({ error: "not found" }, 404, origin);
    } catch (e) {
      // Includes the free-tier daily limit; the game treats any error as "stats unavailable".
      return json({ error: "unavailable" }, 503, origin);
    }
  },
};
