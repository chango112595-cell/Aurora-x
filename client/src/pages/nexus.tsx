import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Activity, Brain, Cpu, HeartPulse, Network, Package, Sparkles } from "lucide-react";
import ActivityMonitor from "@/components/ActivityMonitor";
import UnifiedSystemStatus from "@/components/UnifiedSystemStatus";

interface UnifiedStatus {
  v2: {
    connected: boolean;
    port?: number;
    quantum_coherence?: number;
    healthy_services?: number;
    ai_learning_active?: boolean;
    autonomous_healing_active?: boolean;
  };
  v3: {
    connected: boolean;
    state?: string;
    version?: string;
  };
  unified: {
    anyConnected: boolean;
    allConnected: boolean;
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

interface V2Status {
  status?: string;
  version?: string;
  services?: Record<string, { status?: string; health?: number }>;
  quantum_coherence?: number;
  healthy_services?: number;
  ai_learning_active?: boolean;
  autonomous_healing_active?: boolean;
  embedded?: boolean;
}

function formatCount(value?: number) {
  return typeof value === "number" ? value.toLocaleString() : "Unavailable";
}

function formatPercent(value?: number) {
  if (typeof value !== "number") return "Unavailable";
  return `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
}

function StatusBadge({ active, label }: { active?: boolean; label: string }) {
  return (
    <Badge className={active ? "bg-emerald-500/20 text-emerald-200 border-emerald-500/40" : "bg-slate-800 text-slate-300 border-slate-600/40"}>
      {label}
    </Badge>
  );
}

export default function NexusPage() {
  const { data: unifiedStatus } = useQuery<UnifiedStatus>({
    queryKey: ["/api/nexus/status"],
    refetchInterval: 10000,
  });

  const v2Connected = unifiedStatus?.v2?.connected !== false;
  const v3Connected = unifiedStatus?.v3?.connected !== false;

  const { data: v2Status } = useQuery<V2Status>({
    queryKey: ["/api/luminar-nexus/v2/status"],
    refetchInterval: 15000,
    enabled: v2Connected,
  });

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

  const coherence = typeof v2Status?.quantum_coherence === "number"
    ? v2Status.quantum_coherence
    : unifiedStatus?.v2?.quantum_coherence;
  const coherencePercent = coherence !== undefined ? coherence * 100 : undefined;

  const v2Services = v2Status?.services || {};
  const v2ServiceEntries = Object.entries(v2Services);
  const v2ServiceCount = v2Status ? v2ServiceEntries.length : undefined;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20 text-white p-6">
      <div className="container mx-auto max-w-7xl space-y-8">
        <header className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <Sparkles className="h-6 w-6 text-cyan-400" />
            <h1 className="text-3xl font-semibold text-cyan-100">Nexus</h1>
            <Badge className="bg-cyan-500/20 text-cyan-200 border-cyan-500/40">
              Unified V2 + V3
            </Badge>
          </div>
          <p className="text-sm text-cyan-200/70">
            Production telemetry for Aurora Nexus V3 and Luminar Nexus V2. All values reflect live services.
          </p>
          <div className="flex flex-wrap gap-2">
            <StatusBadge active={unifiedStatus?.v3?.connected} label="Nexus V3" />
            <StatusBadge active={unifiedStatus?.v2?.connected} label="Nexus V2" />
            <StatusBadge active={unifiedStatus?.unified?.allConnected} label="Unified" />
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-slate-900/60 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-cyan-200">
                <Brain className="h-5 w-5 text-cyan-400" />
                Aurora Nexus V3
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
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-lg bg-slate-950/60 border border-cyan-500/20 p-3">
                  <div className="text-cyan-200/70">Workers</div>
                  <div className="text-lg font-semibold text-cyan-100">
                    {formatCount(v3Capabilities?.workers)}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-950/60 border border-cyan-500/20 p-3">
                  <div className="text-cyan-200/70">Modules</div>
                  <div className="text-lg font-semibold text-cyan-100">
                    {formatCount(v3Capabilities?.modules)}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-950/60 border border-cyan-500/20 p-3">
                  <div className="text-cyan-200/70">Tiers</div>
                  <div className="text-lg font-semibold text-cyan-100">
                    {formatCount(v3Capabilities?.tiers)}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-950/60 border border-cyan-500/20 p-3">
                  <div className="text-cyan-200/70">AEMs</div>
                  <div className="text-lg font-semibold text-cyan-100">
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

          <Card className="bg-slate-900/60 border-purple-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-purple-200">
                <Network className="h-5 w-5 text-purple-400" />
                Luminar Nexus V2
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <StatusBadge active={v2Connected} label="Online" />
                <Badge className="bg-slate-800 text-slate-300 border-slate-600/40">
                  {v2Status?.version ? `v${v2Status.version}` : "Version Unknown"}
                </Badge>
              </div>
              <div className="space-y-2 rounded-lg bg-slate-950/60 border border-purple-500/20 p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-purple-200/70">Quantum Coherence</span>
                  <span className="text-purple-100 font-semibold">{formatPercent(coherencePercent)}</span>
                </div>
                <Progress value={coherencePercent ?? 0} className="h-2 bg-slate-800" />
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-lg bg-slate-950/60 border border-purple-500/20 p-3">
                  <div className="text-purple-200/70">Healthy Services</div>
                  <div className="text-lg font-semibold text-purple-100">
                    {formatCount(v2Status?.healthy_services ?? unifiedStatus?.v2?.healthy_services)}
                  </div>
                </div>
                <div className="rounded-lg bg-slate-950/60 border border-purple-500/20 p-3">
                  <div className="text-purple-200/70">Services Online</div>
                  <div className="text-lg font-semibold text-purple-100">
                    {formatCount(v2ServiceCount)}
                  </div>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-xs">
                <StatusBadge active={v2Status?.ai_learning_active ?? unifiedStatus?.v2?.ai_learning_active} label="AI Learning" />
                <StatusBadge active={v2Status?.autonomous_healing_active ?? unifiedStatus?.v2?.autonomous_healing_active} label="Auto-Healing" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="bg-slate-900/60 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-cyan-200">
                <Cpu className="h-5 w-5 text-cyan-400" />
                Worker Load
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-cyan-200/70">Total</span>
                <span className="text-cyan-100 font-semibold">{formatCount(v3Workers?.total)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-cyan-200/70">Active</span>
                <span className="text-cyan-100 font-semibold">{formatCount(v3Workers?.active)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-cyan-200/70">Idle</span>
                <span className="text-cyan-100 font-semibold">{formatCount(v3Workers?.idle)}</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900/60 border-emerald-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-200">
                <HeartPulse className="h-5 w-5 text-emerald-400" />
                Self-Healing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Active Healers</span>
                <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.active)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Total Healers</span>
                <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.total)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-emerald-200/70">Heals Performed</span>
                <span className="text-emerald-100 font-semibold">{formatCount(v3Healers?.healsPerformed)}</span>
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
        </div>

        {v2ServiceEntries.length > 0 && (
          <Card className="bg-slate-900/60 border-purple-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-purple-200">
                <Activity className="h-5 w-5 text-purple-400" />
                V2 Service Health
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
              {v2ServiceEntries.map(([name, service]) => (
                <div key={name} className="rounded-lg border border-purple-500/20 bg-slate-950/60 p-3">
                  <div className="text-purple-100 font-semibold">{name}</div>
                  <div className="text-purple-200/70">Status: {service.status ?? "Unknown"}</div>
                  {typeof service.health === "number" && (
                    <div className="text-purple-200/70">Health: {service.health}%</div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <UnifiedSystemStatus />
          <ActivityMonitor />
        </div>
      </div>
    </div>
  );
}
