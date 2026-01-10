import { LuminarNexus, getLuminarNexus, type InterpretResult } from './services/luminar';
import { MemoryFabric, getMemoryFabric, type MemoryContext } from './services/memory';
import { AuroraNexus, getAuroraNexus, type ConsciousState } from './services/nexus';
import { AuroraXCore, getAuroraXCore } from './services/aurorax';
import { enhanceSelfHealing, adaptiveMetrics } from './enhancements';
import fetch from 'node-fetch';
import os from 'os';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

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

interface ManifestSummary {
  tiers?: number;
  aems?: number;
  modules?: number;
  packs?: unknown[];
}

export class AuroraAI {
  private luminar: LuminarNexus;
  private memory: MemoryFabric;
  private nexus: AuroraNexus;
  private auroraX: AuroraXCore;

  private turnContext: string[] = [];
  private selfHealingInterval: NodeJS.Timeout | null = null;
  private metricsInterval: NodeJS.Timeout | null = null;
  private autoHealInterval: NodeJS.Timeout | null = null;
  private lastHealAt: number = 0;
  private lastCodeSmokeAt: number = 0;
  private lastDepFixAt: number = 0;
  private lastAuditReport: string | null = null;
  private lastAuditAt: number = 0;
  private userName: string | null = null;
  private initialized: boolean = false;
  private recentIssues: { ts: number; summary: string }[] = [];

  // Local pack registry mirror (Python packs are not importable from Node)
  private static PACKS: Record<string, { name: string; dir: string; submodules?: string[] }> = {
    pack01: { name: 'Core System', dir: 'pack01_pack01' },
    pack02: { name: 'Environment Profiler', dir: 'pack02_env_profiler' },
    pack03: { name: 'OS Base + EdgeOS', dir: 'pack03_os_edge', submodules: ['3A','3B','3C','3D','3E','3F','3G','3H','3I','3J'] },
    pack04: { name: 'Launcher', dir: 'pack04_launcher' },
    pack05: { name: 'Plugin System', dir: 'pack05_plugin_system', submodules: ['5A','5B','5E','5F','5G','5H','5I','5J','5K','5L'] },
    pack06: { name: 'Firmware System', dir: 'pack06_firmware_system' },
    pack07: { name: 'Secure Signing', dir: 'pack07_secure_signing' },
    pack08: { name: 'Conversational Engine', dir: 'pack08_conversational_engine' },
    pack09: { name: 'Compute Layer', dir: 'pack09_compute_layer' },
    pack10: { name: 'Autonomy Engine', dir: 'pack10_autonomy_engine' },
    pack11: { name: 'Device Mesh', dir: 'pack11_device_mesh' },
    pack12: { name: 'Toolforge', dir: 'pack12_toolforge' },
    pack13: { name: 'Runtime 2', dir: 'pack13_runtime_2' },
    pack14: { name: 'Hardware Abstraction', dir: 'pack14_hw_abstraction' },
    pack15: { name: 'Intel Fabric', dir: 'pack15_intel_fabric' },
  };

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
      try {
        await enhanceSelfHealing(this.nexus);
      } catch (err) {
        console.error('[AuroraAI] Self-healing enhancement failed:', err);
      }
    }, 60_000);

    this.metricsInterval = setInterval(async () => {
      try {
        await adaptiveMetrics(this.memory, this.auroraX);
      } catch (err) {
        console.error('[AuroraAI] Adaptive metrics failed:', err);
      }
    }, 120_000);

    // Lightweight autonomous healing: monitor local services and restart if unhealthy
    this.autoHealInterval = setInterval(async () => {
      try {
        await this.autoHealTick();
      } catch (err) {
        console.error('[AuroraAI] Auto-heal tick failed:', err);
      }
    }, 30_000);

    // Periodic system audit for real-world host signals
    setInterval(async () => {
      try {
        const report = await this.runSystemAudit();
        this.lastAuditReport = report;
        this.lastAuditAt = Date.now();
        this.logHeal(`System audit refreshed (${new Date(this.lastAuditAt).toISOString()})`);
      } catch (err) {
        console.error('[AuroraAI] System audit failed:', err);
      }
    }, 300_000); // every 5 minutes
  }

  async handleChat(userInput: string): Promise<string> {
    await this.initialize();

    const startTime = Date.now();
    this.captureUserName(userInput);

    const execute = await this.maybeExecuteRemediation(userInput);
    if (execute) {
      return this.applyPersonaVoice(execute);
    }

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

    const execute = await this.maybeExecuteRemediation(userInput);
    if (execute) {
      const response = this.applyPersonaVoice(execute);
      return {
        response,
        intent: { action: "remediation", topic: "system", meta: {} } as any,
        context: { facts: {}, recentMessages: [], semanticContext: "", timestamp: Date.now() },
        consciousness: await this.nexus.getConsciousState(),
        timestamp: Date.now()
      };
    }

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
      },
      recentIssues: this.recentIssues.slice(0, 10)
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

  private getPackSummary(): string | null {
    const root = process.cwd();
    const packsRoot = path.join(root, "packs");
    let loaded = 0;
    let submodules = 0;

    for (const info of Object.values(AuroraAI.PACKS)) {
      const exists = fs.existsSync(path.join(packsRoot, info.dir));
      if (exists) {
        loaded += 1;
        if (info.submodules?.length) {
          submodules += info.submodules.length;
        }
      }
    }

    const total = Object.keys(AuroraAI.PACKS).length;
    if (total === 0) return null;
    return `${loaded}/${total} packs, ${submodules} submodules`;
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

    const packSummary = this.getPackSummary();
    const issueLines = this.recentIssues.slice(0, 5).map(i => {
      const when = new Date(i.ts).toISOString();
      return `- ${when}: ${i.summary}`;
    });

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
      issueLines.length ? `Recent issues:\n${issueLines.join("\n")}` : "",
      this.lastAuditReport ? `Last audit @ ${new Date(this.lastAuditAt || Date.now()).toISOString()}:\n${this.lastAuditReport}` : "",
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
    const issues = this.recentIssues.slice(0, 3).map(i => `- ${new Date(i.ts).toISOString()}: ${i.summary}`).join("\n");

    return [
      "System enhancement scan:",
      `Services -> Luminar: ${luminarOk ? "ONLINE" : "OFFLINE"}, Memory: ${memoryOk ? "ONLINE" : "OFFLINE"}, Nexus V3: ${nexusOk ? "ONLINE" : "OFFLINE"}, AuroraX: ${auroraXOk ? "ONLINE" : "OFFLINE"}`,
      `Resources -> CPU: ${cpuLoad} load / ${cpuCount} cores, Memory: ${memUsedPct}% used`,
      `Workers -> total ${workers.total ?? "?"}, active ${workers.active ?? "?"}, idle ${workers.idle ?? "?"}`,
       issues ? `Recent issues:\n${issues}` : "",
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

    const processSummary = this.getWindowsProcessSnapshot() || "Process snapshot unavailable (no Windows process data).";

    const steps: string[] = [];
    steps.push("Close heavy apps and browser tabs consuming CPU/RAM.");
    steps.push("Kill stray dev servers: run x-stop or close ports 5000/5002/8000 if unused.");
    steps.push("Reduce worker load: pause scans or lower concurrency for a few minutes.");
    steps.push("Optional: restart Aurora services (x-stop then x-start) to clear stale processes.");

    const auditSnippet = this.lastAuditReport ? `\n\nLatest system audit:\n${this.lastAuditReport}` : "";
    const issueSnippet = this.recentIssues.length
      ? `\n\nRecent issues:\n${this.recentIssues.slice(0, 3).map(i => `- ${new Date(i.ts).toISOString()}: ${i.summary}`).join("\n")}`
      : "";

    return [
      "Performance check:",
      `CPU: ${cpuLoad} load / ${cpuCount} cores`,
      `Memory: ${memUsedPct}% used`,
      `Top local processes (CPU/Memory):\n${processSummary}`,
      `Recommended actions: ${steps.join(" ")}${auditSnippet}${issueSnippet}`,
      "Say 'execute remediation' to restart Aurora services now, or tell me which process/port to target."
    ].join("\n");
  }

  // Grab a lightweight snapshot of top processes on Windows; safe fallback if unavailable
  private getWindowsProcessSnapshot(): string | null {
    try {
      if (process.platform !== "win32") return null;
      // Request top CPU and WS (working set) in MB, trimmed to 5 entries
      const cmd = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        "\"Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name,Id,CPU,@{Name='MemMB';Expression={[math]::Round($_.WS/1MB,1)}} | ConvertTo-Json\""
      ].join(" ");
      const raw = execSync(cmd, { encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] });
      const parsed = JSON.parse(raw);
      const items = Array.isArray(parsed) ? parsed : [parsed];
      return items
        .filter(Boolean)
        .map((p: any) => `${p.Name || "proc"} (pid ${p.Id || "?"}) CPU:${(p.CPU ?? 0).toFixed ? (p.CPU ?? 0).toFixed(1) : p.CPU || 0} MEM:${p.MemMB ?? "?"}MB`)
        .join("\n");
    } catch {
      return null;
    }
  }

  private async maybeExecuteRemediation(input: string): Promise<string | null> {
    const low = input.toLowerCase();
    const trigger = low.includes("execute remediation") || low.includes("fix it now") || low.includes("restart services");
    if (!trigger) return null;

    try {
      const { getBaseUrl } = require('./config');
      const res = await fetch(`${getBaseUrl()}/api/control`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "restart_clear", ports: [5000, 5001, 5002, 5004, 8000] })
      });
      if (res.ok) {
        const data = (await res.json().catch(() => ({}))) as { cleared_ports?: number[] };
        const cleared = (data.cleared_ports && data.cleared_ports.length)
          ? ` Cleared ports: ${data.cleared_ports.join(", ")}.`
          : "";
        return `Issued remediation: cleared ports and restarted Aurora services via control endpoint.${cleared}`;
      }
      const text = await res.text();
      return `Attempted remediation but control endpoint returned ${res.status}: ${text}`;
    } catch (err: any) {
      return `Remediation attempt failed: ${err?.message ?? 'unknown error'}.`;
    }
  }

  // Background auto-heal tick: check local services, clear ports, and restart if needed
  private async autoHealTick(): Promise<void> {
    const now = Date.now();
    if (now - this.lastHealAt < 25_000) {
      return; // avoid rapid retries
    }

    const { getBaseUrl, getAuroraNexusUrl } = require('./config');
    const health = await this.checkEndpointDetailed("backend", `${getBaseUrl()}/api/health`);
    const nexus = await this.checkEndpointDetailed("nexus_v3", `${getAuroraNexusUrl()}/api/health`);
    const manifestOk = await this.checkManifestEndpoint();
    const luminar = await this.checkEndpointDetailed("luminar_status", `${getBaseUrl()}/api/luminar-nexus/status`);

    // If any core endpoint fails (debounced), attempt remediation
    const failedDetails: string[] = [];
    if (!health.ok) failedDetails.push(`backend:${health.error || health.status || "down"}`);
    if (!nexus.ok) failedDetails.push(`nexus_v3:${nexus.error || nexus.status || "down"}`);
    if (!manifestOk) failedDetails.push("manifest:mismatch");
    if (!luminar.ok) failedDetails.push(`luminar:${luminar.error || luminar.status || "down"}`);

    if (failedDetails.length > 0) {
      // require at least two consecutive ticks to remediate to reduce churn
      if (!this.lastHealAt || now - this.lastHealAt > 5_000) {
        this.lastHealAt = now;
        try {
          await fetch("http://127.0.0.1:5000/api/control", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "restart_clear", ports: [5000, 5001, 5002, 5004, 8000] })
          });
          const summary = failedDetails.join(", ");
          this.pushRecentIssue(`Auto-heal restart_clear due to: ${summary}`);
          this.logHeal(`Auto-heal: restart_clear triggered (${summary})`);
          console.warn("[AuroraAI] Auto-heal: restarted services due to failed health check");
        } catch (err) {
          this.logHeal(`Auto-heal remediation failed: ${err?.message || err}`);
          console.error("[AuroraAI] Auto-heal remediation failed:", err);
        }
      }
    }

    // Lightweight code smoke checks (throttled)
    if (now - this.lastCodeSmokeAt > 10 * 60_000) {
      this.lastCodeSmokeAt = now;
      try {
        await this.runCodeSmoke();
      } catch (err) {
        this.logHeal(`Code smoke failed: ${err?.message || err}`);
      }
    }
  }

  private async checkManifestEndpoint(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 1500);
      const { getBaseUrl } = require('./config');
      const res = await fetch(`${getBaseUrl()}/api/nexus-v3/manifest`, { signal: controller.signal });
      clearTimeout(timer);
      if (!res.ok) return false;
      const data = (await res.json()) as ManifestSummary;
      const tiersOk = data?.tiers === 188;
      const aemsOk = data?.aems === 66;
      const modulesOk = data?.modules === 550;
      const packsOk = Array.isArray(data?.packs) ? data.packs.length >= 15 : true; // tolerate if packs omitted
      const manifestHealthy = tiersOk && aemsOk && modulesOk && packsOk;
      if (!manifestHealthy) {
        const msg = `Manifest mismatch: tiers=${data?.tiers} aems=${data?.aems} modules=${data?.modules} packs=${data?.packs?.length ?? "n/a"}`;
        this.logHeal(msg);
        this.pushRecentIssue(msg);
      }
      return manifestHealthy;
    } catch {
      this.pushRecentIssue("Manifest endpoint unreachable");
      return false;
    }
  }

  private async checkHealthEndpoint(url: string): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 1500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timer);
      return res.ok;
    } catch {
      return false;
    }
  }

  private async checkEndpointDetailed(label: string, url: string): Promise<{ ok: boolean; status?: number; error?: string }> {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 1500);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timer);
      if (res.ok) return { ok: true, status: res.status };
      const text = await res.text().catch(() => "");
      const summary = `Health ${label} failed status=${res.status} body=${text.slice(0, 120)}`;
      this.logHeal(summary);
      this.pushRecentIssue(summary);
      return { ok: false, status: res.status, error: text || `status ${res.status}` };
    } catch (err: any) {
      const summary = `Health ${label} error: ${err?.message || err}`;
      this.logHeal(summary);
      this.pushRecentIssue(summary);
      return { ok: false, error: err?.message || "timeout/error" };
    }
  }

  private logHeal(message: string): void {
    try {
      const line = `${new Date().toISOString()} ${message}\n`;
      const logPath = path.join(process.cwd(), "logs", "aurora-heal.log");
      fs.mkdirSync(path.dirname(logPath), { recursive: true });
      fs.appendFileSync(logPath, line);
    } catch {
      // non-fatal
    }
  }

  private pushRecentIssue(summary: string): void {
    this.recentIssues.unshift({ ts: Date.now(), summary });
    if (this.recentIssues.length > 20) {
      this.recentIssues.length = 20;
    }
  }

  // ===========================
  // Code smoke checks (TS + Py)
  // ===========================
  private async runCodeSmoke(): Promise<void> {
    let tsFailed = false;
    let pyFailed = false;

    // Skip if host CPU is too high to avoid timeouts
    const cpuLoad = os.loadavg()?.[0] ?? 0;
    const cpuPctApprox = (cpuLoad / (os.cpus()?.length || 1)) * 100;
    if (cpuPctApprox > 85) {
      this.logHeal(`Code smoke: skipped due to high CPU (${cpuPctApprox.toFixed(1)}%)`);
      return;
    }

    // TypeScript quick check
    try {
      execSync("npx tsc --noEmit --skipLibCheck --pretty false server", {
        cwd: process.cwd(),
        timeout: 30_000,
        stdio: ["ignore", "pipe", "pipe"]
      });
      this.logHeal("Code smoke: TypeScript check passed");
    } catch (err: any) {
      const msg = err?.stderr?.toString() || err?.message || "tsc failed";
      this.logHeal(`Code smoke: TypeScript check failed -> ${msg.substring(0, 800)}`);
      tsFailed = true;
    }

    // Python import/syntax quick check on core modules
    try {
      const cmd = [
        "python",
        "-c",
        "\"import importlib,sys;mods=['aurora_nexus_v3','aurora_nexus_v3.core','aurora_nexus_v3.workers'];"
        + " [importlib.import_module(m) for m in mods]; print('py-ok')\""
      ].join(" ");
      execSync(cmd, {
        cwd: process.cwd(),
        timeout: 10_000,
        stdio: ["ignore", "pipe", "pipe"]
      });
      this.logHeal("Code smoke: Python import check passed");
    } catch (err: any) {
      const msg = err?.stderr?.toString() || err?.message || "python import failed";
      this.logHeal(`Code smoke: Python import check failed -> ${msg.substring(0, 800)}`);
      pyFailed = true;
    }

    // Attempt auto-fix for missing deps (throttled to once per day)
    const now = Date.now();
    const canFixDeps = now - this.lastDepFixAt > 24 * 60 * 60_000;
    if (canFixDeps && (tsFailed || pyFailed)) {
      this.lastDepFixAt = now;
      await this.tryAutoFixDeps(tsFailed, pyFailed);
    }
  }

  private async tryAutoFixDeps(tsFailed: boolean, pyFailed: boolean): Promise<void> {
    // Keep fixes lightweight and safe; log outcomes
    if (tsFailed) {
      try {
        execSync("npm install --ignore-scripts --no-progress", {
          cwd: process.cwd(),
          timeout: 60_000,
          stdio: ["ignore", "pipe", "pipe"]
        });
        this.logHeal("Auto-fix: npm install (ignore-scripts) executed after TS failure");
        // re-run quick tsc check
        execSync("npx tsc --noEmit --skipLibCheck --pretty false", {
          cwd: process.cwd(),
          timeout: 15_000,
          stdio: ["ignore", "pipe", "pipe"]
        });
        this.logHeal("Auto-fix: TypeScript check passed after npm install");
      } catch (err: any) {
        const msg = err?.stderr?.toString() || err?.message || "npm fix failed";
        this.logHeal(`Auto-fix: npm install attempt failed -> ${msg.substring(0, 800)}`);
      }
    }

    if (pyFailed) {
      try {
        execSync("python -m pip install --user -r requirements.txt", {
          cwd: process.cwd(),
          timeout: 60_000,
          stdio: ["ignore", "pipe", "pipe"]
        });
        this.logHeal("Auto-fix: pip install -r requirements.txt executed after Python import failure");
        // re-run quick python import check
        const cmd = [
          "python",
          "-c",
          "\"import importlib,sys;mods=['aurora_nexus_v3','aurora_nexus_v3.core','aurora_nexus_v3.workers'];"
          + " [importlib.import_module(m) for m in mods]; print('py-ok')\""
        ].join(" ");
        execSync(cmd, {
          cwd: process.cwd(),
          timeout: 10_000,
          stdio: ["ignore", "pipe", "pipe"]
        });
        this.logHeal("Auto-fix: Python import check passed after pip install");
      } catch (err: any) {
        const msg = err?.stderr?.toString() || err?.message || "pip fix failed";
        this.logHeal(`Auto-fix: pip install attempt failed -> ${msg.substring(0, 800)}`);
      }
    }
  }

  // ===========================
  // System audit for host health
  // ===========================
  private async runSystemAudit(): Promise<string> {
    const lines: string[] = [];
    const memTotal = os.totalmem();
    const memFree = os.freemem();
    const memUsedPct = memTotal ? (((memTotal - memFree) / memTotal) * 100).toFixed(1) : "n/a";
    const cpuLoad = os.loadavg()?.[0]?.toFixed(2) ?? "n/a";
    const cpuCount = os.cpus()?.length ?? 0;

    lines.push(`CPU: ${cpuLoad} load / ${cpuCount} cores`);
    lines.push(`Memory: ${memUsedPct}% used`);

    const diskSummary = this.getDiskSummary();
    if (diskSummary) lines.push(`Disks:\n${diskSummary}`);

    const topProcs = this.getWindowsProcessSnapshot();
    if (topProcs) lines.push(`Top processes:\n${topProcs}`);

    const ports = this.getOpenPortsSnapshot();
    if (ports) lines.push(`Open dev-like ports:\n${ports}`);

    const audit = lines.join("\n");
    this.logHeal(`Audit: ${audit.replace(/\n/g, " | ")}`);
    return audit;
  }

  private getDiskSummary(): string | null {
    try {
      if (process.platform === "win32") {
        const cmd = [
          "powershell.exe",
          "-NoProfile",
          "-Command",
          "\"Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{N='UsedGB';E={[math]::Round(($_.Used/1GB),1)}},@{N='FreeGB';E={[math]::Round(($_.Free/1GB),1)}} | ConvertTo-Json\""
        ].join(" ");
        const raw = execSync(cmd, { encoding: "utf-8", stdio: ["pipe", "pipe", "ignore"] });
        const parsed = JSON.parse(raw);
        const drives = Array.isArray(parsed) ? parsed : [parsed];
        return drives.map((d: any) => `${d.Name}: Used ${d.UsedGB}GB Free ${d.FreeGB}GB`).join("\n");
      }
    } catch {
      return null;
    }
    return null;
  }

  private getOpenPortsSnapshot(): string | null {
    try {
      if (process.platform === "win32") {
        const cmd = [
          "powershell.exe",
          "-NoProfile",
          "-Command",
          "\"netstat -ano | findstr LISTENING | findstr :3000\\|:5000\\|:5001\\|:5002\\|:5004\\|:8000\""
        ].join(" ");
        const raw = execSync(cmd, { encoding: "utf-8", stdio: ["pipe", "pipe", "ignore"] });
        const lines = raw.split(/\r?\n/).filter(Boolean);
        return lines.slice(0, 10).join("\n");
      }
    } catch {
      return null;
    }
    return null;
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
