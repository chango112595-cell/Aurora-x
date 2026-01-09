import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';

export interface ConsciousState {
  ok: boolean;
  state: string;
  awarenessLevel: string;
  autonomousMode: boolean;
  hybridMode: boolean;
  workers: {
    total: number;
    active: number;
    idle: number;
  };
  peakCapabilities: {
    tiers: number;
    aems: number;
    modules: number;
    workers: number;
  };
  uptime: number;
}

const PROJECT_ROOT = path.resolve(process.cwd());
const MANIFEST_DIR = path.join(PROJECT_ROOT, "manifests");

function readJsonFile<T>(filePath: string): T | null {
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function getManifestCounts() {
  const tiers = readJsonFile<{ tiers?: unknown[]; totalTiers?: number }>(path.join(MANIFEST_DIR, "tiers.manifest.json"));
  const executions = readJsonFile<{ executions?: unknown[]; totalExecutions?: number }>(
    path.join(MANIFEST_DIR, "executions.manifest.json")
  );
  const modules = readJsonFile<{ modules?: unknown[]; totalModules?: number }>(
    path.join(MANIFEST_DIR, "modules.manifest.json")
  );

  return {
    tiers: tiers?.tiers?.length ?? tiers?.totalTiers ?? 0,
    aems: executions?.executions?.length ?? executions?.totalExecutions ?? 0,
    modules: modules?.modules?.length ?? modules?.totalModules ?? 0
  };
}

async function fetchLocal(url: string, body?: any): Promise<any> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(url, {
      method: body ? 'POST' : 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const data = await res.json() as any;
    return data;
  } catch (error) {
    console.warn(`[Nexus] Service call failed: ${url}`, error);
    return null;
  }
}

export class AuroraNexus {
  private baseUrl: string;
  private enabled: boolean = false;
  private lastHealthCheck: number = 0;
  private healthCheckInterval: number = 30000;
  readonly WORKER_COUNT = 300;

  constructor(port: number = 5002) {
    const host = process.env.NEXUS_V3_HOST || process.env.AURORA_HOST || '127.0.0.1';
    this.baseUrl = `http://${host}:${port}`;
  }

  async checkHealth(): Promise<boolean> {
    const now = Date.now();

    if (now - this.lastHealthCheck < this.healthCheckInterval && this.enabled) {
      return true;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      const res = await fetch(`${this.baseUrl}/api/health`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      this.enabled = res.ok;
      this.lastHealthCheck = now;
      return this.enabled;
    } catch {
      this.enabled = false;
      this.lastHealthCheck = now;
      return false;
    }
  }

  async getConsciousState(): Promise<ConsciousState> {
    const result = await fetchLocal(`${this.baseUrl}/api/consciousness`);
    const manifestCounts = getManifestCounts();

    if (result && result.success) {
      return {
        ok: true,
        state: result.consciousness_state ?? 'active',
        awarenessLevel: result.awareness_level ?? 'standard',
        autonomousMode: result.autonomous_mode ?? true,
        hybridMode: result.hybrid_mode ?? true,
        workers: {
          total: result.workers?.total ?? 300,
          active: result.workers?.active ?? 0,
          idle: result.workers?.idle ?? 300
        },
        peakCapabilities: {
          tiers: result.peak_capabilities?.tiers ?? manifestCounts.tiers,
          aems: result.peak_capabilities?.aems ?? manifestCounts.aems,
          modules: result.peak_capabilities?.modules ?? manifestCounts.modules,
          workers: result.peak_capabilities?.workers ?? 300
        },
        uptime: result.uptime ?? 0
      };
    }

    return {
      ok: false,
      state: 'offline',
      awarenessLevel: 'minimal',
      autonomousMode: false,
      hybridMode: false,
      workers: { total: 0, active: 0, idle: 0 },
      peakCapabilities: { tiers: manifestCounts.tiers, aems: manifestCounts.aems, modules: manifestCounts.modules, workers: 300 },
      uptime: 0
    };
  }

  async reportEvent(event: string, details: Record<string, unknown> = {}): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/api/cognitive-event`, {
      event_type: event,
      source: 'aurora_orchestrator',
      message: `Event: ${event}`,
      context: details,
      importance: 0.7
    });
    return result?.success ?? false;
  }

  async dispatchTask(taskType: string, payload: Record<string, unknown>, priority: string = 'normal'): Promise<any> {
    const result = await fetchLocal(`${this.baseUrl}/api/dispatch-task`, {
      task_type: taskType,
      payload,
      priority
    });
    return result;
  }

  async getCapabilities(): Promise<Record<string, unknown>> {
    const result = await fetchLocal(`${this.baseUrl}/api/capabilities`);
    return result ?? {};
  }

  async getManifest(): Promise<Record<string, number>> {
    const result = await fetchLocal(`${this.baseUrl}/api/manifest`);
    if (result) {
      return result;
    }
    const counts = getManifestCounts();
    return { tiers: counts.tiers, aems: counts.aems, modules: counts.modules };
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let nexusInstance: AuroraNexus | null = null;

export function getAuroraNexus(): AuroraNexus {
  if (!nexusInstance) {
    nexusInstance = new AuroraNexus(5002);
  }
  return nexusInstance;
}

export default AuroraNexus;
