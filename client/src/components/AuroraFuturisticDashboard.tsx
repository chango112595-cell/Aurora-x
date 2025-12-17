import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Brain,
  Cpu,
  Database,
  HeartPulse,
  Network,
  Package,
  Sparkles,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import UnifiedSystemStatus from "./UnifiedSystemStatus";
import ActivityMonitor from "./ActivityMonitor";

interface V3Capabilities {
  workers?: number;
  tiers?: number;
  aems?: number;
  modules?: number;
  hyperspeed_enabled?: boolean;
  hybrid_mode_enabled?: boolean;
  autonomous_mode?: boolean;
  available?: boolean;
}

interface V3Status {
  state?: string;
  version?: string;
  uptime?: number;
}

interface V3SelfHealers {
  total?: number;
  active?: number;
  healsPerformed?: number;
}

interface V3Workers {
  total?: number;
  active?: number;
  idle?: number;
}

interface PackSummary {
  total_packs?: number;
  loaded_packs?: number;
  total_submodules?: number;
}

interface V2Status {
  quantum_coherence?: number;
}

interface SystemMetrics {
  cpu?: number;
  memory?: number;
  disk?: number;
}

interface DbStatus {
  ready?: boolean;
  configured?: boolean;
}

function formatCount(value?: number) {
  return typeof value === "number" ? value.toLocaleString() : "Unavailable";
}

function formatPercent(value?: number) {
  if (typeof value !== "number") return "Unavailable";
  return `${value.toFixed(1)}%`;
}

export default function AuroraFuturisticDashboard() {
  const { data: v3Capabilities } = useQuery<V3Capabilities>({
    queryKey: ["/api/nexus-v3/capabilities"],
    refetchInterval: 15000,
  });

  const { data: v3Status } = useQuery<V3Status>({
    queryKey: ["/api/nexus-v3/status"],
    refetchInterval: 15000,
  });

  const { data: v3Workers } = useQuery<V3Workers>({
    queryKey: ["/api/nexus-v3/workers"],
    refetchInterval: 15000,
  });

  const { data: v3Healers } = useQuery<V3SelfHealers>({
    queryKey: ["/api/nexus-v3/self-healers"],
    refetchInterval: 20000,
  });

  const { data: packSummary } = useQuery<PackSummary>({
    queryKey: ["/api/nexus-v3/packs"],
    refetchInterval: 60000,
  });

  const { data: v2Status } = useQuery<V2Status>({
    queryKey: ["/api/luminar-nexus/v2/status"],
    refetchInterval: 15000,
  });

  const { data: systemMetrics } = useQuery<SystemMetrics>({
    queryKey: ["/api/system/metrics"],
    refetchInterval: 10000,
  });

  const { data: dbStatus } = useQuery<DbStatus>({
    queryKey: ["/api/database/status"],
    refetchInterval: 30000,
  });

  const coherencePercent = typeof v2Status?.quantum_coherence === "number"
    ? v2Status.quantum_coherence * 100
    : undefined;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white p-6">
      <div className="mb-8 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 blur-3xl" />
        <div className="relative bg-slate-900/60 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-8">
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Brain className="h-14 w-14 text-cyan-400 animate-pulse" />
                <div className="absolute inset-0 bg-cyan-400/20 blur-xl rounded-full" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  AURORA
                </h1>
                <p className="text-cyan-300/70 text-sm mt-1">Production Operations Dashboard</p>
                <div className="flex flex-wrap gap-2 mt-2 text-xs">
                  <Badge className="bg-slate-800 text-slate-200 border-slate-600/40">
                    {v3Status?.state ? v3Status.state.toUpperCase() : "STATE UNAVAILABLE"}
                  </Badge>
                  <Badge className="bg-slate-800 text-slate-200 border-slate-600/40">
                    {v3Status?.version ? `Nexus V3 ${v3Status.version}` : "Nexus V3 Unknown"}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="text-right space-y-2 min-w-[200px]">
              <div className="text-3xl font-bold text-cyan-400">
                {coherencePercent !== undefined ? `${coherencePercent.toFixed(1)}%` : "Unavailable"}
              </div>
              <div className="text-xs text-cyan-300/60">Quantum Coherence (V2)</div>
              <Progress value={coherencePercent ?? 0} className="h-2 bg-slate-800" />
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-6 text-xs">
            <Badge className={v3Capabilities?.hyperspeed_enabled ? "bg-purple-500/30 text-purple-100 border-purple-400/50" : "bg-slate-800 text-slate-300 border-slate-600/40"}>
              Hyperspeed {v3Capabilities?.hyperspeed_enabled ? "Enabled" : "Disabled"}
            </Badge>
            <Badge className={v3Capabilities?.hybrid_mode_enabled ? "bg-emerald-500/30 text-emerald-100 border-emerald-400/50" : "bg-slate-800 text-slate-300 border-slate-600/40"}>
              Hybrid {v3Capabilities?.hybrid_mode_enabled ? "Enabled" : "Disabled"}
            </Badge>
            <Badge className={v3Capabilities?.autonomous_mode ? "bg-cyan-500/30 text-cyan-100 border-cyan-400/50" : "bg-slate-800 text-slate-300 border-slate-600/40"}>
              Autonomous {v3Capabilities?.autonomous_mode ? "Enabled" : "Disabled"}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-6">
        <Card className="bg-slate-900/60 border-cyan-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-cyan-200 text-sm">
              <Network className="h-4 w-4 text-cyan-400" />
              Knowledge Tiers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-cyan-100">
            {formatCount(v3Capabilities?.tiers)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-purple-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-purple-200 text-sm">
              <Zap className="h-4 w-4 text-purple-400" />
              AEMs
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-purple-100">
            {formatCount(v3Capabilities?.aems)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-pink-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-pink-200 text-sm">
              <Activity className="h-4 w-4 text-pink-400" />
              Modules
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-pink-100">
            {formatCount(v3Capabilities?.modules)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-emerald-200 text-sm">
              <Cpu className="h-4 w-4 text-emerald-400" />
              Workers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-100">
            {formatCount(v3Workers?.total ?? v3Capabilities?.workers)}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <Card className="bg-slate-900/60 border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-amber-200 text-sm">
              <Package className="h-4 w-4 text-amber-400" />
              Packs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-amber-200/70">Total</span>
              <span className="text-amber-100 font-semibold">{formatCount(packSummary?.total_packs)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-amber-200/70">Loaded</span>
              <span className="text-amber-100 font-semibold">{formatCount(packSummary?.loaded_packs)}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-emerald-200 text-sm">
              <HeartPulse className="h-4 w-4 text-emerald-400" />
              Self-Healing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Active</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.active)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Total</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.total)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Heals</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.healsPerformed)}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-blue-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-blue-200 text-sm">
              <Database className="h-4 w-4 text-blue-400" />
              Database
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-blue-200/70">Status</span>
              <span className="text-blue-100 font-semibold">
                {dbStatus?.ready ? "Ready" : "Unavailable"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-blue-200/70">Configured</span>
              <span className="text-blue-100 font-semibold">
                {dbStatus?.configured ? "Yes" : "No"}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card className="bg-slate-900/60 border-cyan-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-cyan-200 text-sm">
              <Sparkles className="h-4 w-4 text-cyan-400" />
              System Load
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-cyan-200/70">CPU</span>
                <span className="text-cyan-100 font-semibold">{formatPercent(systemMetrics?.cpu)}</span>
              </div>
              <Progress value={systemMetrics?.cpu ?? 0} className="h-2 bg-slate-800" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-cyan-200/70">Memory</span>
                <span className="text-cyan-100 font-semibold">{formatPercent(systemMetrics?.memory)}</span>
              </div>
              <Progress value={systemMetrics?.memory ?? 0} className="h-2 bg-slate-800" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-cyan-200/70">Disk</span>
                <span className="text-cyan-100 font-semibold">{formatPercent(systemMetrics?.disk)}</span>
              </div>
              <Progress value={systemMetrics?.disk ?? 0} className="h-2 bg-slate-800" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <UnifiedSystemStatus />
        <ActivityMonitor />
      </div>
    </div>
  );
}
