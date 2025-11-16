import React from 'react';
import { Brain, Cpu, Activity, Zap, Network, TrendingUp } from 'lucide-react';

export default function Intelligence() {
  const metrics = [
    { name: 'Neural Processing', value: 98.7, unit: '%', icon: <Brain className="w-5 h-5" />, color: 'text-cyan-400' },
    { name: 'Learning Rate', value: 94.2, unit: '%', icon: <TrendingUp className="w-5 h-5" />, color: 'text-purple-400' },
    { name: 'Context Retention', value: 99.1, unit: '%', icon: <Cpu className="w-5 h-5" />, color: 'text-pink-400' },
    { name: 'Response Time', value: 0.3, unit: 's', icon: <Zap className="w-5 h-5" />, color: 'text-yellow-400' },
    { name: 'Network Efficiency', value: 97.5, unit: '%', icon: <Network className="w-5 h-5" />, color: 'text-green-400' },
    { name: 'System Activity', value: 96.8, unit: '%', icon: <Activity className="w-5 h-5" />, color: 'text-blue-400' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            Intelligence Core
          </h1>
          <p className="text-purple-300">Real-time cognitive metrics and system intelligence</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {metrics.map((metric, idx) => (
            <div
              key={idx}
              className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-6 hover:border-purple-500/40 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={metric.color}>{metric.icon}</div>
                <span className={`text-2xl font-bold ${metric.color}`}>
                  {metric.value}{metric.unit}
                </span>
              </div>
              <h3 className="text-white font-semibold">{metric.name}</h3>
              <div className="mt-3 h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                  style={{ width: metric.unit === '%' ? `${metric.value}%` : '100%' }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Core Services</span>
                <span className="text-green-400 font-semibold">5/5 Active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Memory Usage</span>
                <span className="text-cyan-400 font-mono">2.1 GB</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Uptime</span>
                <span className="text-purple-400 font-mono">47h 23m</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Tasks Completed</span>
                <span className="text-cyan-400 font-mono">13/13</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Knowledge Tiers</span>
                <span className="text-purple-400 font-mono">34/34</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Overall Health</span>
                <span className="text-green-400 font-semibold">Excellent</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
