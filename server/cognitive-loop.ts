/**
 * Aurora Cognitive Event Loop
 * 
 * Unified orchestration of Aurora's internal reasoning cycle:
 * Perception → Reasoning → Action → Reflection → Learning
 * 
 * All internal, no external APIs required.
 */

import { getNexusV3Client, type ConsciousnessState } from './nexus-v3-client';
import { getMemoryFabricClient } from './memory-fabric-client';

const nexusV3 = getNexusV3Client();
const memoryFabric = getMemoryFabricClient();

export interface CognitiveEvent {
  type: 'perception' | 'reasoning' | 'action' | 'reflection' | 'learning';
  source: string;
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface CognitiveContext {
  consciousness: ConsciousnessState | null;
  memoryContext: string;
  facts: Record<string, any>;
  recentEvents: CognitiveEvent[];
}

export interface LearningFeedback {
  success: boolean;
  magnitude: number;
  category: string;
  details?: string;
}

class CognitiveLoopManager {
  private eventHistory: CognitiveEvent[] = [];
  private learningBuffer: LearningFeedback[] = [];
  private readonly maxHistorySize = 100;

  /**
   * Phase 1: Perception - Process incoming input
   */
  async perceive(input: string, sessionId: string): Promise<CognitiveEvent> {
    const event: CognitiveEvent = {
      type: 'perception',
      source: 'user-input',
      content: input,
      timestamp: new Date().toISOString(),
      metadata: { sessionId, inputLength: input.length }
    };

    this.recordEvent(event);
    
    await nexusV3.reportCognitiveEvent({
      event_type: 'perception',
      source: 'cognitive-loop',
      message: `Perceived input: ${input.substring(0, 100)}`,
      context: { sessionId },
      importance: 0.7
    }).catch(() => {});

    return event;
  }

  /**
   * Phase 2: Context Retrieval - Gather relevant memories
   */
  async retrieveContext(query: string): Promise<CognitiveContext> {
    const [consciousnessResult, factsResult, contextResult] = await Promise.all([
      nexusV3.getConsciousnessState().catch(() => null),
      memoryFabric.getFacts().catch(() => ({ success: false, facts: {} })),
      memoryFabric.getContext().catch(() => ({ success: false, context: '' }))
    ]);

    const context: CognitiveContext = {
      consciousness: consciousnessResult,
      memoryContext: contextResult.success && contextResult.context ? contextResult.context : '',
      facts: factsResult.success && factsResult.facts ? factsResult.facts : {},
      recentEvents: this.eventHistory.slice(-10)
    };

    await nexusV3.reportCognitiveEvent({
      event_type: 'context_retrieval',
      source: 'cognitive-loop',
      message: `Retrieved context for: ${query.substring(0, 50)}`,
      context: { 
        factCount: Object.keys(context.facts).length,
        hasConsciousness: !!context.consciousness
      },
      importance: 0.5
    }).catch(() => {});

    return context;
  }

  /**
   * Phase 3: Reasoning - Process through Luminar Nexus V2
   */
  async reason(input: string, context: CognitiveContext): Promise<CognitiveEvent> {
    const event: CognitiveEvent = {
      type: 'reasoning',
      source: 'luminar-nexus-v2',
      content: `Processing: ${input}`,
      timestamp: new Date().toISOString(),
      metadata: {
        consciousnessState: context.consciousness?.consciousness_state,
        awarenessLevel: context.consciousness?.awareness_level,
        contextLength: context.memoryContext.length
      }
    };

    this.recordEvent(event);

    await nexusV3.reportCognitiveEvent({
      event_type: 'reasoning',
      source: 'cognitive-loop',
      message: `Reasoning about: ${input.substring(0, 50)}`,
      context: event.metadata,
      importance: 0.8
    }).catch(() => {});

    return event;
  }

  /**
   * Phase 4: Action - Execute the determined action
   */
  async executeAction(
    actionType: 'chat' | 'synthesis' | 'task',
    content: string,
    result: string
  ): Promise<CognitiveEvent> {
    const event: CognitiveEvent = {
      type: 'action',
      source: actionType === 'synthesis' ? 'aurora-x-core' : 
              actionType === 'task' ? 'nexus-worker' : 'luminar-nexus-v2',
      content: result,
      timestamp: new Date().toISOString(),
      metadata: { actionType, inputLength: content.length, outputLength: result.length }
    };

    this.recordEvent(event);

    await nexusV3.reportCognitiveEvent({
      event_type: 'action_executed',
      source: 'cognitive-loop',
      message: `Executed ${actionType}: ${result.substring(0, 50)}`,
      context: event.metadata,
      importance: 0.6
    }).catch(() => {});

    return event;
  }

  /**
   * Phase 5: Reflection - Store outcomes and update memory
   */
  async reflect(
    input: string,
    output: string,
    context: CognitiveContext
  ): Promise<CognitiveEvent> {
    const event: CognitiveEvent = {
      type: 'reflection',
      source: 'memory-fabric-v2',
      content: `Stored interaction: ${input.substring(0, 50)} → ${output.substring(0, 50)}`,
      timestamp: new Date().toISOString(),
      metadata: {
        inputHash: this.simpleHash(input),
        outputHash: this.simpleHash(output)
      }
    };

    this.recordEvent(event);

    await Promise.all([
      memoryFabric.saveMessage('user', input, 0.7, ['input']),
      memoryFabric.saveMessage('assistant', output, 0.6, ['response'])
    ]).catch(() => {});

    await nexusV3.reportCognitiveEvent({
      event_type: 'reflection',
      source: 'cognitive-loop',
      message: `Reflected on interaction`,
      context: event.metadata,
      importance: 0.5
    }).catch(() => {});

    return event;
  }

  /**
   * Phase 6: Learning - Adaptive Bias Update
   */
  async learn(feedback: LearningFeedback): Promise<CognitiveEvent> {
    this.learningBuffer.push(feedback);

    const event: CognitiveEvent = {
      type: 'learning',
      source: 'adaptive-bias-scheduler',
      content: `Learning feedback: ${feedback.category} - ${feedback.success ? 'success' : 'failure'}`,
      timestamp: new Date().toISOString(),
      metadata: {
        success: feedback.success,
        magnitude: feedback.magnitude,
        category: feedback.category,
        bufferSize: this.learningBuffer.length
      }
    };

    this.recordEvent(event);

    if (this.learningBuffer.length >= 5) {
      await this.flushLearningBuffer();
    }

    await nexusV3.reportCognitiveEvent({
      event_type: 'learning',
      source: 'cognitive-loop',
      message: `Learning: ${feedback.category}`,
      context: event.metadata,
      importance: 0.7
    }).catch(() => {});

    return event;
  }

  /**
   * Complete cognitive cycle for a user message
   */
  async processMessage(
    input: string,
    sessionId: string,
    actionType: 'chat' | 'synthesis' | 'task' = 'chat'
  ): Promise<{
    context: CognitiveContext;
    events: CognitiveEvent[];
  }> {
    const cycleEvents: CognitiveEvent[] = [];

    const perceptionEvent = await this.perceive(input, sessionId);
    cycleEvents.push(perceptionEvent);

    const context = await this.retrieveContext(input);

    const reasoningEvent = await this.reason(input, context);
    cycleEvents.push(reasoningEvent);

    return { context, events: cycleEvents };
  }

  /**
   * Complete the cycle after response generation
   */
  async completeCycle(
    input: string,
    output: string,
    context: CognitiveContext,
    success: boolean = true
  ): Promise<CognitiveEvent[]> {
    const events: CognitiveEvent[] = [];

    const actionEvent = await this.executeAction('chat', input, output);
    events.push(actionEvent);

    const reflectionEvent = await this.reflect(input, output, context);
    events.push(reflectionEvent);

    const learningEvent = await this.learn({
      success,
      magnitude: success ? 1.0 : 0.5,
      category: 'conversation',
      details: success ? 'Response generated' : 'Fallback used'
    });
    events.push(learningEvent);

    return events;
  }

  private async flushLearningBuffer(): Promise<void> {
    const successRate = this.learningBuffer.filter(f => f.success).length / this.learningBuffer.length;
    
    console.log(`[CognitiveLoop] Learning flush: ${this.learningBuffer.length} events, ${(successRate * 100).toFixed(1)}% success`);
    
    this.learningBuffer = [];
  }

  private recordEvent(event: CognitiveEvent): void {
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(-this.maxHistorySize);
    }
  }

  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }

  getEventHistory(): CognitiveEvent[] {
    return [...this.eventHistory];
  }

  getStats(): { totalEvents: number; byType: Record<string, number> } {
    const byType: Record<string, number> = {};
    for (const event of this.eventHistory) {
      byType[event.type] = (byType[event.type] || 0) + 1;
    }
    return { totalEvents: this.eventHistory.length, byType };
  }
}

let instance: CognitiveLoopManager | null = null;

export function getCognitiveLoop(): CognitiveLoopManager {
  if (!instance) {
    instance = new CognitiveLoopManager();
  }
  return instance;
}

export { CognitiveLoopManager };
