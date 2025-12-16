import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { useQuery } from "@tanstack/react-query";
import { Zap, RefreshCw, Bot, Cpu, Play, Pause, CheckCircle, Clock, AlertCircle, Layers, Wrench, Shield, Code, Sparkles, AlertTriangle } from "lucide-react";
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

interface AutonomousTool {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'idle' | 'disabled';
  category: string;
  lastRun: string;
  successRate: number;
  icon: string;
}

interface WorkerTask {
  id: string;
  type: string;
  status: 'running' | 'queued' | 'completed' | 'failed';
  priority: 'high' | 'medium' | 'low';
  description: string;
  progress: number;
  startedAt: string;
}

export default function AutonomousPage() {
  const [autoHealEnabled, setAutoHealEnabled] = useState(true);
  const [autoOptimizeEnabled, setAutoOptimizeEnabled] = useState(true);

  const { data: auroraStatus, isLoading, isError, error, refetch, isRefetching } = useQuery<AuroraStatus>({
    queryKey: ['/api/aurora/status'],
    refetchInterval: 5000,
  });

  const autonomousTools: AutonomousTool[] = [
    { id: '1', name: 'Auto-Fixer', description: 'Automatically detects and repairs code issues', status: 'active', category: 'repair', lastRun: '2 min ago', successRate: 94, icon: 'wrench' },
    { id: '2', name: 'Code Optimizer', description: 'Optimizes code for performance and readability', status: 'active', category: 'optimization', lastRun: '5 min ago', successRate: 91, icon: 'zap' },
    { id: '3', name: 'Pattern Detector', description: 'Identifies code patterns and suggests improvements', status: 'idle', category: 'analysis', lastRun: '15 min ago', successRate: 88, icon: 'sparkles' },
    { id: '4', name: 'Security Scanner', description: 'Scans for vulnerabilities and security issues', status: 'active', category: 'security', lastRun: '1 min ago', successRate: 97, icon: 'shield' },
    { id: '5', name: 'Type Inferencer', description: 'Infers and adds TypeScript types automatically', status: 'idle', category: 'typing', lastRun: '30 min ago', successRate: 85, icon: 'code' },
    { id: '6', name: 'Memory Manager', description: 'Manages and optimizes memory consolidation', status: 'active', category: 'memory', lastRun: '3 min ago', successRate: 92, icon: 'layers' },
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
        progress: 50, 
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

  const getToolIcon = (icon: string) => {
    switch (icon) {
      case 'wrench': return <Wrench className="w-5 h-5" />;
      case 'zap': return <Zap className="w-5 h-5" />;
      case 'sparkles': return <Sparkles className="w-5 h-5" />;
      case 'shield': return <Shield className="w-5 h-5" />;
      case 'code': return <Code className="w-5 h-5" />;
      case 'layers': return <Layers className="w-5 h-5" />;
      default: return <Bot className="w-5 h-5" />;
    }
  };

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
                      {auroraStatus?.autofixer?.workers || 300}
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
                      {auroraStatus?.autofixer?.active || 0}
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
                      {auroraStatus?.autofixer?.queued || 0}
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
                      {auroraStatus?.autofixer?.completed || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-auto-settings">
              <CardHeader className="border-b border-cyan-500/20">
                <CardTitle className="text-lg text-cyan-300">Autonomous Settings</CardTitle>
                <CardDescription className="text-cyan-300/60">Configure self-directed behavior</CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-green-400" />
                    <div>
                      <p className="text-sm text-cyan-200">Auto-Heal</p>
                      <p className="text-xs text-cyan-300/60">Automatically repair issues</p>
                    </div>
                  </div>
                  <Switch 
                    checked={autoHealEnabled} 
                    onCheckedChange={setAutoHealEnabled}
                    data-testid="switch-auto-heal"
                  />
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <div>
                      <p className="text-sm text-cyan-200">Auto-Optimize</p>
                      <p className="text-xs text-cyan-300/60">Continuous optimization</p>
                    </div>
                  </div>
                  <Switch 
                    checked={autoOptimizeEnabled} 
                    onCheckedChange={setAutoOptimizeEnabled}
                    data-testid="switch-auto-optimize"
                  />
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
                              {task.status === 'running' && (
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
                Autonomous Tools
              </CardTitle>
              <CardDescription className="text-cyan-300/60">Self-directed capabilities and automation modules</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {autonomousTools.map((tool, index) => (
                  <motion.div
                    key={tool.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="border-cyan-500/20 bg-slate-800/50 hover:border-cyan-400/40 transition-colors" data-testid={`card-tool-${tool.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-2 mb-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center text-cyan-400">
                            {getToolIcon(tool.icon)}
                          </div>
                          <Badge variant="outline" className={`text-xs ${getStatusColor(tool.status)}`}>
                            {tool.status}
                          </Badge>
                        </div>
                        <h3 className="text-sm font-semibold text-cyan-200 mb-1">{tool.name}</h3>
                        <p className="text-xs text-cyan-300/60 mb-3">{tool.description}</p>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">Last run: {tool.lastRun}</span>
                          <span className="text-green-400">{tool.successRate}% success</span>
                        </div>
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
