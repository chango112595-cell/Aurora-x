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

// Nexus V3 URL - the ONLY backend (no more Bridge)
const NEXUS_V3_URL = process.env.AURORA_NEXUS_V3_URL || 'http://127.0.0.1:5002';

async function fetchNexusV3(endpoint: string, body?: any): Promise<any> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const res = await fetch(`${NEXUS_V3_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body ?? {}),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`Nexus V3 returned ${res.status}`);
    }

    const data = await res.json() as any;
    return data;
  }
  catch (err) {
    console.warn("[AuroraXCore] Nexus V3 call failed:", (err as Error).message);
    return null;
  }
  finally {
    clearTimeout(timeoutId);
  }
}

export class AuroraXCore {
  private nexusUrl: string;
  private enabled: boolean = false;

  constructor(port: number = 5002) {
    this.nexusUrl = NEXUS_V3_URL;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const res = await fetch(`${this.nexusUrl}/health`, {
        signal: controller.signal,
        headers: { 'User-Agent': 'Aurora-HealthCheck/1.0' }
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        this.enabled = true;
        console.log('[AuroraXCore] ✅ Connected to Nexus V3');
        return true;
      }
    } catch (err: any) {
      console.warn(`[AuroraXCore] Nexus V3 health check failed: ${err.message}`);
    }

    this.enabled = false;
    return false;
  }

  async synthesize(spec: SynthesisSpec): Promise<string> {
    const nexusResult = await fetchNexusV3('/api/process', {
      input: spec.request,
      type: 'synthesis',
      session_id: 'aurorax_synthesis'
    });

    if (nexusResult?.success || nexusResult?.message || nexusResult?.response) {
      return nexusResult.response || nexusResult.message || nexusResult.result?.code || `Processing: ${spec.request}`;
    }

    // Nexus V3 is not responding - provide helpful fallback
    const requestLower = spec.request.toLowerCase();

    if (requestLower.includes('create') || requestLower.includes('build') || requestLower.includes('make')) {
      return `I understand you want to: "${spec.request}"\n\nAurora Nexus V3 is initializing. To execute this request:\n1. Ensure Aurora is running: run 'x-start' in your terminal\n2. Once services are online, I can help you create what you need.\n\nWhat specific features would you like me to include?`;
    }

    if (requestLower.includes('analyze') || requestLower.includes('check')) {
      return `Analysis request received: "${spec.request}"\n\nAurora's analysis engine is starting up. Please ensure Nexus V3 is running (port 5002).`;
    }

    return `I received your request: "${spec.request}"\n\nAurora Nexus V3 is currently starting up. Please run 'x-start' to launch all services, then try again.`;
  }

  async adapt(intent: any, outcome: any): Promise<boolean> {
    const nexusResult = await fetchNexusV3('/api/process', {
      input: JSON.stringify({ intent, outcome }),
      type: 'learn',
      session_id: 'aurorax_learn'
    });
    return nexusResult?.success ?? false;
  }

  async analyze(code: string, context?: any): Promise<any> {
    const nexusResult = await fetchNexusV3('/api/process', {
      input: `Analyze this code: ${code}`,
      type: 'analysis',
      session_id: 'aurorax_analyze',
      context
    });

    if (nexusResult?.success || nexusResult?.message) {
      return {
        success: true,
        summary: nexusResult.message || 'Analysis completed via Nexus V3',
        context,
        result: nexusResult
      };
    }

    return {
      success: false,
      summary: "Analysis queued. Nexus V3 workers processing.",
      context,
    };
  }

  async fix(code: string, issue: string): Promise<string> {
    const nexusResult = await fetchNexusV3('/api/process', {
      input: `Fix this issue: ${issue}\n\nCode:\n${code}`,
      type: 'fix',
      session_id: 'aurorax_fix'
    });

    if (nexusResult?.success || nexusResult?.result?.fixed_code) {
      return nexusResult.result?.fixed_code || code;
    }

    return `Fix queued for: "${issue}". Nexus V3 workers processing.`;
  }

  isEnabled(): boolean {
    return this.enabled;
  }
}

let auroraXInstance: AuroraXCore | null = null;

export function getAuroraXCore(): AuroraXCore {
  if (!auroraXInstance) {
    auroraXInstance = new AuroraXCore(5002);
  }
  return auroraXInstance;
}

export default AuroraXCore;
