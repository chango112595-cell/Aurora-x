import React from 'react';
import { Brain, Network, Zap, Database, Code, Sparkles, Shield, TrendingUp } from 'lucide-react';

export default function Tiers() {
  const categories = [
    {
      name: 'Foundation',
      icon: <Sparkles className="w-6 h-6" />,
      color: 'from-cyan-500 to-blue-500',
      tiers: ['System Architecture', 'Core Logic', 'Data Structures', 'Algorithms']
    },
    {
      name: 'Intelligence',
      icon: <Brain className="w-6 h-6" />,
      color: 'from-purple-500 to-pink-500',
      tiers: ['Natural Language', 'Context Analysis', 'Decision Making', 'Pattern Recognition', 'Learning Systems']
    },
    {
      name: 'Integration',
      icon: <Network className="w-6 h-6" />,
      color: 'from-green-500 to-teal-500',
      tiers: ['API Management', 'Service Communication', 'Data Flow', 'Event Systems']
    },
    {
      name: 'Execution',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-yellow-500 to-orange-500',
      tiers: ['Task Processing', 'Autonomous Actions', 'Command Execution', 'Real-time Operations']
    },
    {
      name: 'Data',
      icon: <Database className="w-6 h-6" />,
      color: 'from-blue-500 to-indigo-500',
      tiers: ['Storage Management', 'Query Optimization', 'Data Integrity', 'Caching Systems', 'Backup & Recovery']
    },
    {
      name: 'Development',
      icon: <Code className="w-6 h-6" />,
      color: 'from-pink-500 to-rose-500',
      tiers: ['Code Generation', 'Debugging Tools', 'Testing Systems', 'Optimization']
    },
    {
      name: 'Security',
      icon: <Shield className="w-6 h-6" />,
      color: 'from-red-500 to-orange-500',
      tiers: ['Authentication', 'Authorization', 'Validation', 'Encryption']
    },
    {
      name: 'Performance',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-emerald-500 to-cyan-500',
      tiers: ['Monitoring', 'Metrics', 'Optimization', 'Scaling']
    }
  ];

  const totalTiers = categories.reduce((sum, cat) => sum + cat.tiers.length, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            34 Knowledge Tiers
          </h1>
          <p className="text-purple-300">Organized intelligence across 8 core categories</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-4">
            <div className="text-2xl font-bold text-cyan-400">{categories.length}</div>
            <div className="text-sm text-purple-300">Categories</div>
          </div>
          <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-4">
            <div className="text-2xl font-bold text-purple-400">{totalTiers}</div>
            <div className="text-sm text-purple-300">Knowledge Tiers</div>
          </div>
          <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-4">
            <div className="text-2xl font-bold text-green-400">100%</div>
            <div className="text-sm text-purple-300">Integrated</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {categories.map((category, idx) => (
            <div
              key={idx}
              className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-6 hover:border-purple-500/40 transition-all hover:shadow-lg hover:shadow-purple-500/20"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${category.color}`}>
                  {category.icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{category.name}</h3>
                  <p className="text-xs text-purple-400">{category.tiers.length} tiers</p>
                </div>
              </div>
              <div className="space-y-2">
                {category.tiers.map((tier, tierIdx) => (
                  <div
                    key={tierIdx}
                    className="flex items-center gap-2 text-sm text-purple-200 bg-slate-800/30 rounded-lg p-2"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-cyan-400 to-purple-400" />
                    {tier}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
