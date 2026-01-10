import fetch from 'node-fetch';

export interface InterpretResult {
  action: 'synthesize' | 'reflect' | 'queryMemory' | 'respond';
  spec?: any;
  topic?: string;
  query?: string;
  confidence: number;
}

async function fetchLocal(url: string, body?: any): Promise<any> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body ?? {}),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const data = await res.json() as any;
    return data.result ?? data;
  } catch (error) {
    console.warn(`[Luminar] Service call failed: ${url}`, error);
    return null;
  }
}

export class LuminarNexus {
  private baseUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 8000) {
    const { getLuminarUrl } = require('../config');
    this.baseUrl = process.env.LUMINAR_URL || getLuminarUrl();
  }

  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      const res = await fetch(`${this.baseUrl}/health`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      this.enabled = res.ok;
      return this.enabled;
    } catch {
      this.enabled = false;
      return false;
    }
  }

  async interpret(text: string, ctx: any, state: any): Promise<InterpretResult> {
    const result = await fetchLocal(`${this.baseUrl}/interpret`, { text, ctx, state });

    if (result && result.action) {
      return result as InterpretResult;
    }

    const lowerText = text.toLowerCase();
    let action: InterpretResult['action'] = 'respond';

    if (lowerText.includes('write') || lowerText.includes('create') || lowerText.includes('generate') || lowerText.includes('code')) {
      action = 'synthesize';
    } else if (lowerText.includes('remember') || lowerText.includes('recall') || lowerText.includes('what did')) {
      action = 'queryMemory';
    } else if (lowerText.includes('think') || lowerText.includes('analyze') || lowerText.includes('consider')) {
      action = 'reflect';
    }

    return {
      action,
      spec: action === 'synthesize' ? { request: text } : undefined,
      topic: action === 'reflect' ? text : undefined,
      query: action === 'queryMemory' ? text : undefined,
      confidence: 0.6
    };
  }

  async respond(intent: InterpretResult, ctx: any): Promise<string> {
    const result = await fetchLocal(`${this.baseUrl}/respond`, { intent, ctx });
    return result?.response ?? result ?? '';
  }

  async reflect(topic: string, ctx: any): Promise<string> {
    const result = await fetchLocal(`${this.baseUrl}/reflect`, { topic, ctx });
    return result?.reflection ?? result ?? `Reflecting on: ${topic}`;
  }

  async learnPattern(pattern: any): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/learn`, { pattern });
    return result?.success ?? false;
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let luminarInstance: LuminarNexus | null = null;

export function getLuminarNexus(): LuminarNexus {
  if (!luminarInstance) {
    luminarInstance = new LuminarNexus(8000);
  }
  return luminarInstance;
}

export default LuminarNexus;
