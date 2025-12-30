/* @ts-nocheck */
/**
 * Local Aurora response service (no external APIs).
 * Routes requests to Luminar Nexus V2 (chat engine) for live responses.
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const LUMINAR_URL = process.env.LUMINAR_URL || "http://127.0.0.1:8000";

async function callLuminar(message: string, context: ChatMessage[] = []): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const res = await fetch(`${LUMINAR_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: 'aurora-local',
        context
      }),
      signal: controller.signal
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Luminar V2 error: ${res.status} ${text}`);
    }

    const data = await res.json();
    return data.response || data.message || JSON.stringify(data);
  } finally {
    clearTimeout(timeoutId);
  }
}

export function isAuroraLocalAvailable(): boolean {
  return true;
}

export async function generateAuroraResponse(
  userMessage: string,
  _conversationType: string,
  _memoryContext: string = '',
  previousMessages: ChatMessage[] = []
): Promise<{ response: string; success: boolean }> {
  try {
    const response = await callLuminar(userMessage, previousMessages);
    return { response, success: true };
  } catch (error: any) {
    return { response: `Luminar V2 unavailable: ${error.message}`, success: false };
  }
}

export async function analyzeCode(code: string, language: string): Promise<string> {
  const prompt = `Analyze this ${language} code and report issues and improvements:\n\n${code}`;
  return callLuminar(prompt);
}

export async function generateCode(
  specification: string,
  language: string = 'python'
): Promise<string> {
  const prompt = `Generate production-ready ${language} code for this request:\n${specification}`;
  return callLuminar(prompt);
}
/* @ts-nocheck */
