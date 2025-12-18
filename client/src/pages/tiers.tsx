'use client';

import React from 'react';
import { useQuery } from "@tanstack/react-query";
import { Brain, Globe, Sparkles } from 'lucide-react';

interface TierCategory {
  name: string;
  count: number;
}

interface TierSummary {
  totalTiers: number;
  categories: TierCategory[];
  mode?: string;
}

const categoryPalette = [
  'from-amber-500 to-orange-500',
  'from-blue-500 to-cyan-500',
  'from-green-500 to-emerald-500',
  'from-purple-500 to-pink-500',
  'from-red-500 to-rose-500',
  'from-pink-500 to-fuchsia-500',
  'from-cyan-500 to-blue-500',
  'from-violet-500 to-purple-500',
  'from-teal-500 to-emerald-500',
  'from-lime-500 to-green-500',
  'from-sky-500 to-indigo-500',
  'from-rose-500 to-pink-500',
];

const formatLabel = (value: string) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

export default function TiersPage() {
  const { data, isLoading, isError } = useQuery<TierSummary>({
    queryKey: ['/api/nexus-v3/tiers'],
    refetchInterval: 60000
  });

  const totalTiers = data?.totalTiers ?? 0;
  const categories = (data?.categories ?? []).slice().sort((a, b) => b.count - a.count);

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            {totalTiers ? `${totalTiers} Knowledge Tiers` : 'Knowledge Tiers'}
          </h1>
          <p className="text-purple-400 text-lg">Live tier distribution from the Nexus V3 manifest</p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16 text-purple-300">
            Loading tier distribution...
          </div>
        ) : isError ? (
          <div className="flex items-center justify-center py-16 text-red-300">
            Failed to load tier distribution.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category, index) => {
              const colorClass = categoryPalette[index % categoryPalette.length];
              const Icon = index % 2 === 0 ? Globe : Brain;
              const percent = totalTiers > 0 ? Math.round((category.count / totalTiers) * 100) : 0;

              return (
                <div key={category.name} className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClass} flex items-center justify-center`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">{formatLabel(category.name)}</h2>
                      <p className="text-purple-400 text-sm">{category.count} tiers</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-purple-400">Share of total</span>
                      <span className="text-cyan-400 font-mono">{percent}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${colorClass} transition-all`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-8 bg-slate-900/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Knowledge Tier Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                {totalTiers || 'Unavailable'}
              </div>
              <div className="text-purple-400 text-sm">Total Tiers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {categories.length || 'Unavailable'}
              </div>
              <div className="text-purple-400 text-sm">Domains</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">
                {data?.mode ?? 'Unknown'}
              </div>
              <div className="text-purple-400 text-sm">Mode</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                <Sparkles className="w-8 h-8 inline-block" />
              </div>
              <div className="text-purple-400 text-sm">Nexus V3</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
