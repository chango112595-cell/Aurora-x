/**
 * ASE-∞ Vault Bridge for Node.js
 * Provides secure secret management through Python vault bridge
 */
import { spawnSync, spawn } from "child_process";
import * as crypto from "crypto";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";
import { resolvePythonCommand } from "./python-runtime";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const VAULT_READ_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_read.py");
const VAULT_LIST_PY = path.join(ROOT, "aurora_supervisor", "secure", "vault_list.py");
const OPLOG_PATH = path.join(ROOT, "aurora_supervisor", "secure", "vault_oplog.jsonl");
const PYTHON_CMD = resolvePythonCommand();
const VAULT_LAYER_COUNT = 22;
const VAULT_LAYER_PREFIX = "ase22:";

type VaultLayerEnvelope = {
  v: number;
  data: string;
  layers: Array<{ iv: string; tag: string }>;
};

function deriveLayerKey(master: string, layer: number): Buffer {
  const salt = `ase-infinity-vault-layer-${layer}`;
  return crypto.scryptSync(master, salt, 32);
}

function encryptWithVaultLayers(value: string, master: string): string {
  let data = Buffer.from(value, "utf8");
  const layers: VaultLayerEnvelope["layers"] = [];

  for (let i = 1; i <= VAULT_LAYER_COUNT; i += 1) {
    const key = deriveLayerKey(master, i);
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
    data = Buffer.concat([cipher.update(data), cipher.final()]);
    const tag = cipher.getAuthTag();
    layers.push({ iv: iv.toString("base64"), tag: tag.toString("base64") });
  }

  const payload: VaultLayerEnvelope = {
    v: 1,
    data: data.toString("base64"),
    layers
  };

  return `${VAULT_LAYER_PREFIX}${Buffer.from(JSON.stringify(payload)).toString("base64")}`;
}

function decryptVaultLayers(value: string, master: string): string | null {
  if (!value.startsWith(VAULT_LAYER_PREFIX)) {
    return value;
  }

  try {
    const encoded = value.slice(VAULT_LAYER_PREFIX.length);
    const payload = JSON.parse(Buffer.from(encoded, "base64").toString("utf8")) as VaultLayerEnvelope;
    let data = Buffer.from(payload.data, "base64");

    for (let i = payload.layers.length - 1; i >= 0; i -= 1) {
      const layer = payload.layers[i];
      const key = deriveLayerKey(master, i + 1);
      const iv = Buffer.from(layer.iv, "base64");
      const tag = Buffer.from(layer.tag, "base64");
      const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
      decipher.setAuthTag(tag);
      data = Buffer.concat([decipher.update(data), decipher.final()]);
    }

    return data.toString("utf8");
  } catch (error) {
    console.warn("[Vault Bridge] Failed to decrypt vault layers:", error);
    return null;
  }
}

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
    const out = spawnSync(PYTHON_CMD, [VAULT_READ_PY, alias, master], {
      encoding: "utf8",
      timeout: 10000
    });
    
    if (out.status !== 0) {
      console.warn(`[Vault Bridge] Failed to read secret '${alias}'`);
      return null;
    }
    
    return decryptVaultLayers(out.stdout.trim(), master);
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
    const out = spawnSync(PYTHON_CMD, [VAULT_LIST_PY], {
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
    
    const child = spawn(PYTHON_CMD, [VAULT_READ_PY, alias, master], {
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
      resolve(decryptVaultLayers(out.trim(), master));
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
    
    const encryptedValue = encryptWithVaultLayers(value, master);
    const child = spawn(PYTHON_CMD, [VAULT_SET_PY, alias, master, encryptedValue], {
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
