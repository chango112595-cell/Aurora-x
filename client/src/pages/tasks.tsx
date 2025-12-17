'use client';

import React from 'react';
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Brain,
  Bug,
  CheckCircle2,
  Code2,
  Gauge,
  Layers,
  BookOpen,
  Rocket,
  Shield,
  Sparkles,
  Wrench,
  Zap
} from 'lucide-react';

interface AemCategory {
  name: string;
  count: number;
  methods: string[];
}

interface AemSummary {
  totalAEMs: number;
  categories: AemCategory[];
  mode?: string;
}

const categoryPalette = [
  'from-cyan-500 to-blue-500',
  'from-blue-500 to-purple-500',
  'from-purple-500 to-pink-500',
  'from-pink-500 to-red-500',
  'from-red-500 to-orange-500',
  'from-orange-500 to-yellow-500',
  'from-yellow-500 to-green-500',
  'from-green-500 to-emerald-500',
  'from-emerald-500 to-teal-500',
  'from-teal-500 to-cyan-500',
];

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  code_generation: Sparkles,
  code_analysis: Brain,
  code_optimization: Zap,
  refactoring: Wrench,
  testing: CheckCircle2,
  debugging: Bug,
  documentation: BookOpen,
  deployment: Rocket,
  monitoring: Activity,
  security_scan: Shield,
  performance_tuning: Gauge,
  data_processing: Layers
};

const formatLabel = (value: string) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

export default function TasksPage() {
  const { data, isLoading, isError } = useQuery<AemSummary>({
    queryKey: ['/api/nexus-v3/aems'],
    refetchInterval: 60000
  });

  const categories = data?.categories ?? [];
  const totalAems = data?.totalAEMs ?? 0;

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            Execution Method Catalog
          </h1>
          <p className="text-purple-400 text-lg">Live AEM categories derived from the Nexus V3 manifest</p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16 text-purple-300">
            Loading execution categories...
          </div>
        ) : isError ? (
          <div className="flex items-center justify-center py-16 text-red-300">
            Failed to load execution categories.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category, index) => {
              const color = categoryPalette[index % categoryPalette.length];
              const Icon = iconMap[category.name] ?? Layers;
              const percent = totalAems > 0 ? Math.round((category.count / totalAems) * 100) : 0;
              const preview = category.methods.slice(0, 3);
              const remaining = category.methods.length - preview.length;

              return (
                <div key={category.name} className="group relative">
                  <div
                    className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity blur-xl"
                    style={{ background: `linear-gradient(to right, var(--tw-gradient-stops))` }}
                  />
                  <div className="relative bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                    <div className="flex items-center gap-4 mb-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="text-xs text-purple-400 font-mono">{category.count} methods</div>
                        <h3 className="text-white font-semibold">{formatLabel(category.name)}</h3>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-purple-400">Share of total</span>
                        <span className="text-cyan-400 font-mono">{percent}%</span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${color} transition-all`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-purple-500/20">
                      <div className="text-xs text-purple-400 mb-2">Sample methods</div>
                      <div className="space-y-1 text-xs text-cyan-300/80">
                        {preview.length > 0 ? preview.map((method) => (
                          <div key={method} className="truncate">• {method}</div>
                        )) : (
                          <div>No methods listed</div>
                        )}
                        {remaining > 0 && (
                          <div className="text-purple-400">+{remaining} more</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-8 bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Execution Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                {totalAems || 'Unavailable'}
              </div>
              <div className="text-purple-400 text-sm">Total AEMs</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {categories.length || 'Unavailable'}
              </div>
              <div className="text-purple-400 text-sm">Categories</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">
                {data?.mode ?? 'Unknown'}
              </div>
              <div className="text-purple-400 text-sm">Mode</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
