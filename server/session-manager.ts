/**
 * Session Manager - Centralized session context management for Aurora
 * 
 * This module manages session contexts across all entry points (HTTP, WebSocket)
 * to ensure proper session isolation and prevent cross-session context bleed.
 */

import { conversationDetector } from './conversation-detector';

// Session context for multi-turn dialogue
interface SessionContext {
  lastTopic?: string;
  mentionedTechs: string[];
  conversationDepth: number;
}

// Centralized session contexts map
const sessionContexts = new Map<string, SessionContext>();

/**
 * Reset session context - clears both contexts map and conversation detector
 * Call this when a session ends or needs to be cleaned up
 */
export function resetSessionContext(sessionId: string): void {
  sessionContexts.delete(sessionId);
  conversationDetector.resetSession(sessionId);
  console.log(`[SessionManager] Session reset: ${sessionId}`);
}

/**
 * Initialize fresh session context - creates new context entries
 * Call this when a new session starts (page load, WebSocket connect)
 */
export function initSessionContext(sessionId: string): void {
  conversationDetector.resetSession(sessionId);
  sessionContexts.delete(sessionId);
  sessionContexts.set(sessionId, { mentionedTechs: [], conversationDepth: 0 });
  console.log(`[SessionManager] Session initialized: ${sessionId}`);
}

/**
 * Get session context - returns existing or creates new context
 */
export function getSessionContext(sessionId: string = 'default'): SessionContext {
  if (!sessionContexts.has(sessionId)) {
    sessionContexts.set(sessionId, { mentionedTechs: [], conversationDepth: 0 });
  }
  return sessionContexts.get(sessionId)!;
}

/**
 * Check if session exists
 */
export function hasSession(sessionId: string): boolean {
  return sessionContexts.has(sessionId);
}

/**
 * Get all active session IDs (for debugging/monitoring)
 */
export function getActiveSessions(): string[] {
  return Array.from(sessionContexts.keys());
}

/**
 * Clear all sessions (for maintenance/testing)
 */
export function clearAllSessions(): void {
  sessionContexts.clear();
  conversationDetector.clearAllSessions();
  console.log('[SessionManager] All sessions cleared');
}

// Export the contexts map for backward compatibility (routes.ts still needs direct access)
export { sessionContexts as contexts };
export type { SessionContext };