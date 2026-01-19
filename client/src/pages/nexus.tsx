'use client';

import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Brain,
  Cpu,
  HeartPulse,
  Network,
  Package,
  Sparkles,
  Zap,
} from "lucide-react";
import ActivityMonitor from "@/components/ActivityMonitor";
import UnifiedSystemStatus from "@/components/UnifiedSystemStatus";

interface UnifiedStatus {
  v3: {
    connected: boolean;
    state?: string;
    version?: string;
  };
  unified: {
    anyConnected: boolean;
    timestamp: string;
  };
}

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
  available?: boolean;
}

interface V3Workers {
  total?: number;
  active?: number;
  idle?: number;
  available?: boolean;
}

interface V3SelfHealers {
  total?: number;
  active?: number;
  healing?: number;
  cooldown?: number;
  healsPerformed?: number;
  healthyComponents?: number;
  totalComponents?: number;
}

interface PackSummary {
  total_packs?: number;
  loaded_packs?: number;
  total_submodules?: number;
  available?: boolean;
}

function formatCount(value?: number) {
  return typeof value === "number" ? value.toLocaleString() : "Unavailable";
}

function StatusBadge({ active, label }: { active?: boolean; label: string }) {
  return (
    <Badge
      className={
        active
          ? "bg-emerald-500/20 text-emerald-200 border-emerald-500/40"
          : "bg-slate-800 text-slate-300 border-slate-600/40"
      }
    >
      {label}
    </Badge>
  );
}

export default function NexusPage() {
  const { data: unifiedStatus } = useQuery<UnifiedStatus>({
    queryKey: ["/api/nexus/status"],
    refetchInterval: 10000,
  });

  const v3Connected = unifiedStatus?.v3?.connected !== false;

  const { data: v3Status } = useQuery<V3Status>({
    queryKey: ["/api/nexus-v3/status"],
    refetchInterval: 10000,
    enabled: v3Connected,
  });

  const { data: v3Capabilities } = useQuery<V3Capabilities>({
    queryKey: ["/api/nexus-v3/capabilities"],
    refetchInterval: 15000,
    enabled: v3Connected,
  });

  const { data: v3Workers } = useQuery<V3Workers>({
    queryKey: ["/api/nexus-v3/workers"],
    refetchInterval: 15000,
    enabled: v3Connected,
  });

  const { data: v3Healers } = useQuery<V3SelfHealers>({
    queryKey: ["/api/nexus-v3/self-healers"],
    refetchInterval: 20000,
    enabled: v3Connected,
  });

  const { data: packSummary } = useQuery<PackSummary>({
    queryKey: ["/api/nexus-v3/packs"],
    refetchInterval: 60000,
    enabled: v3Connected,
  });

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-3xl border border-slate-800/70 bg-slate-900/60 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <Sparkles className="h-6 w-6 text-emerald-300" />
              <h1 className="text-2xl font-semibold text-slate-100">Nexus Command</h1>
              <Badge className="bg-emerald-500/20 text-emerald-100 border-emerald-400/40">
                Aurora Nexus V3
              </Badge>
            </div>
            <p className="text-sm text-slate-400">
              Live production telemetry for Aurora Nexus V3 - Universal Consciousness System.
            </p>
            <div className="flex flex-wrap gap-2">
              <StatusBadge active={unifiedStatus?.v3?.connected} label="Nexus V3" />
              <StatusBadge active={unifiedStatus?.unified?.anyConnected} label="System Online" />
            </div>
          </div>
          <div className="text-xs text-slate-500">
            Snapshot {unifiedStatus?.unified?.timestamp ? new Date(unifiedStatus.unified.timestamp).toLocaleTimeString() : "Unavailable"}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-emerald-200">
              <Cpu className="h-4 w-4 text-emerald-400" />
              Workers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-100">
            {formatCount(v3Capabilities?.workers)}
          </CardContent>
        </Card>
        <Card className="bg-slate-900/60 border-sky-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-sky-200">
              <Network className="h-4 w-4 text-sky-400" />
              Tiers
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-sky-100">
            {formatCount(v3Capabilities?.tiers)}
          </CardContent>
        </Card>
        <Card className="bg-slate-900/60 border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm text-amber-200">
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
            <CardTitle className="flex items-center gap-2 text-sm text-emerald-200">
              <Package className="h-4 w-4 text-emerald-400" />
              Modules
            </CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-semibold text-emerald-100">
            {formatCount(v3Capabilities?.modules)}
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-1">
        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-200">
              <Brain className="h-5 w-5 text-emerald-400" />
              Aurora Nexus V3 - Universal Consciousness System
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <StatusBadge active={v3Connected} label="Online" />
              <Badge className="bg-slate-800 text-slate-300 border-slate-600/40">
                {v3Status?.state ? v3Status.state.toUpperCase() : "STATE UNAVAILABLE"}
              </Badge>
              <Badge className="bg-slate-800 text-slate-300 border-slate-600/40">
                {v3Status?.version ? `v${v3Status.version}` : "Version Unknown"}
              </Badge>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="rounded-lg bg-slate-950/60 border border-emerald-500/20 p-3">
                <div className="text-emerald-200/70">Workers</div>
                <div className="text-lg font-semibold text-emerald-100">
                  {formatCount(v3Capabilities?.workers)}
                </div>
              </div>
              <div className="rounded-lg bg-slate-950/60 border border-emerald-500/20 p-3">
                <div className="text-emerald-200/70">Modules</div>
                <div className="text-lg font-semibold text-emerald-100">
                  {formatCount(v3Capabilities?.modules)}
                </div>
              </div>
              <div className="rounded-lg bg-slate-950/60 border border-emerald-500/20 p-3">
                <div className="text-emerald-200/70">Tiers</div>
                <div className="text-lg font-semibold text-emerald-100">
                  {formatCount(v3Capabilities?.tiers)}
                </div>
              </div>
              <div className="rounded-lg bg-slate-950/60 border border-emerald-500/20 p-3">
                <div className="text-emerald-200/70">AEMs</div>
                <div className="text-lg font-semibold text-emerald-100">
                  {formatCount(v3Capabilities?.aems)}
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <StatusBadge active={v3Capabilities?.hyperspeed_enabled} label="Hyperspeed" />
              <StatusBadge active={v3Capabilities?.hybrid_mode_enabled} label="Hybrid Mode" />
              <StatusBadge active={v3Capabilities?.autonomous_mode} label="Autonomous" />
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="bg-slate-900/60 border-emerald-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-200">
              <Cpu className="h-5 w-5 text-emerald-400" />
              Worker Load
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Total</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Workers?.total)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Active</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Workers?.active)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-emerald-200/70">Idle</span>
              <span className="text-emerald-100 font-semibold">{formatCount(v3Workers?.idle)}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-rose-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-rose-200">
              <HeartPulse className="h-5 w-5 text-rose-400" />
              Self-Healing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-rose-200/70">Active Healers</span>
              <span className="text-rose-100 font-semibold">{formatCount(v3Healers?.active)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-rose-200/70">Total Healers</span>
              <span className="text-rose-100 font-semibold">{formatCount(v3Healers?.total)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-rose-200/70">Heals Performed</span>
              <span className="text-rose-100 font-semibold">{formatCount(v3Healers?.healsPerformed)}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-amber-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-200">
              <Package className="h-5 w-5 text-amber-400" />
              Packs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-amber-200/70">Total Packs</span>
              <span className="text-amber-100 font-semibold">{formatCount(packSummary?.total_packs)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-amber-200/70">Loaded Packs</span>
              <span className="text-amber-100 font-semibold">{formatCount(packSummary?.loaded_packs)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-amber-200/70">Submodules</span>
              <span className="text-amber-100 font-semibold">{formatCount(packSummary?.total_submodules)}</span>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <UnifiedSystemStatus />
        <ActivityMonitor />
      </section>
    </div>
  );
}
