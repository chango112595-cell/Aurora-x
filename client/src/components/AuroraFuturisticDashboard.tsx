import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Brain,
  Cpu,
  Database,
  HeartPulse,
  Layers,
  Network,
  Package,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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

interface ModuleOverview {
  timestamp?: string;
  auroraCore?: {
    available?: boolean;
    totalEntries?: number;
    pythonFiles?: number;
    auroraModules?: number;
    standardModules?: number;
    manifestCount?: number;
    temporalBreakdown?: Record<string, number>;
    tierBreakdown?: Record<string, number>;
    lastUpdated?: string | null;
    manifestUpdated?: string | null;
  };
  nexusV3?: {
    available?: boolean;
    moduleFiles?: number;
    registryCount?: number;
    subdirectories?: Array<{
      name: string;
      moduleIds: number;
      init: number;
      execute: number;
      cleanup: number;
      totalFiles: number;
    }>;
    lastUpdated?: string | null;
    registryUpdated?: string | null;
  };
}

interface UpdateStatus {
  timestamp?: string;
  ui?: {
    name?: string;
    version?: string;
    lastUpdated?: string | null;
  };
  backend?: {
    version?: string;
    node?: string;
    uptimeSeconds?: number;
    lastUpdated?: string | null;
  };
  nexusV3?: {
    version?: string | null;
    lastUpdated?: string | null;
  };
  memoryFabric?: {
    lastUpdated?: string | null;
  };
  manifests?: {
    tiers?: { count?: number; lastUpdated?: string | null; generatedAt?: string | null };
    executions?: { count?: number; lastUpdated?: string | null; generatedAt?: string | null };
    modules?: { count?: number; lastUpdated?: string | null; generatedAt?: string | null };
  };
}

function formatCount(value?: number) {
  return typeof value === "number" ? value.toLocaleString() : "Unavailable";
}

function formatPercent(value?: number) {
  if (typeof value !== "number") return "Unavailable";
  return `${value.toFixed(1)}%`;
}

function formatTimestamp(value?: string | null) {
  if (!value) return "Unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unavailable";
  return date.toLocaleString();
}

function formatDuration(seconds?: number) {
  if (typeof seconds !== "number") return "Unavailable";
  const normalized = Math.max(0, seconds);
  const hours = Math.floor(normalized / 3600);
  const minutes = Math.floor((normalized % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

function formatBreakdown(breakdown?: Record<string, number>, maxItems: number = 4) {
  if (!breakdown || Object.keys(breakdown).length === 0) return "Unavailable";
  return Object.entries(breakdown)
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxItems)
    .map(([key, value]) => `${key} ${value}`)
    .join(" | ");
}

function getStateBadgeClass(state?: string) {
  const normalized = state?.toLowerCase();
  if (!normalized) {
    return "bg-slate-900/70 text-slate-200 border-slate-700/60";
  }
  if (["available", "ready", "online", "operational"].includes(normalized)) {
    return "bg-emerald-500/20 text-emerald-100 border-emerald-400/40";
  }
  if (["degraded", "warning"].includes(normalized)) {
    return "bg-amber-500/20 text-amber-100 border-amber-400/40";
  }
  return "bg-rose-500/20 text-rose-100 border-rose-400/40";
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

  const modulesOverviewQuery = useQuery<ModuleOverview>({
    queryKey: ["/api/modules/overview"],
    refetchInterval: 60000,
  });

  const updateStatusQuery = useQuery<UpdateStatus>({
    queryKey: ["/api/aurora/update-status"],
    refetchInterval: 60000,
  });

  const modulesOverview = modulesOverviewQuery.data;
  const updateStatus = updateStatusQuery.data;
  const isRefreshing = modulesOverviewQuery.isFetching || updateStatusQuery.isFetching;

  const coherencePercent = typeof v2Status?.quantum_coherence === "number"
    ? v2Status.quantum_coherence * 100
    : undefined;
  const auroraCoreModules = modulesOverview?.auroraCore;
  const nexusModules = modulesOverview?.nexusV3;

  const handleRefresh = () => {
    modulesOverviewQuery.refetch();
    updateStatusQuery.refetch();
  };

  return (
    <div className="text-slate-100">
      <section className="relative mb-6 overflow-hidden rounded-3xl border border-slate-800/70 bg-slate-900/60 p-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.18),_transparent_60%)]" />
        <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-amber-400/10 blur-3xl" />
        <div className="absolute -left-16 bottom-0 h-32 w-32 rounded-full bg-sky-400/10 blur-3xl" />
        <div className="relative flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Brain className="h-12 w-12 text-emerald-300 animate-pulse" />
              <div className="absolute inset-0 rounded-full bg-emerald-400/20 blur-xl" />
            </div>
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-slate-100">AURORA</h1>
              <p className="mt-1 text-xs uppercase tracking-[0.25em] text-slate-400">Command Operations</p>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                <Badge className={getStateBadgeClass(v3Status?.state)}>
                  {v3Status?.state ? v3Status.state.toUpperCase() : "STATE UNAVAILABLE"}
                </Badge>
                <Badge className="bg-slate-900/70 text-slate-200 border-slate-700/60">
                  {v3Status?.version ? `Nexus V3 ${v3Status.version}` : "Nexus V3 Unknown"}
                </Badge>
              </div>
            </div>
          </div>
          <div className="min-w-[200px] space-y-2 text-right">
            <div className="text-3xl font-semibold text-emerald-300">
              {coherencePercent !== undefined ? `${coherencePercent.toFixed(1)}%` : "Unavailable"}
            </div>
            <div className="text-xs text-slate-400">Quantum Coherence (V2)</div>
            <Progress value={coherencePercent ?? 0} className="h-2 bg-slate-800/80" />
          </div>
        </div>
        <div className="relative mt-6 flex flex-wrap gap-2 text-xs">
          <Badge
            className={
              v3Capabilities?.hyperspeed_enabled
                ? "bg-amber-500/20 text-amber-100 border-amber-400/40"
                : "bg-slate-900/70 text-slate-300 border-slate-700/60"
            }
          >
            Hyperspeed {v3Capabilities?.hyperspeed_enabled ? "Enabled" : "Disabled"}
          </Badge>
          <Badge
            className={
              v3Capabilities?.hybrid_mode_enabled
                ? "bg-emerald-500/20 text-emerald-100 border-emerald-400/40"
                : "bg-slate-900/70 text-slate-300 border-slate-700/60"
            }
          >
            Hybrid {v3Capabilities?.hybrid_mode_enabled ? "Enabled" : "Disabled"}
          </Badge>
          <Badge
            className={
              v3Capabilities?.autonomous_mode
                ? "bg-sky-500/20 text-sky-100 border-sky-400/40"
                : "bg-slate-900/70 text-slate-300 border-slate-700/60"
            }
          >
            Autonomous {v3Capabilities?.autonomous_mode ? "Enabled" : "Disabled"}
          </Badge>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4 mb-6">
        <Card className="bg-slate-900/60 border-sky-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sky-200 text-sm">
              <Network className="h-4 w-4 text-sky-400" />
              Knowledge Tiers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-sky-100">
            {formatCount(v3Capabilities?.tiers)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-amber-200 text-sm">
              <Zap className="h-4 w-4 text-amber-400" />
              AEMs
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-amber-100">
            {formatCount(v3Capabilities?.aems)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-emerald-200 text-sm">
              <Activity className="h-4 w-4 text-emerald-400" />
              Modules
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-100">
            {formatCount(v3Capabilities?.modules)}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-cyan-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-cyan-200 text-sm">
              <Cpu className="h-4 w-4 text-cyan-400" />
              Workers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-cyan-100">
            {formatCount(v3Workers?.total ?? v3Capabilities?.workers)}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <Card className="bg-slate-900/60 border-orange-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-orange-200 text-sm">
              <Package className="h-4 w-4 text-orange-400" />
              Packs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-orange-200/70">Total</span>
              <span className="text-orange-100 font-semibold">{formatCount(packSummary?.total_packs)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-orange-200/70">Loaded</span>
              <span className="text-orange-100 font-semibold">{formatCount(packSummary?.loaded_packs)}</span>
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

        <Card className="bg-slate-900/60 border-sky-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sky-200 text-sm">
              <Database className="h-4 w-4 text-sky-400" />
              Database
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-sky-200/70">Status</span>
              <span className="text-sky-100 font-semibold">
                {dbStatus?.ready ? "Ready" : "Unavailable"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sky-200/70">Configured</span>
              <span className="text-sky-100 font-semibold">
                {dbStatus?.configured ? "Yes" : "No"}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <Card className="bg-slate-900/60 border-slate-700/70">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-slate-200 text-sm">
              <Sparkles className="h-4 w-4 text-emerald-300" />
              System Load
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-slate-300/70">CPU</span>
                <span className="text-slate-100 font-semibold">{formatPercent(systemMetrics?.cpu)}</span>
              </div>
              <Progress value={systemMetrics?.cpu ?? 0} className="h-2 bg-slate-800/80" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-slate-300/70">Memory</span>
                <span className="text-slate-100 font-semibold">{formatPercent(systemMetrics?.memory)}</span>
              </div>
              <Progress value={systemMetrics?.memory ?? 0} className="h-2 bg-slate-800/80" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-slate-300/70">Disk</span>
                <span className="text-slate-100 font-semibold">{formatPercent(systemMetrics?.disk)}</span>
              </div>
              <Progress value={systemMetrics?.disk ?? 0} className="h-2 bg-slate-800/80" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-emerald-200 text-sm">
                <RefreshCw className="h-4 w-4 text-emerald-400" />
                Update Center
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="h-8 px-3 text-xs"
              >
                {isRefreshing ? "Refreshing" : "Refresh"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">UI</span>
                <span className="text-emerald-100 font-semibold">
                  {updateStatus?.ui?.version
                    ? `${updateStatus?.ui?.name ?? "UI"} ${updateStatus?.ui?.version}`
                    : "Unavailable"}
                </span>
              </div>
              <div className="text-xs text-emerald-300/60">Updated {formatTimestamp(updateStatus?.ui?.lastUpdated)}</div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Backend</span>
                <span className="text-emerald-100 font-semibold">{updateStatus?.backend?.version ?? "Unavailable"}</span>
              </div>
              <div className="text-xs text-emerald-300/60">
                Node {updateStatus?.backend?.node ?? "Unknown"} | Uptime {formatDuration(updateStatus?.backend?.uptimeSeconds)}
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Nexus V3</span>
                <span className="text-emerald-100 font-semibold">{updateStatus?.nexusV3?.version ?? "Unavailable"}</span>
              </div>
              <div className="text-xs text-emerald-300/60">Updated {formatTimestamp(updateStatus?.nexusV3?.lastUpdated)}</div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Memory Fabric</span>
                <span className="text-emerald-100 font-semibold">
                  {updateStatus?.memoryFabric?.lastUpdated ? "Ready" : "Unavailable"}
                </span>
              </div>
              <div className="text-xs text-emerald-300/60">Updated {formatTimestamp(updateStatus?.memoryFabric?.lastUpdated)}</div>
            </div>
            <div className="pt-2 border-t border-emerald-500/20 text-xs text-emerald-300/70 space-y-1">
              <div className="flex items-center justify-between">
                <span>Manifests</span>
                <span>{formatCount(updateStatus?.manifests?.modules?.count)} modules</span>
              </div>
              <div className="text-emerald-300/60">
                Tiers {formatCount(updateStatus?.manifests?.tiers?.count)} | AEMs {formatCount(updateStatus?.manifests?.executions?.count)}
              </div>
              <div className="text-emerald-300/60">Updated {formatTimestamp(updateStatus?.manifests?.modules?.lastUpdated)}</div>
            </div>
            <div className="text-xs text-emerald-400/70">Snapshot {formatTimestamp(updateStatus?.timestamp)}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-slate-900/60 border-emerald-500/30 mb-6">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-emerald-200 text-sm">
            <Layers className="h-4 w-4 text-emerald-400" />
            Module Topology
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="rounded-xl border border-emerald-500/20 bg-slate-900/50 p-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-emerald-200/70">Aurora Core Modules</span>
              <span className="text-emerald-100 font-semibold">{formatCount(auroraCoreModules?.manifestCount)}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Aurora Modules</span>
                <span className="text-emerald-100 font-semibold">{formatCount(auroraCoreModules?.auroraModules)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Standard Modules</span>
                <span className="text-emerald-100 font-semibold">{formatCount(auroraCoreModules?.standardModules)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Python Files</span>
                <span className="text-emerald-100 font-semibold">{formatCount(auroraCoreModules?.pythonFiles)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Total Entries</span>
                <span className="text-emerald-100 font-semibold">{formatCount(auroraCoreModules?.totalEntries)}</span>
              </div>
            </div>
            <div className="mt-2 text-xs text-emerald-200/60">
              Temporal: {formatBreakdown(auroraCoreModules?.temporalBreakdown)}
            </div>
            <div className="text-xs text-emerald-200/60">
              Tier: {formatBreakdown(auroraCoreModules?.tierBreakdown)}
            </div>
            <div className="text-xs text-emerald-400/70 mt-1">
              Updated {formatTimestamp(auroraCoreModules?.lastUpdated)}
            </div>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-slate-900/50 p-3 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-emerald-200/70">Nexus V3 Modules</span>
              <span className="text-emerald-100 font-semibold">{formatCount(nexusModules?.registryCount)} registry</span>
            </div>
            <div className="text-xs text-emerald-200/60">
              Root modules {formatCount(nexusModules?.moduleFiles)} | Updated {formatTimestamp(nexusModules?.lastUpdated)}
            </div>
            {nexusModules?.subdirectories && nexusModules.subdirectories.length > 0 ? (
              <div className="space-y-2">
                {nexusModules.subdirectories.map((subdir) => (
                  <div
                    key={subdir.name}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-emerald-500/20 bg-slate-900/60 px-3 py-2 text-xs"
                  >
                    <span className="font-mono text-emerald-200">{subdir.name}</span>
                    <span className="text-emerald-200/70">{formatCount(subdir.moduleIds)} modules</span>
                    <span className="text-emerald-200/70">
                      init {formatCount(subdir.init)} | exec {formatCount(subdir.execute)} | cleanup {formatCount(subdir.cleanup)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-emerald-200/60">Subdirectories unavailable</div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <UnifiedSystemStatus />
        <ActivityMonitor />
      </div>
    </div>
  );
}
