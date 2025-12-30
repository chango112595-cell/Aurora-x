import type { Express } from "express";
import path from "path";
import fs from "fs";
import { AuroraCore } from "./aurora-core";

const NEXUS_V3_BASE = "http://127.0.0.1:5002";
const NEXUS_V2_BASE = process.env.LUMINAR_V2_URL || process.env.LUMINAR_URL || "http://127.0.0.1:8000";
const PROJECT_ROOT = path.resolve(process.cwd());
const MANIFEST_DIR = path.join(PROJECT_ROOT, "manifests");
const PACKS_DIR = path.join(PROJECT_ROOT, "packs");
const ACTIVITY_LOG = path.join(PROJECT_ROOT, "aurora_nexus_v3", "activity_log.jsonl");

function readJson<T>(filePath: string): T | null {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
  } catch {
    return null;
  }
}

function getManifestCounts() {
  const tiers = readJson<{ tiers: unknown[] }>(path.join(MANIFEST_DIR, "tiers.manifest.json"));
  const executions = readJson<{ executions: unknown[] }>(path.join(MANIFEST_DIR, "executions.manifest.json"));
  const modules = readJson<{ modules: unknown[] }>(path.join(MANIFEST_DIR, "modules.manifest.json"));

  return {
    tiers: tiers?.tiers?.length ?? 0,
    aems: executions?.executions?.length ?? 0,
    modules: modules?.modules?.length ?? 0,
  };
}

function getTierSummary() {
  const tiers = readJson<{ tiers: Array<{ name: string; domain?: string[] | string }> }>(
    path.join(MANIFEST_DIR, "tiers.manifest.json")
  );
  const counts: Record<string, number> = {};
  for (const tier of tiers?.tiers ?? []) {
    const domains = Array.isArray(tier.domain) ? tier.domain : tier.domain ? [tier.domain] : ["uncategorized"];
    for (const domain of domains) {
      counts[domain] = (counts[domain] || 0) + 1;
    }
  }
  const categories = Object.entries(counts).map(([name, count]) => ({ name, count }));
  return { totalTiers: tiers?.tiers?.length ?? 0, categories };
}

function getAemSummary() {
  const executions = readJson<{ executions: Array<{ name: string; category?: string }> }>(
    path.join(MANIFEST_DIR, "executions.manifest.json")
  );
  const categories: Record<string, string[]> = {};
  for (const aem of executions?.executions ?? []) {
    const category = aem.category || "uncategorized";
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(aem.name);
  }
  return {
    totalAEMs: executions?.executions?.length ?? 0,
    categories: Object.entries(categories).map(([name, methods]) => ({ name, methods, count: methods.length }))
  };
}

function getPackSummary() {
  if (!fs.existsSync(PACKS_DIR)) {
    return { total_packs: 0, loaded_packs: 0, total_submodules: 0, packs: {} };
  }
  const packDirs = fs.readdirSync(PACKS_DIR).filter((dir) => dir.startsWith("pack"));
  const packs: Record<string, any> = {};
  let totalSubmodules = 0;

  for (const dir of packDirs) {
    const packPath = path.join(PACKS_DIR, dir);
    const entries = fs.readdirSync(packPath, { withFileTypes: true });
    const submodules = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
    packs[dir] = {
      name: dir,
      directory: dir,
      exists: true,
      submodules,
      submodule_count: submodules.length
    };
    totalSubmodules += submodules.length;
  }

  return {
    total_packs: packDirs.length,
    loaded_packs: packDirs.length,
    total_submodules: totalSubmodules,
    packs
  };
}

async function fetchJson(url: string, options: RequestInit = {}, timeoutMs = 3000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch {
    return null;
  } finally {
    clearTimeout(timeoutId);
  }
}

function appendActivityLog(entry: any) {
  fs.mkdirSync(path.dirname(ACTIVITY_LOG), { recursive: true });
  fs.appendFileSync(ACTIVITY_LOG, JSON.stringify(entry) + "\n");
}

export function registerNexusV3Routes(app: Express) {
  app.get("/api/nexus-v3/health", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/health`, {}, 3000);
    if (!data) {
      return res.status(503).json({ ok: false, status: "unavailable", available: false });
    }
    res.json({ ...data, available: true });
  });

  app.get("/api/nexus-v3/status", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/status`, {}, 5000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    const counts = getManifestCounts();
    res.status(503).json({
      state: "unavailable",
      available: false,
      peak_capabilities: {
        workers: 300,
        tiers: counts.tiers,
        aems: counts.aems,
        modules: counts.modules
      }
    });
  });

  app.get("/api/nexus-v3/modules", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/modules`, {}, 3000);
    if (data) {
      return res.json(data);
    }
    const manifest = readJson<{ modules: Array<{ id: string; name: string; category?: string }> }>(
      path.join(MANIFEST_DIR, "modules.manifest.json")
    );
    const modules = (manifest?.modules ?? []).map((mod) => ({
      id: mod.id,
      name: mod.name,
      category: mod.category ?? "unknown",
      status: "registered"
    }));
    res.json({ modules, count: modules.length, available: false });
  });

  app.get("/api/nexus-v3/capabilities", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/capabilities`, {}, 3000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    const counts = getManifestCounts();
    res.json({
      workers: 300,
      tiers: counts.tiers,
      aems: counts.aems,
      modules: counts.modules,
      hyperspeed_enabled: false,
      autonomous_mode: false,
      hybrid_mode_enabled: false,
      available: false
    });
  });

  app.get("/api/nexus-v3/packs", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/packs`, {}, 3000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    res.json({ ...getPackSummary(), available: false });
  });

  app.get("/api/nexus-v3/manifest", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/manifest`, {}, 3000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    const counts = getManifestCounts();
    res.json({ ...counts, available: false });
  });

  app.get("/api/nexus-v3/self-healers", async (req, res) => {
    const aurora = AuroraCore.getInstance();
    const healerStats = aurora.getSelfHealerStats();
    const recentEvents = aurora.getRecentHealingEvents(20);

    res.json({
      total: healerStats.total,
      active: healerStats.active,
      healing: healerStats.healing,
      cooldown: healerStats.cooldown,
      status: healerStats.status,
      healsPerformed: healerStats.healsPerformed,
      healthyComponents: healerStats.healthyComponents,
      totalComponents: healerStats.totalComponents,
      recentEvents: recentEvents.map(event => ({
        id: event.id,
        healerId: event.healerId,
        targetId: event.targetId,
        targetType: event.targetType,
        action: event.action,
        status: event.status,
        startTime: new Date(event.startTime).toISOString(),
        endTime: event.endTime ? new Date(event.endTime).toISOString() : null,
        details: event.details
      })),
      available: true
    });
  });

  app.get("/api/nexus-v3/hyperspeed", async (req, res) => {
    const status = await fetchJson(`${NEXUS_V3_BASE}/api/status`, {}, 3000);
    if (status) {
      return res.json({
        enabled: status.hyperspeed_enabled ?? false,
        hybrid_mode_enabled: status.hybrid_mode_enabled ?? false,
        available: true
      });
    }
    res.json({ enabled: false, hybrid_mode_enabled: false, available: false });
  });

  app.get("/api/nexus-v3/workers", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/workers`, {}, 3000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    res.json({
      total: 300,
      active: 0,
      idle: 0,
      workers: [],
      available: false
    });
  });

  app.get("/api/nexus-v3/tiers", async (req, res) => {
    const summary = getTierSummary();
    res.json({
      totalTiers: summary.totalTiers,
      categories: summary.categories,
      mode: "production"
    });
  });

  app.get("/api/nexus-v3/aems", async (req, res) => {
    const summary = getAemSummary();
    res.json({
      totalAEMs: summary.totalAEMs,
      categories: summary.categories,
      mode: "production"
    });
  });

  app.get("/api/nexus-v3/activity", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/activity`, {}, 3000);
    if (data) {
      return res.json({ ...data, available: true });
    }
    res.json({ activities: [], available: false });
  });

  app.post("/api/nexus-v3/activity/log", async (req, res) => {
    const data = await fetchJson(`${NEXUS_V3_BASE}/api/activity/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body)
    }, 3000);

    if (data) {
      return res.json({ ...data, available: true });
    }

    const entry = {
      id: `act-${Date.now()}`,
      type: req.body.type || "info",
      message: req.body.message || "",
      timestamp: new Date().toISOString(),
      details: req.body.details || {}
    };
    appendActivityLog(entry);
    res.json({ success: true, logged: true, available: false, stored: "local" });
  });

  app.get("/api/nexus/status", async (req, res) => {
    try {
      const [v2Data, v3Data] = await Promise.all([
        fetchJson(`${NEXUS_V2_BASE}/api/nexus/status`, {}, 3000),
        fetchJson(`${NEXUS_V3_BASE}/api/status`, {}, 3000)
      ]);

      res.json({
        v2: v2Data ? { connected: true, port: 8000, ...v2Data } : { connected: false, port: 8000 },
        v3: v3Data ? { connected: true, port: 5002, ...v3Data } : { connected: false, port: 5002 },
        unified: {
          anyConnected: Boolean(v2Data || v3Data),
          allConnected: Boolean(v2Data && v3Data),
          timestamp: new Date().toISOString()
        }
      });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to fetch nexus status", message: error.message });
    }
  });

  console.log("✅ Aurora Nexus V3 routes registered (port 5002 bridge)");
}
/* @ts-nocheck */
