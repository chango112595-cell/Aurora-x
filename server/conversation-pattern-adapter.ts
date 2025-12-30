/**
 * Conversation Pattern Adapter
 * Bridges V3 conversation detection with V2 ML learning engine
 */

import type { ConversationType, ConversationDetection } from './conversation-detector';

const V2_BASE_URL = process.env.LUMINAR_V2_URL || process.env.LUMINAR_URL || "http://127.0.0.1:8000";

export interface ConversationPattern {
  type: ConversationType;
  keywords: string[];
  confidence: number;
  timestamp: number;
  context: string;
  userMessage: string;
}

export interface LearnedPattern {
  type: ConversationType;
  avgConfidence: number;
  commonKeywords: string[];
  patternCount: number;
  improvedMultiplier: number;
}

class ConversationPatternAdapter {
  private v2Available: boolean = false;
  private lastHealthCheck: number = 0;
  private healthCheckInterval: number = 30000;
  private pendingPatterns: Array<{ detection: ConversationDetection; userMessage: string; context: string }> = [];
  private isBootstrapped: boolean = false;

  constructor() {
    this.bootstrap();
  }

  private async bootstrap(): Promise<void> {
    await this.checkV2Health();
    this.isBootstrapped = true;
  }

  private async checkV2Health(): Promise<boolean> {
    const now = Date.now();
    
    if (this.isBootstrapped && now - this.lastHealthCheck < this.healthCheckInterval) {
      return this.v2Available;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      
      const response = await fetch(`${V2_BASE_URL}/api/nexus/status`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      this.v2Available = response.ok;
      this.lastHealthCheck = now;
      
      if (this.v2Available && this.pendingPatterns.length > 0) {
        this.flushPendingPatterns();
      }
    } catch {
      this.v2Available = false;
      this.lastHealthCheck = now;
    }
    
    return this.v2Available;
  }

  private async flushPendingPatterns(): Promise<void> {
    const patterns = [...this.pendingPatterns];
    this.pendingPatterns = [];
    
    for (const p of patterns) {
      const pattern: ConversationPattern = {
        type: p.detection.type,
        keywords: p.detection.keywords,
        confidence: p.detection.confidence,
        timestamp: Date.now(),
        context: p.context,
        userMessage: p.userMessage
      };

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        await fetch(`${V2_BASE_URL}/api/nexus/learn-conversation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(pattern),
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
      } catch {
      }
    }
  }

  async sendPatternToV2(
    detection: ConversationDetection,
    userMessage: string,
    context: string = ''
  ): Promise<void> {
    const isAvailable = await this.checkV2Health();
    
    if (!isAvailable) {
      this.pendingPatterns.push({ detection, userMessage, context });
      if (this.pendingPatterns.length > 50) {
        this.pendingPatterns.shift();
      }
      return;
    }

    const pattern: ConversationPattern = {
      type: detection.type,
      keywords: detection.keywords,
      confidence: detection.confidence,
      timestamp: Date.now(),
      context,
      userMessage
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      await fetch(`${V2_BASE_URL}/api/nexus/learn-conversation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pattern),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
    } catch {
    }
  }

  async getLearnedPatterns(type: ConversationType): Promise<LearnedPattern | null> {
    if (!await this.checkV2Health()) {
      return null;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      const response = await fetch(
        `${V2_BASE_URL}/api/nexus/learned-conversation-patterns/${type}`,
        { signal: controller.signal }
      );
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        return null;
      }
      
      return await response.json();
    } catch {
      return null;
    }
  }

  async getAllLearnedPatterns(): Promise<Record<string, LearnedPattern>> {
    if (!await this.checkV2Health()) {
      return {};
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      const response = await fetch(
        `${V2_BASE_URL}/api/nexus/learned-conversation-patterns`,
        { signal: controller.signal }
      );
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        return {};
      }
      
      return await response.json();
    } catch {
      return {};
    }
  }

  isV2Available(): boolean {
    return this.v2Available;
  }
}

export const conversationPatternAdapter = new ConversationPatternAdapter();
// @ts-nocheck
