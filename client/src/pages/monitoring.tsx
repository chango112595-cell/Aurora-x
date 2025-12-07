import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { Activity, RefreshCw, Server, Cpu, HardDrive, Wifi, CheckCircle, AlertTriangle, XCircle, Clock, Database, Zap, TrendingUp, MemoryStick } from "lucide-react";
import { motion } from "framer-motion";

interface DiagnosticsData {
  status: string;
  timestamp: string;
  services: {
    database?: string;
    websocket?: string;
    bridge?: string;
    progress?: string;
  };
  corpus_count?: number;
  progress_tasks?: number;
}

interface AuroraStatus {
  status: string;
  powerUnits: number;
  autofixer: {
    workers: number;
    active: number;
    queued: number;
    completed: number;
  };
  uptime: number;
}

interface NexusStatus {
  v2: {
    connected: boolean;
    port: number;
    status: string;
  };
  v3: {
    connected: boolean;
    status: string;
    workers: number;
  };
}

interface SystemMetric {
  name: string;
  value: number;
  max: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  icon: string;
}

interface RealMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: { bytes_sent: number; bytes_recv: number };
}

export default function MonitoringPage() {
  const { data: realMetrics } = useQuery<RealMetrics>({
    queryKey: ['/api/system/metrics'],
    refetchInterval: 3000,
  });

  const cpuUsage = realMetrics?.cpu ?? 0;
  const memoryUsage = realMetrics?.memory ?? 0;
  const diskUsage = realMetrics?.disk ?? 0;

  const { data: diagnostics, isLoading: diagLoading, isError, error, refetch, isRefetching } = useQuery<DiagnosticsData>({
    queryKey: ['/api/diagnostics'],
    refetchInterval: 10000,
  });

  const { data: auroraStatus } = useQuery<AuroraStatus>({
    queryKey: ['/api/aurora/status'],
    refetchInterval: 5000,
  });

  const { data: nexusStatus } = useQuery<NexusStatus>({
    queryKey: ['/api/nexus/status'],
    refetchInterval: 10000,
  });

  const networkMbps = realMetrics?.network ? 
    Math.round((realMetrics.network.bytes_sent + realMetrics.network.bytes_recv) / 1024 / 1024) : 0;
  
  const systemMetrics: SystemMetric[] = [
    { name: 'CPU Usage', value: cpuUsage, max: 100, unit: '%', status: cpuUsage > 70 ? 'warning' : 'healthy', icon: 'cpu' },
    { name: 'Memory', value: memoryUsage, max: 100, unit: '%', status: memoryUsage > 80 ? 'warning' : 'healthy', icon: 'memory' },
    { name: 'Disk I/O', value: diskUsage, max: 100, unit: '%', status: diskUsage > 75 ? 'warning' : 'healthy', icon: 'disk' },
    { name: 'Network', value: networkMbps, max: 10000, unit: 'MB', status: 'healthy', icon: 'network' },
  ];

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'ok':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'degraded':
      case 'missing':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'error':
      case 'unreachable':
      case 'inactive':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'ok':
      case 'healthy':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'degraded':
      case 'missing':
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'error':
      case 'unreachable':
      case 'inactive':
      case 'critical':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  const getMetricIcon = (icon: string) => {
    switch (icon) {
      case 'cpu': return <Cpu className="w-5 h-5" />;
      case 'memory': return <MemoryStick className="w-5 h-5" />;
      case 'disk': return <HardDrive className="w-5 h-5" />;
      case 'network': return <Wifi className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  const formatUptime = (ms: number) => {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  const isLoading = diagLoading;

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-green-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-green-400/50 flex items-center justify-center bg-gradient-to-br from-green-500/20 to-cyan-500/20">
                <Activity className="w-6 h-6 text-green-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-green-400 via-cyan-400 to-green-400 bg-clip-text text-transparent" data-testid="text-page-title">
                System Monitor
              </h1>
              <p className="text-sm text-muted-foreground">
                Real-Time Performance & Health Metrics
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            disabled={isRefetching}
            className="border-green-500/30 hover:border-green-400/50"
            data-testid="button-refresh"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Activity className="w-12 h-12 text-green-400 animate-pulse mx-auto mb-4" />
            <p className="text-muted-foreground">Loading system metrics...</p>
          </div>
        </div>
      ) : isError ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-300 mb-2">Failed to load system metrics</p>
            <p className="text-sm text-muted-foreground mb-4">{error?.message || 'An error occurred'}</p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => refetch()}
              className="border-red-500/30 hover:border-red-400/50"
              data-testid="button-retry"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      ) : (
        <ScrollArea className="flex-1 p-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {systemMetrics.map((metric, index) => (
              <motion.div
                key={metric.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className={`border-${metric.status === 'healthy' ? 'green' : metric.status === 'warning' ? 'yellow' : 'red'}-500/30 bg-slate-900/50 backdrop-blur-xl`} data-testid={`card-metric-${metric.name.toLowerCase().replace(' ', '-')}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className={`w-10 h-10 rounded-lg bg-${metric.status === 'healthy' ? 'green' : metric.status === 'warning' ? 'yellow' : 'red'}-500/20 flex items-center justify-center text-${metric.status === 'healthy' ? 'green' : metric.status === 'warning' ? 'yellow' : 'red'}-400`}>
                        {getMetricIcon(metric.icon)}
                      </div>
                      <Badge variant="outline" className={getStatusColor(metric.status)}>
                        {metric.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mb-1">{metric.name}</p>
                    <p className="text-2xl font-bold text-green-400 mb-2">
                      {metric.value.toFixed(1)}{metric.unit}
                    </p>
                    <Progress value={metric.value} className="h-1.5 bg-slate-700" />
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-services">
              <CardHeader className="border-b border-cyan-500/20">
                <CardTitle className="flex items-center gap-2 text-lg text-cyan-300">
                  <Server className="w-5 h-5 text-cyan-400" />
                  Service Status
                </CardTitle>
                <CardDescription className="text-cyan-300/60">Core system services health</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-3">
                  {Object.entries(diagnostics?.services || {}).map(([service, status], index) => (
                    <motion.div
                      key={service}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {getStatusIcon(status)}
                        <span className="text-sm text-cyan-200 capitalize">{service}</span>
                      </div>
                      <Badge variant="outline" className={getStatusColor(status)}>
                        {status}
                      </Badge>
                    </motion.div>
                  ))}
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(nexusStatus?.v2?.connected ? 'connected' : 'error')}
                      <span className="text-sm text-cyan-200">Luminar Nexus V2</span>
                    </div>
                    <Badge variant="outline" className={getStatusColor(nexusStatus?.v2?.connected ? 'connected' : 'error')}>
                      {nexusStatus?.v2?.connected ? 'Connected' : 'Offline'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(nexusStatus?.v3?.connected ? 'connected' : 'error')}
                      <span className="text-sm text-cyan-200">Aurora Nexus V3</span>
                    </div>
                    <Badge variant="outline" className={getStatusColor(nexusStatus?.v3?.connected ? 'connected' : 'error')}>
                      {nexusStatus?.v3?.connected ? 'Connected' : 'Offline'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-aurora-health">
              <CardHeader className="border-b border-purple-500/20">
                <CardTitle className="flex items-center gap-2 text-lg text-purple-300">
                  <Zap className="w-5 h-5 text-purple-400" />
                  Aurora Core Health
                </CardTitle>
                <CardDescription className="text-purple-300/60">AI engine performance metrics</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-purple-300/60 mb-1">Power Units</p>
                      <p className="text-xl font-bold text-purple-300" data-testid="text-power-units">
                        {auroraStatus?.powerUnits || 0}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-purple-300/60 mb-1">Uptime</p>
                      <p className="text-xl font-bold text-purple-300" data-testid="text-uptime">
                        {formatUptime(auroraStatus?.uptime || 0)}
                      </p>
                    </div>
                  </div>
                  <div className="p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-purple-300/60">Worker Utilization</p>
                      <p className="text-xs text-purple-300">
                        {auroraStatus?.autofixer?.active || 0} / {auroraStatus?.autofixer?.workers || 300}
                      </p>
                    </div>
                    <Progress 
                      value={((auroraStatus?.autofixer?.active || 0) / (auroraStatus?.autofixer?.workers || 300)) * 100} 
                      className="h-2 bg-slate-700" 
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <span className="text-sm text-purple-200">Completed Tasks</span>
                    </div>
                    <span className="text-sm font-mono text-green-400">
                      {auroraStatus?.autofixer?.completed || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="border-green-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-system-overview">
            <CardHeader className="border-b border-green-500/20">
              <CardTitle className="flex items-center gap-2 text-lg text-green-300">
                <Database className="w-5 h-5 text-green-400" />
                System Overview
              </CardTitle>
              <CardDescription className="text-green-300/60">General system statistics</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                  <p className="text-xs text-green-300/60 mb-1">Corpus Records</p>
                  <p className="text-lg font-mono text-green-300" data-testid="text-corpus-count">
                    {diagnostics?.corpus_count || 0}
                  </p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                  <p className="text-xs text-green-300/60 mb-1">Progress Tasks</p>
                  <p className="text-lg font-mono text-green-300" data-testid="text-progress-tasks">
                    {diagnostics?.progress_tasks || 0}
                  </p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                  <p className="text-xs text-green-300/60 mb-1">System Status</p>
                  <Badge variant="outline" className={getStatusColor(diagnostics?.status)} data-testid="badge-system-status">
                    {diagnostics?.status || 'Unknown'}
                  </Badge>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                  <p className="text-xs text-green-300/60 mb-1">Last Check</p>
                  <p className="text-sm font-mono text-green-300" data-testid="text-last-check">
                    {diagnostics?.timestamp ? new Date(diagnostics.timestamp).toLocaleTimeString() : 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </ScrollArea>
      )}
    </div>
  );
}
