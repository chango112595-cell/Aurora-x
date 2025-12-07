import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Activity, 
  Cpu, 
  Zap, 
  CheckCircle2, 
  AlertCircle,
  Clock,
  Bot,
  Sparkles,
  Brain,
  RefreshCw
} from "lucide-react";

interface ActivityEntry {
  id: string;
  timestamp: string;
  type: string;
  message: string;
  details: Record<string, any>;
}

interface WorkerMetrics {
  total: number;
  active: number;
  idle: number;
  queued: number;
  completed: number;
  failed: number;
}

interface SystemState {
  state: string;
  hyperspeed: boolean;
  autonomous: boolean;
  hybrid_mode: boolean;
}

interface ActivityData {
  activities: ActivityEntry[];
  workers: WorkerMetrics | null;
  system: SystemState | null;
  timestamp: string;
  error?: string;
}

function getActivityIcon(type: string) {
  switch (type) {
    case "chat": return <Bot className="h-3 w-3" />;
    case "processing": return <Cpu className="h-3 w-3" />;
    case "synthesis": return <Sparkles className="h-3 w-3" />;
    case "thinking": return <Brain className="h-3 w-3" />;
    case "complete": return <CheckCircle2 className="h-3 w-3" />;
    case "error": return <AlertCircle className="h-3 w-3" />;
    default: return <Activity className="h-3 w-3" />;
  }
}

function getActivityColor(type: string) {
  switch (type) {
    case "chat": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    case "processing": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    case "synthesis": return "bg-cyan-500/20 text-cyan-400 border-cyan-500/30";
    case "thinking": return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    case "complete": return "bg-green-500/20 text-green-400 border-green-500/30";
    case "error": return "bg-red-500/20 text-red-400 border-red-500/30";
    default: return "bg-muted text-muted-foreground";
  }
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", { 
    hour: "2-digit", 
    minute: "2-digit",
    second: "2-digit"
  });
}

export function ActivityMonitor() {
  const { data, isLoading, error, refetch } = useQuery<ActivityData>({
    queryKey: ["/api/nexus-v3/activity"],
    refetchInterval: 2000,
  });

  if (isLoading) {
    return (
      <Card className="bg-card/50 backdrop-blur border-border/50" data-testid="activity-monitor-loading">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            Activity Monitor
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card className="bg-card/50 backdrop-blur border-border/50" data-testid="activity-monitor-error">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            Activity Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <AlertCircle className="h-4 w-4 text-destructive" />
            <span>Activity data unavailable</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const workers = data.workers;
  const system = data.system;
  const activities = data.activities || [];

  const workerUtilization = workers ? 
    Math.round((workers.active / workers.total) * 100) : 0;

  return (
    <Card className="bg-card/50 backdrop-blur border-border/50" data-testid="activity-monitor">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            Activity Monitor
          </div>
          <button 
            onClick={() => refetch()} 
            className="p-1 hover:bg-muted rounded transition-colors"
            data-testid="button-refresh-activity"
          >
            <RefreshCw className="h-3 w-3 text-muted-foreground" />
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {system && (
          <div className="flex flex-wrap gap-2" data-testid="system-status-badges">
            <Badge 
              variant="outline" 
              className={system.state === "hyperspeed" ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" : ""}
              data-testid="badge-system-state"
            >
              <Zap className="h-3 w-3 mr-1" />
              {system.state.toUpperCase()}
            </Badge>
            {system.hyperspeed && (
              <Badge variant="outline" className="bg-purple-500/20 text-purple-400 border-purple-500/30" data-testid="badge-hyperspeed">
                <Sparkles className="h-3 w-3 mr-1" />
                HYPERSPEED
              </Badge>
            )}
            {system.autonomous && (
              <Badge variant="outline" className="bg-green-500/20 text-green-400 border-green-500/30" data-testid="badge-autonomous">
                <Bot className="h-3 w-3 mr-1" />
                AUTONOMOUS
              </Badge>
            )}
          </div>
        )}

        {workers && (
          <div className="space-y-2" data-testid="worker-metrics">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Worker Utilization</span>
              <span className="font-mono">{workers.active}/{workers.total} active</span>
            </div>
            <Progress value={workerUtilization} className="h-2" data-testid="progress-worker-utilization" />
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 rounded bg-muted/50">
                <div className="text-lg font-bold text-green-400" data-testid="text-workers-idle">{workers.idle}</div>
                <div className="text-[10px] text-muted-foreground">Idle</div>
              </div>
              <div className="p-2 rounded bg-muted/50">
                <div className="text-lg font-bold text-yellow-400" data-testid="text-tasks-queued">{workers.queued}</div>
                <div className="text-[10px] text-muted-foreground">Queued</div>
              </div>
              <div className="p-2 rounded bg-muted/50">
                <div className="text-lg font-bold text-cyan-400" data-testid="text-tasks-completed">{workers.completed}</div>
                <div className="text-[10px] text-muted-foreground">Done</div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Recent Activity</span>
            <span className="text-[10px] text-muted-foreground">{activities.length} events</span>
          </div>
          <ScrollArea className="h-[200px]" data-testid="activity-feed">
            {activities.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm">
                <Clock className="h-8 w-8 mb-2 opacity-50" />
                <p>No recent activity</p>
                <p className="text-xs">Activity will appear when Aurora processes requests</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activities.map((activity) => (
                  <div 
                    key={activity.id} 
                    className="flex items-start gap-2 p-2 rounded bg-muted/30 border border-border/30"
                    data-testid={`activity-entry-${activity.id}`}
                  >
                    <div className={`p-1 rounded ${getActivityColor(activity.type)}`}>
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs truncate" data-testid={`text-activity-message-${activity.id}`}>
                        {activity.message}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {formatTime(activity.timestamp)}
                      </p>
                    </div>
                    <Badge 
                      variant="outline" 
                      className={`text-[10px] ${getActivityColor(activity.type)}`}
                    >
                      {activity.type}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}

export default ActivityMonitor;
