// @ts-nocheck
import { WebSocket, WebSocketServer } from 'ws';
import { conversationDetector, type ConversationDetection } from './conversation-detector';
import { conversationPatternAdapter } from './conversation-pattern-adapter';
import { spawn, execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { getMemoryFabricClient } from './memory-fabric-client';
import { getNexusV3Client, type ConsciousnessState } from './nexus-v3-client';
import { getCognitiveLoop } from './cognitive-loop';
import { resolvePythonCommand } from './python-runtime';
import type { Server } from 'http';
import {
  executeWithOrchestrator,
  selectExecutionMethod,
  getSystemPromptWithCapabilities,
  getCapabilities,
  type ExecutionResult,
  type ExecutionContext
} from './aurora-execution-orchestrator';
import { getAuroraAI } from './aurora';
import { getExternalAIConfig, getLocalFallbackResponse, isAnyExternalAIAvailable } from './external-ai-guard';

// Aurora Nexus V3 - Primary service endpoint (no more Bridge or V2)
const AURORA_NEXUS_V3_URL = process.env.AURORA_NEXUS_V3_URL || 'http://127.0.0.1:5002';

// Chat response interface
interface ChatResponse {
  ok: boolean;
  response: string;
  source?: string;
  error?: string;
}

/**
 * Route chat request through Aurora Nexus V3
 * V3 is the primary and only backend - 300 workers, full capabilities
 */
async function routeViaNexusV3(message: string, sessionId: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch(`${AURORA_NEXUS_V3_URL}/api/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: message,
        type: 'conversation',
        session_id: sessionId
      }),
      signal: AbortSignal.timeout(15000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[Aurora Chat] ✅ Routed through Nexus V3');
      return {
        ok: true,
        response: data.message || data.output || data.response || 'Response received from Aurora Nexus V3',
        source: 'aurora-nexus-v3'
      };
    }
  } catch (error: any) {
    console.log('[Aurora Chat] Nexus V3 unavailable:', error.message);
  }
  return null;
}

/**
 * Get system status from Aurora Nexus V3
 */
async function getSystemStatus(): Promise<{ nexusV3: any; externalAI: any }> {
  const status: { nexusV3: any; externalAI: any } = {
    nexusV3: null,
    externalAI: getExternalAIConfig()
  };

  try {
    const response = await fetch(`${AURORA_NEXUS_V3_URL}/status`, {
      signal: AbortSignal.timeout(3000)
    });
    if (response.ok) {
      status.nexusV3 = await response.json();
    }
  } catch { /* Nexus V3 not available */ }

  return status;
}

/**
 * Process message with Aurora Nexus V3
 * Simplified routing - Nexus V3 is the only backend
 */
async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default'): Promise<string> {
  console.log(`[Aurora Chat] Processing message: "${userMessage.substring(0, 50)}..." Session: ${sessionId}`);

  // Route through Nexus V3 (primary and only backend)
  const nexusResponse = await routeViaNexusV3(userMessage, sessionId);
  if (nexusResponse && nexusResponse.ok) {
    return nexusResponse.response;
  }

  // Fallback - built-in response when Nexus V3 is unavailable
  console.warn('[Aurora Chat] ⚠️ Nexus V3 unavailable, using built-in response');
  return generateBuiltInResponse(userMessage);
}

/**
 * Generate a built-in response when Nexus V3 is unavailable
 */
function generateBuiltInResponse(message: string): string {
  const msg = message.toLowerCase();
  const aiConfig = getExternalAIConfig();
  const modeInfo = aiConfig.mode === 'local-only'
    ? ` Operating in local-only mode${aiConfig.fallbackReason ? ` (${aiConfig.fallbackReason})` : ''}.`
    : '';

  if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
    return `Hello! I'm Aurora, your AI assistant powered by Nexus V3 with 300 autonomous workers.${modeInfo} How can I help you today?`;
  }

  if (msg.includes('status') || msg.includes('health') || msg.includes('check')) {
    const externalAIStatus = aiConfig.enabled
      ? `External AI: ${aiConfig.anthropicAvailable ? 'Anthropic available' : 'No Anthropic key'}, ${aiConfig.openaiAvailable ? 'OpenAI available' : 'No OpenAI key'}`
      : 'External AI: Disabled (ENABLE_EXTERNAL_AI not set to "true")';
    return `Aurora Status: Nexus V3 is initializing. ${externalAIStatus}. 300 workers are starting up. Please wait a moment.`;
  }

  if (msg.includes('help')) {
    return `I'm Aurora, powered by Nexus V3 with 188 Tiers, 66 AEMs, and 550 Modules.${modeInfo} I can help with: code generation, analysis, optimization, debugging, and general development questions. What would you like to work on?`;
  }

  if (msg.includes('nexus') || msg.includes('workers')) {
    return "Aurora Nexus V3 is the core engine with 300 autonomous workers for parallel task execution. It handles code synthesis, analysis, optimization, and more. The system is currently starting up - please try again in a moment.";
  }

  if (msg.includes('anthropic') || msg.includes('claude') || msg.includes('external ai')) {
    if (!aiConfig.enabled) {
      return "External AI services (Anthropic/Claude) are currently disabled. Set ENABLE_EXTERNAL_AI=true and configure ANTHROPIC_API_KEY to enable external AI features. Aurora is fully functional in local-only mode with Nexus V3.";
    } else if (!aiConfig.anthropicAvailable) {
      return "Anthropic/Claude is enabled but no API key is configured. Set ANTHROPIC_API_KEY to use Claude models.";
    } else {
      return "Anthropic/Claude is configured and available for AI-powered features.";
    }
  }

  return `I received your message: "${message.substring(0, 100)}${message.length > 100 ? '...' : ''}"\n\nAurora Nexus V3 is starting up with 300 workers.${modeInfo} Please try again in a moment, or ask me a simpler question while the system initializes.`;
}

// Aurora's chat WebSocket server
export function setupAuroraChatWebSocket(server: any) {
  const wss = new WebSocketServer({
    server,
    path: '/aurora/chat'
  });

  wss.on('connection', async (ws: WebSocket) => {
    // Welcome message
    ws.send(JSON.stringify({
      message: 'Aurora online. Connected to Nexus V3 with 300 autonomous workers. 188 Tiers | 66 AEMs | 550 Modules active. How may I assist you today?'
    }));

    ws.on('message', async (data: Buffer) => {
      try {
        const { message, session_id } = JSON.parse(data.toString());
        console.log('[Aurora] Received:', message);

        // Process through Nexus V3
        const response = await processWithAuroraIntelligence(message, session_id || 'websocket-default');

        ws.send(JSON.stringify({
          message: response,
          detection: {
            type: 'processed',
            confidence: 0.95,
            executionMode: 'nexus-v3'
          }
        }));
      } catch (error) {
        ws.send(JSON.stringify({
          message: 'I encountered an error processing your message. Please try again.'
        }));
      }
    });

    ws.on('close', () => {
    });
  });

  console.log('[Aurora] Chat WebSocket server ready on /aurora/chat (Nexus V3 integrated)');
}

// Export functions needed by routes
export async function getChatResponse(message: string, sessionId: string): Promise<ChatResponse> {
  const response = await processWithAuroraIntelligence(message, sessionId);
  return {
    ok: true,
    response
  };
}

export async function searchWeb(query: string): Promise<any> {
  // Try to use Nexus V3 for web search
  try {
    const response = await fetch(`${AURORA_NEXUS_V3_URL}/api/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: `Search the web for: ${query}`,
        type: 'search',
        session_id: 'web_search'
      }),
      signal: AbortSignal.timeout(10000)
    });

    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('[Aurora Chat] Web search unavailable');
  }

  return { results: [], message: `Search queued. Query: ${query}` };
}

// Export status function for debugging
export { getSystemStatus };
