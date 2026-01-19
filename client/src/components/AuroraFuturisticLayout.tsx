import React, { useEffect, useState, useCallback } from 'react';
import { Link, useLocation } from 'wouter';
import {
  Activity,
  BarChart3,
  BookOpen,
  Brain,
  Cpu,
  Database,
  FileText,
  GitBranch,
  LayoutDashboard,
  Layers,
  Lock,
  Map,
  Menu,
  MessageSquare,
  Network,
  Palette,
  Server,
  Settings,
  Sparkles,
  TestTube,
  TrendingUp,
  X,
  Zap,
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  category: 'core' | 'intelligence' | 'operations' | 'labs';
  tier: 'essential' | 'advanced';
}

export default function AuroraFuturisticLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [location] = useLocation();

  const navItems: NavItem[] = [
    { path: '/dashboard', label: 'Command Overview', icon: <LayoutDashboard className="w-5 h-5" />, category: 'core', tier: 'essential' },
    { path: '/aurora', label: 'Aurora Core', icon: <Sparkles className="w-5 h-5" />, category: 'core', tier: 'essential' },
    { path: '/chat', label: 'Neural Chat', icon: <MessageSquare className="w-5 h-5" />, category: 'core', tier: 'essential' },
    { path: '/memory', label: 'Memory Fabric', icon: <Database className="w-5 h-5" />, category: 'core', tier: 'essential' },
    { path: '/nexus', label: 'Nexus Command', icon: <Network className="w-5 h-5" />, category: 'core', tier: 'essential' },
    { path: '/library', label: 'Code Library', icon: <BookOpen className="w-5 h-5" />, category: 'core', tier: 'advanced' },

    { path: '/intelligence', label: 'Intelligence Core', icon: <Cpu className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },
    { path: '/tasks', label: 'Execution Methods', icon: <Layers className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },
    { path: '/tiers', label: 'Knowledge Tiers', icon: <GitBranch className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },
    { path: '/evolution', label: 'Evolution Monitor', icon: <TrendingUp className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },
    { path: '/self-learning', label: 'Self-Learning', icon: <Brain className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },
    { path: '/autonomous', label: 'Autonomous Tools', icon: <Zap className="w-5 h-5" />, category: 'intelligence', tier: 'advanced' },

    { path: '/monitoring', label: 'System Monitor', icon: <Activity className="w-5 h-5" />, category: 'operations', tier: 'essential' },
    { path: '/servers', label: 'Server Control', icon: <Server className="w-5 h-5" />, category: 'operations', tier: 'essential' },
    { path: '/database', label: 'Knowledge Base', icon: <Database className="w-5 h-5" />, category: 'operations', tier: 'advanced' },
    { path: '/roadmap', label: 'Roadmap', icon: <Map className="w-5 h-5" />, category: 'operations', tier: 'advanced' },
    { path: '/vault', label: 'Vault', icon: <Lock className="w-5 h-5" />, category: 'operations', tier: 'advanced' },
    { path: '/settings', label: 'Configuration', icon: <Settings className="w-5 h-5" />, category: 'operations', tier: 'essential' },

    { path: '/comparison', label: 'Comparison Lab', icon: <BarChart3 className="w-5 h-5" />, category: 'labs', tier: 'advanced' },
    { path: '/corpus', label: 'Corpus Archive', icon: <FileText className="w-5 h-5" />, category: 'labs', tier: 'advanced' },
    { path: '/aurora-ui', label: 'Aurora UI', icon: <Palette className="w-5 h-5" />, category: 'labs', tier: 'advanced' },
    { path: '/aurora-ai-test', label: 'Aurora AI Test', icon: <TestTube className="w-5 h-5" />, category: 'labs', tier: 'advanced' },
  ];

  const categoryLabels = {
    core: 'Command Core',
    intelligence: 'Intelligence Grid',
    operations: 'Operations',
    labs: 'Labs'
  };

  const [moduleCount, setModuleCount] = useState<number | null>(null);
  const [quantumCoherence, setQuantumCoherence] = useState<number | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hardware, setHardware] = useState<{
    arch: string;
    platform: string;
    cpus: { count: number; model: string; speedMHz: number };
    totalMem: number;
    freeMem: number;
  } | null>(null);
  const [serviceStatus, setServiceStatus] = useState<{
    backend: boolean;
    nexusV3: boolean;
    message?: string;
  }>({ backend: false, nexusV3: false });
  const [controlMessage, setControlMessage] = useState<string | null>(null);

  const fetchWithTimeout = async (url: string, opts: RequestInit = {}, timeoutMs = 2000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, { ...opts, signal: controller.signal });
      clearTimeout(id);
      return res;
    } catch (err) {
      clearTimeout(id);
      throw err;
    }
  };

  const fetchSidebarStats = useCallback(async () => {
    try {
      const [manifestRes, hwRes] = await Promise.allSettled([
        fetchWithTimeout('/api/nexus-v3/manifest'),
        fetchWithTimeout('/api/hardware'),
      ]);

      if (manifestRes.status === 'fulfilled' && manifestRes.value.ok) {
        const data = await manifestRes.value.json();
        if (typeof data.modules === 'number') {
          setModuleCount(data.modules);
        }
      }

      // Backend + V3 status
      try {
        const healthRes = await fetchWithTimeout('/api/health');
        if (healthRes.ok) {
          setServiceStatus((prev) => ({ ...prev, backend: true }));
        }
      } catch {
        setServiceStatus((prev) => ({ ...prev, backend: false }));
      }

      try {
        const v3Status = await fetchWithTimeout('/api/nexus-v3/manifest');
        setServiceStatus((prev) => ({ ...prev, nexusV3: v3Status.ok }));
      } catch {
        setServiceStatus((prev) => ({ ...prev, nexusV3: false }));
      }

      if (hwRes.status === 'fulfilled' && hwRes.value.ok) {
        const data = await hwRes.value.json();
        if (data) {
          setHardware({
            arch: data.arch,
            platform: data.platform,
            cpus: data.cpus || { count: 0, model: 'unknown', speedMHz: 0 },
            totalMem: data.totalMem || 0,
            freeMem: data.freeMem || 0,
          });
        }
      }
    } catch {
      setModuleCount(null);
      setQuantumCoherence(null);
      setHardware(null);
      setServiceStatus({ backend: false, nexusV3: false, message: "Offline" });
    }
  }, []);

  useEffect(() => {
    fetchSidebarStats();
    const interval = setInterval(fetchSidebarStats, 15000);
    return () => {
      clearInterval(interval);
    };
  }, [fetchSidebarStats]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const stored = window.localStorage.getItem('aurora-ui-mode');
    if (stored === 'advanced') {
      setShowAdvanced(true);
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('aurora-ui-mode', showAdvanced ? 'advanced' : 'essential');
  }, [showAdvanced]);

  const coherencePercent = quantumCoherence !== null
    ? Math.min(100, Math.max(0, quantumCoherence * 100))
    : null;

  const visibleNavItems = navItems.filter((item) => showAdvanced || item.tier === 'essential');
  const activeItem = navItems.find((item) => location === item.path || (item.path !== '/' && location?.startsWith(item.path)));

  const moduleLabel = moduleCount !== null ? moduleCount.toLocaleString() : 'Unavailable';
  const coherenceLabel = coherencePercent !== null ? `${coherencePercent.toFixed(1)}%` : 'Unavailable';

  return (
    <div className="min-h-screen text-slate-100">
      <div className="fixed inset-0 -z-10 bg-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.18),_transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,_rgba(14,116,144,0.22),_transparent_65%)]" />
        <div
          className="absolute inset-0 opacity-35"
          style={{
            backgroundImage
              : 'linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px)',
            backgroundSize: '48px 48px'
          }}
        />
        <div className="absolute -left-40 top-24 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute -right-32 bottom-12 h-72 w-72 rounded-full bg-sky-500/10 blur-3xl" />
      </div>

      <aside
        className={`fixed left-0 top-0 z-50 h-screen transition-all duration-300 ${sidebarOpen ? 'w-80' : 'w-20'}`}
      >
        <div className="flex h-full flex-col border-r border-slate-800/60 bg-slate-950/70 backdrop-blur-xl">
          <div className="border-b border-slate-800/60 p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="relative flex h-11 w-11 items-center justify-center rounded-2xl border border-emerald-400/30 bg-gradient-to-br from-emerald-400/20 via-sky-400/10 to-amber-400/20">
                  <Sparkles className="h-5 w-5 text-emerald-300" />
                  <span className="absolute -bottom-1 -right-1 h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                {sidebarOpen && (
                  <div>
                    <h1 className="text-lg font-semibold tracking-wide text-slate-100">Aurora</h1>
                    <p className="text-xs text-slate-400">Nexus Command Deck</p>
                  </div>
                )}
              </div>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2 text-slate-200 transition hover:bg-slate-900"
                aria-label="Toggle sidebar"
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
            {sidebarOpen && (
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                  <div className="text-slate-400">Modules</div>
                  <div className="text-sm font-semibold text-slate-100">{moduleLabel}</div>
                </div>
                <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                  <div className="text-slate-400">Coherence</div>
                  <div className="text-sm font-semibold text-emerald-300">{coherenceLabel}</div>
                </div>
              </div>
            )}
          </div>

          <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
            {sidebarOpen && hardware && (
              <div className="rounded-2xl border border-slate-800/60 bg-slate-900/50 p-3 text-xs mb-2">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Hardware</span>
                  <span className="text-slate-200">{hardware.cpus.count} cores</span>
                </div>
                <div className="mt-2 text-slate-200">
                  <div className="text-[11px] text-slate-400">
                    {hardware.cpus.model || hardware.platform} · {hardware.arch}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    RAM: {(hardware.totalMem / 1_073_741_824).toFixed(1)} GB total
                  </div>
                </div>
              </div>
            )}

            {sidebarOpen && (
              <div className="rounded-2xl border border-slate-800/60 bg-slate-900/50 p-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Navigation Mode</span>
                  <span className="text-slate-200">{showAdvanced ? 'Advanced' : 'Essential'}</span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setShowAdvanced(false)}
                    className={`rounded-lg border px-2 py-1 text-xs transition ${
                      !showAdvanced
                        ? 'border-emerald-400/50 bg-emerald-500/20 text-emerald-100'
                        : 'border-slate-800/60 bg-slate-900/60 text-slate-300 hover:border-slate-700/80'
                    }`}
                    type="button"
                  >
                    Essential
                  </button>
                  <button
                    onClick={() => setShowAdvanced(true)}
                    className={`rounded-lg border px-2 py-1 text-xs transition ${
                      showAdvanced
                        ? 'border-sky-400/50 bg-sky-500/20 text-sky-100'
                        : 'border-slate-800/60 bg-slate-900/60 text-slate-300 hover:border-slate-700/80'
                    }`}
                    type="button"
                  >
                    Advanced
                  </button>
                </div>
              </div>
            )}

            {(['core', 'intelligence', 'operations', 'labs'] as const).map((category) => {
              const categoryItems = visibleNavItems.filter(item => item.category === category);
              if (categoryItems.length === 0) return null;
              return (
                <div key={category}>
                  {sidebarOpen && (
                    <h3 className="px-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                      {categoryLabels[category]}
                    </h3>
                  )}
                  <div className="mt-3 space-y-2">
                    {categoryItems.map(item => {
                      const isActive = location === item.path || (item.path !== '/' && location?.startsWith(item.path));
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`group relative flex items-center gap-3 rounded-2xl border px-3 py-2.5 text-sm transition-all ${
                            isActive
                              ? 'border-emerald-400/40 bg-gradient-to-r from-emerald-500/20 via-slate-900/70 to-slate-900/60 text-white shadow-lg shadow-emerald-500/10'
                              : 'border-transparent bg-slate-900/40 text-slate-300 hover:border-slate-700/70 hover:bg-slate-900/70'
                          }`}
                        >
                          <div className={`${isActive ? 'text-emerald-300' : 'text-slate-400 group-hover:text-slate-200'}`}>
                            {item.icon}
                          </div>
                          {sidebarOpen && (
                            <span className="font-medium">{item.label}</span>
                          )}
                          {isActive && sidebarOpen && (
                            <span className="ml-auto h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.9)]" />
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </nav>

          <div className="border-t border-slate-800/60 p-4">
            {sidebarOpen ? (
              <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">System Pulse</span>
                  <span className="flex items-center gap-2 text-emerald-300">
                    <span className={`h-2 w-2 rounded-full ${serviceStatus.backend ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                    {serviceStatus.backend ? "Online" : "Offline"}
                  </span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${serviceStatus.nexusV3 ? 'bg-emerald-400' : 'bg-yellow-400'}`} />
                    Nexus V3
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${serviceStatus.backend ? 'bg-emerald-400' : 'bg-red-400'}`} />
                    Backend
                  </div>
                </div>
                <div className="mt-3 flex gap-2">
                  {["start","stop","restart"].map(action => (
                    <button
                      key={action}
                      type="button"
                      onClick={async () => {
                        try {
                          setControlMessage(`Executing ${action}…`);
                          const res = await fetch('/api/control', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ action })
                          });
                          const data = await res.json();
                          setControlMessage(data.message || `${action} sent`);
                          // refresh status shortly after
                          setTimeout(() => fetchSidebarStats(), 1200);
                        } catch (err: any) {
                          setControlMessage(`Failed: ${err?.message || 'error'}`);
                        }
                      }}
                      className="flex-1 rounded-lg border border-slate-800/60 bg-slate-900/60 px-2 py-1 text-slate-200 hover:border-emerald-400/50 hover:text-emerald-200 transition"
                    >
                      {action === 'start' ? 'Start' : action === 'stop' ? 'Stop' : 'Restart'}
                    </button>
                  ))}
                </div>
                {controlMessage && (
                  <div className="mt-2 text-[11px] text-slate-400">{controlMessage}</div>
                )}
              </div>
            ) : (
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl border border-slate-800/60 bg-slate-900/60">
                <Activity className="h-5 w-5 text-emerald-300" />
              </div>
            )}
          </div>
        </div>
      </aside>

      <main className={`min-h-screen transition-all duration-300 ${sidebarOpen ? 'ml-80' : 'ml-20'}`}>
        <header className="sticky top-0 z-30 border-b border-slate-800/60 bg-slate-950/70 backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Aurora Command Deck</p>
              <h2 className="text-2xl font-semibold text-slate-100">{activeItem?.label ?? 'Aurora'}</h2>
              <p className="text-xs text-slate-400">Live operations, telemetry, and coordinated execution.</p>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <div className="flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-emerald-200">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                System Online
              </div>
              <div className="rounded-full border border-slate-800/60 bg-slate-900/60 px-3 py-1 text-slate-200">
                Modules {moduleLabel}
              </div>
              <div className="rounded-full border border-slate-800/60 bg-slate-900/60 px-3 py-1 text-slate-200">
                Coherence {coherenceLabel}
              </div>
              <Link
                to="/chat"
                className="rounded-full border border-slate-700/70 bg-slate-900/70 px-3 py-1 text-slate-200 transition hover:border-emerald-400/60 hover:text-emerald-200"
              >
                Open Chat
              </Link>
              <Link
                to="/nexus"
                className="rounded-full border border-emerald-400/40 bg-emerald-400/10 px-3 py-1 text-emerald-200 transition hover:border-emerald-300 hover:bg-emerald-400/20"
              >
                Nexus
              </Link>
            </div>
          </div>
        </header>

        <div className="relative z-10 px-6 py-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
}
