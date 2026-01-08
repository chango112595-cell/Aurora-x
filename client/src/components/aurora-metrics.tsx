import { useEffect, useState } from "react";
import { Activity, Cpu, HardDrive, Users, HeartPulse } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Metrics {
  cpu?: number;
  memory?: number;
  disk?: number;
  workers?: number;
  selfHealingEvents?: number;
  v3Available?: boolean;
}

interface AuroraMetricsOverlayProps {
  className?: string;
  refreshInterval?: number;
}

export function AuroraMetricsOverlay({ className = "", refreshInterval = 5000 }: AuroraMetricsOverlayProps) {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setError(null);
        const [systemRes, workersRes, healersRes, v3Res] = await Promise.allSettled([
          fetch("/api/system/metrics"),
          fetch("/api/nexus-v3/workers"),
          fetch("/api/nexus-v3/self-healers"),
          fetch("/api/nexus-v3/health"),
        ]);

        const nextMetrics: Metrics = {};

        if (systemRes.status === "fulfilled" && systemRes.value.ok) {
          const data = await systemRes.value.json();
          nextMetrics.cpu = typeof data.cpu === "number" ? data.cpu : undefined;
          nextMetrics.memory = typeof data.memory === "number" ? data.memory : undefined;
          nextMetrics.disk = typeof data.disk === "number" ? data.disk : undefined;
        }

        if (workersRes.status === "fulfilled" && workersRes.value.ok) {
          const data = await workersRes.value.json();
          nextMetrics.workers = typeof data.total === "number" ? data.total : undefined;
        }

        if (healersRes.status === "fulfilled" && healersRes.value.ok) {
          const data = await healersRes.value.json();
          nextMetrics.selfHealingEvents = typeof data.healsPerformed === "number" ? data.healsPerformed : undefined;
        }

        if (v3Res.status === "fulfilled" && v3Res.value.ok) {
          const data = await v3Res.value.json();
          nextMetrics.v3Available = data.status === "healthy" || data.available === true;
        }

        if (!Object.keys(nextMetrics).length) {
          setError("Metrics unavailable");
          return;
        }

        setMetrics(nextMetrics);
      } catch (err) {
        console.error("[AuroraMetrics] Failed to fetch:", err);
        setError("Metrics unavailable");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (isLoading) {
    return (
      <div className={`fixed bottom-3 right-3 bg-slate-900/90 backdrop-blur-sm border border-purple-500/30 rounded-lg p-3 text-xs shadow-lg ${className}`} data-testid="metrics-overlay-loading">
        <div className="flex items-center gap-2 text-purple-400">
          <Activity className="w-4 h-4 animate-pulse" />
          <span>Loading metrics...</span>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className={`fixed bottom-3 right-3 bg-slate-900/90 backdrop-blur-sm border border-red-500/30 rounded-lg p-3 text-xs shadow-lg ${className}`} data-testid="metrics-overlay-error">
        <div className="flex items-center gap-2 text-red-400">
          <Activity className="w-4 h-4" />
          <span>{error || "Metrics unavailable"}</span>
        </div>
      </div>
    );
  }

  const getStatusColor = (value: number | undefined, thresholds: { warning: number; critical: number }) => {
    if (typeof value !== "number") return "text-slate-500";
    if (value >= thresholds.critical) return "text-red-400";
    if (value >= thresholds.warning) return "text-yellow-400";
    return "text-green-400";
  };

  return (
    <div
      className={`fixed bottom-3 right-3 bg-slate-900/90 backdrop-blur-sm border border-purple-500/30 rounded-lg p-4 text-xs shadow-lg min-w-[200px] ${className}`}
      data-testid="metrics-overlay"
    >
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-purple-500/20">
        <Activity className="w-4 h-4 text-purple-400" />
        <span className="font-semibold text-purple-300">System Metrics</span>
        <Badge variant="outline" className="ml-auto text-[10px] px-1.5 py-0">
          Live
        </Badge>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between" data-testid="metric-cpu">
          <div className="flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-300">CPU</span>
          </div>
          <span className={getStatusColor(metrics.cpu, { warning: 70, critical: 90 })}>
            {typeof metrics.cpu === "number" ? `${metrics.cpu.toFixed(1)}%` : "Unavailable"}
          </span>
        </div>

        <div className="flex items-center justify-between" data-testid="metric-memory">
          <div className="flex items-center gap-2">
            <HardDrive className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-300">Memory</span>
          </div>
          <span className={getStatusColor(metrics.memory, { warning: 80, critical: 95 })}>
            {typeof metrics.memory === "number" ? `${metrics.memory.toFixed(1)}%` : "Unavailable"}
          </span>
        </div>

        <div className="flex items-center justify-between" data-testid="metric-workers">
          <div className="flex items-center gap-2">
            <Users className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-300">Workers</span>
          </div>
          <span className="text-purple-300">
            {typeof metrics.workers === "number" ? metrics.workers : "Unavailable"}
          </span>
        </div>

        <div className="flex items-center justify-between" data-testid="metric-healing">
          <div className="flex items-center gap-2">
            <HeartPulse className="w-3.5 h-3.5 text-pink-400" />
            <span className="text-slate-300">Self-Heals</span>
          </div>
          <span className="text-pink-300">
            {typeof metrics.selfHealingEvents === "number" ? metrics.selfHealingEvents : "Unavailable"}
          </span>
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-purple-500/20">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-slate-500">Aurora Nexus V3</span>
          <span className={metrics.v3Available ? "text-green-400" : "text-slate-500"}>
            {metrics.v3Available ? "Active" : "Unavailable"}
          </span>
        </div>
      </div>
    </div>
  );
}

export default AuroraMetricsOverlay;
