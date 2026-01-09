
import fetch from 'node-fetch';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://127.0.0.1:8000';

export async function forwardToAI(path: string, data: any, method: string = 'POST') {
  try {
    const res = await fetch(`${AI_BACKEND_URL}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: method !== 'GET' ? JSON.stringify(data) : undefined
    });

    if (!res.ok) {
      throw new Error(`AI backend responded with ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error('AI proxy error:', error);
    throw error;
  }
}

export async function checkAIHealth() {
  try {
    const res = await fetch(`${AI_BACKEND_URL}/healthz`);
    return await res.json();
  } catch (error) {
    return { status: 'unavailable', error: String(error) };
  }
}
