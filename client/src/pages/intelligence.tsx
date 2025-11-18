import React from 'react';
import { Brain, Cpu, Activity, Zap, Database, Network } from 'lucide-react';

export default function IntelligencePage() {
  const metrics = [
    { label: 'Neural Processing', value: '98.7%', trend: '+2.3%', icon: Brain, color: 'from-cyan-500 to-blue-500' },
    { label: 'Quantum Coherence', value: '97.2%', trend: '+1.8%', icon: Zap, color: 'from-purple-500 to-pink-500' },
    { label: 'Learning Rate', value: '95.4%', trend: '+3.1%', icon: Activity, color: 'from-green-500 to-emerald-500' },
    { label: 'System Integration', value: '99.1%', trend: '+0.9%', icon: Network, color: 'from-orange-500 to-red-500' },
    { label: 'Knowledge Access', value: '100%', trend: '0%', icon: Database, color: 'from-pink-500 to-purple-500' },
    { label: 'CPU Efficiency', value: '96.8%', trend: '+1.2%', icon: Cpu, color: 'from-blue-500 to-cyan-500' },
  ];

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            Intelligence Core
          </h1>
          <p className="text-purple-400 text-lg">Real-time monitoring of Aurora's cognitive systems</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {metrics.map((metric) => {
            const Icon = metric.icon;
            return (
              <div key={metric.label} className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${metric.color} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-purple-400 text-sm">{metric.label}</div>
                    <div className="flex items-center gap-2">
                      <div className="text-2xl font-bold text-white">{metric.value}</div>
                      <div className="text-xs text-green-400">{metric.trend}</div>
                    </div>
                  </div>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full bg-gradient-to-r ${metric.color} animate-pulse`} style={{ width: metric.value }} />
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
                <span className="text-purple-400">Foundation Tasks</span>
                <span className="text-cyan-400 font-mono text-lg">13</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Knowledge Tiers</span>
                <span className="text-purple-400 font-mono text-lg">53</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Total Systems</span>
                <span className="text-pink-400 font-mono text-lg">66</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                <span className="text-purple-400">Active Services</span>
                <span className="text-green-400 font-mono text-lg">5/5</span>
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
                  <div className="h-full w-[95%] bg-gradient-to-r from-cyan-500 to-blue-500 animate-pulse" />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400">Learning Mode</span>
                  <span className="text-purple-400 font-mono">Active</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full w-[88%] bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400">Evolution</span>
                  <span className="text-pink-400 font-mono">Active</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full w-[92%] bg-gradient-to-r from-pink-500 to-purple-500 animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
