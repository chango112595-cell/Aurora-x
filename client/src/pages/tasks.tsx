import React from 'react';
import { Brain, Zap, Network, Database, Code2, Sparkles, GitBranch, Shield, Rocket, Eye, Lightbulb, TrendingUp, Cpu } from 'lucide-react';

const foundationTasks = [
  { id: 1, name: 'Understand Context', icon: Brain, progress: 100, color: 'from-cyan-500 to-blue-500' },
  { id: 2, name: 'Learn Continuously', icon: Lightbulb, progress: 100, color: 'from-blue-500 to-purple-500' },
  { id: 3, name: 'Execute Commands', icon: Zap, progress: 100, color: 'from-purple-500 to-pink-500' },
  { id: 4, name: 'Manage Files', icon: Database, progress: 100, color: 'from-pink-500 to-red-500' },
  { id: 5, name: 'Code Analysis', icon: Code2, progress: 100, color: 'from-red-500 to-orange-500' },
  { id: 6, name: 'System Integration', icon: Network, progress: 100, color: 'from-orange-500 to-yellow-500' },
  { id: 7, name: 'Version Control', icon: GitBranch, progress: 100, color: 'from-yellow-500 to-green-500' },
  { id: 8, name: 'Security & Privacy', icon: Shield, progress: 100, color: 'from-green-500 to-emerald-500' },
  { id: 9, name: 'Performance Optimization', icon: Rocket, progress: 100, color: 'from-emerald-500 to-teal-500' },
  { id: 10, name: 'Monitor & Debug', icon: Eye, progress: 100, color: 'from-teal-500 to-cyan-500' },
  { id: 11, name: 'Autonomous Decision', icon: Cpu, progress: 100, color: 'from-cyan-500 to-purple-500' },
  { id: 12, name: 'Adaptive Intelligence', icon: Sparkles, progress: 100, color: 'from-purple-500 to-pink-500' },
  { id: 13, name: 'Evolutionary Growth', icon: TrendingUp, progress: 100, color: 'from-pink-500 to-cyan-500' },
];

export default function TasksPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            13 Foundation Tasks
          </h1>
          <p className="text-purple-400 text-lg">Core cognitive capabilities that power Aurora's intelligence</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {foundationTasks.map((task) => {
            const Icon = task.icon;
            return (
              <div key={task.id} className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity blur-xl" 
                     style={{ background: `linear-gradient(to right, var(--tw-gradient-stops))` }} />
                <div className="relative bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${task.color} flex items-center justify-center`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <div className="text-xs text-purple-400 font-mono">Task {String(task.id).padStart(2, '0')}</div>
                      <h3 className="text-white font-semibold">{task.name}</h3>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-purple-400">Status</span>
                      <span className="text-cyan-400 font-mono">{task.progress}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full bg-gradient-to-r ${task.color} transition-all`}
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-purple-500/20">
                    <div className="flex items-center justify-between text-xs text-purple-400">
                      <span>Operational</span>
                      <span className="flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                        Active
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Foundation Task Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">13</div>
              <div className="text-purple-400 text-sm">Foundation Tasks</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">100%</div>
              <div className="text-purple-400 text-sm">Operational</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">Active</div>
              <div className="text-purple-400 text-sm">Status</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
