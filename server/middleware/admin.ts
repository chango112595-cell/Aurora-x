import crypto from "crypto";
import type { Request, Response, NextFunction } from "express";

function safeEq(a: string, b: string) {
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) return false;
  return crypto.timingSafeEqual(ab, bb);
}

export function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const expected = process.env.AURORA_ADMIN_KEY;
  if (!expected) return res.status(500).json({ error: "AURORA_ADMIN_KEY not set" });

  const auth = req.get("authorization") || "";
  const bearer = auth.toLowerCase().startsWith("bearer ") ? auth.slice(7).trim() : "";
  const apiKey = bearer || req.get("x-api-key") || "";

  if (!apiKey || !safeEq(apiKey, expected)) return res.status(401).json({ error: "Unauthorized" });

  // Localhost-only (protect against remote RCE)
  const ra = req.socket.remoteAddress || "";
  const isLocal = ra.includes("127.0.0.1") || ra.includes("::1");
  if (!isLocal) return res.status(403).json({ error: "Forbidden" });

  next();
}
