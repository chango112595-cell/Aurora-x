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

    console.log('[AuroraAI] Initializing orchestrator...');

    const [luminarOk, memoryOk, nexusOk, auroraXOk] = await Promise.all([
      this.luminar.checkHealth(),
      this.memory.checkHealth(),
      this.nexus.checkHealth(),
      this.auroraX.checkHealth()
    ]);

    console.log('[AuroraAI] Service status:');
    console.log(`  - Luminar Nexus V2: ${luminarOk ? '✅ connected' : '⚠️ offline'}`);
    console.log(`  - Memory Fabric V2: ${memoryOk ? '✅ connected' : '⚠️ offline'}`);
    console.log(`  - Aurora Nexus V3:  ${nexusOk ? '✅ connected' : '⚠️ offline'}`);
    console.log(`  - Aurora-X Core:    ${auroraXOk ? '✅ connected' : '⚠️ offline'}`);

    this.startEnhancements();
    this.initialized = true;
    
    console.log('[AuroraAI] ✅ Orchestrator initialized');
  }

  private startEnhancements(): void {
    this.selfHealingInterval = setInterval(async () => {
      await enhanceSelfHealing(this.nexus);
    }, 60000);

    this.metricsInterval = setInterval(async () => {
      await adaptiveMetrics(this.memory, this.auroraX);
    }, 120000);

    console.log('[AuroraAI] Enhancement hooks started (self-healing: 60s, metrics: 120s)');
  }

  async handleChat(userInput: string): Promise<string> {
    await this.initialize();

    const startTime = Date.now();

    const [context, state] = await Promise.all([
      this.memory.retrieveContext(userInput),
      this.nexus.getConsciousState()
    ]);

    console.log(`[AuroraAI] 🧠 Context retrieved in ${Date.now() - startTime}ms`);
    console.log(`[AuroraAI] 🌌 Consciousness: ${state.state} | Workers: ${state.workers.idle}/${state.workers.total}`);

    const intent = await this.luminar.interpret(userInput, context, state);
    console.log(`[AuroraAI] 🎯 Intent: ${intent.action} (confidence: ${(intent.confidence * 100).toFixed(0)}%)`);

    let result: string;
    switch (intent.action) {
      case 'synthesize':
        console.log('[AuroraAI] ⚡ Executing code synthesis...');
        result = await this.auroraX.synthesize(intent.spec);
        break;
        
      case 'reflect':
        console.log('[AuroraAI] 💭 Reflecting on topic...');
        result = await this.luminar.reflect(intent.topic ?? userInput, context);
        break;
        
      case 'queryMemory':
        console.log('[AuroraAI] 🔍 Querying memory...');
        result = await this.memory.query(intent.query ?? userInput);
        break;
        
      default:
        console.log('[AuroraAI] 💬 Generating response...');
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

    console.log(`[AuroraAI] ✅ Cycle complete in ${Date.now() - startTime}ms`);

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

  async synthesize(spec: any): Promise<string> {
    await this.initialize();
    return this.auroraX.synthesize(spec);
  }

  async analyze(input: string, context?: any): Promise<any> {
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
    console.log('[AuroraAI] Orchestrator shutdown complete');
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
