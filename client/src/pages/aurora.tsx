'use client';

import { useQuery } from '@tanstack/react-query';
import { Link } from 'wouter';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Brain,
  Cpu,
  Database,
  HeartPulse,
  Layers,
  Network,
  Package,
  Sparkles,
  Zap,
} from 'lucide-react';
import ActivityMonitor from '@/components/ActivityMonitor';
import UnifiedSystemStatus from '@/components/UnifiedSystemStatus';

interface AuroraStatus {
  status: string;
  powerUnits: number;
  knowledgeCapabilities: number;
  executionModes: number;
  systemComponents: number;
  totalModules: number;
  autofixer: {
    workers: number;
    active: number;
    queued: number;
    completed: number;
  };
  selfHealers: {
    total: number;
    active: number;
    status: string;
    healsPerformed: number;
    healthyComponents?: number;
    totalComponents?: number;
  };
  packs: {
    total: number;
    loaded: number;
    active: string[];
  };
  nexusV3: {
    connected: boolean;
    version: string | null;
    tiers: number | null;
    aems: number | null;
    modules: number | null;
    hyperspeedEnabled: boolean;
  };
  uptime: number;
  version: string;
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

interface NexusStatus {
  v2: {
    connected: boolean;
    port?: number;
    quantum_coherence?: number;
  };
  v3: {
    connected: boolean;
    port?: number;
    state?: string;
    version?: string;
  };
  unified: {
    anyConnected: boolean;
    allConnected: boolean;
    timestamp: string;
  };
}

function formatCount(value?: number | null) {
  return typeof value === 'number' ? value.toLocaleString() : 'Unavailable';
}

function formatDurationMs(ms?: number) {
  if (typeof ms !== 'number') return 'Unavailable';
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${hours}h ${minutes}m ${seconds}s`;
}

function formatTimestamp(value?: string | null) {
  if (!value) return 'Unavailable';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Unavailable';
  return date.toLocaleString();
}

function formatBreakdown(breakdown?: Record<string, number>, maxItems: number = 4) {
  if (!breakdown || Object.keys(breakdown).length === 0) return 'Unavailable';
  return Object.entries(breakdown)
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxItems)
    .map(([key, value]) => `${key} ${value}`)
    .join(' | ');
}

function statusBadgeClass(status?: string) {
  const normalized = status?.toLowerCase();
  if (!normalized) return 'bg-slate-900/70 text-slate-200 border-slate-700/60';
  if (['operational', 'ready', 'online'].includes(normalized)) {
    return 'bg-emerald-500/20 text-emerald-100 border-emerald-400/40';
  }
  if (['degraded', 'warning'].includes(normalized)) {
    return 'bg-amber-500/20 text-amber-100 border-amber-400/40';
  }
  return 'bg-rose-500/20 text-rose-100 border-rose-400/40';
}

export default function AuroraPage() {
  const { data: status, isLoading, isError } = useQuery<AuroraStatus>({
    queryKey: ['/api/aurora/status'],
    refetchInterval: 5000,
  });

  const { data: modulesOverview } = useQuery<ModuleOverview>({
    queryKey: ['/api/modules/overview'],
    refetchInterval: 60000,
  });

  const { data: updateStatus } = useQuery<UpdateStatus>({
    queryKey: ['/api/aurora/update-status'],
    refetchInterval: 60000,
  });

  const { data: nexusStatus } = useQuery<NexusStatus>({
    queryKey: ['/api/nexus/status'],
    refetchInterval: 15000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center space-y-3">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
          <p className="text-sm text-slate-400">Initializing Aurora command core...</p>
        </div>
      </div>
    );
  }

  if (isError || !status) {
    return (
      <div className="flex items-center justify-center py-24">
        <Card className="border border-rose-500/40 bg-slate-900/60 p-6">
          <p className="text-rose-200">Aurora status unavailable. Check services and refresh.</p>
        </Card>
      </div>
    );
  }

  const healerActive = typeof status.selfHealers?.active === 'number' ? status.selfHealers.active : 0;
  const healerTotal = typeof status.selfHealers?.total === 'number' ? status.selfHealers.total : 0;
  const healerProgress = healerTotal > 0 ? (healerActive / healerTotal) * 100 : 0;

  const componentHealthy = typeof status.selfHealers?.healthyComponents === 'number' ? status.selfHealers.healthyComponents : 0;
  const componentTotal = typeof status.selfHealers?.totalComponents === 'number' ? status.selfHealers.totalComponents : 0;
  const componentProgress = componentTotal > 0 ? (componentHealthy / componentTotal) * 100 : 0;

  const autofixerActive = typeof status.autofixer?.active === 'number' ? status.autofixer.active : 0;
  const autofixerTotal = typeof status.autofixer?.workers === 'number' ? status.autofixer.workers : 0;
  const autofixerProgress = autofixerTotal > 0 ? (autofixerActive / autofixerTotal) * 100 : 0;

  const packLoaded = typeof status.packs?.loaded === 'number' ? status.packs.loaded : 0;
  const packTotal = typeof status.packs?.total === 'number' ? status.packs.total : 0;
  const packProgress = packTotal > 0 ? (packLoaded / packTotal) * 100 : 0;

  const auroraCoreModules = modulesOverview?.auroraCore;
  const nexusModules = modulesOverview?.nexusV3;
  const v2Connected = nexusStatus?.v2?.connected;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="relative overflow-hidden rounded-3xl border border-slate-800/70 bg-slate-900/60 p-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.18),_transparent_60%)]" />
        <div className="absolute -right-24 -top-24 h-40 w-40 rounded-full bg-amber-400/10 blur-3xl" />
        <div className="relative flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Aurora Command Core</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-100">Aurora Intelligence v{status.version}</h1>
            <p className="mt-1 text-sm text-slate-400">
              {formatCount(status.powerUnits)} power units aligned for hybrid execution.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <Badge className={statusBadgeClass(status.status)}>{status.status.toUpperCase()}</Badge>
              <Badge className={status.nexusV3?.connected ? 'bg-emerald-500/20 text-emerald-100 border-emerald-400/40' : 'bg-slate-900/70 text-slate-200 border-slate-700/60'}>
                Nexus V3 {status.nexusV3?.connected ? 'Online' : 'Offline'}
              </Badge>
              <Badge className={v2Connected ? 'bg-sky-500/20 text-sky-100 border-sky-400/40' : 'bg-slate-900/70 text-slate-200 border-slate-700/60'}>
                Nexus V2 {v2Connected ? 'Online' : 'Offline'}
              </Badge>
              <Badge className={status.nexusV3?.hyperspeedEnabled ? 'bg-amber-500/20 text-amber-100 border-amber-400/40' : 'bg-slate-900/70 text-slate-200 border-slate-700/60'}>
                Hyperspeed {status.nexusV3?.hyperspeedEnabled ? 'On' : 'Off'}
              </Badge>
            </div>
          </div>
          <div className="space-y-3 text-right">
            <div className="text-sm text-slate-400">Uptime</div>
            <div className="text-2xl font-semibold text-emerald-200">{formatDurationMs(status.uptime)}</div>
            <div className="flex flex-wrap justify-end gap-2">
              <Button asChild variant="outline" size="sm">
                <Link to="/chat">Open Chat</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link to="/nexus">Nexus</Link>
              </Button>
              <Button asChild size="sm">
                <Link to="/dashboard">Dashboard</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Sparkles className="h-4 w-4 text-emerald-300" />
              Power Units
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-200">
            {formatCount(status.powerUnits)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Brain className="h-4 w-4 text-sky-300" />
              Knowledge Capabilities
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-sky-200">
            {formatCount(status.knowledgeCapabilities)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Zap className="h-4 w-4 text-amber-300" />
              Execution Modes
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-amber-200">
            {formatCount(status.executionModes)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Layers className="h-4 w-4 text-emerald-300" />
              System Components
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-200">
            {formatCount(status.systemComponents)}
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Network className="h-4 w-4 text-sky-300" />
              Nexus Tiers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-sky-200">
            {formatCount(status.nexusV3?.tiers ?? undefined)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Cpu className="h-4 w-4 text-emerald-300" />
              Workers Online
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-200">
            {formatCount(status.autofixer?.workers)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <HeartPulse className="h-4 w-4 text-rose-300" />
              Self-Healers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-rose-200">
            {formatCount(status.selfHealers?.total)}
          </CardContent>
        </Card>
        <Card className="border-slate-800/70 bg-slate-900/60">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
              <Package className="h-4 w-4 text-amber-300" />
              Packs Loaded
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-amber-200">
            {formatCount(status.packs?.loaded)}
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <Card className="border-slate-800/70 bg-slate-900/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
                <Activity className="h-4 w-4 text-emerald-300" />
                Autonomous Operations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Self-Healers Active</span>
                  <span className="text-slate-200">{formatCount(healerActive)} / {formatCount(healerTotal)}</span>
                </div>
                <Progress value={healerProgress} className="h-2 bg-slate-800" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Components Healthy</span>
                  <span className="text-slate-200">{formatCount(componentHealthy)} / {formatCount(componentTotal)}</span>
                </div>
                <Progress value={componentProgress} className="h-2 bg-slate-800" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Autofixer Workforce</span>
                  <span className="text-slate-200">{formatCount(autofixerActive)} / {formatCount(autofixerTotal)}</span>
                </div>
                <Progress value={autofixerProgress} className="h-2 bg-slate-800" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Pack System</span>
                  <span className="text-slate-200">{formatCount(packLoaded)} / {formatCount(packTotal)}</span>
                </div>
                <Progress value={packProgress} className="h-2 bg-slate-800" />
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs text-slate-400">
                <div className="rounded-lg border border-slate-800/70 bg-slate-950/60 p-3">
                  <div className="text-slate-500">Queued Tasks</div>
                  <div className="mt-1 text-sm font-semibold text-slate-200">{formatCount(status.autofixer?.queued)}</div>
                </div>
                <div className="rounded-lg border border-slate-800/70 bg-slate-950/60 p-3">
                  <div className="text-slate-500">Heals Performed</div>
                  <div className="mt-1 text-sm font-semibold text-slate-200">{formatCount(status.selfHealers?.healsPerformed)}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800/70 bg-slate-900/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
                <Network className="h-4 w-4 text-sky-300" />
                Nexus Stack
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2 text-sm">
              <div className="rounded-xl border border-slate-800/70 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Nexus V3</span>
                  <Badge className={status.nexusV3?.connected ? 'bg-emerald-500/20 text-emerald-100 border-emerald-400/40' : 'bg-slate-900/70 text-slate-200 border-slate-700/60'}>
                    {status.nexusV3?.connected ? 'Connected' : 'Offline'}
                  </Badge>
                </div>
                <div className="mt-2 text-xs text-slate-400">Version {status.nexusV3?.version ?? 'Unavailable'}</div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                    <div className="text-slate-500">Tiers</div>
                    <div className="text-sm font-semibold text-slate-200">{formatCount(status.nexusV3?.tiers)}</div>
                  </div>
                  <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                    <div className="text-slate-500">AEMs</div>
                    <div className="text-sm font-semibold text-slate-200">{formatCount(status.nexusV3?.aems)}</div>
                  </div>
                  <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                    <div className="text-slate-500">Modules</div>
                    <div className="text-sm font-semibold text-slate-200">{formatCount(status.nexusV3?.modules)}</div>
                  </div>
                  <div className="rounded-lg border border-slate-800/60 bg-slate-900/60 p-2">
                    <div className="text-slate-500">Hyperspeed</div>
                    <div className="text-sm font-semibold text-slate-200">{status.nexusV3?.hyperspeedEnabled ? 'Enabled' : 'Disabled'}</div>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800/70 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Luminar Nexus V2</span>
                  <Badge className={v2Connected ? 'bg-sky-500/20 text-sky-100 border-sky-400/40' : 'bg-slate-900/70 text-slate-200 border-slate-700/60'}>
                    {v2Connected ? 'Connected' : 'Offline'}
                  </Badge>
                </div>
                <div className="mt-2 text-xs text-slate-400">Port {nexusStatus?.v2?.port ?? 8000}</div>
                <div className="mt-3 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Quantum Coherence</span>
                    <span className="text-slate-200">
                      {typeof nexusStatus?.v2?.quantum_coherence === 'number'
                        ? `${(nexusStatus.v2.quantum_coherence * 100).toFixed(1)}%`
                        : 'Unavailable'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Unified Status</span>
                    <span className="text-slate-200">
                      {nexusStatus?.unified?.allConnected ? 'All Connected' : 'Partial'}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800/70 bg-slate-900/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
                <Package className="h-4 w-4 text-amber-300" />
                Pack System
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Loaded Packs</span>
                <span className="text-slate-200">{formatCount(packLoaded)} / {formatCount(packTotal)}</span>
              </div>
              <Progress value={packProgress} className="h-2 bg-slate-800" />
              <div className="flex flex-wrap gap-2 text-xs text-slate-300">
                {(status.packs?.active || []).slice(0, 12).map((pack) => (
                  <Badge key={pack} variant="outline" className="border-slate-700/70 bg-slate-950/50 text-slate-200">
                    {pack}
                  </Badge>
                ))}
                {status.packs?.active && status.packs.active.length > 12 && (
                  <Badge variant="outline" className="border-slate-700/70 bg-slate-950/50 text-slate-400">
                    +{status.packs.active.length - 12} more
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="border-slate-800/70 bg-slate-900/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
                <Zap className="h-4 w-4 text-amber-300" />
                Update Center
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">UI</span>
                  <span className="text-slate-200">
                    {updateStatus?.ui?.version
                      ? `${updateStatus?.ui?.name ?? 'UI'} ${updateStatus?.ui?.version}`
                      : 'Unavailable'}
                  </span>
                </div>
                <div className="text-xs text-slate-500">Updated {formatTimestamp(updateStatus?.ui?.lastUpdated)}</div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Backend</span>
                  <span className="text-slate-200">{updateStatus?.backend?.version ?? 'Unavailable'}</span>
                </div>
                <div className="text-xs text-slate-500">Node {updateStatus?.backend?.node ?? 'Unknown'}</div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Nexus V3</span>
                  <span className="text-slate-200">{updateStatus?.nexusV3?.version ?? 'Unavailable'}</span>
                </div>
                <div className="text-xs text-slate-500">Updated {formatTimestamp(updateStatus?.nexusV3?.lastUpdated)}</div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Memory Fabric</span>
                  <span className="text-slate-200">{updateStatus?.memoryFabric?.lastUpdated ? 'Ready' : 'Unavailable'}</span>
                </div>
                <div className="text-xs text-slate-500">Updated {formatTimestamp(updateStatus?.memoryFabric?.lastUpdated)}</div>
              </div>
              <div className="border-t border-slate-800/60 pt-3 text-xs text-slate-500">
                Manifests: {formatCount(updateStatus?.manifests?.tiers?.count)} tiers | {formatCount(updateStatus?.manifests?.executions?.count)} AEMs | {formatCount(updateStatus?.manifests?.modules?.count)} modules
              </div>
              <div className="text-xs text-slate-600">Snapshot {formatTimestamp(updateStatus?.timestamp)}</div>
            </CardContent>
          </Card>

          <Card className="border-slate-800/70 bg-slate-900/60">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm text-slate-200">
                <Database className="h-4 w-4 text-emerald-300" />
                Module Topology
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="rounded-xl border border-slate-800/70 bg-slate-950/60 p-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Aurora Core Modules</span>
                  <span className="text-slate-200">{formatCount(auroraCoreModules?.manifestCount)}</span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Aurora Modules</span>
                    <span className="text-slate-200">{formatCount(auroraCoreModules?.auroraModules)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Standard Modules</span>
                    <span className="text-slate-200">{formatCount(auroraCoreModules?.standardModules)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Python Files</span>
                    <span className="text-slate-200">{formatCount(auroraCoreModules?.pythonFiles)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Entries</span>
                    <span className="text-slate-200">{formatCount(auroraCoreModules?.totalEntries)}</span>
                  </div>
                </div>
                <div className="mt-2 text-xs text-slate-500">Temporal: {formatBreakdown(auroraCoreModules?.temporalBreakdown)}</div>
                <div className="text-xs text-slate-500">Tier: {formatBreakdown(auroraCoreModules?.tierBreakdown)}</div>
              </div>
              <div className="rounded-xl border border-slate-800/70 bg-slate-950/60 p-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Nexus V3 Modules</span>
                  <span className="text-slate-200">{formatCount(nexusModules?.registryCount)} registry</span>
                </div>
                <div className="mt-2 text-xs text-slate-500">Root modules {formatCount(nexusModules?.moduleFiles)}</div>
                <div className="mt-3 space-y-2">
                  {(nexusModules?.subdirectories || []).slice(0, 6).map((subdir) => (
                    <div key={subdir.name} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800/60 bg-slate-900/60 px-3 py-2 text-xs">
                      <span className="font-mono text-slate-200">{subdir.name}</span>
                      <span className="text-slate-400">{formatCount(subdir.moduleIds)} modules</span>
                      <span className="text-slate-500">init {formatCount(subdir.init)} | exec {formatCount(subdir.execute)} | cleanup {formatCount(subdir.cleanup)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <UnifiedSystemStatus />
        <ActivityMonitor />
      </section>
    </div>
  );
}
