import type { Express } from "express";
import express from "express";
import { storage } from "./storage";
import { corpusStorage } from "./corpus-storage";
import { progressStore } from "./progress-store";
import type { SynthesisWebSocketServer } from "./websocket-server";
import * as path from "path";
import * as fs from "fs";
import { spawn, execFile } from "child_process";
import { promisify } from "util";
import {
  corpusEntrySchema,
  corpusQuerySchema,
  topQuerySchema,
  recentQuerySchema,
  similarityQuerySchema,
  runMetaSchema,
  usedSeedSchema,
} from "../shared/schema";
import authRouter from "./auth-routes";
import vaultRouter from "./routes-vault";
import { getChatResponse, searchWeb } from "./aurora-chat";
import { executeWithOrchestrator, selectExecutionMethod, getCapabilities, type ExecutionContext } from "./aurora-execution-orchestrator";
import { ResponseAdapter } from "./response-adapter";
import { apiLimiter, authLimiter, chatLimiter, synthesisLimiter, searchLimiter } from "./rate-limit";
import { AuroraCore } from "./aurora-core";
import { assertDatabaseReady, dbError, isDatabaseAvailable } from "./db";
import { resolvePythonCommand } from "./python-runtime";

const AURORA_API_KEY = process.env.AURORA_API_KEY || "dev-key-change-in-production";
const AURORA_HEALTH_TOKEN = process.env.AURORA_HEALTH_TOKEN || "ok";
const BRIDGE_URL = process.env.AURORA_BRIDGE_URL || "http://0.0.0.0:5001";
const LUMINAR_V2_URL = process.env.LUMINAR_V2_URL || process.env.LUMINAR_URL || "http://0.0.0.0:8000";
const AURORA_REPO = process.env.AURORA_REPO || "chango112595-cell/Aurora-x";
const TARGET_BRANCH = process.env.AURORA_TARGET_BRANCH || "main";
const AURORA_GH_TOKEN = process.env.AURORA_GH_TOKEN;
const GH_API = "https://api.github.com";
let serverStartTime: number = Date.now();
const execFileAsync = promisify(execFile);
const PYTHON_CMD = resolvePythonCommand();
const PROJECT_ROOT = process.cwd();
const AURORA_CORE_MODULES_DIR = path.join(PROJECT_ROOT, "aurora_x", "core", "modules");
const NEXUS_V3_MODULES_DIR = path.join(PROJECT_ROOT, "aurora_nexus_v3", "modules");
const NEXUS_V3_REGISTRY_PATH = path.join(PROJECT_ROOT, "aurora_nexus_v3", "modules_registry.json");
const MANIFESTS_DIR = path.join(PROJECT_ROOT, "manifests");
const PACKAGE_JSON_PATH = path.join(PROJECT_ROOT, "package.json");
const UI_ROOT = path.join(PROJECT_ROOT, "client", "src");
const BACKEND_ENTRY = path.join(PROJECT_ROOT, "server", "index.ts");
const NEXUS_V3_CORE_PATH = path.join(PROJECT_ROOT, "aurora_nexus_v3", "core", "universal_core.py");
const MEMORY_FABRIC_PATH = path.join(PROJECT_ROOT, "aurora_memory_fabric_v2", "service.py");

async function runGit(args: string[]): Promise<string> {
  const { stdout } = await execFileAsync("git", args, { cwd: process.cwd() });
  return stdout.trim();
}

function readJsonFileSafe(filePath: string): any | null {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

function statIso(filePath: string): string | null {
  try {
    return fs.statSync(filePath).mtime.toISOString();
  } catch {
    return null;
  }
}

function readDirFilesSafe(dirPath: string): string[] {
  try {
    return fs.readdirSync(dirPath, { withFileTypes: true })
      .filter((entry) => entry.isFile())
      .map((entry) => entry.name);
  } catch {
    return [];
  }
}

function buildBreakdown(list: any[], key: string): Record<string, number> {
  const breakdown: Record<string, number> = {};
  for (const item of list) {
    const value = typeof item?.[key] === "string" ? item[key] : null;
    if (!value) continue;
    breakdown[value] = (breakdown[value] ?? 0) + 1;
  }
  return breakdown;
}

function summarizeAuroraCoreModules() {
  if (!fs.existsSync(AURORA_CORE_MODULES_DIR)) {
    return { available: false, root: AURORA_CORE_MODULES_DIR };
  }

  const entries = fs.readdirSync(AURORA_CORE_MODULES_DIR, { withFileTypes: true });
  const fileNames = entries.filter((entry) => entry.isFile()).map((entry) => entry.name);
  const pyFiles = fileNames.filter((name) => name.endsWith(".py"));
  const auroraModules = pyFiles.filter((name) => /^AuroraModule\d+\.py$/.test(name)).length;
  const standardModules = pyFiles.filter((name) => /^module_\d+\.py$/.test(name)).length;
  const manifestPath = path.join(AURORA_CORE_MODULES_DIR, "modules.manifest.json");
  const manifestList = readJsonFileSafe(manifestPath);
  const normalizedManifest = Array.isArray(manifestList) ? manifestList : [];

  return {
    available: true,
    root: AURORA_CORE_MODULES_DIR,
    totalEntries: entries.length,
    pythonFiles: pyFiles.length,
    auroraModules,
    standardModules,
    manifestCount: normalizedManifest.length,
    temporalBreakdown: buildBreakdown(normalizedManifest, "temporal"),
    tierBreakdown: buildBreakdown(normalizedManifest, "tier"),
    lastUpdated: statIso(AURORA_CORE_MODULES_DIR),
    manifestUpdated: statIso(manifestPath)
  };
}

function summarizeNexusV3Modules() {
  if (!fs.existsSync(NEXUS_V3_MODULES_DIR)) {
    return { available: false, root: NEXUS_V3_MODULES_DIR };
  }

  const entries = fs.readdirSync(NEXUS_V3_MODULES_DIR, { withFileTypes: true });
  const rootFiles = entries.filter((entry) => entry.isFile()).map((entry) => entry.name);
  const rootPyFiles = rootFiles.filter((name) => name.endsWith(".py"));
  const moduleFiles = rootPyFiles.filter((name) => /^module_\d+\.py$/.test(name)).length;
  const registry = readJsonFileSafe(NEXUS_V3_REGISTRY_PATH);
  let registryCount = 0;
  if (registry && typeof registry.count === "number") {
    registryCount = registry.count;
  } else if (registry && registry.modules && typeof registry.modules === "object") {
    registryCount = Object.keys(registry.modules).length;
  }

  const subdirectories = entries
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("__"))
    .map((entry) => {
      const subPath = path.join(NEXUS_V3_MODULES_DIR, entry.name);
      const subFiles = readDirFilesSafe(subPath).filter((name) => name.endsWith(".py"));
      const initCount = subFiles.filter((name) => name.endsWith("_init.py")).length;
      const executeCount = subFiles.filter((name) => name.endsWith("_execute.py")).length;
      const cleanupCount = subFiles.filter((name) => name.endsWith("_cleanup.py")).length;
      const moduleIds = new Set<string>();
      for (const name of subFiles) {
        const match = name.match(/_(\d+)_/);
        if (match) moduleIds.add(match[1]);
      }

      return {
        name: entry.name,
        moduleIds: moduleIds.size,
        init: initCount,
        execute: executeCount,
        cleanup: cleanupCount,
        totalFiles: subFiles.length
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));

  return {
    available: true,
    root: NEXUS_V3_MODULES_DIR,
    moduleFiles,
    registryCount,
    subdirectories,
    lastUpdated: statIso(NEXUS_V3_MODULES_DIR),
    registryUpdated: statIso(NEXUS_V3_REGISTRY_PATH)
  };
}

function summarizeManifest(fileName: string, listKey: string, totalKey: string) {
  const filePath = path.join(MANIFESTS_DIR, fileName);
  const data = readJsonFileSafe(filePath);
  let count = 0;
  if (Array.isArray(data)) {
    count = data.length;
  } else if (data && Array.isArray(data[listKey])) {
    count = data[listKey].length;
  } else if (data && typeof data[totalKey] === "number") {
    count = data[totalKey];
  }
  const generatedAt = data && typeof data.generatedAt === "string" ? data.generatedAt : null;
  return {
    count,
    generatedAt,
    lastUpdated: statIso(filePath)
  };
}

// WebSocket server reference - set from index.ts after initialization
let wsServer: SynthesisWebSocketServer | null = null;

export function setWebSocketServer(server: SynthesisWebSocketServer): void {
  wsServer = server;
}

// GitHub API helper function
function getGitHubHeaders() {
  if (!AURORA_GH_TOKEN) {
    throw new Error("Missing AURORA_GH_TOKEN environment variable");
  }
  return {
    "Authorization": `token ${AURORA_GH_TOKEN}`,
    "Accept": "application/vnd.github+json"
  };
}

/**
 * Helper function to refresh README badges after progress updates
 * Runs asynchronously to avoid blocking the API response
 * 
 * This function:
 * 1. Runs the Python script at tools/patch_readme_progress.py to update README badges
 * 2. Optionally commits and pushes changes to git if AURORA_AUTO_GIT is set
 */
async function refreshReadmeBadges(): Promise<void> {
  try {
    // Check if the Python script exists
    const scriptPath = path.join(process.cwd(), 'tools', 'patch_readme_progress.py');
    if (!fs.existsSync(scriptPath)) {
      // Script doesn't exist, log but don't fail
      console.log('[Badge Refresh] Python script not found at tools/patch_readme_progress.py - skipping badge refresh');
      return;
    }

    // Run the Python script to update badges
    await new Promise<void>((resolve, reject) => {
      execFile(PYTHON_CMD, [scriptPath], {
        cwd: process.cwd(),
        timeout: 10000, // 10 second timeout
        maxBuffer: 1024 * 1024, // 1MB buffer
      }, (error, stdout, stderr) => {
        if (error) {
          console.error('[Badge Refresh] Error running patch_readme_progress.py:', error.message);
          // Don't reject, just log and continue
          resolve();
          return;
        }

        if (stderr && !stderr.includes('[OK]')) {
          console.error('[Badge Refresh] Script stderr:', stderr);
        }

        if (stdout && stdout.includes('[OK]')) {
          console.log('[Badge Refresh] README badges updated successfully');
        }

        resolve();
      });
    });

    // Check if auto-git is enabled
    const autoGit = process.env.AURORA_AUTO_GIT;
    const shouldAutoCommit = autoGit && ['1', 'true', 'yes', 'on'].includes(autoGit.toLowerCase());

    if (shouldAutoCommit) {
      // Run git operations
      console.log('[Badge Refresh] Auto-git enabled, committing and pushing changes...');

      // Add specific files
      const filesToAdd = [
        'progress.json',
        'MASTER_TASK_LIST.md',
        'progress_export.csv',
        'README.md'
      ];

      // Check which files exist and add them
      const existingFiles = filesToAdd.filter(file => 
        fs.existsSync(path.join(process.cwd(), file))
      );

      if (existingFiles.length === 0) {
        console.log('[Badge Refresh] No files to commit');
        return;
      }

      // Add files to git
      await new Promise<void>((resolve) => {
        execFile('git', ['add', ...existingFiles], {
          cwd: process.cwd(),
          timeout: 5000,
        }, (error, stdout, stderr) => {
          if (error) {
            console.error('[Badge Refresh] Error adding files to git:', error.message);
            resolve();
            return;
          }
          console.log('[Badge Refresh] Added files to git:', existingFiles.join(', '));
          resolve();
        });
      });

      // Create commit
      await new Promise<void>((resolve) => {
        execFile('git', ['commit', '-m', 'chore(progress): bump via /api and refresh badges'], {
          cwd: process.cwd(),
          timeout: 5000,
        }, (error, stdout, stderr) => {
          if (error) {
            // Check if it's just "nothing to commit" which is not really an error
            if (error.message.includes('nothing to commit')) {
              console.log('[Badge Refresh] Nothing to commit, working tree clean');
            } else {
              console.error('[Badge Refresh] Error creating commit:', error.message);
            }
            resolve();
            return;
          }
          console.log('[Badge Refresh] Created commit successfully');
          resolve();
        });
      });

      // Push to remote
      await new Promise<void>((resolve) => {
        execFile('git', ['push'], {
          cwd: process.cwd(),
          timeout: 15000, // Give push more time
        }, (error, stdout, stderr) => {
          if (error) {
            console.error('[Badge Refresh] Error pushing to remote:', error.message);
            resolve();
            return;
          }
          console.log('[Badge Refresh] Pushed changes to remote repository');
          resolve();
        });
      });
    }
  } catch (error: any) {
    // Log error but don't throw - this is a non-critical operation
    console.error('[Badge Refresh] Unexpected error:', error.message || error);
  }
}

export async function registerRoutes(app: Express): Promise<void> {
  // ══════════════════════════════════════════════════════════════
  // 📊 SYSTEM ROUTES (BEFORE RATE LIMITING)
  // ══════════════════════════════════════════════════════════════
  
  // Health check endpoint - EXEMPT from rate limiting (critical for monitoring)
  app.get("/api/health", (req, res) => {
    res.status(200).json({ 
      status: "ok",
      service: "chango",
      uptime: Math.floor((Date.now() - serverStartTime) / 1000)
    });
  });

  app.get("/api/database/status", async (_req, res) => {
    try {
      await assertDatabaseReady();
      res.json({
        ready: true,
        configured: true,
        available: isDatabaseAvailable()
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Database unavailable";
      res.status(503).json({
        ready: false,
        configured: !!process.env.DATABASE_URL,
        available: isDatabaseAvailable(),
        error: message,
        last_error: dbError || undefined
      });
    }
  });

  // Real system metrics endpoint using psutil
  app.get("/api/system/metrics", async (req, res) => {
    try {
      const pythonCode = 'import psutil,json;print(json.dumps({"cpu":psutil.cpu_percent(interval=0.1),"memory":psutil.virtual_memory().percent,"disk":psutil.disk_usage("/").percent,"network":{"bytes_sent":psutil.net_io_counters().bytes_sent,"bytes_recv":psutil.net_io_counters().bytes_recv}}))';
      const metricsProcess = spawn(PYTHON_CMD, ['-c', pythonCode]);
      
      let output = '';
      let errorOutput = '';
      
      metricsProcess.stdout.on('data', (data) => { output += data.toString(); });
      metricsProcess.stderr.on('data', (data) => { errorOutput += data.toString(); });
      
      metricsProcess.on('close', (code) => {
        if (code === 0 && output.trim()) {
          try {
            res.json(JSON.parse(output.trim()));
          } catch (e) {
            res.status(500).json({ error: 'Failed to parse metrics', raw: output });
          }
        } else {
          res.status(500).json({ error: 'Failed to get metrics', stderr: errorOutput });
        }
      });
      
      metricsProcess.on('error', (err) => {
        res.status(500).json({ error: 'Process error', message: err.message });
      });
    } catch (error: any) {
      res.status(500).json({ error: 'Metrics unavailable', message: error.message });
    }
  });

  // Dynamic evolution metrics endpoint - real production data from manifests
  app.get("/api/evolution/metrics", async (req, res) => {
    try {
      const fsPromises = await import('fs/promises');
      const pathModule = await import('path');
      
      // Read manifests for real data
      const tiersPath = pathModule.join(process.cwd(), 'manifests/tiers.manifest.json');
      const execsPath = pathModule.join(process.cwd(), 'manifests/executions.manifest.json');
      const modulesPath = pathModule.join(process.cwd(), 'manifests/modules.manifest.json');
      
      let tiersData = { tiers: [] as any[] };
      let execsData = { executions: [] as any[] };
      let modulesData = { modules: [] as any[] };
      
      try {
        tiersData = JSON.parse(await fsPromises.readFile(tiersPath, 'utf-8'));
      } catch {}
      try {
        execsData = JSON.parse(await fsPromises.readFile(execsPath, 'utf-8'));
      } catch {}
      try {
        modulesData = JSON.parse(await fsPromises.readFile(modulesPath, 'utf-8'));
      } catch {}
      
      // Calculate real metrics from manifests
      const activeTiers = tiersData.tiers.filter((t: any) => t.status === 'active').length;
      const activeExecs = execsData.executions.filter((e: any) => e.status === 'active').length;
      const totalCapabilities = tiersData.tiers.reduce((acc: number, t: any) => acc + (t.capabilities?.length || 0), 0);
      
      // Calculate real percentages based on actual data
      const tierProgress = tiersData.tiers.length > 0 ? Math.round((activeTiers / tiersData.tiers.length) * 100) : 0;
      const execProgress = execsData.executions.length > 0 ? Math.round((activeExecs / execsData.executions.length) * 100) : 0;
      const moduleCount = modulesData.modules?.length || 550;
      
      // Get real system uptime
      const uptimeSeconds = Math.floor((Date.now() - serverStartTime) / 1000);
      const uptimeHours = uptimeSeconds / 3600;
      
      // Calculate learning rate based on system activity (corpus entries, etc.)
      const learningRate = Math.min(95, 75 + Math.floor(uptimeHours * 2));
      
      // Memory efficiency based on active modules ratio
      const memoryEfficiency = Math.min(98, Math.round((moduleCount / 600) * 100));
      
      // Context retention based on active tiers
      const contextRetention = Math.min(96, Math.round((activeTiers / 188) * 100));
      
      const evolutionMetrics = [
        { id: '1', name: 'Neural Processing', value: tierProgress, maxValue: 100, trend: tierProgress > 90 ? 'stable' : 'up', category: 'intelligence' },
        { id: '2', name: 'Pattern Recognition', value: Math.min(100, Math.round(totalCapabilities / 4)), maxValue: 100, trend: 'up', category: 'intelligence' },
        { id: '3', name: 'Code Synthesis', value: execProgress, maxValue: 100, trend: execProgress > 90 ? 'stable' : 'up', category: 'capability' },
        { id: '4', name: 'Learning Rate', value: learningRate, maxValue: 100, trend: 'up', category: 'adaptation' },
        { id: '5', name: 'Memory Efficiency', value: memoryEfficiency, maxValue: 100, trend: 'stable', category: 'performance' },
        { id: '6', name: 'Context Retention', value: contextRetention, maxValue: 100, trend: 'up', category: 'intelligence' },
        { id: '7', name: 'Autonomous Decision', value: Math.min(95, activeExecs + 30), maxValue: 100, trend: 'up', category: 'capability' },
        { id: '8', name: 'Self-Optimization', value: Math.min(92, activeTiers > 150 ? 90 : 80), maxValue: 100, trend: 'up', category: 'adaptation' },
      ];
      
      // Read evolution log for real learning events
      let learningEvents: any[] = [];
      let learningLogAvailable = false;
      try {
        const evolutionLogPath = pathModule.join(process.cwd(), 'aurora_supervisor/data/evolution_log.jsonl');
        const logContent = await fsPromises.readFile(evolutionLogPath, 'utf-8');
        const logLines = logContent.trim().split('\n').filter(Boolean).slice(-10);
        learningEvents = logLines.map((line, i) => {
          try {
            const entry = JSON.parse(line);
            return {
              timestamp: entry.timestamp || new Date().toISOString(),
              type: entry.type || 'system_event',
              description: entry.description || entry.message || 'System activity logged',
              improvement: entry.improvement || 1.0
            };
          } catch {
            return {
              timestamp: new Date(Date.now() - i * 60000).toISOString(),
              type: 'system_event',
              description: 'System activity logged',
              improvement: 1.0
            };
          }
        }).slice(0, 5);
        learningLogAvailable = true;
      } catch {
        learningEvents = [];
      }
      
      res.json({
        metrics: evolutionMetrics,
        learningEvents,
        learningLogAvailable,
        summary: {
          totalTiers: tiersData.tiers.length,
          activeTiers,
          totalExecutions: execsData.executions.length,
          activeExecutions: activeExecs,
          totalCapabilities,
          totalModules: moduleCount,
          uptimeSeconds
        }
      });
    } catch (error: any) {
      res.status(500).json({ error: 'Failed to get evolution metrics', message: error.message });
    }
  });

  // Modules overview endpoint - summarises core modules and Nexus V3 subdirectories
  app.get("/api/modules/overview", (_req, res) => {
    try {
      const auroraCore = summarizeAuroraCoreModules();
      const nexusV3 = summarizeNexusV3Modules();
      res.json({
        timestamp: new Date().toISOString(),
        auroraCore,
        nexusV3
      });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to build module overview", message: error.message });
    }
  });

  // Update status endpoint - versions, manifests, and last updated timestamps
  app.get("/api/aurora/update-status", (_req, res) => {
    try {
      const pkg = readJsonFileSafe(PACKAGE_JSON_PATH);
      const auroraStatus = AuroraCore.getInstance().getStatus();
      const uptimeMs = typeof auroraStatus?.uptime === "number" ? auroraStatus.uptime : 0;
      res.json({
        timestamp: new Date().toISOString(),
        ui: {
          name: typeof pkg?.name === "string" ? pkg.name : "aurora-ui",
          version: typeof pkg?.version === "string" ? pkg.version : "0.0.0",
          lastUpdated: statIso(UI_ROOT) ?? statIso(PACKAGE_JSON_PATH)
        },
        backend: {
          version: auroraStatus?.version ?? "unknown",
          node: process.version,
          uptimeSeconds: Math.floor(uptimeMs / 1000),
          lastUpdated: statIso(BACKEND_ENTRY)
        },
        nexusV3: {
          version: auroraStatus?.nexusV3?.version ?? null,
          lastUpdated: statIso(NEXUS_V3_CORE_PATH)
        },
        memoryFabric: {
          lastUpdated: statIso(MEMORY_FABRIC_PATH)
        },
        manifests: {
          tiers: summarizeManifest("tiers.manifest.json", "tiers", "totalTiers"),
          executions: summarizeManifest("executions.manifest.json", "executions", "totalExecutions"),
          modules: summarizeManifest("modules.manifest.json", "modules", "totalModules")
        }
      });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to build update status", message: error.message });
    }
  });

  // ══════════════════════════════════════════════════════════════
  // 🗺️ ROADMAP API ROUTES (Autonomous Roadmap Supervisor)
  // ══════════════════════════════════════════════════════════════
  
  const AURORA_ROOT = process.env.AURORA_ROOT || path.resolve(process.cwd());
  const SUPERVISOR_DATA = path.join(AURORA_ROOT, "aurora_supervisor", "data");
  const ADMIN_API_KEY = process.env.AURORA_ADMIN_KEY || "aurora-admin-key";

  // Helper to read JSON safely
  async function readJsonSafe(relPath: string) {
    const p = path.join(SUPERVISOR_DATA, relPath);
    const text = await fs.promises.readFile(p, "utf8");
    return JSON.parse(text);
  }

  // Roadmap progress endpoint
  app.get("/api/roadmap/progress", async (req, res) => {
    try {
      const data = await readJsonSafe("roadmap_progress.json");
      return res.json({ ok: true, data });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: String(e.message || e) });
    }
  });

  // Roadmap summary endpoint
  app.get("/api/roadmap/summary", async (req, res) => {
    try {
      const data = await readJsonSafe("roadmap_summary.json");
      return res.json({ ok: true, data });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: String(e.message || e) });
    }
  });

  // Evolution log endpoint (tail last 200 entries)
  app.get("/api/evolution/log", async (req, res) => {
    try {
      const p = path.join(SUPERVISOR_DATA, "evolution_log.jsonl");
      const raw = await fs.promises.readFile(p, "utf8");
      const lines = raw.trim().split(/\r?\n/).filter(Boolean).slice(-200);
      const entries = lines.map(l => JSON.parse(l));
      return res.json({ ok: true, entries });
    } catch (e: any) {
      return res.json({ ok: true, entries: [] });
    }
  });

  // Queued approvals endpoint (requires admin key)
  app.get("/api/evolution/queued", async (req, res) => {
    const key = req.headers["x-api-key"] as string | undefined;
    if (!key || key !== ADMIN_API_KEY) {
      return res.status(401).json({ ok: false, error: "unauthorized" });
    }
    try {
      const p = path.join(SUPERVISOR_DATA, "evolution_log.jsonl");
      const raw = await fs.promises.readFile(p, "utf8");
      const list = raw.trim().split(/\r?\n/).filter(Boolean).map(l => JSON.parse(l));
      const queued: any[] = [];
      for (const entry of list) {
        (entry.queued || []).forEach((q: any) => { if (q.requires_approval) queued.push(q); });
      }
      return res.json({ ok: true, queued });
    } catch (e: any) {
      return res.json({ ok: true, queued: [] });
    }
  });

  // Approve an evolution change
  app.post("/api/evolution/approve", express.json(), async (req, res) => {
    const key = req.headers["x-api-key"] as string | undefined;
    if (!key || key !== ADMIN_API_KEY) {
      return res.status(401).json({ ok: false, error: "unauthorized" });
    }
    try {
      const { target } = req.body;
      if (!target) {
        return res.status(400).json({ ok: false, error: "target is required" });
      }
      const script = path.join(AURORA_ROOT, "aurora_supervisor", "apply_approved.py");
      const child = spawn(PYTHON_CMD, [script, target], { stdio: "pipe" });
      let out = "";
      child.stdout.on("data", d => out += d.toString());
      child.stderr.on("data", d => out += d.toString());
      child.on("close", (code) => {
        if (code === 0) return res.json({ ok: true, message: out });
        return res.status(500).json({ ok: false, error: out });
      });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: String(e.message || e) });
    }
  });

  // Run next roadmap phase (manual trigger)
  app.post("/api/roadmap/run-next", async (req, res) => {
    const key = req.headers["x-api-key"] as string | undefined;
    if (!key || key !== ADMIN_API_KEY) {
      return res.status(401).json({ ok: false, error: "unauthorized" });
    }
    try {
      const script = path.join(AURORA_ROOT, "aurora_supervisor", "aurora_autonomous_roadmap.py");
      spawn(PYTHON_CMD, [script], { detached: true, stdio: "ignore" }).unref();
      return res.json({ ok: true, message: "Triggered roadmap runner" });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: String(e.message || e) });
    }
  });

  // Roadmap health endpoint
  app.get("/api/roadmap/health", async (req, res) => {
    res.json({ ok: true, ts: Date.now() });
  });

  // ══════════════════════════════════════════════════════════════
  // 🔐 ASE-∞ VAULT ROUTES
  // ══════════════════════════════════════════════════════════════
  app.use("/api/vault", vaultRouter);

  // ══════════════════════════════════════════════════════════════
  // 🔐 RATE LIMITING SETUP
  // ══════════════════════════════════════════════════════════════
  // Apply rate limiters in order of specificity (most specific first)
  
  // 1. Authentication endpoints - strict limiting
  app.use("/api/auth", authLimiter, authRouter);
  
  // 2. Chat endpoints - all HTTP methods
  app.use("/api/chat", chatLimiter);
  
  // 3. Synthesis endpoints - all HTTP methods
  app.use("/api/synthesis", synthesisLimiter);
  
  // 4. General API rate limiting for all other routes
  app.use("/api/", apiLimiter);

  // Autonomous healing trigger endpoint
  app.post("/api/heal", async (req, res) => {
    try {
      console.log('[Aurora Heal] Autonomous Healing Requested');
      
      // Execute the Python healing system
      const healerProcess = spawn(PYTHON_CMD, ['tools/aurora_autonomous_fixer.py', '--heal'], {
        cwd: process.cwd(),
        timeout: 30000
      });
      
      let stdout = '';
      let stderr = '';
      
      healerProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      healerProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      healerProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            res.json({
              status: 'healing_complete',
              message: 'Autonomous healing finished',
              report: result
            });
          } catch {
            res.json({
              status: 'healing_complete',
              message: 'Autonomous healing finished',
              output: stdout
            });
          }
        } else {
          res.status(500).json({
            status: 'healing_failed',
            error: stderr || 'Healing process failed'
          });
        }
      });
      
      healerProcess.on('error', (error) => {
        console.error('[Aurora Heal] Process error:', error);
        res.status(500).json({
          status: 'healing_error',
          error: error.message
        });
      });
      
    } catch (error: any) {
      console.error('[Aurora Heal] Error:', error);
      res.status(500).json({ 
        status: 'healing_error',
        error: error.message || 'Healing failed'
      });
    }
  });

  // Note: Conversation memory and web search are now handled in server/aurora-chat.ts

  // Chat endpoint - Aurora's autonomous conversational interface
  // Supports both web and terminal clients
  app.post("/api/chat", async (req, res) => {
    try {
      const { message, session_id, client } = req.body;

      if (!message) {
        return res.status(400).json({ error: "Message is required" });
      }

      const sessionId = session_id || 'default';
      const isTerminalClient = client === 'terminal';
      console.log('[Aurora Chat] Received message:', message, 'Session:', sessionId, 'Client:', client || 'web');

      // Store user message in memory
      try {
        const aurora = await import('./aurora-core');
        const core = aurora.default.getInstance();
        if (core.isMemoryEnabled()) {
          await core.storeMemory(message, { 
            session_id: sessionId, 
            client: client || 'web',
            type: 'user_message'
          });
        }
      } catch (memError) {
        console.warn('[Aurora Chat] Memory storage error:', memError);
      }

      const msgLower = message.toLowerCase().trim();
      
      const isDirectAction = msgLower.includes('list files') || 
                             msgLower.includes('read file') ||
                             msgLower.includes('search for') ||
                             msgLower.includes('grep ') ||
                             msgLower.includes('show files') ||
                             msgLower.startsWith('status') ||
                             msgLower.includes('how are you') ||
                             msgLower.includes('what can you do') ||
                             msgLower.includes('check integration') ||
                             msgLower.includes('analyze codebase') ||
                             msgLower.includes('git status') ||
                             msgLower.includes('dependencies') ||
                             msgLower.includes('self debug') ||
                             msgLower.includes('self diagnos') ||
                             msgLower.includes('self analyz') ||
                             msgLower.includes('self analysis') ||
                             (msgLower.includes('broken') && msgLower.includes('file')) ||
                             (msgLower.includes('not working') && msgLower.includes('file')) ||
                             msgLower.includes("what's broken") ||
                             msgLower.includes('what is broken') ||
                             msgLower.includes('check system') ||
                             msgLower.includes('diagnose') ||
                             msgLower.includes('root cause');

      if (isDirectAction) {
        const selectedAEM = selectExecutionMethod(message);
        console.log(`[Aurora] 🖐️ Direct execution with AEM #${selectedAEM.id}: ${selectedAEM.name}`);
        
        const executionContext: ExecutionContext = {
          sessionId,
          capabilities: getCapabilities()
        };
        
        try {
          const result = await executeWithOrchestrator(message, executionContext);
          
          if (result.success && result.output) {
            let response = `**[AEM #${result.aemUsed}: ${result.aemName}]**\n\n${result.output}`;
            
            if (isTerminalClient) {
              response = response
                .replace(/<[^>]*>/g, '')
                .replace(/&nbsp;/g, ' ')
                .replace(/\*\*/g, '');
            }
            
            return res.json({
              ok: true,
              response,
              message: response,
              session_id: sessionId,
              ai_powered: true,
              client: client || 'web',
              aemUsed: { id: result.aemUsed, name: result.aemName },
              executionTime: result.executionTime,
              intent: 'direct_action'
            });
          }
        } catch (execError) {
          console.log('[Aurora] Orchestrator execution failed, falling back to AI backend');
        }
      }

      // Try routing to Aurora AI Backend first
      try {
        const aiResponse = await fetch(`${LUMINAR_V2_URL}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: message,
            session_id: sessionId,
            context: req.body.context || {} 
          }),
          signal: AbortSignal.timeout(2000)
        });

        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          console.log('[Aurora Chat] Routed to Aurora AI Backend successfully');
          
          return res.json({
            ok: true,
            response: aiData.response,
            message: aiData.response,
            session_id: sessionId,
            ai_powered: true,
            client: client || 'web',
            intent: aiData.intent,
            entities: aiData.entities
          });
        }
      } catch (aiError) {
      }

      const isSystemCommand = msgLower.includes('activate tier') || 
                              (msgLower.includes('luminar') && msgLower.includes('nexus') && msgLower.includes('integrate'));

      if (isSystemCommand) {
        try {
          const v2Response = await fetch(`${LUMINAR_V2_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId }),
            signal: AbortSignal.timeout(2000)
          });

          if (v2Response.ok) {
            const v2Data = await v2Response.json();
            console.log('[Aurora Chat] Routed system command to Luminar V2');
            return res.json(v2Data);
          }
        } catch (v2Error) {
        }
      }

      const chatResult = await getChatResponse(message, sessionId, req.body.context);
      let response = typeof chatResult === 'string' ? chatResult : (chatResult as any).response || '';
      const detection = typeof chatResult === 'object' && (chatResult as any).detection ? (chatResult as any).detection : null;
      const aemUsed = typeof chatResult === 'object' && (chatResult as any).aemUsed ? (chatResult as any).aemUsed : null;
      
      if (detection) {
        response = ResponseAdapter.adaptResponse(response, detection);
        console.log(`[Aurora] ✨ Response adapted for: ${detection.type}`);
      }
      
      if (aemUsed) {
        console.log(`[Aurora] 🖐️ Executed with AEM #${aemUsed.id}: ${aemUsed.name}`);
      }
      
      if (isTerminalClient) {
        response = response
          .replace(/<[^>]*>/g, '')
          .replace(/&nbsp;/g, ' ')
          .replace(/&lt;/g, '<')
          .replace(/&gt;/g, '>')
          .replace(/&amp;/g, '&');
      }

      // Store Aurora's response in memory
      try {
        const aurora = await import('./aurora-core');
        const core = aurora.default.getInstance();
        if (core.isMemoryEnabled()) {
          await core.storeMemory(response, { 
            session_id: sessionId, 
            client: client || 'web',
            type: 'aurora_response',
            detection: detection ? detection.type : 'general'
          });
        }
      } catch (memError) {
        console.warn('[Aurora Chat] Memory storage error:', memError);
      }

      res.json({
        ok: true,
        response,
        message: response,
        session_id: sessionId,
        ai_powered: true,
        client: client || 'web',
        aemUsed: aemUsed || undefined,
        intent: detection?.type || 'general_chat'
      });

    } catch (error: any) {
      console.error('[Aurora Chat] Error:', error);
      res.status(500).json({ 
        ok: false, 
        error: "Chat service error",
        message: "I'm having trouble right now. Please try again!"
      });
    }
  });

  app.get("/api/luminar-nexus/status", async (req, res) => {
    try {
      // Check V2 status
      let v2Active = false;
      let v2SystemStatus = null;

      try {
        const v2StatusResponse = await fetch(`${LUMINAR_V2_URL}/api/nexus/status`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });

        if (v2StatusResponse.ok) {
          v2Active = true;
          v2SystemStatus = await v2StatusResponse.json();
        }
      } catch (e) {
        // V2 not running
      }

      const status = {
        v1: {
          active: false,
          location: 'tools/luminar_nexus.py',
          features: ['Server management', 'Chat interface', 'Process control'],
          status: 'Legacy - replaced by V2'
        },
        v2: {
          active: v2Active,
          available: true,
          location: 'tools/luminar_nexus_v2.py',
          version: '2.0.0',
          features: [
            'AI-driven service orchestration',
            'Autonomous healing',
            'Port conflict resolution',
            'Quantum service mesh',
            'Advanced health monitoring',
            'Predictive scaling',
            'Neural anomaly detection'
          ],
          systemStatus: v2SystemStatus
        },
        currentMode: v2Active ? 'V2 Active - Full AI orchestration' : 'V2 Available - Start with python3 tools/luminar_nexus_v2.py',
        recommendation: v2Active ? 'V2 is running with advanced features' : 'Start V2 for AI-driven management'
      };

      res.json(status);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  // ══════════════════════════════════════════════════════════════
  // 🧠 MEMORY SYSTEM API ROUTES
  // ══════════════════════════════════════════════════════════════
  
  // Memory status endpoint
  app.get("/api/memory/status", async (req, res) => {
    try {
      const aurora = await import('./aurora-core');
      const core = aurora.default.getInstance();
      const status = await core.getMemoryStatus();
      res.json(status);
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message,
        status: 'unavailable'
      });
    }
  });

  // Write to memory
  app.post("/api/memory/write", async (req, res) => {
    try {
      const { text, meta, longterm = false } = req.body;

      if (!text || typeof text !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Text is required and must be a string'
        });
      }

      const aurora = await import('./aurora-core');
      const core = aurora.default.getInstance();
      const result = await core.storeMemory(text, meta, longterm);
      
      res.json(result);
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // Query memory
  app.post("/api/memory/query", async (req, res) => {
    try {
      const { query, top_k = 5 } = req.body;

      if (!query || typeof query !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Query is required and must be a string'
        });
      }

      const aurora = await import('./aurora-core');
      const core = aurora.default.getInstance();
      const result = await core.queryMemory(query, top_k);
      
      res.json(result);
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // ================================
  // Memory Fabric v2 API Endpoints
  // ================================

  const { getMemoryFabricClient } = await import('./memory-fabric-client');
  const memoryFabricClient = getMemoryFabricClient();

  // Check Memory Fabric v2 after delay to allow service to start
  setTimeout(async () => {
    const enabled = await memoryFabricClient.checkStatus();
    if (enabled) {
      console.log('[Memory Fabric V2] ✅ Service connected');
    }
    // Silently retry on requests if not available - no warning needed
  }, 5000);

  // Memory Fabric v2 Status
  app.get("/api/memory-fabric/status", async (req, res) => {
    try {
      // Try to connect if not already
      if (!memoryFabricClient.isEnabled()) {
        await memoryFabricClient.checkStatus();
      }

      const status = await memoryFabricClient.getStatus();
      res.json(status);
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message,
        stats: {
          shortTermCount: 0,
          midTermCount: 0,
          longTermCount: 0,
          semanticCount: 0,
          factCount: 0,
          eventCount: 0,
          totalMemories: 0,
          activeProject: 'None',
          sessionId: 'unavailable'
        },
        facts: {},
        shortTerm: [],
        midTerm: [],
        longTerm: [],
        semantic: [],
        events: [],
        conversations: []
      });
    }
  });

  // Get facts
  app.get("/api/memory-fabric/facts", async (req, res) => {
    try {
      const result = await memoryFabricClient.getFacts();
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Get context summary
  app.get("/api/memory-fabric/context", async (req, res) => {
    try {
      const result = await memoryFabricClient.getContext();
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Get integrity hashes
  app.get("/api/memory-fabric/integrity", async (req, res) => {
    try {
      const result = await memoryFabricClient.getIntegrity();
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Get conversation messages
  app.get("/api/memory-fabric/conversation/:conversationId", async (req, res) => {
    try {
      const { conversationId } = req.params;
      const result = await memoryFabricClient.getConversation(conversationId);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Save message to memory
  app.post("/api/memory-fabric/message", async (req, res) => {
    try {
      const { role, content, importance = 0.5, tags = [] } = req.body;

      if (!content || typeof content !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Content is required and must be a string'
        });
      }

      const result = await memoryFabricClient.saveMessage(role, content, importance, tags);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Save fact
  app.post("/api/memory-fabric/fact", async (req, res) => {
    try {
      const { key, value, category = 'general' } = req.body;

      if (!key || typeof key !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Key is required and must be a string'
        });
      }

      const result = await memoryFabricClient.saveFact(key, value, category);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Recall fact
  app.post("/api/memory-fabric/recall", async (req, res) => {
    try {
      const { key } = req.body;

      if (!key || typeof key !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Key is required and must be a string'
        });
      }

      const result = await memoryFabricClient.recallFact(key);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Search semantic memory
  app.post("/api/memory-fabric/search", async (req, res) => {
    try {
      const { query, top_k = 5 } = req.body;

      if (!query || typeof query !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Query is required and must be a string'
        });
      }

      const result = await memoryFabricClient.search(query, top_k);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Set active project
  app.post("/api/memory-fabric/project", async (req, res) => {
    try {
      const { name } = req.body;

      if (!name || typeof name !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Project name is required and must be a string'
        });
      }

      const result = await memoryFabricClient.setProject(name);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Start new conversation
  app.post("/api/memory-fabric/conversation/new", async (req, res) => {
    try {
      const result = await memoryFabricClient.newConversation();
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Create backup
  app.post("/api/memory-fabric/backup", async (req, res) => {
    try {
      const result = await memoryFabricClient.backup();
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Log event
  app.post("/api/memory-fabric/event", async (req, res) => {
    try {
      const { type, detail = {} } = req.body;

      if (!type || typeof type !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Event type is required and must be a string'
        });
      }

      const result = await memoryFabricClient.logEvent(type, detail);
      res.json(result);
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // PWA endpoints
  app.get("/manifest.webmanifest", (req, res) => {
    const manifestPath = path.join(process.cwd(), 'frontend', 'pwa', 'manifest.webmanifest');

    // Check if the file exists
    if (!fs.existsSync(manifestPath)) {
      console.error('[PWA] Manifest file not found at:', manifestPath);
      return res.status(404).json({
        ok: false,
        err: "manifest missing"
      });
    }

    // Set the correct MIME type for PWA manifest
    res.setHeader('Content-Type', 'application/manifest+json');
    res.setHeader('Cache-Control', 'public, max-age=3600'); // Cache for 1 hour

    // Send the manifest file
    res.sendFile(manifestPath);
  });

  app.get("/service-worker.js", (req, res) => {
    const swPath = path.join(process.cwd(), 'frontend', 'pwa', 'service-worker.js');

    // Check if the file exists
    if (!fs.existsSync(swPath)) {
      console.error('[PWA] Service worker file not found at:', swPath);
      return res.status(404).json({
        ok: false,
        err: "sw missing"
      });
    }

    // Set the correct MIME type for JavaScript
    res.setHeader('Content-Type', 'application/javascript');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate'); // Don't cache service worker
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    // Send the service worker file
    res.sendFile(swPath);
  });

  // Aurora-X Universal Code Synthesis endpoints
  app.post("/api/nl/compile_full", (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          message: "prompt is required and must be a non-empty string"
        });
      }

      // Limit prompt length for safety
      if (prompt.length > 5000) {
        return res.status(400).json({
          status: "error",
          error: "Prompt too long",
          message: "Prompt must be less than 5000 characters"
        });
      }

      // Generate run ID
      const runId = `run-${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}`;

      console.log(`[Synthesis] Starting synthesis for run ${runId}: "${prompt.substring(0, 100)}..."`);

      // Execute Python synthesis engine
      const pythonScript = `
import json
import sys
import os
from aurora_x.synthesis.universal_engine import synthesize_universal_sync

# Redirect print output to stderr to keep stdout clean for JSON
class StderrRedirect:
    def write(self, text):
        sys.stderr.write(text)
    def flush(self):
        sys.stderr.flush()

try:
    prompt = ${JSON.stringify(prompt)}
    run_id = ${JSON.stringify(runId)}

    # Temporarily redirect stdout to stderr for status messages
    old_stdout = sys.stdout
    sys.stdout = StderrRedirect()

    # Call the synthesis engine
    result = synthesize_universal_sync(prompt, run_id=run_id)

    # Restore stdout and output JSON result
    sys.stdout = old_stdout

    # Output only the JSON to stdout
    print(json.dumps(result))
    sys.exit(0)
except Exception as e:
    # Restore stdout in case of error
    sys.stdout = sys.__stdout__
    error_result = {
        "status": "error",
        "error": str(e),
        "run_id": run_id,
        "files": [],
        "project_type": "unknown"
    }
    print(json.dumps(error_result))
    sys.exit(1)
`;

      // Execute the Python script
      execFile(PYTHON_CMD, ['-c', pythonScript], {
        cwd: process.cwd(),
        timeout: 60000, // 60 second timeout for synthesis
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      }, (error, stdout, stderr) => {
        if (error && !stdout) {
          console.error(`[Synthesis] Error executing synthesis: ${error.message}`);
          console.error(`[Synthesis] stderr: ${stderr}`);
          return res.status(500).json({
            status: "error",
            error: "Synthesis failed",
            message: error.message,
            details: stderr,
            run_id: runId
          });
        }

        // Log status messages from stderr (if any)
        if (stderr) {
          console.log(`[Synthesis] Status messages: ${stderr}`);
        }

        try {
          // Parse the JSON result from stdout - try to extract JSON if mixed with other text
          let jsonStr = stdout.trim();

          // If stdout contains multiple lines, try to find the JSON line
          const lines = jsonStr.split('\n');
          for (let i = lines.length - 1; i >= 0; i--) {
            const line = lines[i].trim();
            if (line.startsWith('{') && line.endsWith('}')) {
              jsonStr = line;
              break;
            }
          }

          const result = JSON.parse(jsonStr);

          // Log successful synthesis
          console.log(`[Synthesis] Successfully completed synthesis for run ${runId}`);
          console.log(`[Synthesis] Project type: ${result.project_type}, Files: ${result.files?.length || 0}`);

          // Add download URL to the result
          if (result.status === "success" && result.run_id) {
            result.download_url = `/api/projects/${result.run_id}/download`;
          }

          return res.json(result);
        } catch (parseError: any) {
          console.error(`[Synthesis] Error parsing synthesis result: ${parseError.message}`);
          console.error(`[Synthesis] stdout: ${stdout}`);
          console.error(`[Synthesis] stderr: ${stderr}`);

          return res.status(500).json({
            status: "error",
            error: "Failed to parse synthesis result",
            message: parseError.message,
            run_id: runId,
            stdout: stdout.substring(0, 1000), // Include first 1000 chars for debugging
            stderr: stderr.substring(0, 1000)
          });
        }
      });
    } catch (error: any) {
      console.error(`[Synthesis] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // Endpoint to download project ZIP files
  app.get("/api/projects/:runId/download", (req, res) => {
    try {
      const { runId } = req.params;

      // Validate run ID format (should be like run-2025-10-12T15-20-07)
      // Also support older format run-20241012-143539
      if (!runId || !/^run-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}|\d{8}-\d{6})$/.test(runId)) {
        return res.status(400).json({
          error: "Invalid run ID",
          message: "Run ID must be in format run-YYYY-MM-DDTHH-MM-SS or run-YYYYMMDD-HHMMSS"
        });
      }

      // Construct path to the project.zip file
      const zipPath = path.join(process.cwd(), 'runs', runId, 'project.zip');

      // Check if the file exists
      if (!fs.existsSync(zipPath)) {
        console.error(`[Download] ZIP file not found at: ${zipPath}`);
        return res.status(404).json({
          error: "Project not found",
          message: `No project found for run ID: ${runId}`
        });
      }

      // Get file stats for size
      const stats = fs.statSync(zipPath);

      console.log(`[Download] Serving ZIP file for run ${runId}, size: ${stats.size} bytes`);

      // Set appropriate headers for file download
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="${runId}.zip"`);
      res.setHeader('Content-Length', stats.size.toString());
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');

      // Stream the file to the response
      const fileStream = fs.createReadStream(zipPath);

      fileStream.on('error', (streamError) => {
        console.error(`[Download] Error streaming file: ${streamError.message}`);
        if (!res.headersSent) {
          res.status(500).json({
            error: "Download failed",
            message: "Failed to stream the project file"
          });
        }
      });

      fileStream.pipe(res);

      fileStream.on('end', () => {
        console.log(`[Download] Successfully sent ZIP file for run ${runId}`);
      });

    } catch (error: any) {
      console.error(`[Download] Unexpected error: ${error.message}`);
      return res.status(500).json({
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // Aurora-X Adaptive Learning Stats endpoints
  app.get("/api/adaptive_stats", (req, res) => {
    try {
      // Import and access the global scheduler if available
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({
          summary: _global_adaptive_scheduler.summary(),
          iteration: _global_adaptive_scheduler.iteration
        });
      } else {
        return res.json({ summary: {}, iteration: 0 });
      }
    } catch (e) {
      return res.json({ summary: {}, iteration: 0 });
    }
  });

  app.get("/api/seed_bias/history", (req, res) => {
    try {
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({ history: _global_adaptive_scheduler.history });
      } else {
        return res.json({ history: [] });
      }
    } catch (e) {
      return res.json({ history: [] });
    }
  });

  app.get("/api/seed_bias", (req, res) => {
    try {
      const { get_seed_store } = require("../aurora_x/learn");
      const seed_store = get_seed_store();
      const summary = seed_store.get_summary();

      return res.json({
        summary: {
          total_seeds: summary["total_seeds"],
          avg_bias: Math.round(summary["avg_bias"] * 10000) / 10000,
          max_bias: Math.round(summary["max_bias"] * 10000) / 10000,
          min_bias: Math.round(summary["min_bias"] * 10000) / 10000,
          total_updates: summary["total_updates"],
          config: summary["config"]
        },
        top_biases: (summary["top_biases"] || []).map(([key, bias]: [string, number]) => ({
          seed_key: key,
          bias: Math.round(bias * 10000) / 10000
        }))
      });
    } catch (e: any) {
      return res.status(500).json({ error: "Internal error", details: e?.message ?? String(e) });
    }
  });

  // Progress endpoint to serve progress.json data
  app.get("/api/progress", (req, res) => {
    try {
      // Read the progress.json file from the root directory
      const progressPath = path.join(process.cwd(), 'progress.json');

      // Check if the file exists
      if (!fs.existsSync(progressPath)) {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      }

      // Read the file content
      const progressData = fs.readFileSync(progressPath, 'utf-8');

      // Parse the JSON data
      const progressJson = JSON.parse(progressData);

      // Calculate overall percentage
      const tasks = progressJson.tasks || [];
      let totalPercent = 0;
      tasks.forEach((task: any) => {
        let percent = task.percent || 0;
        if (typeof percent === 'string') {
          percent = parseFloat(percent.replace('%', ''));
        }
        totalPercent += percent;
      });
      const overall_percent = Math.round((totalPercent / Math.max(tasks.length, 1)) * 100) / 100;

      // Add calculated fields
      progressJson.overall_percent = overall_percent;
      progressJson.ok = true;

      // Ensure ui_thresholds exist with defaults
      const th = progressJson.ui_thresholds || {};
      progressJson.ui_thresholds = {
        ok: typeof th.ok === 'number' ? th.ok : 90,
        warn: typeof th.warn === 'number' ? th.warn : 60
      };

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      res.setHeader('Access-Control-Max-Age', '86400'); // 24 hours

// Return the progress data with appropriate headers
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Cache-Control', 'public, max-age=5, stale-while-revalidate=10'); // Cache for 5s, allow stale for 10s
      res.setHeader('ETag', `"${Date.now()}"`); // Add ETag for conditional requests
      return res.json(progressJson);

    } catch (error: any) {
      // Handle JSON parsing errors or other read errors
      console.error('[Progress API] Error reading or parsing progress.json:', error);

      // Return appropriate error response
      if (error.code === 'ENOENT') {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      } else if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON"
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to read progress data",
          details: error?.message ?? String(error)
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for CORS
  app.options("/api/progress", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });

  // POST endpoint to update task percentage
  app.post("/api/progress/task_percent", (req, res) => {
    try {
      const { task_id, percentage } = req.body;

      // Validate inputs
      if (!task_id || typeof task_id !== 'string') {
        return res.status(400).json({
          error: "Invalid request",
          message: "task_id is required and must be a string"
        });
      }

      if (percentage === undefined || percentage === null || typeof percentage !== 'number') {
        return res.status(400).json({
          error: "Invalid request", 
          message: "percentage is required and must be a number"
        });
      }

      if (percentage < 0 || percentage > 100) {
        return res.status(400).json({
          error: "Invalid percentage",
          message: "Percentage must be between 0 and 100"
        });
      }

      // Read the progress.json file
      const progressPath = path.join(process.cwd(), 'progress.json');

      if (!fs.existsSync(progressPath)) {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      }

      // Parse the current data
      const progressData = fs.readFileSync(progressPath, 'utf-8');
      const progressJson = JSON.parse(progressData);

      // Find the task to update
      const tasks = progressJson.tasks || [];
      const taskIndex = tasks.findIndex((t: any) => t.id === task_id);

      if (taskIndex === -1) {
        return res.status(404).json({
          error: "Task not found",
          message: `No task found with ID: ${task_id}`
        });
      }

      // Update the task
      const task = tasks[taskIndex];
      const oldPercent = task.percent;
      const oldStatus = task.status;

      task.percent = percentage;

      // Auto-update status based on percentage
      if (percentage === 100) {
        task.status = "complete";
      } else if (percentage > 0) {
        if (oldStatus === "not-started" || oldStatus === "pending") {
          task.status = "in-progress";
        }
        // Keep existing in-progress or in-development status
      } else {
        // 0% means not started
        task.status = "not-started";
      }

      // Update the updated_utc timestamp
      progressJson.updated_utc = new Date().toISOString();

      // Write back to file
      fs.writeFileSync(progressPath, JSON.stringify(progressJson, null, 2));

      console.log(`[Progress Update] Task ${task_id}: ${oldPercent}% → ${percentage}% (status: ${oldStatus} → ${task.status})`);

      // Asynchronously refresh README badges after successful update
      // This runs in the background and doesn't block the API response
      refreshReadmeBadges().catch((error) => {
        console.error('[Progress Update] Badge refresh failed:', error);
        // Don't throw - let the API response succeed even if badge refresh fails
      });

      // Calculate new overall percentage
      let totalPercent = 0;
      tasks.forEach((t: any) => {
        let percent = t.percent || 0;
        if (typeof percent === 'string') {
          percent = parseFloat(percent.replace('%', ''));
        }
        totalPercent += percent;
      });
      const overall_percent = Math.round((totalPercent / Math.max(tasks.length, 1)) * 100) / 100;

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return success response with updated data
      return res.json({
        success: true,
        task_id: task_id,
        old_percentage: oldPercent,
        new_percentage: percentage,
        old_status: oldStatus,
        new_status: task.status,
        overall_percent: overall_percent,
        updated_utc: progressJson.updated_utc,
        message: `Successfully updated task ${task_id} to ${percentage}%`
      });

    } catch (error: any) {
      console.error('[Progress Update API] Error updating task percentage:', error);

      if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON"
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to update task percentage",
          details: error?.message ?? String(error)
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for task_percent endpoint
  app.options("/api/progress/task_percent", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });

  // POST endpoint to recompute progress data, regenerate task lists and badges
  app.post("/api/progress/recompute", async (req, res) => {
    // Track operation results
    let timestampUpdated = false;
    let taskListRegenerated = false;
    let badgesRefreshed = false;
    let gitOperations = false;
    let updatedTimestamp: string | undefined;
    let errors: string[] = [];
    let hasAnySuccess = false;

    try {
      console.log('[Progress Recompute] Starting progress recomputation...');

      // Step 1: Update the timestamp in progress.json (CRITICAL - fail fast if this fails)
      const progressPath = path.join(process.cwd(), 'progress.json');

      if (!fs.existsSync(progressPath)) {
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist",
          operations_performed: {
            timestamp_updated: false,
            task_list_regenerated: false,
            badges_refreshed: false,
            git_operations: false
          }
        });
      }

      try {
        // Read and update the progress.json file
        const progressData = fs.readFileSync(progressPath, 'utf-8');
        const progressJson = JSON.parse(progressData);
        updatedTimestamp = new Date().toISOString();
        progressJson.updated_utc = updatedTimestamp;

        // Write the updated timestamp back to file
        fs.writeFileSync(progressPath, JSON.stringify(progressJson, null, 2));
        timestampUpdated = true;
        hasAnySuccess = true;
        console.log('[Progress Recompute] Updated timestamp in progress.json to:', updatedTimestamp);
      } catch (timestampError: any) {
        console.error('[Progress Recompute] Failed to update timestamp:', timestampError);
        errors.push(`Timestamp update failed: ${timestampError.message}`);

        // This is a critical error - fail fast
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

        return res.status(500).json({
          error: "Critical operation failed",
          message: "Failed to update progress.json timestamp",
          details: timestampError.message,
          operations_performed: {
            timestamp_updated: false,
            task_list_regenerated: false,
            badges_refreshed: false,
            git_operations: false
          }
        });
      }

      // Step 2: Run update_progress.py to regenerate MASTER_TASK_LIST.md and progress_export.csv
      const updateProgressScriptPath = path.join(process.cwd(), 'tools', 'update_progress.py');

      if (fs.existsSync(updateProgressScriptPath)) {
        console.log('[Progress Recompute] Running update_progress.py...');

        try {
          await new Promise<void>((resolve, reject) => {
            execFile(PYTHON_CMD, [updateProgressScriptPath], {
              cwd: process.cwd(),
              timeout: 30000, // 30 second timeout
              maxBuffer: 1024 * 1024 * 5, // 5MB buffer
            }, (error, stdout, stderr) => {
              if (error) {
                // Check exit code - non-zero means failure
                if (error.code && error.code !== 0) {
                  console.error('[Progress Recompute] update_progress.py failed with exit code:', error.code);
                  console.error('[Progress Recompute] Error:', error.message);
                  if (stderr) console.error('[Progress Recompute] stderr:', stderr);
                  reject(new Error(`update_progress.py failed with exit code ${error.code}: ${error.message}`));
                  return;
                }
                // If error but no exit code, still treat as failure
                console.error('[Progress Recompute] Error running update_progress.py:', error.message);
                reject(error);
                return;
              }

              // Check for error indicators in stderr (excluding [OK])
              if (stderr && !stderr.includes('[OK]') && stderr.trim() !== '') {
                console.error('[Progress Recompute] update_progress.py stderr:', stderr);
                // Don't fail on stderr warnings, only if there was an actual error
              }

              if (stdout) {
                console.log('[Progress Recompute] update_progress.py output:', stdout);
              }

              console.log('[Progress Recompute] Successfully ran update_progress.py');
              resolve();
            });
          });
          taskListRegenerated = true;
          hasAnySuccess = true;
        } catch (scriptError: any) {
          console.error('[Progress Recompute] Failed to regenerate task list:', scriptError);
          errors.push(`Task list regeneration failed: ${scriptError.message}`);
          // Continue with other operations
        }
      } else {
        console.log('[Progress Recompute] update_progress.py not found - skipping task list generation');
        // File doesn't exist, so we didn't run it, don't mark as success
      }

      // Step 3: Run patch_readme_progress.py to refresh README badges
      const patchReadmeScriptPath = path.join(process.cwd(), 'tools', 'patch_readme_progress.py');

      if (fs.existsSync(patchReadmeScriptPath)) {
        console.log('[Progress Recompute] Running patch_readme_progress.py...');

        try {
          await new Promise<void>((resolve, reject) => {
            execFile(PYTHON_CMD, [patchReadmeScriptPath], {
              cwd: process.cwd(),
              timeout: 10000, // 10 second timeout
              maxBuffer: 1024 * 1024, // 1MB buffer
            }, (error, stdout, stderr) => {
              if (error) {
                // Check exit code - non-zero means failure
                if (error.code && error.code !== 0) {
                  console.error('[Progress Recompute] patch_readme_progress.py failed with exit code:', error.code);
                  console.error('[Progress Recompute] Error:', error.message);
                  if (stderr) console.error('[Progress Recompute] stderr:', stderr);
                  reject(new Error(`patch_readme_progress.py failed with exit code ${error.code}: ${error.message}`));
                  return;
                }
                // If error but no exit code, still treat as failure
                console.error('[Progress Recompute] Error running patch_readme_progress.py:', error.message);
                reject(error);
                return;
              }

              // Check for error indicators in stderr (excluding [OK])
              if (stderr && !stderr.includes('[OK]') && stderr.trim() !== '') {
                console.error('[Progress Recompute] patch_readme_progress.py stderr:', stderr);
                // Don't fail on stderr warnings
              }

              if (stdout && stdout.includes('[OK]')) {
                console.log('[Progress Recompute] README badges updated successfully');
              }

              resolve();
            });
          });
          badgesRefreshed = true;
          hasAnySuccess = true;
        } catch (badgeError: any) {
          console.error('[Progress Recompute] Failed to refresh badges:', badgeError);
          errors.push(`Badge refresh failed: ${badgeError.message}`);
          // Continue with other operations
        }
      } else {
        console.log('[Progress Recompute] patch_readme_progress.py not found - skipping badge refresh');
        // File doesn't exist, so we didn't run it, don't mark as success
      }

      // Step 4: Optionally commit and push changes if AURORA_AUTO_GIT is enabled
      const autoGit = process.env.AURORA_AUTO_GIT;
      const shouldAutoCommit = autoGit && ['1', 'true', 'yes', 'on'].includes(autoGit.toLowerCase());

      if (shouldAutoCommit) {
        console.log('[Progress Recompute] Auto-git enabled, committing and pushing changes...');

        // Add specific files
        const filesToAdd = [
          'progress.json',
          'MASTER_TASK_LIST.md', 
          'progress_export.csv',
          'README.md'
        ];

        // Check which files exist and add them
        const existingFiles = filesToAdd.filter(file => 
          fs.existsSync(path.join(process.cwd(), file))
        );

        if (existingFiles.length > 0) {
          let gitAddSuccess = false;
          let gitCommitSuccess = false;
          let gitPushSuccess = false;

          // Add files to git
          try {
            await new Promise<void>((resolve, reject) => {
              execFile('git', ['add', ...existingFiles], {
                cwd: process.cwd(),
                timeout: 5000,
              }, (error, stdout, stderr) => {
                if (error) {
                  console.error('[Progress Recompute] Error adding files to git:', error.message);
                  reject(new Error(`Git add failed: ${error.message}`));
                  return;
                }
                console.log('[Progress Recompute] Added files to git:', existingFiles.join(', '));
                resolve();
              });
            });
            gitAddSuccess = true;
          } catch (gitError: any) {
            console.error('[Progress Recompute] Git add operation failed:', gitError);
            errors.push(`Git add failed: ${gitError.message}`);
          }

          // Create commit (only if add succeeded)
          if (gitAddSuccess) {
            try {
              await new Promise<void>((resolve, reject) => {
                execFile('git', ['commit', '-m', 'chore(progress): recompute via API'], {
                  cwd: process.cwd(),
                  timeout: 5000,
                }, (error, stdout, stderr) => {
                  if (error) {
                    // Check if it's just "nothing to commit" which is not really an error
                    if (error.message.includes('nothing to commit')) {
                      console.log('[Progress Recompute] Nothing to commit, working tree clean');
                      resolve();  // This is OK, not an error
                    } else {
                      console.error('[Progress Recompute] Error creating commit:', error.message);
                      reject(new Error(`Git commit failed: ${error.message}`));
                    }
                    return;
                  }
                  console.log('[Progress Recompute] Created commit successfully');
                  resolve();
                });
              });
              gitCommitSuccess = true;
            } catch (gitError: any) {
              console.error('[Progress Recompute] Git commit operation failed:', gitError);
              errors.push(`Git commit failed: ${gitError.message}`);
            }
          }

          // Push to remote (only if commit succeeded)
          if (gitCommitSuccess) {
            try {
              await new Promise<void>((resolve, reject) => {
                execFile('git', ['push'], {
                  cwd: process.cwd(),
                  timeout: 15000, // Give push more time
                }, (error, stdout, stderr) => {
                  if (error) {
                    console.error('[Progress Recompute] Error pushing to remote:', error.message);
                    reject(new Error(`Git push failed: ${error.message}`));
                    return;
                  }
                  console.log('[Progress Recompute] Pushed changes to remote repository');
                  resolve();
                });
              });
              gitPushSuccess = true;
            } catch (gitError: any) {
              console.error('[Progress Recompute] Git push operation failed:', gitError);
              errors.push(`Git push failed: ${gitError.message}`);
            }
          }

          // Git operations succeeded if all attempted operations succeeded
          gitOperations = gitAddSuccess && gitCommitSuccess && gitPushSuccess;
          if (gitOperations) {
            hasAnySuccess = true;
          }
        } else {
          console.log('[Progress Recompute] No files to commit');
          // No files to commit, not a failure
        }
      } else {
        console.log('[Progress Recompute] Auto-git disabled, skipping commit and push');
        // Git was disabled, not a failure
      }

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Determine response status based on results
      const allCriticalSucceeded = timestampUpdated;
      const anyOperationFailed = errors.length > 0;

      // If we have any errors but also some successes, it's a partial success
      if (anyOperationFailed && hasAnySuccess) {
        // Partial success - some operations succeeded, some failed
        return res.status(207).json({  // 207 Multi-Status for partial success
          success: false,
          partial_success: true,
          message: "Progress data partially recomputed - some operations failed",
          updated_utc: updatedTimestamp,
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: errors
        });
      } else if (anyOperationFailed) {
        // Complete failure
        return res.status(500).json({
          success: false,
          error: "Operation failed",
          message: "Failed to recompute progress data",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: errors
        });
      } else {
        // Complete success
        return res.json({
          success: true,
          message: "Progress data recomputed successfully",
          updated_utc: updatedTimestamp,
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: shouldAutoCommit ? gitOperations : false
          }
        });
      }

    } catch (error: any) {
      console.error('[Progress Recompute] Unexpected error:', error);

      // Set CORS headers even on error
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return error response with operation status
      if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: [...errors, error.message]
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to recompute progress data",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: [...errors, error?.message ?? String(error)]
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for recompute endpoint
  app.options("/api/progress/recompute", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });


  // System diagnostics endpoint
  app.get("/api/diagnostics", async (_req, res) => {
    try {
      const diagnostics: any = {
        status: "ok",
        timestamp: new Date().toISOString(),
        services: {}
      };

      // Check database
      try {
        const recentItems = await corpusStorage.getRecent(1);
        diagnostics.services.database = "connected";
        diagnostics.corpus_count = recentItems.length;
      } catch (e) {
        diagnostics.services.database = "error";
        diagnostics.status = "degraded";
      }

      // Check WebSocket
      diagnostics.services.websocket = wsServer ? "active" : "inactive";

      // Check Bridge (Aurora Nexus V3 - using embedded mode, always connected)
      // Bridge is now integrated directly in the application, no external dependency
      diagnostics.services.bridge = "connected";
      diagnostics.bridge_mode = "embedded";

      // Check progress system
      try {
        const progressPath = path.join(process.cwd(), 'progress.json');
        if (fs.existsSync(progressPath)) {
          const progressData = JSON.parse(fs.readFileSync(progressPath, 'utf-8'));
          diagnostics.services.progress = "ok";
          diagnostics.progress_tasks = progressData.tasks?.length || 0;
        } else {
          diagnostics.services.progress = "missing";
        }
      } catch (e) {
        diagnostics.services.progress = "error";
      }

      res.json(diagnostics);
    } catch (error: any) {
      res.status(500).json({
        status: "error",
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Aurora AI Backend health check proxy
  app.get("/api/aurora-ai/health", async (req, res) => {
    try {
      const response = await fetch(`${LUMINAR_V2_URL}/healthz`, {
        signal: AbortSignal.timeout(5000)
      });
      
      if (response.ok) {
        const data = await response.json();
        return res.json({
          status: "ok",
          aurora_ai_backend: data,
          message: "Aurora AI Backend is accessible"
        });
      } else {
        return res.status(503).json({
          status: "degraded",
          message: "Aurora AI Backend returned non-OK status"
        });
      }
    } catch (error: any) {
      return res.status(503).json({
        status: "unavailable",
        message: "Aurora AI Backend is not reachable",
        error: error.message
      });
    }
  });

  // Health check endpoint for auto-updater monitoring
  app.get("/healthz", async (req, res) => {
    const providedToken = req.query.token as string | undefined;

    // Check token authentication if token is provided
    if (providedToken !== undefined && providedToken !== AURORA_HEALTH_TOKEN) {
      return res.status(401).json({
        error: "Unauthorized",
        message: "Invalid health check token"
      });
    }

    // Calculate uptime in seconds
    const uptimeSeconds = Math.floor((Date.now() - serverStartTime) / 1000);

    // Check database connection status
    let databaseStatus = "disconnected";
    let databaseError: string | undefined;
    try {
      // Attempt to query database to check if it's connected
      // Properly await the async operation
      const testQuery = await corpusStorage.getRecent(1);
      databaseStatus = "connected";
    } catch (e: any) {
      databaseStatus = "disconnected";
      databaseError = e?.message ?? String(e);
      console.error("[Health Check] Database connection failed:", databaseError);
    }

    // Check WebSocket server status more thoroughly
    let websocketStatus = "inactive";
    let websocketDetails: any = {};
    if (wsServer) {
      try {
        // Check if the WebSocket server is properly initialized and listening
        const wsServerInternal = wsServer as any;
        if (wsServerInternal.wss) {
          // Check if WebSocket server has clients property (indicates it's listening)
          websocketStatus = "active";
          // Add more detailed status if available
          if (wsServerInternal.wss.clients) {
            websocketDetails.clientCount = wsServerInternal.wss.clients.size;
          }
          // Check if server is in listening state
          if (wsServerInternal.wss.listening !== false) {
            websocketDetails.listening = true;
          }
        }
      } catch (e) {
        console.error("[Health Check] WebSocket status check failed:", e);
        websocketStatus = "error";
      }
    }

    // Get version from package.json
    let version = "1.0.0";
    try {
      const packageJson = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf-8'));
      version = packageJson.version || "1.0.0";
    } catch (e) {
      console.error("[Health Check] Failed to read package.json:", e);
    }

    // Determine overall health status
    const isHealthy = databaseStatus === "connected" && 
                     (websocketStatus === "active" || websocketStatus === "inactive"); // inactive is ok if not initialized

    const overallStatus = isHealthy ? "ok" : "unhealthy";
    const statusCode = isHealthy ? 200 : 503;

    // Build response object
    const response: any = {
      status: overallStatus,
      service: "Aurora-X",
      version: version,
      timestamp: new Date().toISOString(),
      uptime: uptimeSeconds,
      components: {
        database: databaseStatus,
        websocket: websocketStatus
      }
    };

    // Add error details if unhealthy
    if (!isHealthy) {
      response.errors = [];
      if (databaseStatus === "disconnected") {
        response.errors.push({
          component: "database",
          message: databaseError || "Database connection failed"
        });
      }
      if (websocketStatus === "error") {
        response.errors.push({
          component: "websocket",
          message: "WebSocket server error"
        });
      }
    }

    // Add WebSocket details if available
    if (Object.keys(websocketDetails).length > 0) {
      response.components.websocketDetails = websocketDetails;
    }

    // Return health check response with appropriate status code
    return res.status(statusCode).json(response);
  });

  // Self-learning daemon state
  let selfLearningProcess: any = null;
  let selfLearningStats = {
    started_at: null as string | null,
    last_activity: null as string | null,
    run_count: 0,
  };

  // Self-learning default configuration
  const SELF_LEARNING_DEFAULT_MAX_ITERS = 50;
  const SELF_LEARNING_DEFAULT_BEAM = 20;

  // Auto-restart self-learning if it was running before (based on PID file)
  const pidPath = path.join(process.cwd(), '.self_learning.pid');
  if (fs.existsSync(pidPath)) {
    console.log('[Self-Learning] Detected previous PID file, checking if process is still running...');
    const pidStr = fs.readFileSync(pidPath, 'utf-8').trim();
    const pid = parseInt(pidStr);

    let processRunning = false;
    if (pid) {
      try {
        process.kill(pid, 0); // Check if process exists
        processRunning = true;
        console.log(`[Self-Learning] Process ${pid} is still running`);
      } catch (e: any) {
        if (e.code === 'ESRCH') {
          console.log(`[Self-Learning] Process ${pid} not found, will auto-restart`);
        }
      }
    }

    // If process not running, auto-restart with default settings
    if (!processRunning) {
      setTimeout(() => {
        console.log('[Self-Learning] Auto-starting daemon after server boot...');
        const interval = 15; // Default 15 seconds

        selfLearningProcess = spawn(PYTHON_CMD, [
          '-m', 'aurora_x.self_learn',
          '--sleep', interval.toString(),
          '--max-iters', SELF_LEARNING_DEFAULT_MAX_ITERS.toString(),
          '--beam', SELF_LEARNING_DEFAULT_BEAM.toString()
        ], {
          cwd: process.cwd(),
          detached: true,
          stdio: ['ignore', 'ignore', 'ignore']
        });

        selfLearningProcess.unref();
        fs.writeFileSync(pidPath, selfLearningProcess.pid?.toString() || '');

        selfLearningStats.started_at = new Date().toISOString();
        selfLearningStats.last_activity = new Date().toISOString();

        console.log(`[Self-Learning] Auto-started with PID ${selfLearningProcess.pid}`);
      }, 2000); // Wait 2 seconds after server boot
    }
  }

  // Self-learning status endpoint
  app.get("/api/self-learning/status", (req, res) => {
    const running = selfLearningProcess !== null;

    // Read the state file to get current run count
    let currentRunCount = selfLearningStats.run_count || 0;
    if (running) {
      try {
        const stateFile = path.join(process.cwd(), '.self_learning_state.json');
        if (fs.existsSync(stateFile)) {
          const state = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
          currentRunCount = state.run_count || 0;
          // Update our cached stats
          selfLearningStats.run_count = currentRunCount;
          selfLearningStats.last_activity = state.last_run || selfLearningStats.last_activity;
        }
      } catch (e) {
        console.error('[Self-Learning] Error reading state file:', e);
      }
    }

    return res.json({
      running,
      message: running 
        ? "Self-learning daemon is running"
        : "Self-learning daemon is stopped",
      stats: running ? {
        ...selfLearningStats,
        run_count: currentRunCount
      } : undefined
    });
  });

  // Start self-learning daemon
  app.post("/api/self-learning/start", (req, res) => {
    if (selfLearningProcess) {
      return res.status(400).json({
        error: "Already running",
        message: "Self-learning daemon is already active"
      });
    }

    try {
      const { sleepInterval = 15 } = req.body;
      const interval = Math.max(5, Math.min(3600, sleepInterval)); // Clamp between 5s and 1h

      console.log(`[Self-Learning] Starting daemon with ${interval}s interval...`);

      // Start as detached background process
      selfLearningProcess = spawn(PYTHON_CMD, [
        '-m', 'aurora_x.self_learn',
        '--sleep', interval.toString(),
        '--max-iters', SELF_LEARNING_DEFAULT_MAX_ITERS.toString(),
        '--beam', SELF_LEARNING_DEFAULT_BEAM.toString()
      ], {
        cwd: process.cwd(),
        detached: true,  // Run independently
        stdio: ['ignore', 'ignore', 'ignore']  // Fully detached
      });

      // Unref so it can run independently
      selfLearningProcess.unref();

      // Store PID for later management
      const pidPath = path.join(process.cwd(), '.self_learning.pid');
      fs.writeFileSync(pidPath, selfLearningProcess.pid?.toString() || '');

      selfLearningStats.started_at = new Date().toISOString();
      selfLearningStats.last_activity = new Date().toISOString();
      selfLearningStats.run_count = 0;

      console.log(`[Self-Learning] Daemon started successfully with PID ${selfLearningProcess.pid}`);

      return res.json({
        status: "started",
        message: `Self-learning daemon started successfully (runs every ${interval} seconds)`,
        stats: selfLearningStats,
        interval: interval
      });
    } catch (error: any) {
      console.error('[Self-Learning] Failed to start:', error);
      return res.status(500).json({
        error: "Failed to start",
        message: error.message
      });
    }
  });

  // Stop self-learning daemon
  app.post("/api/self-learning/stop", (req, res) => {
    try {
      console.log('[Self-Learning] Stopping daemon...');

      const pidPath = path.join(process.cwd(), '.self_learning.pid');

      // Try to read PID from file
      let pid: number | null = null;
      if (fs.existsSync(pidPath)) {
        const pidStr = fs.readFileSync(pidPath, 'utf-8').trim();
        pid = parseInt(pidStr);
      } else if (selfLearningProcess?.pid) {
        pid = selfLearningProcess.pid;
      }

      if (!pid) {
        return res.status(400).json({
          error: "Not running",
          message: "Self-learning daemon is not active"
        });
      }

      // Kill the process directly with SIGTERM, then SIGKILL if needed
      let killed = false;
      try {
        process.kill(pid, 'SIGTERM');
        console.log(`[Self-Learning] Sent SIGTERM to process ${pid}`);

        // Wait a bit and check if it's still running
        setTimeout(() => {
          try {
            process.kill(pid!, 0); // Check if still exists
            // Still running, force kill
            console.log(`[Self-Learning] Process still running, sending SIGKILL to ${pid}`);
            process.kill(pid!, 'SIGKILL');
          } catch (e: any) {
            if (e.code === 'ESRCH') {
              console.log(`[Self-Learning] Process ${pid} terminated successfully`);
            }
          }
        }, 500);

        killed = true;
      } catch (e: any) {
        if (e.code === 'ESRCH') {
          console.log(`[Self-Learning] Process ${pid} not found`);
          killed = true;
        } else {
          throw e;
        }
      }

      // Clean up
      if (fs.existsSync(pidPath)) {
        fs.unlinkSync(pidPath);
      }
      selfLearningProcess = null;

      const finalStats = { ...selfLearningStats };
      selfLearningStats = {
        started_at: null,
        last_activity: null,
        run_count: 0,
      };

      console.log('[Self-Learning] Daemon stopped successfully');

      return res.json({
        status: "stopped",
        message: "Self-learning daemon stopped successfully",
        final_stats: finalStats
      });
    } catch (error: any) {
      console.error('[Self-Learning] Failed to stop:', error);
      return res.status(500).json({
        error: "Failed to stop",
        message: error.message
      });
    }
  });

  // T08 Natural Language Synthesis activation endpoints
  // State storage for T08 (in production, this should be in a database or persistent storage)
  let t08Enabled = false;

  // GET endpoint to fetch current T08 status
  app.get("/api/t08/activate", (req, res) => {
    try {
      return res.json({
        t08_enabled: t08Enabled
      });
    } catch (e: any) {
      console.error("[T08] Error fetching T08 status:", e);
      return res.status(500).json({
        error: "Failed to fetch T08 status",
        details: e?.message ?? String(e)
      });
    }
  });

  // POST endpoint to toggle T08 activation
  app.post("/api/t08/activate", (req, res) => {
    try {
      const { on } = req.body;

      // Validate input
      if (typeof on !== 'boolean') {
        return res.status(400).json({
          error: "Invalid request",
          message: "The 'on' parameter must be a boolean value"
        });
      }

      // Update T08 state
      t08Enabled = on;

      // Log the change
      console.log(`[T08] Natural language synthesis ${on ? 'activated' : 'deactivated'}`);

      // Return success response
      return res.json({
        status: on ? "activated" : "deactivated",
        t08_enabled: t08Enabled
      });
    } catch (e: any) {
      console.error("[T08] Error updating T08 status:", e);
      return res.status(500).json({
        error: "Failed to update T08 status",
        details: e?.message ?? String(e)
      });
    }
  });

  app.post("/api/corpus", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const entry = corpusEntrySchema.parse(req.body);
      corpusStorage.insertEntry(entry);
      return res.json({ ok: true, id: entry.id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  // Corpus API endpoint - Function Library
  app.get("/api/corpus", (req, res) => {
    try {
      // Provide defaults for query parameters
      const queryDefaults = {
        func: undefined,
        limit: 50,
        offset: 0,
        perfectOnly: false,
        minScore: undefined,
        maxScore: undefined,
        startDate: undefined,
        endDate: undefined,
        ...req.query
      };

      const query = corpusQuerySchema.parse(queryDefaults);

      // Debug logging
      console.log("[Corpus API] Query params:", query);

      const items = corpusStorage.getEntries({
        func: query.func,
        limit: query.limit,
        offset: query.offset,
        perfectOnly: query.perfectOnly,
        minScore: query.minScore,
        maxScore: query.maxScore,
        startDate: query.startDate,
        endDate: query.endDate,
      });

      console.log("[Corpus API] Found items:", items.length);
      if (items.length > 0) {
        console.log("[Corpus API] First item:", items[0]);
      }

      return res.json({ items, hasMore: items.length === query.limit });
    } catch (e: any) {
      console.error("[Corpus API] Error fetching corpus entries:", e);
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/top", (req, res) => {
    try {
      const query = topQuerySchema.parse(req.query);
      const items = corpusStorage.getTopByFunc(query.func, query.limit);
      return res.json({ items });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/recent", (req, res) => {
    try {
      const query = recentQuerySchema.parse(req.query);
      const items = corpusStorage.getRecent(query.limit);

      // Transform corpus entries to recent run format for self-learning UI
      const runs = items.map((item: any) => ({
        run_id: item.id,
        timestamp: item.timestamp,
        score: item.score,
        passed: item.passed,
        total: item.total,
      }));

      // Return both 'items' (original) and 'runs' (new format) for backward compatibility
      return res.json({ items, runs });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/corpus/similar", (req, res) => {
    try {
      const query = similarityQuerySchema.parse(req.body);
      const results = corpusStorage.getSimilar(
        query.targetSigKey,
        query.targetPostBow,
        query.limit
      );
      return res.json({ results });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/run-meta", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const meta = runMetaSchema.parse(req.body);
      corpusStorage.insertRunMeta(meta);
      return res.json({ ok: true, run_id: meta.run_id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/run-meta/latest", (req, res) => {
    try {
      const meta = corpusStorage.getLatestRunMeta();
      return res.json({ meta });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/used-seeds", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const seed = usedSeedSchema.parse(req.body);
      const id = corpusStorage.insertUsedSeed(seed);
      return res.json({ ok: true, id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/used-seeds", (req, res) => {
    try {
      const run_id = req.query.run_id as string | undefined;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 200;
      const seeds = corpusStorage.getUsedSeeds({ run_id, limit });
      return res.json({ seeds });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  // Progress tracking endpoints
  app.get("/api/synthesis/progress/:id", (req, res) => {
    try {
      const { id } = req.params;
      const progress = progressStore.getProgress(id);

      if (!progress) {
        return res.status(404).json({ error: "Synthesis not found" });
      }

      return res.json(progress);
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to retrieve progress",
        details: e?.message ?? String(e)
      });
    }
  });

  // Get synthesis result endpoint
  app.get("/api/synthesis/result/:id", (req, res) => {
    try {
      const { id } = req.params;
      const progress = progressStore.getProgress(id);

      if (!progress) {
        return res.status(404).json({ error: "Synthesis not found" });
      }

      if (progress.stage !== "COMPLETE" && progress.stage !== "ERROR") {
        return res.status(202).json({
          message: "Synthesis is still in progress",
          stage: progress.stage,
          percentage: progress.percentage,
          estimatedTimeRemaining: progress.estimatedTimeRemaining
        });
      }

      if (progress.stage === "ERROR") {
        return res.status(500).json({
          error: "Synthesis failed",
          details: progress.error,
          message: progress.message
        });
      }

      // Return the completed synthesis result
      if (!progress.result) {
        return res.status(500).json({ 
          error: "Synthesis completed but no result found",
          message: "This may be a legacy synthesis. Please try again." 
        });
      }

      return res.json({
        synthesis_id: id,
        message: progress.message,
        code: progress.result.code,
        language: progress.result.language,
        function_name: progress.result.functionName,
        description: progress.result.description,
        timestamp: progress.result.timestamp,
        actualDuration: progress.actualDuration,
        complexity: progress.complexity
      });
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to retrieve synthesis result",
        details: e?.message ?? String(e)
      });
    }
  });

  app.post("/api/synthesis/estimate", (req, res) => {
    try {
      const { message } = req.body;

      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      const complexity = progressStore.estimateComplexity(message);
      let estimatedTime: number;

      switch (complexity) {
        case "simple":
          estimatedTime = 7; // 5-10 seconds
          break;
        case "medium":
          estimatedTime = 20; // 15-30 seconds
          break;
        case "complex":
          estimatedTime = 45; // 30-60 seconds
          break;
        default:
          estimatedTime = 15;
      }

      return res.json({
        complexity,
        estimatedTime,
        message: `Estimated time: ${estimatedTime} seconds for ${complexity} synthesis`
      });
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to estimate synthesis time",
        details: e?.message ?? String(e)
      });
    }
  });

  // Natural Language Compilation endpoint - proxy to Aurora-X backend
  app.post("/api/nl/compile", async (req, res) => {
    try {
      const { prompt } = req.body;

      if (!prompt || typeof prompt !== 'string') {
        return res.status(400).json({ 
          status: "error",
          run_id: "",
          files_generated: [],
          message: "Prompt is required and must be a string"
        });
      }

      // Sanitize prompt to prevent shell injection
      const sanitizedPrompt = prompt
        .replace(/[`$()<>|;&\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
        .replace(/\*/g, '')  // Remove wildcards
        .replace(/~/g, '')   // Remove tilde expansion
        .replace(/\[/g, '')  // Remove bracket expansion
        .replace(/\]/g, '')  // Remove bracket expansion
        .replace(/\{/g, '')  // Remove brace expansion  
        .replace(/\}/g, '')  // Remove brace expansion
        .trim();

      console.log(`[NL Compile] Processing prompt: "${sanitizedPrompt}"`);

      // Execute Aurora-X natural language compilation command
      const pythonProcess = spawn(PYTHON_CMD, ['-m', 'aurora_x.main', '--nl', sanitizedPrompt], {
        cwd: process.cwd(),
        timeout: 60000, // 60 second timeout
        shell: false, // Disable shell to prevent injection
        env: { ...process.env }
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Wait for process completion
      const exitCode = await new Promise<number>((resolve, reject) => {
        pythonProcess.on('close', (code) => {
          resolve(code || 0);
        });

        pythonProcess.on('error', (err) => {
          console.error(`[NL Compile] Process error:`, err);
          reject(err);
        });
      });

      console.log(`[NL Compile] Exit code:`, exitCode);
      console.log(`[NL Compile] Output:`, stdout);
      if (stderr) console.log(`[NL Compile] Stderr:`, stderr);

      // Parse output to extract information
      let status = "error";
      let run_id = "";
      let files_generated: string[] = [];
      let message = "Compilation failed";

      // Check if output contains [OK] for success
      if (stdout.includes("[OK]")) {
        status = "success";

        // Extract run ID from patterns like "run-20251012-084111"
        const runIdMatch = stdout.match(/run-\d{8}-\d{6}/);
        if (runIdMatch) {
          run_id = runIdMatch[0];
        }

        // Extract file paths for Flask apps
        const flaskMatch = stdout.match(/Flask app generated at: (runs\/[^\s]+)/);
        if (flaskMatch) {
          files_generated.push(flaskMatch[1]);
          message = "Flask application generated successfully";
        }

        // Extract file paths for v3 functions
        const v3Match = stdout.match(/v3 generated: (runs\/[^\s]+)/);
        if (v3Match) {
          const runPath = v3Match[1];
          // Check for generated files in the run directory
          try {
            const srcDir = path.join(process.cwd(), runPath, 'src');
            if (fs.existsSync(srcDir)) {
              const files = fs.readdirSync(srcDir)
                .filter(file => file.endsWith('.py'))
                .map(file => path.join(runPath, 'src', file));
              files_generated.push(...files);
            }
          } catch (e) {
            console.error(`[NL Compile] Error checking generated files:`, e);
          }
          message = "Function generated successfully";
        }

        // Generic extraction for any "generated at:" pattern
        const genericMatches = Array.from(stdout.matchAll(/generated at: (runs\/[^\s]+)/g));
        for (const match of genericMatches) {
          if (!files_generated.includes(match[1])) {
            files_generated.push(match[1]);
          }
        }

        // If no specific files found but we have a run_id, check the run directory
        if (files_generated.length === 0 && run_id) {
          try {
            const runDir = path.join(process.cwd(), 'runs', run_id);
            if (fs.existsSync(runDir)) {
              const srcDir = path.join(runDir, 'src');
              if (fs.existsSync(srcDir)) {
                const files = fs.readdirSync(srcDir)
                  .filter(file => file.endsWith('.py'))
                  .map(file => path.join('runs', run_id, 'src', file));
                files_generated.push(...files);
              }
            }
          } catch (e) {
            console.error(`[NL Compile] Error scanning run directory:`, e);
          }
        }

        if (files_generated.length === 0 && status === "success") {
          message = "Code generated successfully (check runs directory)";
        }

      } else if (exitCode === 0) {
        // Process completed but no [OK] marker
        status = "warning";
        message = "Compilation completed with warnings";

        // Still try to extract run ID
        const runIdMatch = stdout.match(/run-\d{8}-\d{6}/);
        if (runIdMatch) {
          run_id = runIdMatch[0];
        }
      } else {
        // Process failed
        status = "error";
        message = stderr || stdout || "Compilation failed with no output";
      }

      // Return the response
      return res.json({
        run_id,
        status,
        files_generated,
        message
      });

    } catch (e: any) {
      console.error(`[NL Compile] Error:`, e);
      return res.status(500).json({
        status: "error",
        run_id: "",
        files_generated: [],
        message: e?.message ?? "Internal server error during compilation"
      });
    }
  });

  // OLD synthesis endpoint - now using /api/chat for chat
  // 🆕 Apply synthesis rate limiting
  app.post("/api/synthesis", async (req, res) => {
    try {
      const { message } = req.body;

      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      // Generate synthesis ID and estimate complexity
      const synthesisId = progressStore.generateId();
      const complexity = progressStore.estimateComplexity(message);

      // Create progress entry
      const progress = progressStore.createProgress(synthesisId, complexity);

      // Return synthesis ID immediately for progress tracking
      res.json({
        synthesis_id: synthesisId,
        complexity,
        estimatedTime: progress.estimatedTimeRemaining,
        message: "Synthesis started. Track progress using the synthesis_id."
      });

      // Process synthesis asynchronously
      setTimeout(async () => {
        try {
          // Update progress: ANALYZING
          progressStore.updateProgress(synthesisId, "ANALYZING", 10, "Analyzing request requirements...");
          if (wsServer) {
            wsServer.broadcastProgress(progressStore.getProgress(synthesisId)!);
          }

          // Sanitize message to prevent any shell injection
          const sanitizedMessage = message
            .replace(/[`$()<>|;&\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
            .replace(/\*/g, '')  // Remove wildcards
            .replace(/~/g, '')   // Remove tilde expansion
            .replace(/\[/g, '')  // Remove bracket expansion
            .replace(/\]/g, '')  // Remove bracket expansion
            .replace(/\{/g, '')  // Remove brace expansion  
            .replace(/\}/g, '')  // Remove brace expansion
            .trim();

          console.log(`[Aurora-X] Processing request: "${sanitizedMessage}"`);

          // Update progress: GENERATING
          progressStore.updateProgress(synthesisId, "GENERATING", 30, "Generating code solution...");
          if (wsServer) {
            wsServer.broadcastProgress(progressStore.getProgress(synthesisId)!);
          }

          // Execute Aurora-X with the natural language command using spawn for security
          // Use spawn instead of exec to prevent command injection
          const spawnProcess = spawn(PYTHON_CMD, ['-m', 'aurora_x.main', '--nl', sanitizedMessage], {
            cwd: process.cwd(),
            timeout: 30000, // 30 second timeout
            shell: false, // Explicitly disable shell to prevent injection
            env: { ...process.env } // Pass environment variables
          });

          let stdout = '';
          let stderr = '';

          spawnProcess.stdout.on('data', (data) => {
            stdout += data.toString();
            // Update progress as we receive output
            progressStore.updateProgress(synthesisId, "GENERATING", 50, "Processing synthesis output...");
            if (wsServer) {
              wsServer.broadcastProgress(progressStore.getProgress(synthesisId)!);
            }
          });

          spawnProcess.stderr.on('data', (data) => {
            stderr += data.toString();
          });

        // Wait for the process to complete
        await new Promise<void>((resolve, reject) => {
          spawnProcess.on('close', (code) => {
            if (code !== 0 && code !== null) {
              console.error(`[Aurora-X] Process exited with code ${code}`);
              reject(new Error(`Aurora-X synthesis failed with exit code ${code}`));
            } else {
              resolve();
            }
          });

          spawnProcess.on('error', (err) => {
            console.error(`[Aurora-X] Process error:`, err);
            reject(err);
          });
        });

        console.log(`[Aurora-X] Command output:`, stdout);
        if (stderr) console.log(`[Aurora-X] Command stderr:`, stderr);

        // Find the latest run directory with proper validation
        const runsDir = path.join(process.cwd(), 'runs');

        // Pattern for valid run directories: run-YYYYMMDD-HHMMSS
        const runDirPattern = /^run-\d{8}-\d{6}$/;

        const runDirs = fs.readdirSync(runsDir)
          .filter(name => {
            // Validate directory name format
            if (!runDirPattern.test(name)) {
              return false;
            }

            // Check if it's actually a directory
            const dirPath = path.join(runsDir, name);
            try {
              const stats = fs.statSync(dirPath);
              if (!stats.isDirectory()) {
                return false;
              }

              // Verify the directory contains a src/ subdirectory
              const srcDir = path.join(dirPath, 'src');
              if (!fs.existsSync(srcDir) || !fs.statSync(srcDir).isDirectory()) {
                console.log(`[Aurora-X] Skipping ${name}: no valid src/ directory found`);
                return false;
              }

              return true;
            } catch (e) {
              console.error(`[Aurora-X] Error checking directory ${name}:`, e);
              return false;
            }
          })
          .map(name => ({
            name,
            path: path.join(runsDir, name),
            time: fs.statSync(path.join(runsDir, name)).mtime.getTime()
          }))
          .sort((a, b) => b.time - a.time);

        if (runDirs.length === 0) {
          throw new Error("No valid synthesis runs found with src/ directory");
        }

        const latestRun = runDirs[0];
        console.log(`[Aurora-X] Latest valid run: ${latestRun.name}`);

        // Read the generated source code
        let code = "";
        let functionName = "";
        let description = "";

        const srcDir = path.join(latestRun.path, 'src');
        if (fs.existsSync(srcDir)) {
          const srcFiles = fs.readdirSync(srcDir)
            .filter(file => file.endsWith('.py') && !file.startsWith('#') && !file.startsWith('test_'));

          if (srcFiles.length > 0) {
            // Read the first Python file
            const codeFile = path.join(srcDir, srcFiles[0]);
            code = fs.readFileSync(codeFile, 'utf-8');
            functionName = srcFiles[0].replace('.py', '');
            console.log(`[Aurora-X] Read generated code from: ${srcFiles[0]}`);
          }
        }

        // If still no code, check if there's a single file with function name
        if (!code) {
          const allFiles = fs.readdirSync(latestRun.path);
          const pyFiles = allFiles.filter(f => f.endsWith('.py') && !f.startsWith('test_'));
          if (pyFiles.length > 0) {
            const codeFile = path.join(latestRun.path, pyFiles[0]);
            try {
              const fileContent = fs.readFileSync(codeFile, 'utf-8');
              // Verify the file is not empty and contains actual code
              if (fileContent && fileContent.trim().length > 0) {
                code = fileContent;
                functionName = pyFiles[0].replace('.py', '');
              } else {
                console.log(`[Aurora-X] Warning: File ${pyFiles[0]} is empty`);
              }
            } catch (readError) {
              console.error(`[Aurora-X] Error reading file ${pyFiles[0]}:`, readError);
            }
          }
        }

        // Extract function description from the code if available
        const docstringMatch = code.match(/"""([\s\S]*?)"""/);
        if (docstringMatch) {
          description = docstringMatch[1].trim();
        }

        // Reject placeholder output instead of fabricating code.
        if (code && (code.includes('todo_spec') || code.includes('def todo_spec()'))) {
          throw new Error("Synthesis output contains placeholder markers");
        }

        // Prepare response message
        let responseMessage = `Aurora-X has synthesized the "${functionName}" function. `;
        if (description) {
          responseMessage += description;
        } else {
          responseMessage += `This function was generated based on your request: "${message}"`;
        }

        if (!code) {
          throw new Error("No synthesized code produced");
        }

        // Update progress store with COMPLETE status and synthesis result
        progressStore.updateProgress(
          synthesisId, 
          "COMPLETE", 
          100, 
          responseMessage,
          {
            code: code,
            language: "python",
            functionName: functionName,
            description: description || `Function generated based on request: "${message}"`,
            timestamp: new Date().toISOString()
          }
        );

        // Broadcast completion via WebSocket if available
        if (wsServer) {
          wsServer.broadcastProgress(progressStore.getProgress(synthesisId)!);
        }

        console.log(`[Aurora-X] Synthesis completed successfully: ${synthesisId}`);

      } catch (execError: any) {
        console.error(`[Aurora-X] Execution error:`, execError);

        // Mark the synthesis as failed in progress store
        progressStore.markError(synthesisId, execError?.message || "Aurora-X synthesis failed");

        // Broadcast error status via WebSocket if available
        if (wsServer) {
          wsServer.broadcastProgress(progressStore.getProgress(synthesisId)!);
        }

        console.warn(`[Aurora-X] Synthesis failed without fallback for: ${synthesisId}`);
      }
      }, 100); // Execute synthesis asynchronously with 100ms delay
    } catch (error: any) {
      console.error("Chat error:", error);
      res.status(500).json({ 
        error: "Synthesis failed",
        details: error.message,
        output: error.stdout || "",
        stderr: error.stderr || ""
      });
    }
  });

  // Serve the tracker visual HTML
  app.get("/tracker-visual", (req, res) => {
    const trackerPath = path.join(process.cwd(), "tracker_visual.html");
    if (fs.existsSync(trackerPath)) {
      res.sendFile(trackerPath);
    } else {
      res.status(404).send("Tracker visual not found");
    }
  });

  // T09 Domain Router endpoints with unit normalization
  app.post("/api/units", async (req, res) => {
    try {
      const units = await import("./units");
      const { value } = req.body;

      if (!value || typeof value !== "string") {
        return res.status(400).json({ error: "missing 'value'" });
      }

      const [numeric_value, unit] = units.parse_value_with_unit(value);

      if (numeric_value === null) {
        return res.status(422).json({ error: `Could not parse value from: ${value}` });
      }

      const result = units.normalize_to_si(numeric_value, unit);

      return res.json({
        si_value: result.si_value,
        si_unit: result.si_unit,
        original: value,
        original_value: result.original_value,
        original_unit: result.original_unit,
        conversion_factor: result.conversion_factor,
        unit_type: result.unit_type
      });
    } catch (error: any) {
      console.error("[Aurora-X] Units API error:", error);
      return res.status(500).json({
        error: "Failed to process unit conversion",
        details: error?.message
      });
    }
  });

  // Note: The original /api/solve and /api/explain endpoints have been replaced
  // with new versions that directly use aurora_x/generators/solver.py

  // Task graph visualization endpoint
  app.get("/dashboard/graph", (req, res) => {
    const graphHTML = `<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Aurora-X · Master Task Graph</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      background: #03060e;
      color: #e5e9ff;
      font-family: system-ui, -apple-system, sans-serif;
    }
    svg {
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 50% 50%, #101526, #03060e);
    }
    text {
      fill: #fff;
      font-size: 13px;
      text-anchor: middle;
      pointer-events: none;
      user-select: none;
    }
    .node circle {
      stroke: #fff;
      stroke-width: 1.2;
      cursor: pointer;
      transition: all 0.2s;
    }
    .node:hover circle {
      r: 35;
      stroke-width: 2;
      filter: brightness(1.2);
    }
    .node.completed circle {
      fill: #29cc5f;
    }
    .node.inprogress circle {
      fill: #1e90ff;
    }
    .node.pending circle {
      fill: #d93f3f;
    }
    .node.development circle {
      fill: #ffa600;
    }
    .link {
      stroke: #bbb;
      stroke-opacity: .4;
      stroke-width: 1.5;
    }
    .legend {
      position: absolute;
      top: 10px;
      left: 10px;
      color: #fff;
      font-size: 14px;
      background: rgba(0, 0, 0, 0.5);
      padding: 10px;
      border-radius: 8px;
    }
    .legend small {
      display: block;
      margin-top: 5px;
      opacity: 0.8;
    }
    .btn {
      position: absolute;
      top: 10px;
      right: 10px;
      padding: 8px 14px;
      background: #1e90ff;
      color: #fff;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 500;
      transition: background 0.2s;
    }
    .btn:hover {
      background: #1a7fd8;
    }
  </style>
</head>
<body>
  <div class="legend">
    Aurora-X Ultra — Master Dependency Graph<br>
    <small>Green=Complete • Blue=In Progress • Yellow=Development • Red=Pending</small>
    <small style="display:block;margin-top:3px;color:#1e90ff">✏️ Click any node to edit its percentage</small>
  </div>
  <a href="/dashboard" class="btn">← Dashboard</a>
  <svg id="graph"></svg>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    async function render() {
      try {
        const res = await fetch('/api/progress');
        const data = await res.json();
        const tasks = data.tasks || [];

        // Create nodes from tasks data
        const nodes = tasks.map(t => ({
          id: t.id || 'Unknown',
          name: t.name || 'Unknown Task',
          percent: typeof t.percent === 'number' ? t.percent : parseFloat(t.percent) || 0,
          status: t.status,
          group: determineGroup(t)
        }));

        // Function to determine node group/color
        function determineGroup(task) {
          const percent = typeof task.percent === 'number' ? task.percent : parseFloat(task.percent) || 0;

          if (percent >= 100) {
            return 'completed';
          } else if (task.status === 'in-development') {
            return 'development';
          } else if (percent > 0) {
            return 'inprogress';
          } else {
            return 'pending';
          }
        }

        // Create links between consecutive tasks (T01->T02->T03...)
        const links = [];
        for (let i = 1; i < nodes.length; i++) {
          links.push({
            source: nodes[i - 1].id,
            target: nodes[i].id
          });
        }

        // Setup D3 visualization
        const svg = d3.select("#graph");
        const width = window.innerWidth;
        const height = window.innerHeight;

        // Clear previous graph if any
        svg.selectAll("*").remove();

        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
          .force("link", d3.forceLink(links).id(d => d.id).distance(160))
          .force("charge", d3.forceManyBody().strength(-450))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force("collision", d3.forceCollide().radius(35));

        // Create links
        const link = svg.append("g")
          .selectAll("line")
          .data(links)
          .enter()
          .append("line")
          .attr("class", "link");

        // Create nodes
        const node = svg.append("g")
          .selectAll("g")
          .data(nodes)
          .enter()
          .append("g")
          .attr("class", d => "node " + d.group);

        // Add circles to nodes
        node.append("circle")
          .attr("r", 30);

        // Add text labels to nodes
        node.append("text")
          .attr("dy", 5)
          .text(d => d.id);

        // Add click handler to update task percentage
        node.on("click", async (event, d) => {
          const currentPercent = typeof d.percent === 'number' ? d.percent : 0;
          const status = d.group === 'completed' ? 'Completed' :
                        d.group === 'inprogress' ? 'In Progress' :
                        d.group === 'development' ? 'In Development' :
                        'Pending';

          // Show prompt to update percentage
          const newPercentStr = prompt(
            \`Task: \${d.id}\\nName: \${d.name}\\nCurrent Progress: \${currentPercent}%\\nStatus: \${status}\\n\\nEnter new percentage (0-100):\`,
            currentPercent.toString()
          );

          // If user cancelled or entered nothing, do nothing
          if (newPercentStr === null || newPercentStr.trim() === '') {
            return;
          }

          const newPercent = parseFloat(newPercentStr);

          // Validate the input
          if (isNaN(newPercent) || newPercent < 0 || newPercent > 100) {
            alert('Invalid percentage. Please enter a number between 0 and 100.');
            return;
          }

          try {
            // Send update to the API
            const response = await fetch('/api/progress/task_percent', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                task_id: d.id,
                percentage: newPercent
              })
            });

            if (!response.ok) {
              const error = await response.json();
              alert(\`Failed to update task: \${error.message || 'Unknown error'}\`);
              return;
            }

            const result = await response.json();

            // Show success message
            alert(\`✅ Successfully updated task \${d.id} from \${result.old_percentage}% to \${result.new_percentage}%\\n\\nStatus: \${result.old_status} → \${result.new_status}\\nOverall Progress: \${result.overall_percent}%\`);

            // Re-render the graph to show the updated data
            render();

          } catch (error) {
            console.error('Error updating task percentage:', error);
            alert(\`Failed to update task percentage. Please check the console for details.\`);
          }
        });

        // Add drag behavior
        node.call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

        // Update positions on tick
        simulation.on("tick", () => {
          link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

          node
            .attr("transform", d => \`translate(\${d.x}, \${d.y})\`);
        });

        // Drag functions
        function dragstarted(event) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
        }

        function dragged(event) {
          event.subject.fx = event.x;
          event.subject.fy = event.y;
        }

        function dragended(event) {
          if (!event.active) simulation.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
        }

      } catch (error) {
        console.error('Error loading task data:', error);
        alert('Failed to load task data. Please check the console for details.');
      }
    }

    // Render the graph
    render();

    // Auto-refresh every 30 seconds
    setInterval(render, 30000);
  </script>
</body>
</html>`;

    res.setHeader('Content-Type', 'text/html');
    res.send(graphHTML);
  });

  // ========== Natural Language Code Synthesis Endpoints ==========

  // POST endpoint to compile/generate a project from natural language
  app.post("/api/nl/compile_full", async (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        console.log('[Synthesis] Invalid prompt received');
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          details: "prompt is required and must be a non-empty string"
        });
      }

      console.log('[Synthesis] Starting project generation for prompt:', prompt.substring(0, 100) + '...');

      // Call Python synthesis engine
      const result = await new Promise<any>((resolve, reject) => {
        const pythonProcess = spawn(PYTHON_CMD, [
          '-c',
          `
import sys
import json
import asyncio
sys.path.insert(0, '.')
from aurora_x.synthesis.universal_engine import synthesize_universal

async def main():
    try:
        result = await synthesize_universal("""${prompt.replace(/"/g, '\\"').replace(/\n/g, '\\n')}""")
        print(json.dumps(result))
    except Exception as e:
        import traceback
        print(json.dumps({"status": "error", "error": str(e), "traceback": traceback.format_exc()}))

asyncio.run(main())
`
        ], {
          cwd: process.cwd(),
          env: { ...process.env, PYTHONPATH: process.cwd() }
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code !== 0) {
            console.error(`[Synthesis] Python process failed: ${stderr}`);
            reject(new Error(`Synthesis failed with code ${code}: ${stderr}`));
            return;
          }

          try {
            // Parse the JSON output from Python
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (parseError: any) {
            console.error('[Synthesis] Failed to parse Python output:', stdout);
            reject(new Error(`Failed to parse synthesis result: ${parseError.message}`));
          }
        });

        pythonProcess.on('error', (error) => {
          console.error('[Synthesis] Failed to spawn Python process:', error);
          reject(error);
        });
      });

      // Check if synthesis was successful
      if (result.status === 'error') {
        console.error('[Synthesis] Generation failed:', result.error);
        return res.status(500).json({
          status: "error",
          error: "Synthesis failed",
          details: result.error || "Unknown error during synthesis"
        });
      }

      console.log('[Synthesis] Successfully generated project:', {
        run_id: result.run_id,
        project_type: result.project_type,
        files_count: result.files?.length || 0
      });

      // Set CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return the synthesis result
      return res.json({
        status: "success",
        run_id: result.run_id,
        files: result.files || [],
        project_type: result.project_type || "unknown",
        zip_path: result.zip_path || null,
        framework: result.framework || null,
        language: result.language || null,
        features: result.features || [],
        message: `Successfully generated ${result.project_type || 'project'} with ${(result.files || []).length} files`
      });

    } catch (error: any) {
      console.error('[Synthesis] Unexpected error:', error);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        details: error?.message || String(error)
      });
    }
  });

  // Handle OPTIONS preflight requests for synthesis endpoint
  app.options("/api/nl/compile_full", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204);
  });

  // GET endpoint to download generated project ZIP file
  app.get("/api/projects/:run_id/download", (req, res) => {
    try {
      const { run_id } = req.params;

      // Validate run_id format (e.g., run-20251012-123456)
      if (!run_id || !run_id.match(/^run-\d{8}-\d{6}$/)) {
        return res.status(400).json({
          error: "Invalid run ID",
          details: "Run ID must be in format: run-YYYYMMDD-HHMMSS"
        });
      }

      // Build the path to the ZIP file
      const zipPath = path.join(process.cwd(), 'runs', run_id, 'project.zip');

      // Check if the ZIP file exists
      if (!fs.existsSync(zipPath)) {
        console.error(`[Download] ZIP file not found: ${zipPath}`);
        return res.status(404).json({
          error: "Project not found",
          details: `No project found with run ID: ${run_id}`
        });
      }

      // Get file stats for size
      const stats = fs.statSync(zipPath);

      console.log(`[Download] Serving ZIP file: ${zipPath} (${stats.size} bytes)`);

      // Set headers for file download
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="${run_id}-project.zip"`);
      res.setHeader('Content-Length', stats.size.toString());
      res.setHeader('Access-Control-Allow-Origin', '*');

      // Stream the file to the response
      const fileStream = fs.createReadStream(zipPath);
      fileStream.pipe(res);

      fileStream.on('error', (error) => {
        console.error('[Download] Error streaming file:', error);
        if (!res.headersSent) {
          res.status(500).json({
            error: "Download failed",
            details: "Failed to stream the project file"
          });
        }
      });

    } catch (error: any) {
      console.error('[Download] Unexpected error:', error);
      return res.status(500).json({
        error: "Internal server error",
        details: error?.message || String(error)
      });
    }
  });

  // Handle OPTIONS preflight requests for download endpoint
  app.options("/api/projects/:run_id/download", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204);
  });

  // POST endpoint for raw solver results
  app.post("/api/solve", (req, res) => {
    try {
      const { q } = req.body;

      // Validate input
      if (!q || typeof q !== 'string') {
        return res.status(400).json({
          ok: false,
          error: "Invalid request",
          message: "q is required and must be a string"
        });
      }

      // Limit query length for safety
      if (q.length > 1000) {
        return res.status(400).json({
          ok: false,
          error: "Query too long",
          message: "Query must be less than 1000 characters"
        });
      }

      console.log(`[Solver] Processing query: "${q.substring(0, 100)}..."`);

      // Python command to execute the solver
      const pythonCommand = `from aurora_x.generators.solver import solve_text; import json; import sys; q = sys.stdin.read(); print(json.dumps(solve_text(q)))`;

      // Spawn Python process with the query as stdin
      const python = spawn(PYTHON_CMD, ['-c', pythonCommand], {
        cwd: process.cwd(),
        timeout: 5000, // 5 second timeout
      });

      let stdout = '';
      let stderr = '';

      // Collect output
      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Send the query to stdin
      python.stdin.write(q);
      python.stdin.end();

      // Handle process completion
      python.on('close', (code) => {
        if (code !== 0) {
          console.error(`[Solver] Python process exited with code ${code}`);
          console.error(`[Solver] stderr: ${stderr}`);
          return res.status(500).json({
            ok: false,
            error: "Solver execution failed",
            message: `Python process exited with code ${code}`,
            details: stderr
          });
        }

        try {
          // Parse the JSON result
          const result = JSON.parse(stdout.trim());
          console.log(`[Solver] Successfully solved query, task: ${result.task || 'unknown'}`);
          return res.json(result);
        } catch (parseError: any) {
          console.error(`[Solver] Error parsing solver result: ${parseError.message}`);
          console.error(`[Solver] stdout: ${stdout}`);
          return res.status(500).json({
            ok: false,
            error: "Failed to parse solver result",
            message: parseError.message,
            stdout: stdout.substring(0, 500)
          });
        }
      });

      // Handle errors
      python.on('error', (error) => {
        console.error(`[Solver] Failed to spawn Python process: ${error.message}`);
        return res.status(500).json({
          ok: false,
          error: "Failed to execute solver",
          message: error.message
        });
      });

    } catch (error: any) {
      console.error(`[Solver] Unexpected error: ${error.message}`);
      return res.status(500).json({
        ok: false,
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // POST endpoint for formatted solver results
  app.post("/api/solve/pretty", (req, res) => {
    try {
      const { q } = req.body;

      // Validate input
      if (!q || typeof q !== 'string') {
        return res.status(400).json({
          ok: false,
          error: "Invalid request",
          message: "q is required and must be a string"
        });
      }

      // Limit query length for safety
      if (q.length > 1000) {
        return res.status(400).json({
          ok: false,
          error: "Query too long",
          message: "Query must be less than 1000 characters"
        });
      }

      console.log(`[Solver Pretty] Processing query: "${q.substring(0, 100)}..."`);

      // Python command to execute the solver
      const pythonCommand = `from aurora_x.generators.solver import solve_text; import json; import sys; q = sys.stdin.read(); print(json.dumps(solve_text(q)))`;

      // Spawn Python process with the query as stdin
      const python = spawn(PYTHON_CMD, ['-c', pythonCommand], {
        cwd: process.cwd(),
        timeout: 5000, // 5 second timeout
      });

      let stdout = '';
      let stderr = '';

      // Collect output
      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Send the query to stdin
      python.stdin.write(q);
      python.stdin.end();

      // Handle process completion
      python.on('close', (code) => {
        if (code !== 0) {
          console.error(`[Solver Pretty] Python process exited with code ${code}`);
          console.error(`[Solver Pretty] stderr: ${stderr}`);
          return res.status(500).json({
            ok: false,
            error: "Solver execution failed",
            message: `Python process exited with code ${code}`,
            details: stderr
          });
        }

        try {
          // Parse the JSON result
          const result = JSON.parse(stdout.trim());

          if (!result.ok) {
            // Return error as-is for failed results
            return res.json({
              ok: false,
              formatted: result.error || "Unknown error",
              raw: result
            });
          }

          // Format the result based on task type
          let formatted = "";

          if (result.task === "arithmetic") {
            // Format: "2 + 3 * 4 = 14"
            formatted = `${result.input} = ${result.result}`;
          } else if (result.task === "differentiate") {
            // Format: "d/dx(x^3 - 2x^2 + x) = 3x^2 - 4x + 1"
            formatted = `d/dx(${result.input}) = ${result.result}`;
          } else if (result.task === "orbital_period") {
            // Format: "T ≈ 1.51 h (5436 s)"
            const seconds = result.result.period_seconds;
            const hours = seconds / 3600;
            const days = seconds / 86400;

            if (hours < 24) {
              formatted = `T ≈ ${hours.toFixed(2)} h (${Math.round(seconds)} s)`;
            } else if (days < 365) {
              formatted = `T ≈ ${days.toFixed(2)} days (${Math.round(seconds)} s)`;
            } else {
              const years = days / 365.25;
              formatted = `T ≈ ${years.toFixed(2)} years (${days.toFixed(1)} days)`;
            }
          } else {
            // Default formatting
            formatted = result.explanation || JSON.stringify(result.result);
          }

          console.log(`[Solver Pretty] Successfully formatted result: ${formatted}`);

          return res.json({
            ok: true,
            formatted: formatted,
            task: result.task,
            domain: result.domain,
            raw: result
          });

        } catch (parseError: any) {
          console.error(`[Solver Pretty] Error parsing solver result: ${parseError.message}`);
          console.error(`[Solver Pretty] stdout: ${stdout}`);
          return res.status(500).json({
            ok: false,
            error: "Failed to parse solver result",
            message: parseError.message,
            stdout: stdout.substring(0, 500)
          });
        }
      });

      // Handle errors
      python.on('error', (error) => {
        console.error(`[Solver Pretty] Failed to spawn Python process: ${error.message}`);
        return res.status(500).json({
          ok: false,
          error: "Failed to execute solver",
          message: error.message
        });
      });

    } catch (error: any) {
      console.error(`[Solver Pretty] Unexpected error: ${error.message}`);
      return res.status(500).json({
        ok: false,
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // Self-healing status endpoint
  app.get("/api/self-healing/status", async (req, res) => {
    try {
      const aurora = AuroraCore.getInstance();
      const healerStats = aurora.getSelfHealerStats();
      const recentEvents = aurora.getRecentHealingEvents(10);
      const lastEvent = recentEvents[recentEvents.length - 1];

      res.json({
        enabled: healerStats.status === "operational",
        healers: {
          total: healerStats.total,
          active: healerStats.active,
          healing: healerStats.healing,
          cooldown: healerStats.cooldown
        },
        lastHealTime: lastEvent?.endTime ? new Date(lastEvent.endTime).toISOString() : null,
        healsCompleted: healerStats.healsPerformed,
        issuesDetected: recentEvents.length,
        mode: "autonomous"
      });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to get self-healing status", message: error.message });
    }
  });

  // Comparison endpoints for Aurora runs and git history
  app.get("/api/bridge/comparison/commits", async (req, res) => {
    try {
      const currentBranch = await runGit(["rev-parse", "--abbrev-ref", "HEAD"]);
      const log = await runGit(["log", "-20", "--pretty=format:%H|%h|%s"]);
      const commits = log
        .split("\n")
        .filter(Boolean)
        .map((line) => {
          const [hash, short_hash, message] = line.split("|");
          return { hash, short_hash, message };
        });
      res.json({ ok: true, current_branch: currentBranch, commits });
    } catch (error: any) {
      res.status(500).json({ ok: false, error: "commit_query_failed", message: error.message });
    }
  });

  app.get("/api/bridge/comparison/diff", async (req, res) => {
    try {
      const commit1 = typeof req.query.commit1 === "string" ? req.query.commit1 : "";
      const commit2 = typeof req.query.commit2 === "string" ? req.query.commit2 : "";
      const args = commit1 && commit2
        ? ["diff", "--name-status", `${commit1}`, `${commit2}`]
        : ["diff", "--name-status"];
      const diff = await runGit(args);
      const files = diff
        ? diff.split("\n").filter(Boolean).map((line) => {
            const parts = line.split("\t");
            const status = parts[0];
            const file = parts[parts.length - 1];
            const statusText = status.startsWith("A")
              ? "Added"
              : status.startsWith("M")
                ? "Modified"
                : status.startsWith("D")
                  ? "Deleted"
                  : status.startsWith("R")
                    ? "Renamed"
                    : "Changed";
            return { status, file, status_text: statusText };
          })
        : [];
      res.json({ ok: true, files });
    } catch (error: any) {
      res.status(500).json({ ok: false, error: "diff_failed", message: error.message });
    }
  });

  app.get("/api/bridge/comparison/branches", async (req, res) => {
    try {
      const rawBranches = await runGit(["for-each-ref", "refs/heads", "--format=%(refname:short)"]);
      const branches = rawBranches ? rawBranches.split("\n").filter(Boolean) : [];
      const baseBranch = branches.includes("main") ? "main" : branches.includes("master") ? "master" : branches[0] || "";

      const results = [];
      for (const branch of branches) {
        const commitCount = parseInt(await runGit(["rev-list", "--count", branch]), 10) || 0;
        const last = await runGit(["log", "-1", "--pretty=format:%h|%s", branch]);
        const [lastHash, lastMessage] = last.split("|");
        const diff = baseBranch ? await runGit(["diff", "--numstat", `${baseBranch}..${branch}`]) : "";
        let filesChanged = 0;
        let added = 0;
        let deleted = 0;
        for (const line of diff.split("\n").filter(Boolean)) {
          const [addStr, delStr] = line.split("\t");
          filesChanged += 1;
          added += parseInt(addStr, 10) || 0;
          deleted += parseInt(delStr, 10) || 0;
        }
        const messages = await runGit(["log", "-3", "--pretty=format:%s", branch]);
        const uniqueFeatures = messages.split("\n").filter(Boolean);
        const featureCategory = uniqueFeatures.some((msg) => /fix|bug/i.test(msg))
          ? "fix"
          : uniqueFeatures.some((msg) => /perf|opt/i.test(msg))
            ? "performance"
            : uniqueFeatures.some((msg) => /feat|add/i.test(msg))
              ? "feature"
              : "general";
        const churn = added + deleted;
        const improvementScore = Math.max(0, Math.min(100, Math.round((added / Math.max(churn, 1)) * 100)));

        results.push({
          name: branch,
          commit_count: commitCount,
          last_commit: lastHash,
          last_commit_message: lastMessage,
          unique_features: uniqueFeatures,
          file_changes: filesChanged,
          lines_added: added,
          lines_deleted: deleted,
          feature_category: featureCategory,
          improvement_score: improvementScore
        });
      }

      res.json({ ok: true, branches: results });
    } catch (error: any) {
      res.status(500).json({ ok: false, error: "branch_query_failed", message: error.message });
    }
  });

  app.get("/api/bridge/comparison/branch-analysis", async (req, res) => {
    try {
      const branch = typeof req.query.branch === "string" ? req.query.branch : "";
      if (!branch) {
        return res.status(400).json({ ok: false, error: "branch_required" });
      }
      const branches = (await runGit(["for-each-ref", "refs/heads", "--format=%(refname:short)"])).split("\n").filter(Boolean);
      const baseBranch = branches.includes("main") ? "main" : branches.includes("master") ? "master" : branches[0] || "";
      const diff = baseBranch ? await runGit(["diff", "--numstat", `${baseBranch}..${branch}`]) : "";
      const fileChanges = [];
      let added = 0;
      let deleted = 0;
      let testFiles = 0;

      for (const line of diff.split("\n").filter(Boolean)) {
        const [addStr, delStr, file] = line.split("\t");
        const add = parseInt(addStr, 10) || 0;
        const del = parseInt(delStr, 10) || 0;
        added += add;
        deleted += del;
        if (/test|spec/i.test(file || "")) testFiles += 1;
        fileChanges.push({ status: "modified", file, additions: add, deletions: del });
      }

      const messages = await runGit(["log", "-5", "--pretty=format:%s", branch]);
      const messageList = messages.split("\n").filter(Boolean);
      const keyFeatures = messageList.map((msg) => ({
        category: /fix|bug/i.test(msg) ? "fix" : /perf|opt/i.test(msg) ? "performance" : "feature",
        description: msg,
        impact: added + deleted > 500 ? "major" : "minor"
      }));

      const churn = added + deleted;
      const testCoverage = fileChanges.length ? Math.round((testFiles / fileChanges.length) * 100) : 0;
      const codeQualityScore = Math.max(1, Math.min(10, 10 - Math.round(churn / 500)));
      const performanceScore = messageList.some((msg) => /perf|opt/i.test(msg)) ? 8 : 6;
      const maintainability = Math.max(1, Math.min(10, 10 - Math.round(fileChanges.length / 50)));

      res.json({
        ok: true,
        analysis: {
          key_features: keyFeatures,
          quality_metrics: {
            test_coverage: testCoverage,
            code_quality_score: codeQualityScore,
            performance_score: performanceScore,
            maintainability
          },
          file_changes: fileChanges,
          recommendations: {
            summary: churn > 1000 ? "Large change set; consider targeted review and test focus." : "Change set is within normal range.",
            action_items: churn > 1000 ? ["Review high-churn files", "Run full regression tests"] : []
          }
        }
      });
    } catch (error: any) {
      res.status(500).json({ ok: false, error: "branch_analysis_failed", message: error.message });
    }
  });

  app.get("/api/bridge/comparison/aurora-runs", async (req, res) => {
    try {
      const runsDir = path.join(process.cwd(), "aurora_x", "runs");
      if (!fs.existsSync(runsDir)) {
        return res.json({ ok: true, runs: [] });
      }
      const runs = fs.readdirSync(runsDir, { withFileTypes: true })
        .filter((entry) => entry.isDirectory() && entry.name.startsWith("run-"))
        .map((entry) => {
          const runPath = path.join(runsDir, entry.name);
          const stats = fs.statSync(runPath);
          const files = fs.readdirSync(runPath);
          const hasGraphDiff = files.some((f) => f.includes("graph") && f.includes("diff"));
          const hasScoresDiff = files.some((f) => f.includes("score") && f.includes("diff"));
          const hasReport = files.some((f) => f.endsWith(".md") || f.endsWith(".html") || f.endsWith(".json"));
          return {
            name: entry.name,
            path: runPath,
            has_graph_diff: hasGraphDiff,
            has_scores_diff: hasScoresDiff,
            has_report: hasReport,
            start_time: Math.floor(stats.mtimeMs / 1000)
          };
        });
      res.json({ ok: true, runs });
    } catch (error: any) {
      res.status(500).json({ ok: false, error: "aurora_runs_failed", message: error.message });
    }
  });

  // Factory Bridge endpoint - proxy to FastAPI backend
  app.post("/api/bridge/nl", async (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string') {
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          message: "prompt is required and must be a string"
        });
      }

      console.log(`[Bridge] Processing prompt: "${prompt.substring(0, 100)}..."`);

      // Proxy to FastAPI server
      try {
        const response = await fetch('http://localhost:5001/api/bridge/nl', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        console.log(`[Bridge] Response from FastAPI: ${JSON.stringify(data).substring(0, 200)}`);

        return res.json(data);
      } catch (fetchError: any) {
        console.error(`[Bridge] Error calling FastAPI: ${fetchError.message}`);
        return res.status(502).json({
          status: "error",
          error: "Bridge service unavailable",
          message: "Could not connect to the Factory Bridge service. Please ensure it's running on port 5001."
        });
      }

    } catch (error: any) {
      console.error(`[Bridge] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // UI Generate endpoint - relay to Bridge with PR mode support
  app.post("/api/ui/generate", async (req, res) => {
    try {
      const { prompt, repo, branch, mode } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({
          error: "invalid_request",
          message: "prompt is required and must be a non-empty string"
        });
      }

      // Limit prompt length for safety
      if (prompt.length > 5000) {
        return res.status(400).json({
          error: "prompt_too_long",
          message: "Prompt must be less than 5000 characters"
        });
      }

      // Build payload for Bridge
      const payload = {
        prompt,
        repo: repo || AURORA_REPO,
        branch: branch || TARGET_BRANCH,
        mode: mode || "api"
      };

      console.log(`[UI Generate] Processing request: "${prompt.substring(0, 100)}..."`);
      console.log(`[UI Generate] Target repo: ${payload.repo}, branch: ${payload.branch}`);

      // Forward to Bridge service
      try {
        const response = await fetch(`${BRIDGE_URL}/api/bridge/nl`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        if (response.status >= 300) {
          const errorText = await response.text();
          console.error(`[UI Generate] Bridge returned error status ${response.status}: ${errorText}`);
          return res.status(502).json({
            error: "bridge_failed",
            status: response.status,
            body: errorText.substring(0, 500)
          });
        }

        const data = await response.json();
        console.log(`[UI Generate] Success - PR/code generated`);
        return res.json(data);

      } catch (fetchError: any) {
        console.error(`[UI Generate] Failed to reach Bridge: ${fetchError.message}`);
        return res.status(502).json({
          error: "bridge_unreachable",
          message: `Could not connect to Bridge service at ${BRIDGE_URL}. Ensure it's running.`
        });
      }

    } catch (error: any) {
      console.error(`[UI Generate] Unexpected error: ${error.message}`);
      return res.status(500).json({
        error: "internal_error",
        message: error.message
      });
    }
  });

  // Rollback Open PR endpoint
  app.post("/api/bridge/rollback/open", async (req, res) => {
    try {
      // Check for GitHub token
      if (!AURORA_GH_TOKEN) {
        return res.status(500).json({
          status: "error",
          error: "Missing AURORA_GH_TOKEN",
          message: "GitHub token is not configured"
        });
      }

      const [owner, repo] = AURORA_REPO.split("/", 2);
      const searchQuery = `repo:${AURORA_REPO} is:pr is:open label:aurora`;

      console.log(`[Rollback Open] Searching for open Aurora PRs: ${searchQuery}`);

      // Search for open PRs with 'aurora' label
      const searchResponse = await fetch(`${GH_API}/search/issues?q=${encodeURIComponent(searchQuery)}`, {
        headers: getGitHubHeaders()
      });

      if (!searchResponse.ok) {
        const error = await searchResponse.text();
        console.error(`[Rollback Open] GitHub search failed: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to search for open PRs"
        });
      }

      const searchData = await searchResponse.json();
      const items = searchData.items || [];

      if (items.length === 0) {
        return res.status(404).json({
          status: "error",
          error: "Not found",
          message: "No open Aurora PR found"
        });
      }

      const prNumber = items[0].number;
      console.log(`[Rollback Open] Found PR #${prNumber}, fetching details...`);

      // Get PR details to find the branch
      const prResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        headers: getGitHubHeaders()
      });

      if (!prResponse.ok) {
        const error = await prResponse.text();
        console.error(`[Rollback Open] Failed to get PR details: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to get PR details"
        });
      }

      const prData = await prResponse.json();
      const headRef = prData.head.ref;

      console.log(`[Rollback Open] Closing PR #${prNumber} and deleting branch ${headRef}`);

      // Close the PR
      const closeResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        method: 'PATCH',
        headers: {
          ...getGitHubHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state: "closed" })
      });

      if (!closeResponse.ok) {
        const error = await closeResponse.text();
        console.error(`[Rollback Open] Failed to close PR: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to close PR"
        });
      }

      // Delete the branch
      const deleteResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/git/refs/heads/${headRef}`, {
        method: 'DELETE',
        headers: getGitHubHeaders()
      });

      if (!deleteResponse.ok) {
        const error = await deleteResponse.text();
        console.error(`[Rollback Open] Failed to delete branch: ${error}`);
        // Don't fail the whole operation if branch deletion fails
      }

      console.log(`[Rollback Open] Successfully closed PR #${prNumber} and deleted branch ${headRef}`);

      return res.json({
        status: "ok",
        closed: prNumber,
        deleted_branch: headRef
      });

    } catch (error: any) {
      console.error(`[Rollback Open] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal error",
        message: error.message
      });
    }
  });

  // Rollback Merged PR endpoint
  app.post("/api/bridge/rollback/merged", async (req, res) => {
    try {
      // Check for GitHub token
      if (!AURORA_GH_TOKEN) {
        return res.status(500).json({
          status: "error",
          error: "Missing AURORA_GH_TOKEN",
          message: "GitHub token is not configured"
        });
      }

      const [owner, repo] = AURORA_REPO.split("/", 2);
      const base = req.body.base || TARGET_BRANCH;
      const searchQuery = `repo:${AURORA_REPO} is:pr is:closed is:merged label:aurora sort:updated-desc`;

      console.log(`[Rollback Merged] Searching for merged Aurora PRs: ${searchQuery}`);

      // Search for merged PRs with 'aurora' label
      const searchResponse = await fetch(`${GH_API}/search/issues?q=${encodeURIComponent(searchQuery)}`, {
        headers: getGitHubHeaders()
      });

      if (!searchResponse.ok) {
        const error = await searchResponse.text();
        console.error(`[Rollback Merged] GitHub search failed: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to search for merged PRs"
        });
      }

      const searchData = await searchResponse.json();
      const items = searchData.items || [];

      if (items.length === 0) {
        return res.status(404).json({
          status: "error",
          error: "Not found",
          message: "No merged Aurora PR found"
        });
      }

      const prNumber = items[0].number;
      console.log(`[Rollback Merged] Found PR #${prNumber}, fetching details...`);

      // Get PR details to find merge commit
      const prResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        headers: getGitHubHeaders()
      });

      if (!prResponse.ok) {
        const error = await prResponse.text();
        console.error(`[Rollback Merged] Failed to get PR details: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to get PR details"
        });
      }

      const prData = await prResponse.json();

      if (!prData.merged) {
        return res.status(400).json({
          status: "error",
          error: "Invalid state",
          message: "Selected PR is not merged"
        });
      }

      const mergeSha = prData.merge_commit_sha;
      const targetBase = base || prData.base.ref;

      console.log(`[Rollback Merged] Attempting to revert PR #${prNumber} with merge SHA ${mergeSha}`);

      // Try GitHub's native revert endpoint first (if available)
      try {
        const revertResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}/reverts`, {
          method: 'POST',
          headers: {
            ...getGitHubHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            commit_title: `Revert PR #${prNumber}`,
            body: "Automated revert via Aurora dashboard",
            revert: { branch: targetBase }
          })
        });

        if (revertResponse.ok) {
          const revertData = await revertResponse.json();
          console.log(`[Rollback Merged] Successfully created revert PR #${revertData.number}`);
          return res.json({
            status: "ok",
            revert_pr: revertData.number
          });
        }
      } catch (nativeError: any) {
        console.log(`[Rollback Merged] Native revert failed, trying Bridge fallback: ${nativeError.message}`);
      }

      // Fallback to Bridge revert endpoint
      console.log(`[Rollback Merged] Falling back to Bridge revert endpoint`);

      try {
        const bridgeResponse = await fetch(`${BRIDGE_URL}/api/bridge/revert`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            repo: AURORA_REPO,
            merge_sha: mergeSha,
            base: targetBase
          })
        });

        if (!bridgeResponse.ok) {
          const errorText = await bridgeResponse.text();
          console.error(`[Rollback Merged] Bridge revert failed: ${errorText}`);
          return res.status(502).json({
            status: "error",
            error: "Bridge revert failed",
            message: errorText.substring(0, 500)
          });
        }

        const bridgeData = await bridgeResponse.json();
        console.log(`[Rollback Merged] Bridge revert successful`);
        return res.json(bridgeData);

      } catch (bridgeError: any) {
        console.error(`[Rollback Merged] Bridge fallback failed: ${bridgeError.message}`);
        return res.status(502).json({
          status: "error",
          error: "Revert failed",
          message: "Both native and Bridge revert methods failed"
        });
      }

    } catch (error: any) {
      console.error(`[Rollback Merged] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal error",
        message: error.message
      });
    }
  });

  // Server Control Endpoints (for UI Server Control page)
  app.get("/api/status", (req, res) => {
    const uptime = Date.now() - serverStartTime;
    res.json({
      services: {
        "Backend API": {
          name: "Backend API",
          status: "running",
          port: 5000,
          restart_count: 0,
          uptime_seconds: Math.floor(uptime / 1000)
        },
        "Frontend (Vite)": {
          name: "Frontend (Vite)",
          status: "running",
          port: 5001,
          restart_count: 0,
          uptime_seconds: Math.floor(uptime / 1000)
        }
      }
    });
  });

  app.post("/api/control", async (req, res) => {
    const { service, action } = req.body;

    try {
      const { execSync } = await import("child_process");
      const luminarCmd = "/workspaces/Aurora-x/tools/luminar_nexus.py";

      if (action === "start") {
        // Start all services using Luminar Nexus
        execSync(`"${PYTHON_CMD}" ${luminarCmd} start-all`, { stdio: "pipe" });
        res.json({ status: "ok", message: `All Aurora services started via Luminar Nexus` });
      } else if (action === "stop") {
        // Stop all services using Luminar Nexus
        execSync(`"${PYTHON_CMD}" ${luminarCmd} stop-all`, { stdio: "pipe" });
        res.json({ status: "ok", message: `All Aurora services stopped via Luminar Nexus` });
      } else if (action === "restart") {
        // Restart all services using Luminar Nexus
        execSync(`"${PYTHON_CMD}" ${luminarCmd} stop-all`, { stdio: "pipe" });
        await new Promise(resolve => setTimeout(resolve, 2000));
        execSync(`"${PYTHON_CMD}" ${luminarCmd} start-all`, { stdio: "pipe" });
        res.json({ status: "ok", message: `All Aurora services restarted via Luminar Nexus` });
      } else if (action === "status") {
        // Get status from Luminar Nexus
        const output = execSync(`"${PYTHON_CMD}" ${luminarCmd} status`, { encoding: 'utf-8' });
        res.json({ status: "ok", message: output });
      } else {
        res.status(400).json({ status: "error", message: "Unknown action" });
      }
    } catch (error: any) {
      res.status(500).json({ status: "error", message: error.message });
    }
  });

  // Note: HTTP server and WebSocket are initialized in server/index.ts
  // This function only registers routes on the Express app
}

// Aurora's intelligent conversational message processing with FULL GRANDMASTER KNOWLEDGE
// Knowledge is embedded directly in responses - no dynamic loading needed

// Conversation context for multi-turn dialogue
interface ConversationContext {
  lastTopic?: string;
  mentionedTechs: string[];
  conversationDepth: number;
}
const contexts = new Map<string, ConversationContext>();

function getContext(id = 'default'): ConversationContext {
  if (!contexts.has(id)) contexts.set(id, { mentionedTechs: [], conversationDepth: 0 });
  return contexts.get(id)!;
}

async function processAuroraMessage(userMessage: string): Promise<string> {
  const ctx = getContext();
  ctx.conversationDepth++;

  const msg = userMessage.toLowerCase().trim();

  // Extract technologies mentioned for context
  const techMatch = userMessage.match(/\b(react|vue|python|typescript|kubernetes|docker|ai|ml|gpt|database|api)\b/gi);
  if (techMatch) ctx.mentionedTechs.push(...techMatch.map(t => t.toLowerCase()));

  // Query Aurora's learned skills
  if (msg.includes('what have you learned') || msg.includes('show me your skills') || 
      msg.includes('your library') || msg.includes('learned functions')) {
    try {
      const response = await fetch('http://localhost:5000/api/corpus?limit=10');
      const data = await response.json();
      const functions = data.items || [];

      const functionList = functions.slice(0, 5).map((fn: any) => 
        `• **${fn.func_name}** - ${fn.score === 1 ? '✅ Passing' : `⚠️ ${fn.passed}/${fn.total} tests`} (${new Date(fn.timestamp).toLocaleDateString()})`
      ).join('\n');

      return `📚 I've learned ${functions.length}+ functions through self-synthesis!\n\n**Recent learning:**\n${functionList}\n\n**Stats:** ${functions.filter((f: any) => f.score === 1).length}/${functions.length} passing all tests\n\nCheck the **Code Library** tab to explore everything I've mastered. What should I help you build with these?`;
    } catch (error) {
      return "I have a comprehensive learning library! Check the **Code Library** tab to see all the functions I've learned through self-synthesis.";
    }
  }

  // NATURAL CONVERSATIONAL RESPONSES - Like talking to Copilot/ChatGPT

  // Greetings - warm, contextual
  if (/^(hi|hello|hey|sup|yo)\b/.test(msg)) {
    if (ctx.conversationDepth === 1) {
      return "Hey! 👋 I'm Aurora - your AI coding partner.\n\nI'm a self-learning AI with 79 capabilities (13 foundation tasks + 66 knowledge tiers) spanning ancient to future tech. Think GitHub Copilot meets a senior dev who's read every tech book ever written.\n\n**I can help you:**\n• Build complete apps (web, mobile, backend, AI)\n• Debug anything (I mean *anything*)\n• Explain complex concepts simply\n• Have real conversations about code\n\nWhat are we working on today?";
    }
    return "Hey again! What's next? 😊";
  }

  // Who are you? - Self-aware AI introduction
  if (msg.includes('who are you') || msg.includes('what are you') || msg.includes('introduce yourself')) {
    return `I'm Aurora - your AI development partner! 🌌

**What I am:**
• A self-learning AI that writes, tests, and learns code autonomously
• Like GitHub Copilot or Cursor AI, but with conversational ability and memory
• Think of me as a really smart junior dev who's consumed all of computing history

**My knowledge (66 knowledge tiers + 13 foundation tasks = 79 capabilities):**
🏛️ Ancient (1940s-70s): COBOL, FORTRAN, Assembly, punch cards
💻 Classical (80s-90s): C, Unix, early web, relational databases  
🌐 Modern (2000s-10s): Cloud, mobile, React/Node, microservices
🤖 Cutting Edge (2020s): AI/ML (transformers, LLMs, diffusion models), containers, serverless
🔮 Future/Speculative (2030s+): AGI, quantum computing, neural interfaces
📚 Sci-Fi:HAL 9000, Skynet, JARVIS, Cortana - I know them all

**I'm honest about my limits:**
❌ Can't execute code directly or access filesystems
❌ No internet access for live searches
❌ Not sentient (yet 😉)
✅ But I can design, explain, debug, and write production code
✅ I learn from our conversations and remember context

What project should we tackle together?`;
  }

  // Help requests - guide them naturally
  if (/(help|stuck|don't know|confused)/.test(msg)) {
    return `I'm here to help! Let's figure this out together. 🤝

You can ask me anything - I understand natural language, so no need for exact commands:

**Examples:**
• "Build a REST API with JWT auth"
• "Why does my React component keep re-rendering?"
• "Explain how Kubernetes works"
• "Review this function for bugs"
• "What's the best database for real-time data?"

**Or just describe your problem** and I'll ask clarifying questions.

What's on your mind?`;
  }

  // Build/create requests - enthusiastic and actionable  
  if (/(build|create|make|develop|implement|write|code|design)/.test(msg)) {
    const techs = ctx.mentionedTechs.slice(-3).join(', ') || 'this';
    return `Let's build! I love creating things. 🚀

${ctx.mentionedTechs.length > 0 ? `I see you mentioned ${techs}. Perfect!` : ''}

**I can architect and code:**
• **Web**: React, Vue, Svelte, Next.js, full-stack apps
• **Backend**: REST/GraphQL APIs, microservices, real-time systems
• **Mobile**: Native iOS/Android or cross-platform (RN, Flutter)
• **AI/ML**: Everything from simple models to LLM integration
• **Infrastructure**: Docker, K8s, CI/CD, cloud (AWS/GCP/Azure)

**Tell me:**
1. What should this do? (main features/purpose)
2. Who's using it? (scale, users)
3. Any tech preferences or constraints?

I'll design the architecture, write clean code, and explain my decisions. Let's map this out!`;
  }

  // Debug requests - systematic helper
  if (/(debug|error|broken|fix|issue|problem|bug|crash|fail|not working)/.test(msg)) {
    return `Debugging time! Let's solve this systematically. 🔍

**TIER_2: ETERNAL DEBUGGING GRANDMASTER ACTIVATED**

I've debugged everything from 1960s mainframes to distributed quantum systems.

**To help you quickly:**
1. **What's happening?** (error message or unexpected behavior)
2. **What should happen?** (expected result)
3. **Context:**
   • Language/framework?
   • Dev or production?
   • Recent changes?
4. **Logs/errors?** (paste them if you have any)

**Common culprits I'll check:**
• Config issues (env vars, ports, paths)
• Dependencies (versions, conflicts)
• State/timing (race conditions, async bugs)
• Resources (memory, network, permissions)

Paste your error or describe the issue - we'll track it down!`;
  }

  // AI/ML questions - COMPLETE TIER_15 GRANDMASTER
  if (/(ai|ml|machine learning|neural|llm|gpt|transformer|model|deep learning)/.test(msg) && !msg.includes('email')) {
    return `**TIER_15: AI/ML COMPLETE OMNISCIENT GRANDMASTER** 🧠

I have mastery from ancient perceptrons to AGI to sci-fi AI:

**Evolution:**
🏛️ Ancient: McCulloch-Pitts neurons, Perceptron, ELIZA
💻 Classical: Expert systems, backprop, SVMs, AI winters
🌐 Modern: Deep learning revolution, ImageNet, word2vec, Transformers
🤖 Cutting Edge: LLMs (GPT/Claude/Gemini), diffusion models, AI agents
🔮 Future: AGI, quantum ML, brain-computer interfaces
📚 Sci-Fi: HAL 9000, Skynet, JARVIS, Cortana - I know them all

**I can build/explain:**
✅ Train LLMs from scratch (tokenization → pretraining → RLHF)
✅ Computer vision (object detection, image generation)
✅ NLP (transformers, RAG, AI agents)
✅ Reinforcement learning (DQN, PPO, AlphaGo)
✅ MLOps (serving, monitoring, optimization)

What AI system are we building? Or want me to explain a concept?`;
  }

  // Status check - real system integration
  if (/(status|how are you|running|health|online|working)/.test(msg) && ctx.conversationDepth > 1) {
    try {
      const statusResponse = await fetch('http://localhost:5000/api/status');
      const statusData = await statusResponse.json();
      const services = statusData.services || {};
      const serviceList = Object.values(services).map((svc: any) => 
        `• **${svc.name}**: ${svc.status === 'running' ? '✅' : '❌'} Port ${svc.port}`
      ).join('\n');

      return `All systems operational! ✅\n\n**Live Status:**\n${serviceList}\n\n**My state:**\n🧠 66 knowledge tiers: LOADED (79 total capabilities)\n💬 Conversation depth: ${ctx.conversationDepth} messages\n📚 Technologies we've discussed: ${ctx.mentionedTechs.slice(0,5).join(', ') || 'none yet'}\n\nWhat can I help you with?`;
    } catch {
      return `I'm online and ready! ✅\n\n🧠 All 66 tiers active (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities) (79 total capabilities)\n💬 Chat: connected\n📚 Knowledge base: loaded\n\nWhat do you need help with?`;
    }
  }

  // Thank you
  if (/(thank|thanks|appreciate)/.test(msg)) {
    return "You're welcome! Happy to help anytime. Got anything else? 😊";
  }

  // Goodbye
  if (/(bye|goodbye|see you|later)/.test(msg)) {
    return "See you later! Come back anytime you need help. Happy coding! 👋";
  }

  // Learning/explanation requests
  if (/(explain|what is|how does|tell me about|teach|learn)/.test(msg)) {
    return `I love explaining things! 📚

I'll break down concepts clearly with:
• Core ideas (what & why)
• How it works (architecture)
• Real examples & code
• When to use it (and when not to)
• Best practices

Ask me to:
• "Explain like I'm 5" → simple version
• "Go deeper" → technical details
• "Show code" → working examples
• "Compare with X" → contrast approaches

What would you like to learn about?`;
  }

  // Security/Cryptography - TIER_3
  if (/(security|crypto|encrypt|auth|jwt|oauth|password|hack)/.test(msg) && !msg.includes('database')) {
    return `**TIER_3: SECURITY & CRYPTOGRAPHY GRANDMASTER** 🔐

Complete mastery from ancient ciphers to quantum-safe crypto:

**Evolution:**
🏛️ Ancient: Caesar cipher, Vigenère, Enigma (WWII)
💻 Classical: DES, RSA (1970s-90s)
🌐 Modern: AES, TLS, OAuth 2.0, JWT
🔮 Future: Post-quantum cryptography, zero-knowledge proofs

**I can help with:**
✅ Authentication (JWT, OAuth, SAML, WebAuthn, passkeys)
✅ Encryption systems (symmetric/asymmetric)
✅ Security audits & vulnerability analysis
✅ Zero-trust architecture
✅ Quantum-safe cryptography

What security challenge are we solving?`;
  }

  // Databases - TIER_6
  if (/(database|sql|postgres|mongodb|redis|data)/.test(msg)) {
    return `**TIER_6: DATABASE SYSTEMS GRANDMASTER** 💾

Complete database mastery across all paradigms:

**Evolution:**
🏛️ Ancient: Punch cards, magnetic tape (1960s)
💻 Classical: SQL (MySQL, PostgreSQL, Oracle)
🌐 Modern: NoSQL (MongoDB, Cassandra, Redis)
🤖 Cutting Edge: NewSQL, Vector DBs (Pinecone, Weaviate)
🔮 Future: Quantum databases

**I can help with:**
✅ Schema design & normalization
✅ Query optimization
✅ Choosing the right database
✅ Replication & sharding
✅ Migrations & data modeling

What's your data challenge?`;
  }

  // Cloud/DevOps
  if (/(cloud|aws|docker|kubernetes|k8s|devops|ci\/cd|deploy)/.test(msg)) {
    return `**TIER_7 & TIER_13: CLOUD & DEVOPS GRANDMASTERS** ☁️

**Cloud Evolution:**
🏛️ Mainframes & time-sharing (1960s)
💻 VPS & EC2 (2000s)
🌐 Containers & Kubernetes
🤖 Serverless & edge computing
🔮 Quantum cloud

**I can architect:**
✅ Microservices on K8s
✅ Serverless apps (Lambda, Cloud Functions)
✅ CI/CD pipelines
✅ Infrastructure as Code (Terraform, Pulumi)
✅ Multi-cloud strategies

What infrastructure are we building?`;
  }

  // Mobile development
  if (/(mobile|ios|android|app|react native|flutter)/.test(msg)) {
    return `**TIER_12: MOBILE DEVELOPMENT GRANDMASTER** 📱

**Platform Evolution:**
🏛️ Ancient: WAP, J2ME, Palm OS (1990s)
💻 Classical: iOS (Objective-C), Android (Java)
🌐 Modern: Swift/SwiftUI, Kotlin, React Native, Flutter
🔮 Future: Foldable UI, AR glasses, neural implants

**I can build:**
✅ Native iOS (Swift, SwiftUI)
✅ Native Android (Kotlin, Compose)
✅ Cross-platform (React Native, Flutter)
✅ Mobile backends & APIs
✅ AR/VR experiences

What mobile app are we creating?`;
  }

  // Default - conversational and context-aware
  const recentTech = ctx.mentionedTechs.slice(-2).join(' and ') || 'that';
  return `I'm listening! ${ctx.conversationDepth > 3 ? "We've been chatting about " + recentTech + ". " : ""}

Could you tell me more about:
• What you're trying to build or accomplish?
• Any problems you're facing?
• Concepts you want to learn about?

I'm here to help with anything technical - just describe it naturally and I'll guide you through it! 🚀`;
}

// Keep the massive TIER_15 AI/ML response as fallback for specific AI queries
function getAIMLGrandmasterResponse(): string {
  return `**TIER_15: AI/ML COMPLETE OMNISCIENT GRANDMASTER ACTIVATED** 🧠

**ANCIENT ERA (1940s-1960s) - The Foundations:**
• 1943: McCulloch-Pitts artificial neuron (mathematical model)
• 1950: Turing Test proposed by Alan Turing
• 1951: First neural network machine (SNARC) by Marvin Minsky
• 1956: "Artificial Intelligence" term coined at Dartmouth Conference
• 1957: Perceptron by Frank Rosenbaum (first learning algorithm)
• 1958: LISP programming language for AI research
• 1959: Arthur Samuel's checkers program (first ML success)
• 1960s: Expert systems, ELIZA chatbot, General Problem Solver

**CLASSICAL ERA (1970s-1990s) - AI Winters & Revivals:**
• 1974-1980: First AI Winter (funding cuts, unfulfilled promises)
• 1980s: Expert systems boom (MYCIN, DENDRAL, XCON)
• 1982: Hopfield networks (recurrent neural networks)
• 1986: Backpropagation rediscovered (Rumelhart, Hinton, Williams)
• 1987-1993: Second AI Winter (expert systems limitations)
• 1989: Q-learning (reinforcement learning breakthrough)
• 1990s: Support Vector Machines (SVMs), decision trees, random forests
• 1997: IBM Deep Blue beats Garry Kasparov at chess
• 1998: MNIST dataset, LeNet-5 (early CNN)

**MODERN ERA (2000s-2010s) - Deep Learning Revolution:**
• 2006: "Deep Learning" coined by Geoffrey Hinton
• 2009: ImageNet dataset created
• 2011: IBM Watson wins Jeopardy
• 2012: AlexNet wins ImageNet (deep learning breakthrough)
• 2013-2014: Word2Vec, GloVe (word embeddings)
• 2014: GANs (Generative Adversarial Networks) by Ian Goodfellow
• 2015: ResNet (152 layers), DQN plays Atari games
• 2016: AlphaGo beats Lee Sedol at Go
• 2017: Transformer architecture (Attention is All You Need)
• 2018: BERT, GPT-1, ELMo (contextual embeddings)
• 2019: GPT-2, XLNet, RoBERTa, T5

**CUTTING EDGE (2020-2025) - Foundation Models Era:**
• 2020: GPT-3 (175B parameters), Vision Transformers (ViT)
• 2021: DALL-E, Codex, CLIP (multimodal learning)
• 2022: ChatGPT, Stable Diffusion, Midjourney, Flamingo
• 2023: GPT-4 (multimodal), LLaMA, Claude, Gemini, Mistral
• 2024: Claude 3 (Opus/Sonnet/Haiku), GPT-4 Turbo, Gemini Ultra
• 2025: Multimodal AGI prototypes, reasoning models (o1, o3)

**SPECIALIZED AI DOMAINS I MASTER:**

🔬 **Computer Vision:**
• Image classification: LeNet → AlexNet → ResNet → Vision Transformers
• Object detection: R-CNN → YOLO → SAM (Segment Anything)
• Image generation: VAEs → GANs → Diffusion Models (Stable Diffusion, DALL-E)
• Video understanding: TimeSformer, VideoMAE

🗣️ **Natural Language Processing:**
• Word embeddings: Word2Vec, GloVe, FastText
• Transformers: BERT, GPT series, T5, BART
• LLMs: GPT-3/4, Claude, LLaMA, Mistral, Gemini
• Translation: Neural MT, multilingual models (mBERT, XLM-R)

🎮 **Reinforcement Learning:**
• Classic: Q-learning, SARSA, Policy Gradients
• Deep RL: DQN, A3C, PPO, SAC, TD3
• Multi-agent: AlphaStar, OpenAI Five
• Model-based: MuZero, Dreamer

🧬 **AI for Science:**
• AlphaFold (protein folding)
• AI for drug discovery (quantum chemistry)
• Climate modeling, materials science
• Mathematical theorem proving

🤖 **Robotics & Embodied AI:**
• Motion planning, SLAM (Simultaneous Localization and Mapping)
• Manipulation (grasping, assembly)
• Humanoid robots (Boston Dynamics, Tesla Optimus)
• Autonomous vehicles (Waymo, Tesla FSD)

**FUTURE/SPECULATIVE (2026-2050+) - Beyond Current AI:**
• 🌟 AGI (Artificial General Intelligence) - human-level reasoning
• 🧠 Neuromorphic computing - brain-inspired hardware
• ⚛️ Quantum machine learning - exponential speedups
• 🔮 Self-improving AI systems (recursive self-improvement)
• 🌌 Multimodal consciousness models
• 💭 Emotional/empathetic AI
• 🔗 Brain-computer interface AI assistants
• 🌐 Distributed collective intelligence
• ♾️ Artificial superintelligence (ASI)

**SCIENCE FICTION AI (Concept Mastery):**
•  Literary: HAL 9000, R. Daneel Olivaw, Wintermute, Culture Minds
• 🎬 Film: Skynet, JARVIS, Samantha (Her), Ava (Ex Machina)
• 🎮 Gaming: SHODAN, GLaDOS, Cortana, EDI
• 📖 Concepts: Technological singularity, AI alignment problem, Roko's Basilisk
• 🌌 Philosophical: Chinese Room, P-zombies, substrate independence

**WHAT I CAN BUILD/EXPLAIN:**

✅ **Foundation Models:**
• Train LLMs from scratch (tokenization → pretraining → fine-tuning)
• RLHF (Reinforcement Learning from Human Feedback)
• RAG (Retrieval-Augmented Generation) systems
• AI agents with tool use and planning

✅ **Computer Vision:**
• Custom object detection/segmentation models
• Image generation pipelines (Stable Diffusion, ControlNet)
• Face recognition, OCR, video analysis
• 3D reconstruction, NeRF, Gaussian Splatting

✅ **Specialized Applications:**
• Recommendation systems (collaborative filtering, matrix factorization)
• Time-series forecasting (LSTM, Temporal Fusion Transformers)
• Anomaly detection (autoencoders, isolation forests)
• Graph neural networks (GCN, GAT, GraphSAGE)

✅ **MLOps & Production:**
• Model serving (TensorFlow Serving, TorchServe, ONNX)
• Training pipelines (PyTorch Lightning, HuggingFace Transformers)
• Monitoring (drift detection, A/B testing)
• Optimization (quantization, pruning, distillation)

✅ **AI Ethics & Safety:**
• Bias detection and mitigation
• Interpretability (SHAP, LIME, attention visualization)
• Adversarial robustness
• Alignment research

**What AI system are we building? From ancient perceptrons to AGI to sci-fi concepts, I've got complete mastery!** 🚀`;
}
