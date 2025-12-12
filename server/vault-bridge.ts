/**
 * ASE-∞ Vault Bridge for Node.js
 * Provides secure secret management through Python vault bridge
 */
import { spawnSync, spawn } from "child_process";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const VAULT_READ_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_read.py");
const VAULT_LIST_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_list.py");
const OPLOG_PATH = path.join(ROOT, "aurora_supervisor", "secure", "vault_oplog.jsonl");

/**
 * Read a secret from the ASE-∞ vault
 * @param alias The secret alias to read
 * @returns The decrypted secret value or null if not found/decryption failed
 */
export function readVaultSecret(alias: string): string | null {
  const master = process.env.AURORA_MASTER_PASSPHRASE || "";
  if (!master) {
    console.warn("[Vault Bridge] AURORA_MASTER_PASSPHRASE not set");
    return null;
  }
  
  try {
    const out = spawnSync("python3", [VAULT_READ_PY, alias, master], {
      encoding: "utf8",
      timeout: 10000
    });
    
    if (out.status !== 0) {
      console.warn(`[Vault Bridge] Failed to read secret '${alias}'`);
      return null;
    }
    
    return out.stdout.trim();
  } catch (error) {
    console.error("[Vault Bridge] Error reading vault:", error);
    return null;
  }
}

/**
 * List all secret aliases in the vault
 * @returns Array of secret aliases
 */
export function listVaultSecrets(): string[] {
  try {
    const out = spawnSync("python3", [VAULT_LIST_PY], {
      encoding: "utf8",
      timeout: 5000
    });
    
    if (out.status !== 0) {
      return [];
    }
    
    return JSON.parse(out.stdout.trim());
  } catch (error) {
    console.error("[Vault Bridge] Error listing secrets:", error);
    return [];
  }
}

/**
 * Read vault operation log (last N entries)
 * @param limit Maximum number of entries to return
 * @returns Array of operation log entries
 */
export function getVaultOpLog(limit: number = 200): any[] {
  try {
    if (!fs.existsSync(OPLOG_PATH)) {
      return [];
    }
    
    const raw = fs.readFileSync(OPLOG_PATH, "utf8");
    const lines = raw.trim().split(/\r?\n/).filter(Boolean).slice(-limit);
    
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(Boolean);
  } catch (error) {
    console.error("[Vault Bridge] Error reading oplog:", error);
    return [];
  }
}

/**
 * Append an entry to the vault operation log
 * @param entry The log entry to append
 */
export function appendVaultOpLog(entry: Record<string, any>): void {
  try {
    const logEntry = { ts: Date.now(), ...entry };
    fs.appendFileSync(OPLOG_PATH, JSON.stringify(logEntry) + "\n");
  } catch (error) {
    console.error("[Vault Bridge] Error writing oplog:", error);
  }
}

/**
 * Read a vault secret asynchronously
 * @param alias The secret alias to read
 * @returns Promise resolving to the decrypted secret value or null
 */
export function readVaultSecretAsync(alias: string): Promise<string | null> {
  return new Promise((resolve) => {
    const master = process.env.AURORA_MASTER_PASSPHRASE || "";
    if (!master) {
      console.warn("[Vault Bridge] AURORA_MASTER_PASSPHRASE not set");
      resolve(null);
      return;
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
        console.warn(`[Vault Bridge] Failed to read secret '${alias}': ${err}`);
        resolve(null);
        return;
      }
      resolve(out.trim());
    });
    
    child.on("error", (error) => {
      console.error("[Vault Bridge] Process error:", error);
      resolve(null);
    });
  });
}

/**
 * Store a secret in the ASE-∞ vault
 * @param alias The secret alias
 * @param value The secret value to encrypt
 * @returns Promise resolving to success status
 */
export function setVaultSecret(alias: string, value: string): Promise<boolean> {
  return new Promise((resolve) => {
    const master = process.env.AURORA_MASTER_PASSPHRASE || "";
    if (!master) {
      console.warn("[Vault Bridge] AURORA_MASTER_PASSPHRASE not set");
      resolve(false);
      return;
    }
    
    const VAULT_SET_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_set_noninteractive.py");
    
    const child = spawn("python3", [VAULT_SET_PY, alias, master, value], {
      stdio: ["ignore", "pipe", "pipe"]
    });
    
    let out = "";
    let err = "";
    
    child.stdout.on("data", (d) => { out += d.toString(); });
    child.stderr.on("data", (d) => { err += d.toString(); });
    
    child.on("close", (code) => {
      if (code !== 0) {
        console.warn(`[Vault Bridge] Failed to set secret '${alias}': ${err}`);
        resolve(false);
        return;
      }
      appendVaultOpLog({ op: "set_secret", alias });
      resolve(true);
    });
    
    child.on("error", (error) => {
      console.error("[Vault Bridge] Process error:", error);
      resolve(false);
    });
  });
}

/**
 * Delete a secret from the ASE-∞ vault
 * @param alias The secret alias to delete
 * @returns Promise resolving to success status
 */
export function deleteVaultSecret(alias: string): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      const VAULT_FILE = path.join(ROOT, "aurora_supervisor", "secure", "secret_vault.json");
      
      if (!fs.existsSync(VAULT_FILE)) {
        resolve(false);
        return;
      }
      
      const data = JSON.parse(fs.readFileSync(VAULT_FILE, "utf8"));
      
      if (!data.secrets || !data.secrets[alias]) {
        resolve(false);
        return;
      }
      
      delete data.secrets[alias];
      fs.writeFileSync(VAULT_FILE, JSON.stringify(data, null, 2));
      appendVaultOpLog({ op: "delete_secret", alias });
      resolve(true);
    } catch (error) {
      console.error("[Vault Bridge] Error deleting secret:", error);
      resolve(false);
    }
  });
}

export default {
  readVaultSecret,
  readVaultSecretAsync,
  listVaultSecrets,
  getVaultOpLog,
  appendVaultOpLog,
  setVaultSecret,
  deleteVaultSecret
};
