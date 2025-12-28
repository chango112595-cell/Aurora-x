import fetch from 'node-fetch';

export interface SynthesisSpec {
  request: string;
  language?: string;
  framework?: string;
  context?: any;
}

export interface SynthesisResult {
  success: boolean;
  code?: string;
  explanation?: string;
  language?: string;
  error?: string;
}

async function fetchLocal(url: string, body?: any): Promise<any> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 3000);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body ?? {}),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`Bridge returned ${res.status}`);
    }

    const data = await res.json() as any;
    return data.result ?? data;
  }
  catch (err) {
    console.warn("[AuroraXCore] Bridge call failed:", (err as Error).message);
    return null;
  }
  finally {
    clearTimeout(timeoutId);
  }
}

export class AuroraXCore {
  private baseUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 5001) {
    this.baseUrl = `http://127.0.0.1:${port}`;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.baseUrl}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      this.enabled = res.ok;
      return this.enabled;
    } catch {
      this.enabled = false;
      return false;
    }
  }

  async synthesize(spec: SynthesisSpec): Promise<string> {
    const localResult = await fetchLocal(`${this.baseUrl}/synthesize`, { spec });
    if (localResult?.code) {
      return localResult.code;
    }
    return `Aurora bridge offline; synthesized draft for: ${spec.request}`;
  }

  async adapt(intent: any, outcome: any): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/learn`, { intent, outcome });
    return result?.success ?? false;
  }

  async analyze(code: string, context?: any): Promise<any> {
    const localResult = await fetchLocal(`${this.baseUrl}/analyze`, { code, context });
    if (localResult) {
      return localResult;
    }
    return {
      success: false,
      summary: "Aurora bridge offline; returning static analysis stub.",
      context,
    };
  }

  async fix(code: string, issue: string): Promise<string> {
    const localResult = await fetchLocal(`${this.baseUrl}/fix`, { code, issue });
    if (localResult?.fixed_code) {
      return localResult.fixed_code;
    }
    return `Aurora bridge offline; suggested fix for "${issue}":\n\n${code}`;
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let auroraXInstance: AuroraXCore | null = null;

export function getAuroraXCore(): AuroraXCore {
  if (!auroraXInstance) {
    auroraXInstance = new AuroraXCore(5001);
  }
  return auroraXInstance;
}

export default AuroraXCore;
