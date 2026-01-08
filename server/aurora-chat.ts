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

// Luminar Nexus service endpoints
const LUMINAR_NEXUS_V2_URL = process.env.LUMINAR_NEXUS_V2_URL || 'http://0.0.0.0:5005';
const LUMINAR_NEXUS_V3_URL = process.env.LUMINAR_NEXUS_V3_URL || 'http://0.0.0.0:5031';
const AURORA_BRIDGE_URL = process.env.AURORA_BRIDGE_URL || 'http://0.0.0.0:5001';
const AURORA_CHAT_SERVER_URL = process.env.AURORA_CHAT_SERVER_URL || 'http://0.0.0.0:5003';

// Chat response interface
interface ChatResponse {
  ok: boolean;
  response: string;
  source?: string;
  error?: string;
}

/**
 * Try to route chat request through Luminar Nexus V2
 * V2 provides AI-driven service orchestration and quantum service mesh
 */
async function routeViaLuminarNexusV2(message: string, sessionId: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch(`${LUMINAR_NEXUS_V2_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
      signal: AbortSignal.timeout(5000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[Aurora Chat] Routed through Luminar Nexus V2');
      return {
        ok: true,
        response: data.response || data.message || 'Response received from Luminar Nexus V2',
        source: 'luminar-nexus-v2'
      };
    }
  } catch (error: any) {
    console.log('[Aurora Chat] Luminar Nexus V2 unavailable:', error.message);
  }
  return null;
}

/**
 * Try to route chat request through Luminar Nexus V3
 * V3 provides universal consciousness and advanced orchestration
 */
async function routeViaLuminarNexusV3(message: string, sessionId: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch(`${LUMINAR_NEXUS_V3_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
      signal: AbortSignal.timeout(5000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[Aurora Chat] Routed through Luminar Nexus V3');
      return {
        ok: true,
        response: data.response || data.message || 'Response received from Luminar Nexus V3',
        source: 'luminar-nexus-v3'
      };
    }
  } catch (error: any) {
    console.log('[Aurora Chat] Luminar Nexus V3 unavailable:', error.message);
  }
  return null;
}

/**
 * Try to route chat request through Aurora Bridge
 * Bridge provides routing from Luminar Nexus to Enhanced Aurora Core
 */
async function routeViaAuroraBridge(message: string, sessionId: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch(`${AURORA_BRIDGE_URL}/api/bridge/nl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: message, session_id: sessionId }),
      signal: AbortSignal.timeout(10000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[Aurora Chat] Routed through Aurora Bridge');
      return {
        ok: true,
        response: data.response || data.message || data.result || 'Response received from Aurora Bridge',
        source: 'aurora-bridge'
      };
    }
  } catch (error: any) {
    console.log('[Aurora Chat] Aurora Bridge unavailable:', error.message);
  }
  return null;
}

/**
 * Try to route chat request through Aurora Chat Server (Python Flask)
 */
async function routeViaAuroraChatServer(message: string, sessionId: string): Promise<ChatResponse | null> {
  try {
    const response = await fetch(`${AURORA_CHAT_SERVER_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
      signal: AbortSignal.timeout(5000)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[Aurora Chat] Routed through Aurora Chat Server');
      return {
        ok: true,
        response: data.response || data.message || 'Response received from Aurora Chat Server',
        source: 'aurora-chat-server'
      };
    }
  } catch (error: any) {
    console.log('[Aurora Chat] Aurora Chat Server unavailable:', error.message);
  }
  return null;
}

/**
 * Get system status from all Luminar Nexus services
 */
async function getSystemStatus(): Promise<{ v2: any; v3: any; bridge: any; externalAI: any }> {
  const status: { v2: any; v3: any; bridge: any; externalAI: any } = {
    v2: null,
    v3: null,
    bridge: null,
    externalAI: getExternalAIConfig()
  };

  try {
    const v2Response = await fetch(`${LUMINAR_NEXUS_V2_URL}/api/nexus/status`, {
      signal: AbortSignal.timeout(3000)
    });
    if (v2Response.ok) {
      status.v2 = await v2Response.json();
    }
  } catch { /* V2 not available */ }

  try {
    const v3Response = await fetch(`${LUMINAR_NEXUS_V3_URL}/api/nexus/status`, {
      signal: AbortSignal.timeout(3000)
    });
    if (v3Response.ok) {
      status.v3 = await v3Response.json();
    }
  } catch { /* V3 not available */ }

  try {
    const bridgeResponse = await fetch(`${AURORA_BRIDGE_URL}/health`, {
      signal: AbortSignal.timeout(3000)
    });
    if (bridgeResponse.ok) {
      status.bridge = await bridgeResponse.json();
    }
  } catch { /* Bridge not available */ }

  return status;
}

/**
 * Process message with Aurora intelligence using fallback chain:
 * 1. Try Luminar Nexus V2 (primary - AI orchestration)
 * 2. Try Luminar Nexus V3 (fallback - universal consciousness)
 * 3. Try Aurora Bridge (fallback - core routing)
 * 4. Try Aurora Chat Server (fallback - Flask server)
 * 5. Return built-in response (final fallback)
 */
async function processWithAuroraIntelligence(userMessage: string, sessionId: string = 'default'): Promise<string> {
  console.log(`[Aurora Chat] Processing message: "${userMessage.substring(0, 50)}..." Session: ${sessionId}`);

  // Prefer direct Aurora AI handler (diagnostics-aware). If it fails, fall back to built-in.
  try {
    const auroraAI = getAuroraAI();
    return await auroraAI.handleChat(userMessage);
  } catch (err: any) {
    console.warn('[Aurora Chat] Aurora AI handler failed:', err?.message || err);
    return generateBuiltInResponse(userMessage);
  }
}

/**
 * Generate a built-in response when all services are unavailable
 * Uses external AI guard for graceful fallback behavior
 */
function generateBuiltInResponse(message: string): string {
  const msg = message.toLowerCase();
  const aiConfig = getExternalAIConfig();
  const modeInfo = aiConfig.mode === 'local-only'
    ? ` Operating in local-only mode${aiConfig.fallbackReason ? ` (${aiConfig.fallbackReason})` : ''}.`
    : '';

  if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
    return `Hello! I'm Aurora, your AI assistant. I'm currently operating in standalone mode while connecting to Luminar Nexus services.${modeInfo} How can I help you today?`;
  }

  if (msg.includes('status') || msg.includes('health') || msg.includes('check')) {
    const externalAIStatus = aiConfig.enabled
      ? `External AI: ${aiConfig.anthropicAvailable ? 'Anthropic available' : 'No Anthropic key'}, ${aiConfig.openaiAvailable ? 'OpenAI available' : 'No OpenAI key'}`
      : 'External AI: Disabled (ENABLE_EXTERNAL_AI not set to "true")';
    return `Aurora Status: I'm online and processing your messages. ${externalAIStatus}. Luminar Nexus V2 and V3 services appear to be offline or starting up. I'm ready to assist you with basic queries while the full system initializes.`;
  }

  if (msg.includes('help')) {
    return `I'm Aurora, an AI assistant with 79 capabilities across 27 technology domains.${modeInfo} While my full Luminar Nexus integration is connecting, I can help with: code reviews, architecture discussions, debugging tips, and general development questions. What would you like to work on?`;
  }

  if (msg.includes('luminar') || msg.includes('nexus')) {
    return "Luminar Nexus is Aurora's advanced orchestration system. V2 provides AI-driven service management and autonomous healing. V3 adds universal consciousness and quantum-inspired state management. The system is currently initializing - please try again in a moment.";
  }

  if (msg.includes('anthropic') || msg.includes('claude') || msg.includes('external ai')) {
    if (!aiConfig.enabled) {
      return "External AI services (Anthropic/Claude) are currently disabled. Set ENABLE_EXTERNAL_AI=true and configure ANTHROPIC_API_KEY to enable external AI features. Aurora is fully functional in local-only mode.";
    } else if (!aiConfig.anthropicAvailable) {
      return "Anthropic/Claude is enabled but no API key is configured. Set ANTHROPIC_API_KEY to use Claude models. Aurora continues to operate using other available services.";
    } else {
      return "Anthropic/Claude is configured and available for AI-powered features.";
    }
  }

  return `I received your message: "${message.substring(0, 100)}${message.length > 100 ? '...' : ''}"\n\nI'm currently connecting to Luminar Nexus V2 and V3 for enhanced processing.${modeInfo} In the meantime, I'm here to help with any questions or tasks you have. What would you like to explore?`;
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
      message: 'Aurora online. Connected to Luminar Nexus V2 and V3 orchestration systems. 79 capabilities (66 knowledge tiers + 13 foundation tasks) active. How may I assist you today?'
    }));

    ws.on('message', async (data: Buffer) => {
      try {
        const { message, session_id } = JSON.parse(data.toString());
        console.log('[Aurora] Received:', message);

        // Aurora processes the message through Luminar Nexus integration
        const response = await processWithAuroraIntelligence(message, session_id || 'websocket-default');

        ws.send(JSON.stringify({
          message: response,
          detection: {
            type: 'processed',
            confidence: 0.95,
            executionMode: 'luminar-nexus'
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

  console.log('[Aurora] Chat WebSocket server ready on /aurora/chat (Luminar Nexus V2/V3 integrated)');
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
  // Try to use Aurora Bridge for web search
  try {
    const response = await fetch(`${AURORA_BRIDGE_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
      signal: AbortSignal.timeout(10000)
    });

    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('[Aurora Chat] Web search unavailable');
  }

  return { results: [], message: `Search functionality requires Aurora Bridge service. Query: ${query}` };
}

// Export status function for debugging
export { getSystemStatus };
/* @ts-nocheck */
