import { AuroraNexus } from './services/nexus';
import { MemoryFabric } from './services/memory';
import { AuroraXCore } from './services/aurorax';

export async function enhanceSelfHealing(nexus: AuroraNexus): Promise<void> {
  try {
    const status = await nexus.getConsciousState();

    if (!status.ok) {
      console.warn('[SelfHealing] Nexus health degraded; auto-recovery initiated.');
      await nexus.reportEvent('self_heal_trigger', {
        reason: 'health_check_failed',
        timestamp: Date.now()
      });
    } else {
      if (status.workers.idle < status.workers.total * 0.1) {
        console.warn('[SelfHealing] Worker pool under pressure, reporting for optimization.');
        await nexus.reportEvent('worker_pressure', {
          idle: status.workers.idle,
          total: status.workers.total,
          utilization: ((status.workers.total - status.workers.idle) / status.workers.total * 100).toFixed(1) + '%'
        });
      }
    }
  } catch (error) {
    console.warn('[SelfHealing] Health check failed:', error);
  }
}

export async function adaptiveMetrics(memory: MemoryFabric, auroraX: AuroraXCore): Promise<void> {
  try {
    const recentFacts = await memory.getRecent(20);

    if (recentFacts.length > 0) {
      const patterns = analyzePatterns(recentFacts);

      await auroraX.adapt(
        { type: 'metricUpdate', patterns },
        { factCount: recentFacts.length, timestamp: Date.now() }
      );

      console.log(`[AdaptiveMetrics] Processed ${recentFacts.length} recent facts, ${patterns.length} patterns detected`);
    }
  } catch (error) {
    console.warn('[AdaptiveMetrics] Metric update failed:', error);
  }
}

function analyzePatterns(facts: any[]): string[] {
  const patterns: string[] = [];
  const actionCounts: Record<string, number> = {};

  for (const fact of facts) {
    const intent = fact.intent ?? fact.metadata?.intent;
    if (intent?.action) {
      actionCounts[intent.action] = (actionCounts[intent.action] || 0) + 1;
    }
  }

  const dominantAction = Object.entries(actionCounts)
    .sort(([, a], [, b]) => b - a)[0];

  if (dominantAction && dominantAction[1] > facts.length * 0.3) {
    patterns.push(`dominant_action:${dominantAction[0]}`);
  }

  const recentTimestamps = facts
    .map(f => f.timestamp)
    .filter(Boolean)
    .sort((a, b) => b - a)
    .slice(0, 5);

  if (recentTimestamps.length >= 2) {
    const avgInterval = (recentTimestamps[0] - recentTimestamps[recentTimestamps.length - 1]) / recentTimestamps.length;
    if (avgInterval < 30000) {
      patterns.push('high_activity');
    } else if (avgInterval > 300000) {
      patterns.push('low_activity');
    }
  }

  return patterns;
}

export async function runDiagnostics(
  nexus: AuroraNexus,
  memory: MemoryFabric,
  auroraX: AuroraXCore
): Promise<Record<string, unknown>> {
  const [nexusHealth, memoryHealth, auroraXHealth] = await Promise.all([
    nexus.checkHealth(),
    memory.checkHealth(),
    auroraX.checkHealth()
  ]);

  const consciousness = await nexus.getConsciousState();
  const facts = await memory.getFacts();

  return {
    timestamp: Date.now(),
    services: {
      nexus: nexusHealth,
      memory: memoryHealth,
      auroraX: auroraXHealth
    },
    consciousness: {
      state: consciousness.state,
      workers: consciousness.workers,
      capabilities: consciousness.peakCapabilities
    },
    memoryStats: {
      factCount: Object.keys(facts).length
    },
    recommendations: generateRecommendations(nexusHealth, memoryHealth, auroraXHealth, consciousness)
  };
}

function generateRecommendations(
  nexusOk: boolean,
  memoryOk: boolean,
  auroraXOk: boolean,
  consciousness: any
): string[] {
  const recommendations: string[] = [];

  if (!nexusOk) {
    recommendations.push('Restart Aurora Nexus V3 service');
  }
  if (!memoryOk) {
    recommendations.push('Check Memory Fabric V2 service status');
  }
  if (!auroraXOk) {
    recommendations.push('Verify Aurora-X Core is running');
  }

  if (consciousness.workers?.idle < 10) {
    recommendations.push('Consider scaling worker pool');
  }

  if (recommendations.length === 0) {
    recommendations.push('All systems nominal');
  }

  return recommendations;
}
