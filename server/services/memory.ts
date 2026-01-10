import fetch from 'node-fetch';
import { getMemoryFabricUrl } from '../config';

export interface MemoryContext {
  facts: Record<string, unknown>;
  recentMessages: string[];
  semanticContext: string;
  timestamp: number;
}

export interface StoredFact {
  userInput: string;
  response: string;
  intent: any;
  timestamp: number;
}

async function fetchLocal(url: string, body?: any): Promise<any> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(url, {
      method: body ? 'POST' : 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const data = await res.json() as any;
    return data.result ?? data;
  } catch (error) {
    console.warn(`[Memory] Service call failed: ${url}`, error);
    return null;
  }
}

export class MemoryFabric {
  private baseUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 5004) {
    this.baseUrl = getMemoryFabricUrl();
  }

  async checkHealth(): Promise<boolean> {
    // Retry logic for resilience
    let lastError: Error | null = null;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutMs = 3000 + (attempt * 1000);
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

        const res = await fetch(`${this.baseUrl}/status`, {
          signal: controller.signal,
          headers: { 'User-Agent': 'Aurora-HealthCheck/1.0' }
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          this.enabled = true;
          return true;
        }

        if (attempt === 0) {
          console.warn(`[Memory Fabric] Health check returned ${res.status} for ${this.baseUrl}`);
        }
      } catch (err: any) {
        lastError = err;
        if (attempt < 1 && err.name !== 'AbortError') {
          await new Promise(resolve => setTimeout(resolve, 500));
          continue;
        }
      }
    }

    if (this.enabled) {
      console.warn(`[Memory Fabric] Service went offline: ${lastError?.message || 'Connection failed'}`);
    }
    this.enabled = false;
    return false;
  }

  async retrieveContext(prompt: string): Promise<MemoryContext> {
    const result = await fetchLocal(`${this.baseUrl}/context`, { prompt });

    if (result && typeof result === 'object') {
      return {
        facts: result.facts ?? {},
        recentMessages: result.recentMessages ?? [],
        semanticContext: result.context ?? result.semanticContext ?? '',
        timestamp: Date.now()
      };
    }

    return {
      facts: {},
      recentMessages: [],
      semanticContext: '',
      timestamp: Date.now()
    };
  }

  async storeFact(fact: StoredFact): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/fact`, {
      key: `interaction_${fact.timestamp}`,
      value: fact,
      category: 'conversation'
    });
    return result?.success ?? false;
  }

  async query(q: string): Promise<string> {
    const result = await fetchLocal(`${this.baseUrl}/search`, { query: q, top_k: 5 });

    if (result?.results && Array.isArray(result.results)) {
      return result.results.map((r: any) => r.content).join('\n');
    }

    return result?.context ?? '';
  }

  async saveMessage(role: string, content: string, importance: number = 0.5, tags: string[] = []): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/message`, {
      role, content, importance, tags
    });
    return result?.success ?? false;
  }

  async getFacts(): Promise<Record<string, unknown>> {
    const result = await fetchLocal(`${this.baseUrl}/facts`);
    return result?.facts ?? {};
  }

  async getRecent(limit: number = 10): Promise<any[]> {
    const result = await fetchLocal(`${this.baseUrl}/status`);
    return result?.shortTerm ?? [];
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let memoryInstance: MemoryFabric | null = null;

export function getMemoryFabric(): MemoryFabric {
  if (!memoryInstance) {
    memoryInstance = new MemoryFabric(5004);
  }
  return memoryInstance;
}

export default MemoryFabric;
