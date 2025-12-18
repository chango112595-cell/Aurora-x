import { LuminarNexus, getLuminarNexus, type InterpretResult } from './services/luminar';
import { MemoryFabric, getMemoryFabric, type MemoryContext } from './services/memory';
import { AuroraNexus, getAuroraNexus, type ConsciousState } from './services/nexus';
import { AuroraXCore, getAuroraXCore } from './services/aurorax';
import { enhanceSelfHealing, adaptiveMetrics } from './enhancements';

export interface ChatResponse {
  response: string;
  intent: InterpretResult;
  context: MemoryContext;
  consciousness: ConsciousState;
  timestamp: number;
}

import type { SynthesisSpec as AuroraXSynthesisSpec } from './services/aurorax';

type SynthesisSpec = AuroraXSynthesisSpec;

interface AnalysisContext {
  [key: string]: unknown;
}

export class AuroraAI {
  private luminar: LuminarNexus;
  private memory: MemoryFabric;
  private nexus: AuroraNexus;
  private auroraX: AuroraXCore;

  private turnContext: string[] = [];
  private selfHealingInterval: NodeJS.Timeout | null = null;
  private metricsInterval: NodeJS.Timeout | null = null;
  private initialized: boolean = false;

  constructor() {
    this.luminar = getLuminarNexus();
    this.memory = getMemoryFabric();
    this.nexus = getAuroraNexus();
    this.auroraX = getAuroraXCore();
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    const [luminarOk, memoryOk, nexusOk, auroraXOk] = await Promise.all([
      this.luminar.checkHealth(),
      this.memory.checkHealth(),
      this.nexus.checkHealth(),
      this.auroraX.checkHealth()
    ]);

    this.startEnhancements();
    this.initialized = true;
  }

  private startEnhancements(): void {
    this.selfHealingInterval = setInterval(async () => {
      await enhanceSelfHealing(this.nexus);
    }, 60000);

    this.metricsInterval = setInterval(async () => {
      await adaptiveMetrics(this.memory, this.auroraX);
    }, 120000);
  }

  async handleChat(userInput: string): Promise<string> {
    await this.initialize();

    const startTime = Date.now();

    const [context, state] = await Promise.all([
      this.memory.retrieveContext(userInput),
      this.nexus.getConsciousState()
    ]);

    const intent = await this.luminar.interpret(userInput, context, state);

    let result: string;
    switch (intent.action) {
      case 'synthesize':
        result = await this.auroraX.synthesize(intent.spec);
        break;
        
      case 'reflect':
        result = await this.luminar.reflect(intent.topic ?? userInput, context);
        break;
        
      case 'queryMemory':
        result = await this.memory.query(intent.query ?? userInput);
        break;
        
      default:
        result = await this.luminar.respond(intent, context);
    }

    await Promise.all([
      this.memory.storeFact({
        userInput,
        response: result,
        intent,
        timestamp: Date.now()
      }),
      this.auroraX.adapt(intent, result),
      this.nexus.reportEvent('chat_cycle_complete', {
        action: intent.action,
        duration: Date.now() - startTime
      })
    ]);

    this.turnContext.push(userInput, result);
    if (this.turnContext.length > 20) {
      this.turnContext.splice(0, 2);
    }

    return result;
  }

  async handleChatFull(userInput: string): Promise<ChatResponse> {
    await this.initialize();

    const [context, consciousness] = await Promise.all([
      this.memory.retrieveContext(userInput),
      this.nexus.getConsciousState()
    ]);

    const intent = await this.luminar.interpret(userInput, context, consciousness);

    let response: string;
    switch (intent.action) {
      case 'synthesize':
        response = await this.auroraX.synthesize(intent.spec);
        break;
      case 'reflect':
        response = await this.luminar.reflect(intent.topic ?? userInput, context);
        break;
      case 'queryMemory':
        response = await this.memory.query(intent.query ?? userInput);
        break;
      default:
        response = await this.luminar.respond(intent, context);
    }

    await this.memory.storeFact({
      userInput,
      response,
      intent,
      timestamp: Date.now()
    });

    await this.auroraX.adapt(intent, response);
    await this.nexus.reportEvent('chat_cycle_complete');

    this.turnContext.push(userInput, response);
    if (this.turnContext.length > 20) {
      this.turnContext.splice(0, 2);
    }

    return {
      response,
      intent,
      context,
      consciousness,
      timestamp: Date.now()
    };
  }

  async synthesize(spec: SynthesisSpec): Promise<string> {
    await this.initialize();
    return this.auroraX.synthesize(spec);
  }

  async analyze(input: string, context?: AnalysisContext): Promise<Record<string, unknown>> {
    await this.initialize();
    return this.auroraX.analyze(input, context);
  }

  async fix(code: string, issue: string): Promise<string> {
    await this.initialize();
    return this.auroraX.fix(code, issue);
  }

  async getStatus(): Promise<Record<string, unknown>> {
    const [luminarOk, memoryOk, nexusOk, auroraXOk] = await Promise.all([
      this.luminar.checkHealth(),
      this.memory.checkHealth(),
      this.nexus.checkHealth(),
      this.auroraX.checkHealth()
    ]);

    const consciousness = await this.nexus.getConsciousState();

    return {
      initialized: this.initialized,
      services: {
        luminar: luminarOk,
        memory: memoryOk,
        nexus: nexusOk,
        auroraX: auroraXOk
      },
      consciousness,
      turnContextSize: this.turnContext.length,
      enhancements: {
        selfHealing: this.selfHealingInterval !== null,
        adaptiveMetrics: this.metricsInterval !== null
      }
    };
  }

  getTurnContext(): string[] {
    return [...this.turnContext];
  }

  shutdown(): void {
    if (this.selfHealingInterval) {
      clearInterval(this.selfHealingInterval);
      this.selfHealingInterval = null;
    }
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
      this.metricsInterval = null;
    }
    this.initialized = false;
  }
}

let auroraInstance: AuroraAI | null = null;

export function getAuroraAI(): AuroraAI {
  if (!auroraInstance) {
    auroraInstance = new AuroraAI();
  }
  return auroraInstance;
}

export default AuroraAI;
