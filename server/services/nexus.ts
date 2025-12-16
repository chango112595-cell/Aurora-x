import fetch from 'node-fetch';

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

  constructor(port: number = 5002) {
    this.baseUrl = `http://127.0.0.1:${port}`;
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
          tiers: result.peak_capabilities?.tiers ?? 188,
          aems: result.peak_capabilities?.aems ?? 66,
          modules: result.peak_capabilities?.modules ?? 550,
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
      peakCapabilities: { tiers: 188, aems: 66, modules: 550, workers: 300 },
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
    return result ?? { tiers: 188, aems: 66, modules: 550 };
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
