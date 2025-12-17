import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'wouter';
import {
  LayoutDashboard, MessageSquare, Brain, Network, Settings,
  Zap, Activity, Database, Layers, GitBranch, Code2,
  Sparkles, TrendingUp, Menu, X
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  category: 'core' | 'intelligence' | 'tools';
}

export default function AuroraFuturisticLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [location] = useLocation();

  const navItems: NavItem[] = [
    // Core Systems
    { path: '/dashboard', label: 'Quantum Dashboard', icon: <LayoutDashboard className="w-5 h-5" />, category: 'core' },
    { path: '/chat', label: 'Neural Chat', icon: <MessageSquare className="w-5 h-5" />, category: 'core' },
    { path: '/memory', label: 'Memory Fabric', icon: <Brain className="w-5 h-5" />, category: 'core' },
    { path: '/intelligence', label: 'Intelligence Core', icon: <Brain className="w-5 h-5" />, category: 'core' },

    // Intelligence Systems
    { path: '/tasks', label: 'Execution Methods', icon: <Layers className="w-5 h-5" />, category: 'intelligence' },
    { path: '/tiers', label: 'Knowledge Tiers', icon: <Network className="w-5 h-5" />, category: 'intelligence' },
    { path: '/evolution', label: 'Evolution Monitor', icon: <TrendingUp className="w-5 h-5" />, category: 'intelligence' },

    // Advanced Tools
    { path: '/memory-fabric', label: 'Memory Fabric', icon: <Brain className="w-5 h-5" />, category: 'tools' },
    { path: '/nexus', label: 'Nexus', icon: <Sparkles className="w-5 h-5" />, category: 'tools' },
    { path: '/autonomous', label: 'Autonomous Tools', icon: <Zap className="w-5 h-5" />, category: 'tools' },
    { path: '/monitoring', label: 'System Monitor', icon: <Activity className="w-5 h-5" />, category: 'tools' },
    { path: '/database', label: 'Knowledge Base', icon: <Database className="w-5 h-5" />, category: 'tools' },
    { path: '/settings', label: 'Configuration', icon: <Settings className="w-5 h-5" />, category: 'tools' },
  ];

  const categoryLabels = {
    core: 'Core Systems',
    intelligence: 'Intelligence Matrix',
    tools: 'Advanced Tools'
  };

  const [moduleCount, setModuleCount] = useState<number | null>(null);
  const [quantumCoherence, setQuantumCoherence] = useState<number | null>(null);

  useEffect(() => {
    let isActive = true;

    const fetchSidebarStats = async () => {
      try {
        const [manifestRes, v2Res] = await Promise.allSettled([
          fetch('/api/nexus-v3/manifest'),
          fetch('/api/luminar-nexus/v2/status'),
        ]);

        if (manifestRes.status === 'fulfilled' && manifestRes.value.ok) {
          const data = await manifestRes.value.json();
          if (isActive && typeof data.modules === 'number') {
            setModuleCount(data.modules);
          }
        }

        if (v2Res.status === 'fulfilled' && v2Res.value.ok) {
          const data = await v2Res.value.json();
          if (isActive && typeof data.quantum_coherence === 'number') {
            setQuantumCoherence(data.quantum_coherence);
          }
        }
      } catch {
        if (isActive) {
          setModuleCount(null);
          setQuantumCoherence(null);
        }
      }
    };

    fetchSidebarStats();
    const interval = setInterval(fetchSidebarStats, 15000);
    return () => {
      isActive = false;
      clearInterval(interval);
    };
  }, []);

  const coherencePercent = quantumCoherence !== null
    ? Math.min(100, Math.max(0, quantumCoherence * 100))
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
      {/* Animated Background */}
      <div className="fixed inset-0 opacity-30">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(139,92,246,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(59,130,246,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(236,72,153,0.1),transparent_50%)]" />
      </div>

      {/* Sidebar */}
      <aside className={`fixed left-0 top-0 h-screen z-50 transition-all duration-300 ${sidebarOpen ? 'w-72' : 'w-20'
        }`}>
        <div className="h-full bg-slate-950/50 backdrop-blur-xl border-r border-purple-500/20">
          {/* Header */}
          <div className="p-6 border-b border-purple-500/20">
            <div className="flex items-center justify-between">
              {sidebarOpen && (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-purple-500 to-pink-500 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                      Aurora
                    </h1>
                    <p className="text-xs text-purple-400">
                      {moduleCount !== null ? `${moduleCount} Modules Online` : "Modules Unavailable"}
                    </p>
                  </div>
                </div>
              )}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 transition-colors"
              >
                {sidebarOpen ? <X className="w-5 h-5 text-purple-400" /> : <Menu className="w-5 h-5 text-purple-400" />}
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-120px)]">
            {(['core', 'intelligence', 'tools'] as const).map(category => (
              <div key={category}>
                {sidebarOpen && (
                  <h3 className="text-xs font-semibold text-purple-400/60 uppercase tracking-wider mb-3 px-3">
                    {categoryLabels[category]}
                  </h3>
                )}
                <div className="space-y-1">
                  {navItems.filter(item => item.category === category).map(item => {
                    const isActive = location === item.path || (item.path !== '/' && location?.startsWith(item.path));
                    return (
                      <Link key={item.path} to={item.path} className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 block ${isActive
                        ? 'bg-gradient-to-r from-purple-600/40 to-pink-600/40 border border-purple-400/50 text-white shadow-lg shadow-purple-500/30'
                        : 'bg-slate-800/50 text-purple-300 hover:bg-purple-500/30 hover:text-white border border-transparent hover:border-purple-500/30'
                        }`}>
                        <div className={isActive ? 'text-purple-400' : 'text-purple-500'}>
                          {item.icon}
                        </div>
                        {sidebarOpen && (
                          <span className="font-medium text-sm">{item.label}</span>
                        )}
                        {isActive && sidebarOpen && (
                          <div className="ml-auto w-2 h-2 rounded-full bg-gradient-to-r from-cyan-400 to-purple-400 animate-pulse" />
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          {/* Footer Status */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-purple-500/20">
            {sidebarOpen ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-purple-400">Quantum Coherence</span>
                  <span className="text-cyan-400 font-mono">
                    {coherencePercent !== null ? `${coherencePercent.toFixed(1)}%` : "Unavailable"}
                  </span>
                </div>
                <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 animate-pulse"
                    style={{ width: `${coherencePercent ?? 0}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="w-10 h-10 mx-auto rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center">
                <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`transition-all duration-300 ${sidebarOpen ? 'ml-72' : 'ml-20'}`}>
        <div className="relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
}
