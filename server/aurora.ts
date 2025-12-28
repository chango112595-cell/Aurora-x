import { LuminarNexus, getLuminarNexus, type InterpretResult } from './services/luminar';
import { MemoryFabric, getMemoryFabric, type MemoryContext } from './services/memory';
import { AuroraNexus, getAuroraNexus, type ConsciousState } from './services/nexus';
import { AuroraXCore, getAuroraXCore } from './services/aurorax';
import { enhanceSelfHealing, adaptiveMetrics } from './enhancements';
import os from 'os';

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

    const perf = await this.maybeHandlePerformanceConcerns(userInput);
    if (perf) {
      return this.applyPersonaVoice(perf);
    }

    const proactive = await this.maybeHandleEnhanceOrAnalyze(userInput);
    if (proactive) {
      return this.applyPersonaVoice(proactive);
    }

    const systemIntercept = await this.maybeHandleSystemQuery(userInput);
    if (systemIntercept) {
      return this.applyPersonaVoice(systemIntercept);
    }

    const intercept = this.maybeHandleNameQuery(userInput);
    if (intercept) {
      return this.applyPersonaVoice(intercept);
    }

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

    const perf = await this.maybeHandlePerformanceConcerns(userInput);
    if (perf) {
      const response = this.applyPersonaVoice(perf);
      return {
        response,
        intent: { action: "performance", topic: "system", meta: {} } as any,
        context: { facts: {}, recentMessages: [], semanticContext: "", timestamp: Date.now() },
        consciousness: await this.nexus.getConsciousState(),
        timestamp: Date.now()
      };
    }

    const proactive = await this.maybeHandleEnhanceOrAnalyze(userInput);
    if (proactive) {
      const response = this.applyPersonaVoice(proactive);
      return {
        response,
        intent: { action: "system_enhancement", topic: "analysis", meta: {} } as any,
        context: { facts: {}, recentMessages: [], semanticContext: "", timestamp: Date.now() },
        consciousness: await this.nexus.getConsciousState(),
        timestamp: Date.now()
      };
    }

    const systemIntercept = await this.maybeHandleSystemQuery(userInput);
    if (systemIntercept) {
      const response = this.applyPersonaVoice(systemIntercept);
      return {
        response,
        intent: { action: "system_diagnostics", topic: "status", meta: {} } as any,
        context: { facts: {}, recentMessages: [], semanticContext: "", timestamp: Date.now() },
        consciousness: await this.nexus.getConsciousState(),
        timestamp: Date.now()
      };
    }

    const intercept = this.maybeHandleNameQuery(userInput);
    if (intercept) {
      const response = this.applyPersonaVoice(intercept);
      return {
        response,
        intent: { action: "smalltalk", topic: "identity", meta: {} } as any,
        context: { facts: {}, recentMessages: [], semanticContext: "", timestamp: Date.now() },
        consciousness: await this.nexus.getConsciousState(),
        timestamp: Date.now()
      };
    }

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

  private maybeHandleNameQuery(input: string): string | null {
    const low = input.toLowerCase();
    const asksName = low.includes("your name") || low.includes("know my name") || low.includes("remember my name") || low.includes("do you remember me");
    if (!asksName) return null;
    if (this.userName) {
      return `Yes, I remember. You are ${this.userName}.`;
    }
    return "I don’t have your name yet. Tell me once and I will remember for this session.";
  }

  private async maybeHandleSystemQuery(input: string): Promise<string | null> {
    const low = input.toLowerCase();
    const wantsStatus =
      low.includes("system status") ||
      low.includes("system analysis") ||
      low.includes("analyze system") ||
      low.includes("analyze your system") ||
      low.includes("analyze my computer") ||
      low.includes("system audit") ||
      low.trim() === "status" ||
      low.trim() === "diagnostics";

    if (!wantsStatus) return null;

    const [luminarOk, memoryOk, nexusOk, auroraXOk] = await Promise.all([
      this.luminar.checkHealth(),
      this.memory.checkHealth(),
      this.nexus.checkHealth(),
      this.auroraX.checkHealth()
    ]);
    const consciousness = await this.nexus.getConsciousState();

    let packSummary: string | null = null;
    try {
      // Lazy import to avoid startup cost if packs not needed
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { get_pack_summary } = require("packs");
      const summary = get_pack_summary();
      packSummary = `${summary.loaded_packs}/${summary.total_packs} packs, ${summary.total_submodules} submodules`;
    } catch {
      packSummary = null;
    }

    const workers = consciousness?.workers || { total: this.nexus.WORKER_COUNT, idle: 0, active: 0 };
    const services = [
      `Luminar: ${luminarOk ? "ONLINE" : "OFFLINE"}`,
      `Memory: ${memoryOk ? "ONLINE" : "OFFLINE"}`,
      `Nexus V3: ${nexusOk ? `ONLINE (${consciousness?.state ?? "unknown"})` : "OFFLINE"}`,
      `AuroraX: ${auroraXOk ? "ONLINE" : "OFFLINE"}`
    ].join(" | ");

    const recs: string[] = [];
    if (!luminarOk || !memoryOk || !nexusOk || !auroraXOk) {
      recs.push("Restart offline services via control panel or x-start.");
    }
    if ((workers.idle ?? 0) < (workers.total ?? 0) * 0.1) {
      recs.push("Worker pool under pressure; consider scaling or pausing heavy jobs.");
    }
    if (recs.length === 0) {
      recs.push("No critical faults detected.");
    }

    return [
      "Diagnostics report:",
      services,
      `Workers: total ${workers.total ?? "?"}, active ${workers.active ?? "?"}, idle ${workers.idle ?? "?"}`,
      packSummary ? `Packs: ${packSummary}` : "",
      `Recommendations: ${recs.join(" ")}`.trim()
    ]
      .filter(Boolean)
      .join("\n");
  }

  private async maybeHandleEnhanceOrAnalyze(input: string): Promise<string | null> {
    const low = input.toLowerCase();
    const wantsEnhance =
      low.includes("enhance") ||
      low.includes("optimize") ||
      low.includes("reprogram") ||
      low.includes("upgrade") ||
      low.includes("improve") ||
      low.includes("analyze system") ||
      low.includes("system analysis") ||
      low.includes("system structure") ||
      low.includes("structure") ||
      low.trim() === "analyze" ||
      low.trim() === "enhance";

    if (!wantsEnhance) return null;

    const [luminarOk, memoryOk, nexusOk, auroraXOk] = await Promise.all([
      this.luminar.checkHealth(),
      this.memory.checkHealth(),
      this.nexus.checkHealth(),
      this.auroraX.checkHealth()
    ]);
    const consciousness = await this.nexus.getConsciousState();
    const workers = consciousness?.workers || { total: this.nexus.WORKER_COUNT, idle: 0, active: 0 };

    const memTotal = os.totalmem();
    const memFree = os.freemem();
    const memUsedPct = memTotal ? (((memTotal - memFree) / memTotal) * 100).toFixed(1) : "n/a";
    const cpuLoad = os.loadavg()?.[0]?.toFixed(2) ?? "n/a";
    const cpuCount = os.cpus()?.length ?? 0;

    const recs: string[] = [];
    if (!luminarOk || !memoryOk || !nexusOk || !auroraXOk) {
      recs.push("Restart offline services (x-start or control panel).");
    }
    if (parseFloat(memUsedPct) > 85) {
      recs.push("Memory high: close heavy tasks or increase limits.");
    }
    if (parseFloat(cpuLoad) > cpuCount * 0.75) {
      recs.push("CPU busy: pause background jobs or scale worker pool.");
    }
    if ((workers.idle ?? 0) < (workers.total ?? 0) * 0.1) {
      recs.push("Worker pool saturated: consider scaling or deferring tasks.");
    }
    if (recs.length === 0) {
      recs.push("No critical faults detected. Standing by to execute.");
    }

    const capabilities = `I can execute: code fixes/generation, config tweaks, service restarts. Say "execute enhancements" to let me proceed, or give me a target (file/service) to patch.`;

    return [
      "System enhancement scan:",
      `Services -> Luminar: ${luminarOk ? "ONLINE" : "OFFLINE"}, Memory: ${memoryOk ? "ONLINE" : "OFFLINE"}, Nexus V3: ${nexusOk ? "ONLINE" : "OFFLINE"}, AuroraX: ${auroraXOk ? "ONLINE" : "OFFLINE"}`,
      `Resources -> CPU: ${cpuLoad} load / ${cpuCount} cores, Memory: ${memUsedPct}% used`,
      `Workers -> total ${workers.total ?? "?"}, active ${workers.active ?? "?"}, idle ${workers.idle ?? "?"}`,
      `Actions -> ${recs.join(" ")}`,
      capabilities
    ]
      .filter(Boolean)
      .join("\n");
  }

  private async maybeHandlePerformanceConcerns(input: string): Promise<string | null> {
    const low = input.toLowerCase();
    const flags = ["slow", "lag", "overloaded", "overload", "cpu", "performance", "fast", "faster", "scan"];
    const matches = flags.some(f => low.includes(f));
    if (!matches) return null;

    const memTotal = os.totalmem();
    const memFree = os.freemem();
    const memUsedPct = memTotal ? (((memTotal - memFree) / memTotal) * 100).toFixed(1) : "n/a";
    const cpuLoad = os.loadavg()?.[0]?.toFixed(2) ?? "n/a";
    const cpuCount = os.cpus()?.length ?? 0;

    const steps: string[] = [];
    steps.push("Close heavy apps and browser tabs consuming CPU/RAM.");
    steps.push("Kill stray dev servers: run x-stop or close ports 5000/5002/8000 if unused.");
    steps.push("Reduce worker load: pause scans or lower concurrency for a few minutes.");
    steps.push("Optional: restart Aurora services (x-stop then x-start) to clear stale processes.");

    return [
      "Performance check:",
      `CPU: ${cpuLoad} load / ${cpuCount} cores`,
      `Memory: ${memUsedPct}% used`,
      `Recommended actions: ${steps.join(" ")}`,
      "Tell me to execute a restart or target a process, and I’ll proceed."
    ].join("\n");
  }

  private applyPersonaVoice(base: string): string {
    return (base || "").trim();
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
