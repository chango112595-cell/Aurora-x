'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

export default function EvolutionPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-20">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-cyan-500 via-purple-500 to-pink-500 flex items-center justify-center">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            Evolution Monitor
          </h1>
          <p className="text-purple-400 text-lg mb-8">Track Aurora's continuous growth and adaptation</p>
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-purple-500/20 border border-purple-500/30 rounded-xl">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-purple-400">Coming Soon</span>
          </div>
        </div>
      </div>
    </div>
  );
}
