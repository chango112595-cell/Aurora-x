import React from 'react';
import { Globe, Code, Database, Brain, Sparkles, Zap } from 'lucide-react';

const knowledgeTiers = {
  'Ancient Languages': [
    { id: 1, name: 'Ancient Languages', progress: 100 },
    { id: 2, name: 'Classical Studies', progress: 100 },
    { id: 3, name: 'Historical Linguistics', progress: 100 },
  ],
  'Modern Languages': [
    { id: 4, name: 'European Languages', progress: 100 },
    { id: 5, name: 'Asian Languages', progress: 100 },
    { id: 6, name: 'Middle Eastern Languages', progress: 100 },
    { id: 7, name: 'African Languages', progress: 100 },
  ],
  'Programming': [
    { id: 8, name: 'Systems Programming', progress: 100 },
    { id: 9, name: 'Web Development', progress: 100 },
    { id: 10, name: 'Mobile Development', progress: 100 },
    { id: 11, name: 'Database Systems', progress: 100 },
  ],
  'AI & Machine Learning': [
    { id: 12, name: 'Neural Networks', progress: 100 },
    { id: 13, name: 'Deep Learning', progress: 100 },
    { id: 14, name: 'NLP Systems', progress: 100 },
    { id: 15, name: 'Computer Vision', progress: 100 },
  ],
  'Engineering': [
    { id: 16, name: 'Software Architecture', progress: 100 },
    { id: 17, name: 'DevOps', progress: 100 },
    { id: 18, name: 'Cloud Computing', progress: 100 },
    { id: 19, name: 'Cybersecurity', progress: 100 },
  ],
  'Creative Arts': [
    { id: 20, name: 'Digital Art', progress: 100 },
    { id: 21, name: 'Music Theory', progress: 100 },
    { id: 22, name: 'Creative Writing', progress: 100 },
    { id: 23, name: 'Design Systems', progress: 100 },
  ],
  'Sciences': [
    { id: 24, name: 'Physics', progress: 100 },
    { id: 25, name: 'Chemistry', progress: 100 },
    { id: 26, name: 'Biology', progress: 100 },
    { id: 27, name: 'Mathematics', progress: 100 },
  ],
  'Autonomous Systems': [
    { id: 28, name: 'Self-Learning', progress: 100 },
    { id: 29, name: 'Autonomous Reasoning', progress: 100 },
    { id: 30, name: 'Decision Making', progress: 100 },
    { id: 31, name: 'Error Recovery', progress: 100 },
    { id: 32, name: 'System Optimization', progress: 100 },
    { id: 33, name: 'Adaptive Evolution', progress: 100 },
    { id: 34, name: 'Grandmaster Autonomous', progress: 100 },
    { id: 35, name: 'Pylint Grandmaster', progress: 100 },
    { id: 36, name: 'Self-Monitor', progress: 100 },
    { id: 37, name: 'Tier Expansion', progress: 100 },
    { id: 38, name: 'Tier Orchestrator', progress: 100 },
    { id: 39, name: 'Performance Optimizer', progress: 100 },
    { id: 40, name: 'Full Autonomy', progress: 100 },
    { id: 41, name: 'Strategist', progress: 100 },
    { id: 42, name: 'Pylint Prevention', progress: 100 },
  ],
  'Advanced Capabilities': [
    { id: 43, name: 'Visual Understanding', progress: 100 },
    { id: 44, name: 'Live Integration', progress: 100 },
    { id: 45, name: 'Test Generator', progress: 100 },
    { id: 46, name: 'Security Auditor', progress: 100 },
    { id: 47, name: 'Doc Generator', progress: 100 },
    { id: 48, name: 'Multi-Agent', progress: 100 },
    { id: 49, name: 'UI Generator', progress: 100 },
    { id: 50, name: 'Git Master', progress: 100 },
    { id: 51, name: 'Code Quality Enforcer', progress: 100 },
    { id: 52, name: 'RSA Grandmaster', progress: 100 },
  ],
};

const categoryIcons = {
  'Ancient Languages': Globe,
  'Modern Languages': Globe,
  'Programming': Code,
  'AI & Machine Learning': Brain,
  'Engineering': Database,
  'Creative Arts': Sparkles,
  'Sciences': Zap,
  'Autonomous Systems': Brain,
  'Advanced Capabilities': Sparkles,
};

const categoryColors = {
  'Ancient Languages': 'from-amber-500 to-orange-500',
  'Modern Languages': 'from-blue-500 to-cyan-500',
  'Programming': 'from-green-500 to-emerald-500',
  'AI & Machine Learning': 'from-purple-500 to-pink-500',
  'Engineering': 'from-red-500 to-rose-500',
  'Creative Arts': 'from-pink-500 to-fuchsia-500',
  'Sciences': 'from-cyan-500 to-blue-500',
  'Autonomous Systems': 'from-violet-500 to-purple-500',
  'Advanced Capabilities': 'from-cyan-500 to-purple-500',
};

export default function TiersPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            52 Knowledge Tiers
          </h1>
          <p className="text-purple-400 text-lg">Specialized domain expertise across all fields of knowledge</p>
        </div>

        <div className="space-y-8">
          {Object.entries(knowledgeTiers).map(([category, tiers]) => {
            const Icon = categoryIcons[category as keyof typeof categoryIcons];
            const colorClass = categoryColors[category as keyof typeof categoryColors];

            return (
              <div key={category} className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClass} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">{category}</h2>
                    <p className="text-purple-400 text-sm">{tiers.length} Tiers</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {tiers.map((tier) => (
                    <div key={tier.id} className="bg-slate-800/50 border border-purple-500/20 rounded-xl p-4 hover:border-purple-500/40 transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-purple-400 font-mono">Tier {String(tier.id).padStart(2, '0')}</span>
                        <span className="text-xs text-cyan-400 font-mono">{tier.progress}%</span>
                      </div>
                      <h3 className="text-white font-medium mb-3">{tier.name}</h3>
                      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${colorClass}`}
                          style={{ width: `${tier.progress}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Knowledge Tier Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">51</div>
              <div className="text-purple-400 text-sm">Knowledge Tiers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">9</div>
              <div className="text-purple-400 text-sm">Categories</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">100%</div>
              <div className="text-purple-400 text-sm">Mastery</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Active</div>
              <div className="text-purple-400 text-sm">Status</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
