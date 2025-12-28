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
  private userName: string | null = null;
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
    this.captureUserName(userInput);

    const [context, state] = await Promise.all([
      this.memory.retrieveContext(userInput),
      this.nexus.getConsciousState()
    ]);

    const intent = await this.luminar.interpret(userInput, context, state);

    let result: string;
    try {
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
    } catch (error: any) {
      // Fallback to a local response if bridge services are unavailable
      const fallback = await this.luminar.respond(intent, context);
      result = `${fallback}\n\n[Aurora local mode] Bridge unavailable: ${error?.message ?? 'unknown error'}.`;
    }

    await Promise.all([
      this.memory.storeFact({
        userInput,
        response: result,
        intent,
        timestamp: Date.now()
      }),
      (async () => {
        try {
          await this.auroraX.adapt(intent, result);
        } catch {
          // Ignore adaptation errors in offline mode
        }
      })(),
      this.nexus.reportEvent('chat_cycle_complete', {
        action: intent.action,
        duration: Date.now() - startTime
      })
    ]);

    this.turnContext.push(userInput, result);
    if (this.turnContext.length > 20) {
      this.turnContext.splice(0, 2);
    }

    return this.applyPersonaVoice(result);
  }

  async handleChatFull(userInput: string): Promise<ChatResponse> {
    await this.initialize();

    this.captureUserName(userInput);

    const [context, consciousness] = await Promise.all([
      this.memory.retrieveContext(userInput),
      this.nexus.getConsciousState()
    ]);

    const intent = await this.luminar.interpret(userInput, context, consciousness);

    let response: string;
    try {
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
    } catch (error: any) {
      response = `${await this.luminar.respond(intent, context)}\n\n[Aurora local mode] Bridge unavailable: ${error?.message ?? 'unknown error'}.`;
    }

    await this.memory.storeFact({
      userInput,
      response,
      intent,
      timestamp: Date.now()
    });

    try {
      await this.auroraX.adapt(intent, response);
    } catch {
      // Ignore adaptation errors when bridge is offline
    }
    await this.nexus.reportEvent('chat_cycle_complete');

    this.turnContext.push(userInput, response);
    if (this.turnContext.length > 20) {
      this.turnContext.splice(0, 2);
    }

    return {
      response: this.applyPersonaVoice(response),
      intent,
      context,
      consciousness,
      timestamp: Date.now()
    };
  }

  async synthesize(spec: SynthesisSpec): Promise<string> {
    await this.initialize();
    try {
      return await this.auroraX.synthesize(spec);
    } catch (error: any) {
      return `[Aurora local mode] Unable to reach synthesis bridge. Draft for "${spec.request}": please run x-start or set AURORA_AUTO_START=1.\nReason: ${error?.message ?? 'unknown error'}`;
    }
  }

  async analyze(input: string, context?: AnalysisContext): Promise<Record<string, unknown>> {
    await this.initialize();
    try {
      return await this.auroraX.analyze(input, context);
    } catch (error: any) {
      return {
        success: false,
        message: "Aurora bridge unavailable; returning local placeholder analysis.",
        error: error?.message ?? "bridge offline",
        input,
      };
    }
  }

  async fix(code: string, issue: string): Promise<string> {
    await this.initialize();
    try {
      return await this.auroraX.fix(code, issue);
    } catch (error: any) {
      return `[Aurora local mode] Bridge unavailable, suggested fix for "${issue}":\n${code}\n\nError: ${error?.message ?? 'offline'}`;
    }
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

  private captureUserName(input: string) {
    if (this.userName) return;
    const match =
      input.match(/\b(?:my name is|i am|i['’]m|im)\s+([A-Za-z][\w\-]*)/i);
    if (match && match[1]) {
      const cleaned = match[1].replace(/[^\w\-]/g, "");
      this.userName = cleaned || this.userName;
      // best-effort persistence; ignore failures
      this.memory.saveMessage("profile", `user_name=${this.userName}`, 0.9, ["profile", "name"]).catch(() => {});
    }
  }

  private applyPersonaVoice(base: string): string {
    const name = this.userName || "Commander";
    const preface = `Acknowledged, ${name}.`;
    return `${preface} ${base}`;
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
