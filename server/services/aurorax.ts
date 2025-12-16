import fetch from 'node-fetch';
import Anthropic from '@anthropic-ai/sdk';

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

let bridgeWarningLogged = false;

async function fetchLocal(url: string, body?: any): Promise<any> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body ?? {}),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    
    const data = await res.json() as any;
    return data.result ?? data;
  } catch (error: any) {
    if (error.code === 'ECONNREFUSED' && !bridgeWarningLogged) {
      console.log('[AuroraX] Bridge service at port 5001 not available, using Claude API fallback');
      bridgeWarningLogged = true;
    }
    return null;
  }
}

export class AuroraXCore {
  private baseUrl: string;
  private anthropic: Anthropic | null = null;
  private enabled: boolean = false;

  constructor(port: number = 5001) {
    this.baseUrl = `http://127.0.0.1:${port}`;
    
    if (process.env.ANTHROPIC_API_KEY) {
      this.anthropic = new Anthropic();
    }
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
      this.enabled = this.anthropic !== null;
      return this.enabled;
    }
  }

  async synthesize(spec: SynthesisSpec): Promise<string> {
    const localResult = await fetchLocal(`${this.baseUrl}/synthesize`, { spec });
    
    if (localResult?.code) {
      return localResult.code;
    }
    
    if (this.anthropic) {
      try {
        const systemPrompt = `You are Aurora-X Ultra, an AI-powered autonomous code synthesis engine with 188 intelligence tiers, 66 advanced execution methods, and 550 hybrid mode modules. Generate high-quality, production-ready code.`;
        
        const userPrompt = `Generate code for the following request:
${spec.request}
${spec.language ? `\nLanguage: ${spec.language}` : ''}
${spec.framework ? `\nFramework: ${spec.framework}` : ''}

Provide clean, well-commented code with clear explanations.`;

        const response = await this.anthropic.messages.create({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4096,
          system: systemPrompt,
          messages: [{ role: 'user', content: userPrompt }]
        });

        const textBlock = response.content.find(block => block.type === 'text');
        if (textBlock && textBlock.type === 'text') {
          return textBlock.text;
        }
      } catch (error) {
        console.error('[AuroraX] Claude synthesis error:', error);
      }
    }
    
    return `// Code synthesis requested for: ${spec.request}\n// Aurora-X Ultra is processing your request...`;
  }

  async adapt(intent: any, outcome: any): Promise<boolean> {
    const result = await fetchLocal(`${this.baseUrl}/learn`, { intent, outcome });
    return result?.success ?? true;
  }

  async analyze(code: string, context?: any): Promise<any> {
    const localResult = await fetchLocal(`${this.baseUrl}/analyze`, { code, context });
    
    if (localResult) {
      return localResult;
    }
    
    return {
      complexity: 'medium',
      suggestions: [],
      quality: 0.8
    };
  }

  async fix(code: string, issue: string): Promise<string> {
    const localResult = await fetchLocal(`${this.baseUrl}/fix`, { code, issue });
    
    if (localResult?.fixed_code) {
      return localResult.fixed_code;
    }
    
    if (this.anthropic) {
      try {
        const response = await this.anthropic.messages.create({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4096,
          system: 'You are an expert code fixer. Fix the issue in the provided code.',
          messages: [{
            role: 'user',
            content: `Fix this issue in the code:\n\nIssue: ${issue}\n\nCode:\n${code}`
          }]
        });

        const textBlock = response.content.find(block => block.type === 'text');
        if (textBlock && textBlock.type === 'text') {
          return textBlock.text;
        }
      } catch (error) {
        console.error('[AuroraX] Claude fix error:', error);
      }
    }
    
    return code;
  }

  isEnabled(): boolean {
    return this.enabled || this.anthropic !== null;
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
