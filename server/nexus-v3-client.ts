import fetch from 'node-fetch';

export interface NexusV3Status {
  state: string;
  node_id: string;
  node_name: string;
  version: string;
  codename: string;
  uptime: number;
  platform: {
    system: string;
    release: string;
    machine: string;
    processor: string;
    python_version: string;
  };
  device_tier: string;
  modules_loaded: number;
  modules_healthy: number;
  peak_capabilities: {
    workers: number;
    tiers: number;
    aems: number;
    modules: number;
  };
  hyperspeed_enabled: boolean;
  autonomous_mode: boolean;
  hybrid_mode_enabled: boolean;
  brain_bridge_connected: boolean;
  worker_metrics: {
    active: number;
    idle: number;
    tasks_completed: number;
    tasks_failed: number;
  };
  manifest_status: {
    tiers_loaded: number;
    aems_loaded: number;
    modules_loaded: number;
  };
}

export interface ConsciousnessState {
  success: boolean;
  consciousness_state: string;
  awareness_level: string;
  autonomous_mode: boolean;
  hybrid_mode: boolean;
  brain_bridge_connected: boolean;
  uptime: number;
  workers: {
    total: number;
    active: number;
    idle: number;
    ready_for_tasks: boolean;
  } | null;
  manifest: {
    tiers_loaded: number;
    aems_loaded: number;
    modules_loaded: number;
  } | null;
  peak_capabilities: {
    workers: number;
    tiers: number;
    aems: number;
    modules: number;
  };
  active_goals: string[];
  recent_cognitive_events: CognitiveEvent[];
  timestamp: string;
}

export interface CognitiveEvent {
  id: string;
  timestamp: string;
  type: string;
  message: string;
  details: Record<string, unknown>;
}

export interface CognitiveEventReport {
  event_type: string;
  source: string;
  message: string;
  context?: Record<string, unknown>;
  importance?: number;
}

export interface CognitiveEventResponse {
  success: boolean;
  entry: CognitiveEvent;
  consciousness_acknowledged: boolean;
}

export interface TaskDispatchRequest {
  task_type: string;
  payload: Record<string, unknown>;
  priority?: 'low' | 'normal' | 'high' | 'critical';
}

export interface TaskDispatchResponse {
  success: boolean;
  task_id: string;
  status: string;
  workers_available: number;
}

export class NexusV3Client {
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

      const response = await fetch(`${this.baseUrl}/api/health`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      this.enabled = response.ok;
      this.lastHealthCheck = now;
      return this.enabled;
    } catch {
      this.enabled = false;
      this.lastHealthCheck = now;
      return false;
    }
  }

  async getStatus(): Promise<NexusV3Status | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/status`);
      if (response.ok) {
        return await response.json() as NexusV3Status;
      }
      return null;
    } catch {
      return null;
    }
  }

  async getConsciousnessState(): Promise<ConsciousnessState | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/consciousness`);
      if (response.ok) {
        return await response.json() as ConsciousnessState;
      }
      return null;
    } catch {
      return null;
    }
  }

  async reportCognitiveEvent(event: CognitiveEventReport): Promise<CognitiveEventResponse | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/cognitive-event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });

      if (response.ok) {
        return await response.json() as CognitiveEventResponse;
      }
      return null;
    } catch {
      return null;
    }
  }

  async dispatchTask(task: TaskDispatchRequest): Promise<TaskDispatchResponse | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/dispatch-task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
      });

      if (response.ok) {
        return await response.json() as TaskDispatchResponse;
      }
      return null;
    } catch {
      return null;
    }
  }

  async getCapabilities(): Promise<Record<string, unknown> | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/capabilities`);
      if (response.ok) {
        return await response.json() as Record<string, unknown>;
      }
      return null;
    } catch {
      return null;
    }
  }

  async getManifest(): Promise<Record<string, number> | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/manifest`);
      if (response.ok) {
        return await response.json() as Record<string, number>;
      }
      return null;
    } catch {
      return null;
    }
  }

  async getActivity(): Promise<Record<string, unknown> | null> {
    if (!await this.checkHealth()) return null;

    try {
      const response = await fetch(`${this.baseUrl}/api/activity`);
      if (response.ok) {
        return await response.json() as Record<string, unknown>;
      }
      return null;
    } catch {
      return null;
    }
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let nexusV3Client: NexusV3Client | null = null;

export function getNexusV3Client(): NexusV3Client {
  if (!nexusV3Client) {
    nexusV3Client = new NexusV3Client(5002);
  }
  return nexusV3Client;
}

export default NexusV3Client;
