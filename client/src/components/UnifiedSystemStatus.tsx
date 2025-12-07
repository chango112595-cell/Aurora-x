import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, Server, Zap, Package, Brain, CheckCircle2, XCircle, AlertTriangle, Loader2 } from "lucide-react";

interface NexusV3Status {
  connected: boolean;
  state?: string;
  node_id?: string;
  version?: string;
  uptime?: number;
  modules_loaded?: number;
  workers?: number;
  tiers?: number;
  aems?: number;
  hybrid_mode_enabled?: boolean;
  hyperspeed_enabled?: boolean;
}

interface NexusV2Status {
  connected: boolean;
  port?: number;
  services?: Record<string, any>;
  quantum_coherence?: number;
  healthy_services?: number;
  ai_learning_active?: boolean;
  autonomous_healing_active?: boolean;
}

interface PackSummary {
  total_packs?: number;
  loaded_packs?: number;
  total_submodules?: number;
  packs?: Record<string, any>;
}

interface UnifiedStatus {
  v2: NexusV2Status;
  v3: NexusV3Status;
  unified: {
    anyConnected: boolean;
    allConnected: boolean;
    timestamp: string;
  };
}

function StatusIndicator({ connected, label, testId }: { connected: boolean; label: string; testId: string }) {
  return (
    <div className="flex items-center gap-2" data-testid={`status-indicator-${testId}`}>
      {connected ? (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      ) : (
        <XCircle className="h-4 w-4 text-red-500" />
      )}
      <span className="text-sm text-slate-600">{label}</span>
      <Badge className={`ml-auto ${connected ? "bg-cyan-500 text-white" : "bg-red-500 text-white"}`} data-testid={`badge-status-${testId}`}>
        {connected ? "Online" : "Offline"}
      </Badge>
    </div>
  );
}

function LoadingIndicator({ testId }: { testId: string }) {
  return (
    <div className="flex items-center gap-2" data-testid={`loading-${testId}`}>
      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      <span className="text-sm text-muted-foreground">Checking connection...</span>
    </div>
  );
}

function MetricSkeleton() {
  return (
    <div className="text-center p-4 rounded-lg bg-muted/50">
      <Skeleton className="h-8 w-12 mx-auto mb-2" />
      <Skeleton className="h-4 w-16 mx-auto" />
    </div>
  );
}

export default function UnifiedSystemStatus() {
  const { data: nexusStatus, isLoading: nexusLoading, isError: nexusError } = useQuery<UnifiedStatus>({
    queryKey: ['/api/nexus/status'],
    refetchInterval: 10000,
    retry: 1,
  });

  const v3Connected = nexusStatus?.v3?.connected;
  
  const { data: v3Capabilities, isLoading: capabilitiesLoading, isError: capabilitiesError } = useQuery<any>({
    queryKey: ['/api/nexus-v3/capabilities'],
    refetchInterval: 30000,
    retry: 1,
    enabled: v3Connected !== false,
  });

  const { data: packData, isLoading: packLoading, isError: packError } = useQuery<PackSummary>({
    queryKey: ['/api/nexus-v3/packs'],
    refetchInterval: 60000,
    retry: 1,
    enabled: v3Connected !== false,
  });

  const v2 = nexusStatus?.v2;
  const v3 = nexusStatus?.v3;

  const hasCapabilitiesData = v3Capabilities && typeof v3Capabilities.workers === 'number';
  const workers = hasCapabilitiesData ? v3Capabilities.workers : null;
  const tiers = hasCapabilitiesData ? v3Capabilities.tiers : null;
  const aems = hasCapabilitiesData ? v3Capabilities.aems : null;
  const modules = hasCapabilitiesData ? v3Capabilities.modules : null;

  return (
    <div className="space-y-4" data-testid="unified-system-status">
      <Card className="bg-purple-100/80 border-purple-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-slate-800">
            <Activity className="h-5 w-5 text-purple-600" />
            Aurora System Status
            {nexusLoading && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {nexusError && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-100 text-red-700" data-testid="error-nexus-status">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm">Unable to fetch system status. Backend may be unavailable.</span>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3 p-4 rounded-lg bg-white/90 border border-purple-200">
              <div className="flex items-center gap-2 mb-3">
                <Server className="h-4 w-4 text-slate-600" />
                <span className="font-medium text-slate-800">Luminar Nexus V2</span>
                <Badge variant="outline" className="ml-auto bg-slate-100 text-slate-600 border-slate-300" data-testid="badge-v2-port">Port 8000</Badge>
              </div>
              {nexusLoading ? (
                <LoadingIndicator testId="v2" />
              ) : (
                <>
                  <StatusIndicator 
                    connected={v2?.connected || false} 
                    label="Connection Status" 
                    testId="v2-connection"
                  />
                  {v2?.connected && (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">Quantum Coherence</span>
                        <span className="text-slate-800" data-testid="text-v2-quantum-coherence">{(v2.quantum_coherence || 0).toFixed(2)}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">AI Learning</span>
                        <Badge className={v2.ai_learning_active ? "bg-cyan-500 text-white" : "bg-slate-200 text-slate-600"} data-testid="badge-v2-ai-learning">
                          {v2.ai_learning_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">Auto Healing</span>
                        <Badge className={v2.autonomous_healing_active ? "bg-cyan-500 text-white" : "bg-slate-200 text-slate-600"} data-testid="badge-v2-auto-healing">
                          {v2.autonomous_healing_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </>
                  )}
                  {!v2?.connected && !nexusLoading && (
                    <div className="text-xs text-slate-500" data-testid="text-v2-offline-hint">
                      Service unavailable or not started
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="space-y-3 p-4 rounded-lg bg-white/90 border border-purple-200">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="h-4 w-4 text-slate-600" />
                <span className="font-medium text-slate-800">Aurora Nexus V3</span>
                <Badge variant="outline" className="ml-auto bg-slate-100 text-slate-600 border-slate-300" data-testid="badge-v3-port">Port 5002</Badge>
              </div>
              {nexusLoading ? (
                <LoadingIndicator testId="v3" />
              ) : (
                <>
                  <StatusIndicator 
                    connected={v3?.connected || false} 
                    label="Connection Status" 
                    testId="v3-connection"
                  />
                  {v3?.connected && (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">State</span>
                        <Badge className="bg-cyan-500 text-white" data-testid="badge-v3-state">{v3.state?.toUpperCase() || "RUNNING"}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">Hybrid Mode</span>
                        <Badge className={v3Capabilities?.hybrid_mode_enabled ? "bg-cyan-500 text-white" : "bg-slate-200 text-slate-600"} data-testid="badge-v3-hybrid-mode">
                          {v3Capabilities?.hybrid_mode_enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">Hyperspeed</span>
                        <Badge className={v3Capabilities?.hyperspeed_enabled ? "bg-cyan-500 text-white" : "bg-slate-200 text-slate-600"} data-testid="badge-v3-hyperspeed">
                          {v3Capabilities?.hyperspeed_enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </div>
                    </>
                  )}
                  {!v3?.connected && !nexusLoading && (
                    <div className="text-xs text-slate-500" data-testid="text-v3-offline-hint">
                      Service unavailable or not started
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-purple-100/80 border-purple-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-slate-800">
            <Zap className="h-5 w-5 text-purple-600" />
            Peak Capabilities
            {capabilitiesLoading && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {capabilitiesLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricSkeleton />
              <MetricSkeleton />
              <MetricSkeleton />
              <MetricSkeleton />
            </div>
          ) : capabilitiesError ? (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-100 text-red-700" data-testid="error-capabilities">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm">Failed to fetch capabilities data from Nexus V3</span>
            </div>
          ) : v3?.connected && hasCapabilitiesData ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-workers">
                <div className="text-3xl font-bold text-cyan-500" data-testid="text-workers-count">{workers}</div>
                <div className="text-sm text-slate-600">Workers</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-tiers">
                <div className="text-3xl font-bold text-cyan-500" data-testid="text-tiers-count">{tiers}</div>
                <div className="text-sm text-slate-600">Tiers</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-aems">
                <div className="text-3xl font-bold text-cyan-500" data-testid="text-aems-count">{aems}</div>
                <div className="text-sm text-slate-600">AEMs</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-modules">
                <div className="text-3xl font-bold text-cyan-500" data-testid="text-modules-count">{modules}</div>
                <div className="text-sm text-slate-600">Modules</div>
              </div>
            </div>
          ) : (
            <div className="text-center p-6 text-slate-500" data-testid="text-capabilities-unavailable">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Nexus V3 offline - capabilities unavailable</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="bg-purple-100/80 border-purple-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-slate-800">
            <Package className="h-5 w-5 text-purple-600" />
            Pack System
            {packLoading && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {packLoading ? (
            <div className="grid grid-cols-3 gap-4">
              <MetricSkeleton />
              <MetricSkeleton />
              <MetricSkeleton />
            </div>
          ) : packError ? (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-100 text-red-700" data-testid="error-packs">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm">Failed to fetch pack data from Nexus V3</span>
            </div>
          ) : packData && packData.total_packs && packData.total_packs > 0 ? (
            <>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-total-packs">
                  <div className="text-2xl font-bold text-cyan-500" data-testid="text-total-packs">{packData.total_packs}</div>
                  <div className="text-xs text-slate-600">Total Packs</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-loaded-packs">
                  <div className="text-2xl font-bold text-green-500" data-testid="text-loaded-packs">{packData.loaded_packs}</div>
                  <div className="text-xs text-slate-600">Loaded</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-white/90 border border-purple-200" data-testid="metric-submodules">
                  <div className="text-2xl font-bold text-cyan-500" data-testid="text-submodules">{packData.total_submodules}</div>
                  <div className="text-xs text-slate-600">Submodules</div>
                </div>
              </div>
              {packData.packs && Object.keys(packData.packs).length > 0 && (
                <div className="space-y-2">
                  {Object.entries(packData.packs).slice(0, 5).map(([id, pack]: [string, any]) => (
                    <div key={id} className="flex items-center justify-between text-sm p-2 rounded-lg bg-white/70 border border-purple-100" data-testid={`pack-item-${id}`}>
                      <div className="flex items-center gap-2">
                        {pack.exists ? (
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                        ) : (
                          <AlertTriangle className="h-3 w-3 text-yellow-500" />
                        )}
                        <span className="font-mono text-xs text-slate-500" data-testid={`text-pack-id-${id}`}>{id}</span>
                        <span className="text-slate-700" data-testid={`text-pack-name-${id}`}>{pack.name}</span>
                      </div>
                      {pack.submodule_count > 0 && (
                        <Badge variant="outline" className="text-xs bg-slate-100 text-slate-600 border-slate-300" data-testid={`badge-pack-submodules-${id}`}>
                          {pack.submodule_count} submodules
                        </Badge>
                      )}
                    </div>
                  ))}
                  {Object.keys(packData.packs).length > 5 && (
                    <div className="text-xs text-slate-500 text-center" data-testid="text-packs-remaining">
                      +{Object.keys(packData.packs).length - 5} more packs
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center p-6 text-slate-500" data-testid="text-packs-unavailable">
              <Package className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No packs loaded or Nexus V3 offline</p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="text-xs text-slate-500 text-center" data-testid="text-last-updated">
        Last updated: {nexusStatus?.unified?.timestamp ? new Date(nexusStatus.unified.timestamp).toLocaleTimeString() : 'N/A'}
      </div>
    </div>
  );
}
