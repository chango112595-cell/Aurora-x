import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { Zap, RefreshCw, Bot, Cpu, Play, Pause, CheckCircle, Clock, AlertCircle, Shield, Sparkles, AlertTriangle, Activity } from "lucide-react";
import { motion } from "framer-motion";

interface AuroraStatus {
  status: string;
  powerUnits: number;
  autofixer: {
    workers: number;
    active: number;
    queued: number;
    completed: number;
  };
}

interface WorkerTask {
  id: string;
  type: string;
  status: 'running' | 'queued' | 'completed' | 'failed';
  priority: 'high' | 'medium' | 'low';
  description: string;
  progress?: number;
  startedAt: string;
}

interface V3Capabilities {
  autonomous_mode?: boolean;
  hybrid_mode_enabled?: boolean;
  hyperspeed_enabled?: boolean;
  available?: boolean;
}

export default function AutonomousPage() {
  const { data: auroraStatus, isLoading, isError, error, refetch, isRefetching } = useQuery<AuroraStatus>({
    queryKey: ['/api/aurora/status'],
    refetchInterval: 5000,
  });

  const { data: v3Capabilities } = useQuery<V3Capabilities>({
    queryKey: ['/api/nexus-v3/capabilities'],
    refetchInterval: 15000,
  });

  const autonomyModes = [
    {
      id: 'autonomous',
      name: 'Autonomous Mode',
      description: 'Self-directed execution without manual input',
      status: v3Capabilities?.autonomous_mode ? 'active' : 'disabled',
      icon: Bot
    },
    {
      id: 'hybrid',
      name: 'Hybrid Mode',
      description: 'Balanced execution between autonomous and guided control',
      status: v3Capabilities?.hybrid_mode_enabled ? 'active' : 'disabled',
      icon: Activity
    },
    {
      id: 'hyperspeed',
      name: 'Hyperspeed Mode',
      description: 'High-throughput execution pipeline for rapid tasks',
      status: v3Capabilities?.hyperspeed_enabled ? 'active' : 'disabled',
      icon: Sparkles
    }
  ];

  const getWorkerTasks = (): WorkerTask[] => {
    const activeWorkers = auroraStatus?.autofixer?.active || 0;
    const queuedTasks = auroraStatus?.autofixer?.queued || 0;
    const completedTasks = auroraStatus?.autofixer?.completed || 0;

    const tasks: WorkerTask[] = [];

    if (completedTasks > 0) {
      tasks.push({
        id: 'completed-1',
        type: 'system_check',
        status: 'completed',
        priority: 'low',
        description: `Completed ${completedTasks} autonomous task${completedTasks > 1 ? 's' : ''}`,
        progress: 100,
        startedAt: new Date(Date.now() - 300000).toISOString()
      });
    }

    if (activeWorkers > 0) {
      tasks.push({
        id: 'active-1',
        type: 'monitoring',
        status: 'running',
        priority: 'medium',
        description: `${activeWorkers} worker${activeWorkers > 1 ? 's' : ''} actively processing`,
        startedAt: new Date(Date.now() - 60000).toISOString()
      });
    }

    if (queuedTasks > 0) {
      tasks.push({
        id: 'queued-1',
        type: 'pending',
        status: 'queued',
        priority: 'low',
        description: `${queuedTasks} task${queuedTasks > 1 ? 's' : ''} in queue`,
        progress: 0,
        startedAt: ''
      });
    }

    if (tasks.length === 0) {
      tasks.push({
        id: 'idle-1',
        type: 'standby',
        status: 'completed',
        priority: 'low',
        description: 'All workers idle - ready for new tasks',
        progress: 100,
        startedAt: new Date().toISOString()
      });
    }

    return tasks;
  };

  const workerTasks = getWorkerTasks();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'idle': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'disabled': return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
      case 'running': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'queued': return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'completed': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'failed': return 'bg-red-500/20 text-red-300 border-red-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  const formatCount = (value?: number) =>
    typeof value === 'number' ? value.toLocaleString() : 'Unavailable';

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Play className="w-4 h-4 text-cyan-400" />;
      case 'queued': return <Clock className="w-4 h-4 text-purple-400" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-400" />;
      default: return <Pause className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-purple-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-purple-400/50 flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-cyan-500/20">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent" data-testid="text-page-title">
                Autonomous Tools
              </h1>
              <p className="text-sm text-muted-foreground">
                Self-Directed Capabilities & Worker Management
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="border-purple-500/30 hover:border-purple-400/50"
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
            <Bot className="w-12 h-12 text-purple-400 animate-pulse mx-auto mb-4" />
            <p className="text-muted-foreground">Loading autonomous systems...</p>
          </div>
        </div>
      ) : isError ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-300 mb-2">Failed to load autonomous systems</p>
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
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-workers">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-xs text-cyan-300/60">Workers</p>
                    <p className="text-2xl font-bold text-cyan-400" data-testid="text-workers">
                      {formatCount(auroraStatus?.autofixer?.workers)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-active">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <Play className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-300/60">Active</p>
                    <p className="text-2xl font-bold text-green-400" data-testid="text-active">
                      {formatCount(auroraStatus?.autofixer?.active)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-queued">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-purple-300/60">Queued</p>
                    <p className="text-2xl font-bold text-purple-400" data-testid="text-queued">
                      {formatCount(auroraStatus?.autofixer?.queued)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-pink-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-completed">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-pink-400" />
                  </div>
                  <div>
                    <p className="text-xs text-pink-300/60">Completed</p>
                    <p className="text-2xl font-bold text-pink-400" data-testid="text-completed">
                      {formatCount(auroraStatus?.autofixer?.completed)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-auto-settings">
              <CardHeader className="border-b border-cyan-500/20">
                <CardTitle className="text-lg text-cyan-300">Autonomy Status</CardTitle>
                <CardDescription className="text-cyan-300/60">Live mode flags from Nexus V3</CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-green-400" />
                    <div>
                      <p className="text-sm text-cyan-200">Autonomous Mode</p>
                      <p className="text-xs text-cyan-300/60">Self-directed orchestration</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(v3Capabilities?.autonomous_mode ? 'active' : 'disabled')}>
                    {v3Capabilities?.autonomous_mode ? 'Active' : 'Disabled'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <div>
                      <p className="text-sm text-cyan-200">Hybrid Mode</p>
                      <p className="text-xs text-cyan-300/60">Blended execution strategy</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(v3Capabilities?.hybrid_mode_enabled ? 'active' : 'disabled')}>
                    {v3Capabilities?.hybrid_mode_enabled ? 'Active' : 'Disabled'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <div>
                      <p className="text-sm text-cyan-200">Hyperspeed Mode</p>
                      <p className="text-xs text-cyan-300/60">High-throughput execution</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(v3Capabilities?.hyperspeed_enabled ? 'active' : 'disabled')}>
                    {v3Capabilities?.hyperspeed_enabled ? 'Active' : 'Disabled'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <div className="lg:col-span-2">
              <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-worker-tasks">
                <CardHeader className="border-b border-purple-500/20">
                  <CardTitle className="flex items-center gap-2 text-lg text-purple-300">
                    <Cpu className="w-5 h-5 text-purple-400" />
                    Worker Task Queue
                  </CardTitle>
                  <CardDescription className="text-purple-300/60">Current and pending autonomous tasks</CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  <ScrollArea className="h-[200px]">
                    <div className="space-y-3">
                      {workerTasks.map((task, index) => (
                        <motion.div
                          key={task.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Card className="border-purple-500/20 bg-slate-800/50" data-testid={`card-task-${task.id}`}>
                            <CardContent className="p-3">
                              <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                                <div className="flex items-center gap-2">
                                  {getStatusIcon(task.status)}
                                  <span className="text-sm text-purple-200">{task.description}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className={`text-xs ${getStatusColor(task.status)}`}>
                                    {task.status}
                                  </Badge>
                                  <Badge variant="outline" className={`text-xs ${getPriorityColor(task.priority)}`}>
                                    {task.priority}
                                  </Badge>
                                </div>
                              </div>
                              {task.status === 'running' && typeof task.progress === 'number' && (
                                <div className="mt-2">
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-xs text-purple-300/60">Progress</span>
                                    <span className="text-xs text-purple-300">{task.progress}%</span>
                                  </div>
                                  <Progress value={task.progress} className="h-1.5 bg-slate-700" />
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </div>

            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-autonomous-tools">
              <CardHeader className="border-b border-cyan-500/20">
                <CardTitle className="flex items-center gap-2 text-lg text-cyan-300">
                  <Bot className="w-5 h-5 text-cyan-400" />
                  Autonomy Modes
                </CardTitle>
                <CardDescription className="text-cyan-300/60">Live capability modes from Nexus V3</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {autonomyModes.map((mode, index) => (
                  <motion.div
                    key={mode.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="border-cyan-500/20 bg-slate-800/50 hover:border-cyan-400/40 transition-colors" data-testid={`card-tool-${mode.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-2 mb-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center text-cyan-400">
                            <mode.icon className="w-5 h-5" />
                          </div>
                          <Badge variant="outline" className={`text-xs ${getStatusColor(mode.status)}`}>
                            {mode.status}
                          </Badge>
                        </div>
                        <h3 className="text-sm font-semibold text-cyan-200 mb-1">{mode.name}</h3>
                        <p className="text-xs text-cyan-300/60">{mode.description}</p>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </ScrollArea>
      )}
    </div>
  );
}
