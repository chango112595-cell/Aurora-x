/**
 * ASE-∞ Vault API Routes
 * Provides endpoints for vault unlock requests, approvals, and secret management
 */
import express, { Router, Request, Response, NextFunction } from "express";
import * as path from "path";
import * as fs from "fs";
import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { readVaultSecretAsync, getVaultOpLog, appendVaultOpLog, listVaultSecrets } from "./vault-bridge";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const router = Router();

const ROOT = path.resolve(__dirname, "..");
const OPLOG_PATH = path.join(ROOT, "aurora_supervisor", "secure", "vault_oplog.jsonl");
const VAULT_READ_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_read.py");

const ADMIN_API_KEY = process.env.AURORA_ADMIN_KEY || "";

/**
 * Middleware to require admin authentication
 */
function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const key = req.headers["x-api-key"] as string || req.query.api_key as string || "";
  
  if (!ADMIN_API_KEY) {
    return res.status(500).json({ error: "Admin key not configured on server" });
  }
  
  if (!key || key !== ADMIN_API_KEY) {
    return res.status(401).json({ error: "unauthorized" });
  }
  
  next();
}

/**
 * POST /api/vault/unlock-request
 * Request unlock for a secret (logs the request for admin approval)
 */
router.post("/unlock-request", async (req: Request, res: Response) => {
  try {
    const { alias, requester } = req.body || {};
    
    if (!alias) {
      return res.status(400).json({ error: "alias required" });
    }
    
    const entry = {
      ts: Date.now(),
      op: "unlock_request",
      alias,
      requester: requester || "unknown"
    };
    
    appendVaultOpLog(entry);
    
    return res.json({
      ok: true,
      message: "Unlock requested; check Approvals in dashboard."
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || "Failed to request unlock" });
  }
});

/**
 * POST /api/vault/approve
 * Admin approves unlock and retrieves the secret (short-lived)
 */
router.post("/approve", requireAdmin, async (req: Request, res: Response) => {
  try {
    const { alias } = req.body || {};
    
    if (!alias) {
      return res.status(400).json({ error: "alias required" });
    }
    
    const master = process.env.AURORA_MASTER_PASSPHRASE || "";
    if (!master) {
      return res.status(500).json({ error: "master passphrase not set on server" });
    }
    
    const child = spawn("python3", [VAULT_READ_PY, alias, master], {
      stdio: ["ignore", "pipe", "pipe"]
    });
    
    let out = "";
    let err = "";
    
    child.stdout.on("data", (d) => { out += d.toString(); });
    child.stderr.on("data", (d) => { err += d.toString(); });
    
    child.on("close", (code) => {
      if (code !== 0) {
        return res.status(500).json({ ok: false, error: err || "decrypt failed" });
      }
      
      appendVaultOpLog({ op: "approved_unlock", alias });
      
      return res.json({
        ok: true,
        alias,
        secret: out.trim()
      });
    });
    
    child.on("error", (error: any) => {
      return res.status(500).json({ ok: false, error: error.message || "process error" });
    });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || "Failed to approve unlock" });
  }
});

/**
 * GET /api/vault/requests
 * Get list of vault operation log entries (requires admin)
 */
router.get("/requests", requireAdmin, async (req: Request, res: Response) => {
  try {
    const requests = getVaultOpLog(200).reverse();
    return res.json({ requests });
  } catch (error: any) {
    return res.json({ requests: [] });
  }
});

/**
 * GET /api/vault/aliases
 * Get list of secret aliases in the vault (requires admin)
 */
router.get("/aliases", requireAdmin, async (req: Request, res: Response) => {
  try {
    const aliases = listVaultSecrets();
    return res.json({ ok: true, aliases });
  } catch (error: any) {
    return res.status(500).json({ error: error.message || "Failed to list aliases" });
  }
});

/**
 * GET /api/vault/health
 * Health check for vault system
 */
router.get("/health", async (req: Request, res: Response) => {
  const hasMaster = !!process.env.AURORA_MASTER_PASSPHRASE;
  const hasAdminKey = !!ADMIN_API_KEY;
  
  return res.json({
    ok: true,
    configured: hasMaster && hasAdminKey,
    hasMasterPassphrase: hasMaster,
    hasAdminKey,
    ts: Date.now()
  });
});

export default router;
