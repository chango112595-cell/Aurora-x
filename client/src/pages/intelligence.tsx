'use client';

import { useQuery } from '@tanstack/react-query';
import { Brain, Cpu, Activity, Zap, Database, Network, TrendingUp, Loader2 } from 'lucide-react';

interface EvolutionMetric {
  id: string;
  name: string;
  value: number;
  maxValue: number;
  trend: string;
  category: string;
}

interface EvolutionSummary {
  totalTiers: number;
  activeTiers: number;
  totalExecutions: number;
  activeExecutions: number;
  totalCapabilities: number;
  totalModules: number;
  uptimeSeconds: number;
}

interface EvolutionData {
  metrics: EvolutionMetric[];
  summary: EvolutionSummary;
}

const metricIcons: Record<string, any> = {
  'Neural Processing': Brain,
  'Pattern Recognition': Activity,
  'Code Synthesis': Cpu,
  'Learning Rate': TrendingUp,
  'Memory Efficiency': Database,
  'Context Retention': Brain,
  'Autonomous Decision': Zap,
  'Self-Optimization': Network,
};

const metricColors: Record<string, string> = {
  'Neural Processing': 'from-cyan-500 to-blue-500',
  'Pattern Recognition': 'from-purple-500 to-pink-500',
  'Code Synthesis': 'from-green-500 to-emerald-500',
  'Learning Rate': 'from-orange-500 to-red-500',
  'Memory Efficiency': 'from-pink-500 to-purple-500',
  'Context Retention': 'from-blue-500 to-cyan-500',
  'Autonomous Decision': 'from-yellow-500 to-orange-500',
  'Self-Optimization': 'from-indigo-500 to-purple-500',
};

export default function IntelligencePage() {
  const { data, isLoading, error } = useQuery<EvolutionData>({
    queryKey: ['/api/evolution/metrics'],
    refetchInterval: 30000,
  });

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="flex items-center gap-3 text-purple-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading intelligence metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-500/30 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-red-400">Failed to load metrics</h2>
            <p className="text-red-300/70 mt-2">Please check system connectivity</p>
          </div>
        </div>
      </div>
    );
  }

  const metrics = data?.metrics || [];
  const summary = data?.summary;

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4" data-testid="text-page-title">
            Intelligence Core
          </h1>
          <p className="text-purple-400 text-lg">Real-time monitoring of Aurora's cognitive systems</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric) => {
            const Icon = metricIcons[metric.name] || Brain;
            const color = metricColors[metric.name] || 'from-cyan-500 to-blue-500';
            const trendColor = metric.trend === 'up' ? 'text-green-400' : metric.trend === 'down' ? 'text-red-400' : 'text-yellow-400';
            const trendSymbol = metric.trend === 'up' ? '+' : metric.trend === 'down' ? '-' : '';
            
            return (
              <div 
                key={metric.id} 
                className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 hover:border-purple-500/50 transition-all"
                data-testid={`card-metric-${metric.id}`}
              >
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-purple-400 text-sm">{metric.name}</div>
                    <div className="flex items-center gap-2">
                      <div className="text-2xl font-bold text-white" data-testid={`text-metric-value-${metric.id}`}>{metric.value}%</div>
                      <div className={`text-xs ${trendColor}`}>{trendSymbol}{metric.trend}</div>
                    </div>
                  </div>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${color} transition-all duration-500`} 
                    style={{ width: `${metric.value}%` }} 
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">System Architecture</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Intelligence Tiers</span>
                <span className="text-cyan-400 font-mono text-lg" data-testid="text-total-tiers">
                  {summary?.activeTiers || 0}/{summary?.totalTiers || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Execution Methods</span>
                <span className="text-purple-400 font-mono text-lg" data-testid="text-total-executions">
                  {summary?.activeExecutions || 0}/{summary?.totalExecutions || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Total Modules</span>
                <span className="text-pink-400 font-mono text-lg" data-testid="text-total-modules">
                  {summary?.totalModules || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Capabilities</span>
                <span className="text-green-400 font-mono text-lg" data-testid="text-total-capabilities">
                  {summary?.totalCapabilities || 0}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">Neural Activity</h3>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400">Task Processing</span>
                  <span className="text-cyan-400 font-mono">Active</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500" 
                    style={{ width: `${metrics.find(m => m.name === 'Neural Processing')?.value || 95}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400">Learning Mode</span>
                  <span className="text-purple-400 font-mono">Active</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500" 
                    style={{ width: `${metrics.find(m => m.name === 'Learning Rate')?.value || 88}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400">System Uptime</span>
                  <span className="text-pink-400 font-mono" data-testid="text-uptime">
                    {summary?.uptimeSeconds ? formatUptime(summary.uptimeSeconds) : 'N/A'}
                  </span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full w-full bg-gradient-to-r from-pink-500 to-purple-500" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
