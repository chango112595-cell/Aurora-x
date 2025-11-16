import React from 'react';
import { Sparkles } from 'lucide-react';

export default function Configuration() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-3">
            Configuration
          </h1>
          <p className="text-purple-300 mb-6">System preferences and customization</p>
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-purple-500/20 border border-purple-500/30 rounded-xl">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-sm text-purple-200">Coming Soon</span>
          </div>
        </div>
      </div>
    </div>
  );
}
