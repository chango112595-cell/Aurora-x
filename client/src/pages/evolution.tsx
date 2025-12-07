import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { TrendingUp, Brain, Zap, Target, RefreshCw, Sparkles, Activity, Clock, Layers, ArrowUpRight, ChevronRight, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

interface EvolutionMetric {
  id: string;
  name: string;
  value: number;
  maxValue: number;
  trend: 'up' | 'down' | 'stable';
  category: string;
}

interface LearningEvent {
  timestamp: string;
  type: string;
  description: string;
  improvement: number;
}

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
  uptime: number;
  version: string;
}

export default function EvolutionPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const { data: auroraStatus, isLoading, isError, error, refetch, isRefetching } = useQuery<AuroraStatus>({
    queryKey: ['/api/aurora/status'],
    refetchInterval: 10000,
  });

  const evolutionMetrics: EvolutionMetric[] = [
    { id: '1', name: 'Neural Processing', value: 94, maxValue: 100, trend: 'up', category: 'intelligence' },
    { id: '2', name: 'Pattern Recognition', value: 87, maxValue: 100, trend: 'up', category: 'intelligence' },
    { id: '3', name: 'Code Synthesis', value: 91, maxValue: 100, trend: 'stable', category: 'capability' },
    { id: '4', name: 'Learning Rate', value: 78, maxValue: 100, trend: 'up', category: 'adaptation' },
    { id: '5', name: 'Memory Efficiency', value: 85, maxValue: 100, trend: 'stable', category: 'performance' },
    { id: '6', name: 'Context Retention', value: 92, maxValue: 100, trend: 'up', category: 'intelligence' },
    { id: '7', name: 'Autonomous Decision', value: 76, maxValue: 100, trend: 'up', category: 'capability' },
    { id: '8', name: 'Self-Optimization', value: 83, maxValue: 100, trend: 'up', category: 'adaptation' },
  ];

  const learningEvents: LearningEvent[] = [
    { timestamp: new Date(Date.now() - 300000).toISOString(), type: 'pattern_learned', description: 'Identified new code optimization pattern', improvement: 2.3 },
    { timestamp: new Date(Date.now() - 900000).toISOString(), type: 'capability_enhanced', description: 'Enhanced TypeScript type inference', improvement: 1.8 },
    { timestamp: new Date(Date.now() - 1800000).toISOString(), type: 'memory_consolidated', description: 'Consolidated 47 short-term memories', improvement: 0.5 },
    { timestamp: new Date(Date.now() - 3600000).toISOString(), type: 'self_correction', description: 'Auto-corrected syntax handling logic', improvement: 3.1 },
    { timestamp: new Date(Date.now() - 7200000).toISOString(), type: 'pattern_learned', description: 'Learned React component patterns', improvement: 2.7 },
  ];

  const categories = ['all', 'intelligence', 'capability', 'adaptation', 'performance'];
  
  const filteredMetrics = selectedCategory === 'all' 
    ? evolutionMetrics 
    : evolutionMetrics.filter(m => m.category === selectedCategory);

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return <ArrowUpRight className="w-4 h-4 text-green-400" />;
    if (trend === 'down') return <ArrowUpRight className="w-4 h-4 text-red-400 rotate-90" />;
    return <ChevronRight className="w-4 h-4 text-yellow-400" />;
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'intelligence': return 'cyan';
      case 'capability': return 'purple';
      case 'adaptation': return 'pink';
      case 'performance': return 'green';
      default: return 'cyan';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'pattern_learned': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'capability_enhanced': return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'memory_consolidated': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'self_correction': return 'bg-green-500/20 text-green-300 border-green-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  const formatUptime = (ms: number) => {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-cyan-400/50 flex items-center justify-center bg-gradient-to-br from-cyan-500/20 to-purple-500/20">
                <TrendingUp className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent" data-testid="text-page-title">
                Evolution Monitor
              </h1>
              <p className="text-sm text-muted-foreground">
                Track Aurora's Continuous Growth & Adaptation
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            disabled={isRefetching}
            className="border-cyan-500/30 hover:border-cyan-400/50"
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
            <TrendingUp className="w-12 h-12 text-cyan-400 animate-pulse mx-auto mb-4" />
            <p className="text-muted-foreground">Loading evolution data...</p>
          </div>
        </div>
      ) : isError ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-300 mb-2">Failed to load evolution data</p>
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
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-power">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-xs text-cyan-300/60">Power Units</p>
                    <p className="text-2xl font-bold text-cyan-400" data-testid="text-power-units">
                      {auroraStatus?.powerUnits || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-capabilities">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-purple-300/60">Capabilities</p>
                    <p className="text-2xl font-bold text-purple-400" data-testid="text-capabilities">
                      {auroraStatus?.knowledgeCapabilities || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-pink-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-modules">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                    <Layers className="w-5 h-5 text-pink-400" />
                  </div>
                  <div>
                    <p className="text-xs text-pink-300/60">Total Modules</p>
                    <p className="text-2xl font-bold text-pink-400" data-testid="text-modules">
                      {auroraStatus?.totalModules || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-green-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-uptime">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-300/60">Uptime</p>
                    <p className="text-2xl font-bold text-green-400" data-testid="text-uptime">
                      {formatUptime(auroraStatus?.uptime || 0)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-evolution-metrics">
                <CardHeader className="border-b border-cyan-500/20">
                  <CardTitle className="flex items-center gap-2 text-lg text-cyan-300">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    Evolution Metrics
                  </CardTitle>
                  <CardDescription className="text-cyan-300/60">
                    Real-time capability progression
                  </CardDescription>
                  <div className="flex gap-2 flex-wrap pt-2">
                    {categories.map((cat) => (
                      <Button
                        key={cat}
                        variant={selectedCategory === cat ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedCategory(cat)}
                        className={selectedCategory === cat 
                          ? "bg-gradient-to-r from-cyan-600 to-purple-600" 
                          : "border-cyan-500/30 text-cyan-300 hover:border-cyan-400/50"}
                        data-testid={`button-category-${cat}`}
                      >
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </Button>
                    ))}
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-4">
                    {filteredMetrics.map((metric, index) => (
                      <motion.div
                        key={metric.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-cyan-200">{metric.name}</span>
                            <Badge 
                              variant="outline" 
                              className={`text-xs bg-${getCategoryColor(metric.category)}-500/10 text-${getCategoryColor(metric.category)}-300 border-${getCategoryColor(metric.category)}-500/30`}
                            >
                              {metric.category}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            {getTrendIcon(metric.trend)}
                            <span className="text-sm font-mono text-cyan-400">
                              {metric.value}%
                            </span>
                          </div>
                        </div>
                        <div className="relative">
                          <Progress 
                            value={metric.value} 
                            className="h-2 bg-slate-800"
                          />
                          <div 
                            className="absolute inset-0 h-2 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500" 
                            style={{ width: `${metric.value}%` }}
                          />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div>
              <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-learning-events">
                <CardHeader className="border-b border-purple-500/20">
                  <CardTitle className="flex items-center gap-2 text-lg text-purple-300">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    Learning Events
                  </CardTitle>
                  <CardDescription className="text-purple-300/60">
                    Recent adaptations and improvements
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  <ScrollArea className="h-[400px]">
                    <div className="space-y-3">
                      {learningEvents.map((event, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Card className="border-purple-500/20 bg-slate-800/50" data-testid={`card-event-${index}`}>
                            <CardContent className="p-3">
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <Badge 
                                  variant="outline" 
                                  className={`text-xs ${getEventColor(event.type)}`}
                                  data-testid={`badge-event-type-${index}`}
                                >
                                  {event.type.replace('_', ' ')}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(event.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <p className="text-sm text-purple-200 mb-2" data-testid={`text-event-desc-${index}`}>
                                {event.description}
                              </p>
                              <div className="flex items-center gap-2">
                                <ArrowUpRight className="w-3 h-3 text-green-400" />
                                <span className="text-xs text-green-400">
                                  +{event.improvement.toFixed(1)}% improvement
                                </span>
                              </div>
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

          <Card className="mt-6 border-pink-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-evolution-summary">
            <CardHeader className="border-b border-pink-500/20">
              <CardTitle className="flex items-center gap-2 text-lg text-pink-300">
                <Target className="w-5 h-5 text-pink-400" />
                Evolution Summary
              </CardTitle>
              <CardDescription className="text-pink-300/60">
                Current system version and growth trajectory
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-800/50 rounded-lg border border-pink-500/20">
                  <p className="text-xs text-pink-300/60 mb-1">Version</p>
                  <p className="text-lg font-mono text-pink-300" data-testid="text-version">
                    {auroraStatus?.version || 'Unknown'}
                  </p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-pink-500/20">
                  <p className="text-xs text-pink-300/60 mb-1">Execution Modes</p>
                  <p className="text-lg font-mono text-pink-300" data-testid="text-exec-modes">
                    {auroraStatus?.executionModes || 0}
                  </p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-pink-500/20">
                  <p className="text-xs text-pink-300/60 mb-1">System Components</p>
                  <p className="text-lg font-mono text-pink-300" data-testid="text-components">
                    {auroraStatus?.systemComponents || 0}
                  </p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-pink-500/20">
                  <p className="text-xs text-pink-300/60 mb-1">Status</p>
                  <Badge 
                    variant="outline" 
                    className="bg-green-500/20 text-green-300 border-green-500/30"
                    data-testid="badge-status"
                  >
                    {auroraStatus?.status || 'Unknown'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </ScrollArea>
      )}
    </div>
  );
}
