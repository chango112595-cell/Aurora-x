/**
 * Aurora Nexus V3 Bridge
 * Connects the Express backend to Aurora Nexus V3's Brain Bridge
 * Enables hybrid intelligence processing with all 188 tiers, 66 AEMs, and 550 modules
 */

import axios, { AxiosError } from 'axios';
import { log } from './vite';

// Aurora Nexus V3 API Configuration
const AURORA_NEXUS_HOST = process.env.AURORA_NEXUS_HOST || 'http://localhost:5001';
const AURORA_API_TIMEOUT = 30000; // 30 seconds

interface AuroraResponse {
  success: boolean;
  response?: string;
  tiers_used?: string[];
  aems_invoked?: string[];
  modules_activated?: string[];
  workers_assigned?: number;
  error?: string;
}

interface ChatMessage {
  message: string;
  session_id: string;
  context?: any[];
}

/**
 * Send a chat message to Aurora Nexus V3 for processing
 * Uses the Brain Bridge's hybrid intelligence capabilities
 */
export async function sendToAuroraChat(
  message: string,
  sessionId: string = 'default',
  context: any[] = []
): Promise<AuroraResponse> {
  try {
    log(`[AURORA-BRIDGE] Processing: "${message.substring(0, 50)}..." (session: ${sessionId})`);

    // Try Aurora Nexus V3 first (Python backend)
    const response = await axios.post(
      `${AURORA_NEXUS_HOST}/api/chat`,
      {
        message,
        session_id: sessionId,
        context: context.slice(-4) // Last 4 messages for context
      },
      {
        timeout: AURORA_API_TIMEOUT,
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        }
      }
    );

    const data = response.data;
    log(`[AURORA-BRIDGE] ✅ Response received (${response.status})`);

    return {
      success: true,
      response: data.response || data.message || 'Processing complete',
      tiers_used: data.tiers_used,
      aems_invoked: data.aems_invoked,
      modules_activated: data.modules_activated,
      workers_assigned: data.workers_assigned
    };
  } catch (error) {
    const axiosError = error as AxiosError;

    // Aurora Nexus V3 might not have a chat endpoint yet, try generic process endpoint
    if (axiosError.code === 'ECONNREFUSED' || axiosError.response?.status === 404) {
      log(`[AURORA-BRIDGE] ⚠️  Aurora Nexus V3 chat endpoint not available, trying process endpoint`);

      try {
        const fallbackResponse = await axios.post(
          `${AURORA_NEXUS_HOST}/api/process`,
          {
            input: message,
            type: 'conversation',
            session_id: sessionId
          },
          { timeout: AURORA_API_TIMEOUT }
        );

        return {
          success: true,
          response: fallbackResponse.data.output || message
        };
      } catch (fallbackError) {
        log(`[AURORA-BRIDGE] ⚠️  Fallback endpoint also failed`);
      }
    }

    const errorMsg = axiosError.message || 'Unknown error';
    log(`[AURORA-BRIDGE] ❌ Error: ${errorMsg}`);

    return {
      success: false,
      error: `Aurora connection failed: ${errorMsg}`,
      response: `I'm experiencing connection issues. Please try again. (Error: ${errorMsg})`
    };
  }
}

/**
 * Get Aurora Nexus V3 status
 */
export async function getAuroraStatus(): Promise<any> {
  try {
    const response = await axios.get(`${AURORA_NEXUS_HOST}/api/status`, {
      timeout: 5000
    });
    return response.data;
  } catch (error) {
    log(`[AURORA-BRIDGE] Status check failed`);
    return { status: 'offline', error: 'Unable to reach Aurora Nexus V3' };
  }
}

/**
 * Health check - verify Aurora connection
 */
export async function checkAuroraHealth(): Promise<boolean> {
  try {
    const response = await axios.get(`${AURORA_NEXUS_HOST}/api/health`, {
      timeout: 5000
    });
    return response.status === 200;
  } catch {
    return false;
  }
}