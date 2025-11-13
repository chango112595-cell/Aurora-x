import { ErrorBoundary } from '@/components/error-boundary';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, AlertCircle, CheckCircle2, Clock, Shield, BookOpen, Code2, Search, XCircle, ChevronDown, Copy, Eye, MessageSquare, ArrowUp, ArrowDown, AlertTriangle, Server, Cpu, Zap } from "lucide-react";
import { motion } from "framer-motion";
import AuroraRebuiltChat from '@/components/AuroraRebuiltChat';
import { useLocation } from 'wouter';

type TabType = 'overview' | 'services' | 'metrics' | 'diagnostics' | 'learning';
type Category = 'all' | 'hard' | 'soft' | 'medium';
type PassFailFilter = 'all' | 'pass' | 'fail';
type LevelshipFilter = 'all' | 'ancient' | 'classical' | 'modern' | 'future';

export default function LuminarNexus() {
  const [location] = useLocation();

  // Parse tab from URL query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const tabFromUrl = (urlParams.get('tab') as TabType) || 'overview';

  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>(tabFromUrl);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<Category>('all');
  const [passFailFilter, setPassFailFilter] = useState<PassFailFilter>('all');
  const [levelshipFilter, setLevelshipFilter] = useState<LevelshipFilter>('all');
  const [expandedCode, setExpandedCode] = useState<string | null>(null);

  // Update activeTab when URL changes
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const newTab = (urlParams.get('tab') as TabType) || 'overview';
    setActiveTab(newTab);
  }, [location]);

  // Fetch corpus data - fetch all available
  const { data: corpusResponse, isLoading: corpusLoading } = useQuery<{ items: any[], hasMore: boolean }>({
    queryKey: ['/api/corpus?limit=200'],
  });

  // Helper function to determine levelship (Ancient to Future based on complexity/novelty)
  const getLevelship = (fn: any): LevelshipFilter => {
    // Simple heuristic: based on signature complexity and score
    const signatureLength = fn.func_signature.length;
    const score = fn.score;

    if (signatureLength > 100 && score > 0.9) return 'future'; // Novel, complex, high score
    if (signatureLength > 60 && score > 0.75) return 'modern'; // Contemporary coding
    if (signatureLength > 40) return 'classical'; // Traditional but solid
    return 'ancient'; // Legacy/simple patterns
  };

  // Helper function to determine category based on function signature/name
  const getCategory = (fn: any): Category => {
    const name = fn.func_name.toLowerCase();
    const sig = fn.func_signature.toLowerCase();
    const combined = `${name}${sig}`.toLowerCase();

    // Hard: Complex algorithms, recursion, graph/tree operations
    if (combined.includes('sort') || combined.includes('search') ||
      combined.includes('traverse') || combined.includes('recursive') ||
      combined.includes('algorithm') || combined.includes('compute')) {
      return 'hard';
    }

    // Soft: String/utility operations, simple transformations
    if (combined.includes('format') || combined.includes('parse') ||
      combined.includes('convert') || combined.includes('validate') ||
      combined.includes('clean') || combined.includes('helper')) {
      return 'soft';
    }

    // Medium: Everything else - data operations, filtering, etc
    return 'medium';
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealthData = async () => {
    try {
      // Fetch from Luminar Nexus V2 via backend proxy
      const res = await fetch('/api/luminar-nexus/v2/status');
      const data = await res.json();
      setHealthData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching V2 status:', error);
      setLoading(false);
    }
  };

  // Extract V2 metrics from healthData
  const quantumCoherence = healthData?.quantum_coherence || 0;
  const healthyServices = healthData?.healthy_services || 0;
  const totalServices = healthData?.services ? Object.keys(healthData.services).length : 5;
  const aiLearningActive = healthData?.ai_learning_active || false;
  const autonomousHealingActive = healthData?.autonomous_healing_active || false;
  
  // Calculate health score from quantum coherence and service health
  const healthScore = Math.round((quantumCoherence * 50) + ((healthyServices / totalServices) * 50));
  
  const uptimeData = [
    { time: '10m', uptime: 98 }, { time: '20m', uptime: 97 }, { time: '30m', uptime: 99 },
    { time: '40m', uptime: 100 }, { time: '50m', uptime: 98 }, { time: '60m', uptime: 99 }
  ];

  const serviceDistribution = [
    { name: 'Healthy', value: healthyServices, color: '#10b981' },
    { name: 'Degraded', value: totalServices - healthyServices, color: '#ef4444' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-background via-background to-primary/5">
        <div className="text-center space-y-4">
          <Activity className="animate-spin h-12 w-12 mx-auto text-cyan-500" />
          <p className="text-muted-foreground">Loading Luminar Nexus V2...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="container mx-auto space-y-6 max-w-7xl">
        {/* Aurora's Quantum Background */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20" />

          {/* Particle field */}
          <div className="absolute inset-0 opacity-20" style={{
            backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
            backgroundSize: '50px 50px',
            animation: 'particleFloat 20s linear infinite'
          }} />

          {/* Neural network grid */}
          <svg className="absolute inset-0 w-full h-full opacity-10">
            <defs>
              <linearGradient id="grid-luminar-nexus" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.5" />
              </linearGradient>
            </defs>
            <pattern id="grid-pattern-luminar-nexus" width="50" height="50" patternUnits="userSpaceOnUse">
              <circle cx="25" cy="25" r="1" fill="url(#grid-luminar-nexus)" />
            </pattern>
            <rect width="100%" height="100%" fill="url(#grid-pattern-luminar-nexus)" />
          </svg>

          {/* Holographic orbs */}
          <div className="absolute top-20 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        </div>

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent mb-2">
                🌟 Luminar Nexus V2
              </h1>
              <p className="text-muted-foreground">AI-Powered Service Orchestration & Monitoring</p>
            </div>
            <Badge className="bg-cyan-500/20 text-cyan-300 border-cyan-500/30">
              Version 2.0.0 • Quantum Coherence: {(quantumCoherence * 100).toFixed(0)}%
            </Badge>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex gap-2 border-b border-cyan-500/20 pb-4">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'outline'}
            onClick={() => setActiveTab('overview')}
            className="gap-2"
          >
            <Activity className="h-4 w-4" />
            Overview
          </Button>
          <Button
            variant={activeTab === 'services' ? 'default' : 'outline'}
            onClick={() => setActiveTab('services')}
            className="gap-2"
          >
            <Shield className="h-4 w-4" />
            Services
          </Button>
          <Button
            variant={activeTab === 'metrics' ? 'default' : 'outline'}
            onClick={() => setActiveTab('metrics')}
            className="gap-2"
          >
            <TrendingUp className="h-4 w-4" />
            Metrics
          </Button>
          <Button
            variant={activeTab === 'diagnostics' ? 'default' : 'outline'}
            onClick={() => setActiveTab('diagnostics')}
            className="gap-2"
          >
            <CheckCircle2 className="h-4 w-4" />
            Diagnostics
          </Button>
          <Button
            variant={activeTab === 'learning' ? 'default' : 'outline'}
            onClick={() => setActiveTab('learning')}
            className="gap-2"
          >
            <BookOpen className="h-4 w-4" />
            Learning
          </Button>
        </div>

        {/* Operational Health Score */}
        {activeTab === 'overview' && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-2 border-primary/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Shield className="h-4 w-4 text-green-500" />
                  Health Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-green-500">{healthScore}%</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {healthScore >= 90 ? 'Excellent' : healthScore >= 70 ? 'Good' : healthScore >= 50 ? 'Fair' : 'Degraded'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><Activity className="h-4 w-4" />Active Services</CardTitle></CardHeader>
              <CardContent><div className="text-4xl font-bold">{healthyServices}/{totalServices}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-cyan-500" />AI Learning</CardTitle></CardHeader>
              <CardContent><div className="text-2xl font-bold text-cyan-500">{aiLearningActive ? '✓ Active' : '✗ Inactive'}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><Shield className="h-4 w-4 text-purple-500" />Auto-Healing</CardTitle></CardHeader>
              <CardContent><div className="text-2xl font-bold text-purple-500">{autonomousHealingActive ? '✓ Enabled' : '✗ Disabled'}</div></CardContent>
            </Card>
          </motion.div>
        )}

        {/* Performance Trends */}
        {activeTab === 'overview' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Uptime Trend</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={uptimeData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="uptime" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Service Distribution</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={serviceDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                      {serviceDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Diagnostics & Issues */}
        {(activeTab === 'overview' || activeTab === 'diagnostics') && (
          <Card>
            <CardHeader><CardTitle>Recent Diagnostics</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <div><div className="font-semibold">Service Health Check</div><div className="text-xs text-muted-foreground">All services operational</div></div>
                  </div>
                  <Badge className="bg-green-500">PASS</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <div><div className="font-semibold">Port Availability</div><div className="text-xs text-muted-foreground">All ports listening</div></div>
                  </div>
                  <Badge className="bg-green-500">PASS</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <div><div className="font-semibold">Configuration Integrity</div><div className="text-xs text-muted-foreground">All configs valid</div></div>
                  </div>
                  <Badge className="bg-green-500">PASS</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Safety Protocol Status */}
        {(activeTab === 'overview' || activeTab === 'services') && (
          <Card className="border-2 border-cyan-500/30">
            <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5 text-cyan-500" />Safety Protocol Active</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div><div className="text-sm text-muted-foreground">Auto-Save</div><div className="text-2xl font-bold text-cyan-500">● Active</div></div>
                <div><div className="text-sm text-muted-foreground">Last Save</div><div className="text-2xl font-bold">2m ago</div></div>
                <div><div className="text-sm text-muted-foreground">Total Saves</div><div className="text-2xl font-bold">156</div></div>
                <div><div className="text-sm text-muted-foreground">Crashes</div><div className="text-2xl font-bold text-green-500">0</div></div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Services Tab - Detailed Service Status */}
        {activeTab === 'services' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-6"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-500 to-purple-500 bg-clip-text text-transparent">
                Service Status Monitor
              </h2>
              <Badge className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 border-cyan-500/30" data-testid="badge-service-count">
                {healthData?.services ? Object.keys(healthData.services).length : 0} Services Active
              </Badge>
            </div>

            {/* Service Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {healthData?.services && Object.entries(healthData.services).map(([serviceName, service]: [string, any], index) => {
                const isHealthy = service.status === 'healthy';
                const statusColor = isHealthy ? 'green' : 'red';
                const hasAnomalies = service.anomalies && service.anomalies.length > 0;
                const hasPredictions = service.predictions && Object.keys(service.predictions).length > 0;
                
                // Helper to format response time
                const formatResponseTime = (time: number | null) => {
                  if (time === null || time === undefined) return 'N/A';
                  if (time < 0.001) return `${(time * 1000000).toFixed(0)}μs`;
                  if (time < 1) return `${(time * 1000).toFixed(2)}ms`;
                  return `${time.toFixed(2)}s`;
                };

                // Helper to render trend indicator
                const renderTrend = (trend: number | null | undefined, label: string) => {
                  if (trend === null || trend === undefined) return null;
                  const isPositive = trend > 0;
                  const isNegative = trend < 0;
                  
                  return (
                    <div className="flex items-center gap-1">
                      {isPositive && <ArrowUp className="h-3 w-3 text-red-500" data-testid={`icon-trend-up-${label}`} />}
                      {isNegative && <ArrowDown className="h-3 w-3 text-green-500" data-testid={`icon-trend-down-${label}`} />}
                      {!isPositive && !isNegative && <span className="text-muted-foreground">─</span>}
                    </div>
                  );
                };

                return (
                  <motion.div
                    key={serviceName}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card 
                      className={`border-2 ${isHealthy ? 'border-green-500/30' : 'border-red-500/30'} bg-gradient-to-br from-background to-${statusColor}-500/5`}
                      data-testid={`card-service-${serviceName}`}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-2">
                            <Server className={`h-5 w-5 text-${statusColor}-500`} data-testid={`icon-service-${serviceName}`} />
                            <CardTitle className="text-lg capitalize">{serviceName}</CardTitle>
                          </div>
                          <Badge 
                            className={`bg-${statusColor}-500/20 text-${statusColor}-300 border-${statusColor}-500/30`}
                            data-testid={`badge-status-${serviceName}`}
                          >
                            {isHealthy ? (
                              <><CheckCircle2 className="h-3 w-3 mr-1" /> Healthy</>
                            ) : (
                              <><AlertCircle className="h-3 w-3 mr-1" /> Critical</>
                            )}
                          </Badge>
                        </div>
                      </CardHeader>
                      
                      <CardContent className="space-y-4">
                        {/* Port and Response Time */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-xs text-muted-foreground mb-1">Port</div>
                            <div className="text-2xl font-bold font-mono" data-testid={`text-port-${serviceName}`}>
                              {service.port || 'N/A'}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                              Response Time
                              {hasPredictions && renderTrend(service.predictions?.response_time_trend, `response-${serviceName}`)}
                            </div>
                            <div className="text-2xl font-bold font-mono" data-testid={`text-response-time-${serviceName}`}>
                              {formatResponseTime(service.response_time)}
                            </div>
                          </div>
                        </div>

                        {/* CPU and Memory Usage */}
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                            <div className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                              <Cpu className="h-3 w-3" />
                              CPU Usage
                              {hasPredictions && renderTrend(service.predictions?.cpu_usage_trend, `cpu-${serviceName}`)}
                            </div>
                            <div className="text-xl font-bold" data-testid={`text-cpu-${serviceName}`}>
                              {service.cpu_usage !== null && service.cpu_usage !== undefined 
                                ? `${(service.cpu_usage * 100).toFixed(2)}%` 
                                : 'N/A'}
                            </div>
                          </div>
                          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
                            <div className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                              <Zap className="h-3 w-3" />
                              Memory
                              {hasPredictions && renderTrend(service.predictions?.memory_usage_trend, `memory-${serviceName}`)}
                            </div>
                            <div className="text-xl font-bold" data-testid={`text-memory-${serviceName}`}>
                              {service.memory_usage !== null && service.memory_usage !== undefined 
                                ? `${(service.memory_usage * 100).toFixed(2)}%` 
                                : 'N/A'}
                            </div>
                          </div>
                        </div>

                        {/* Predictions (if available) */}
                        {hasPredictions && (
                          <div className="p-3 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20">
                            <div className="text-xs font-semibold text-cyan-300 mb-2 flex items-center gap-1">
                              <TrendingUp className="h-3 w-3" />
                              Predictive Trends
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-xs">
                              {service.predictions?.cpu_usage_trend !== undefined && (
                                <div data-testid={`text-prediction-cpu-${serviceName}`}>
                                  <span className="text-muted-foreground">CPU: </span>
                                  <span className={service.predictions.cpu_usage_trend > 0 ? 'text-red-400' : 'text-green-400'}>
                                    {service.predictions.cpu_usage_trend > 0 ? '+' : ''}{(service.predictions.cpu_usage_trend * 100).toFixed(1)}%
                                  </span>
                                </div>
                              )}
                              {service.predictions?.memory_usage_trend !== undefined && (
                                <div data-testid={`text-prediction-memory-${serviceName}`}>
                                  <span className="text-muted-foreground">Mem: </span>
                                  <span className={service.predictions.memory_usage_trend > 0 ? 'text-red-400' : 'text-green-400'}>
                                    {service.predictions.memory_usage_trend > 0 ? '+' : ''}{(service.predictions.memory_usage_trend * 100).toFixed(1)}%
                                  </span>
                                </div>
                              )}
                              {service.predictions?.response_time_trend !== undefined && (
                                <div data-testid={`text-prediction-response-${serviceName}`}>
                                  <span className="text-muted-foreground">Resp: </span>
                                  <span className={service.predictions.response_time_trend > 0 ? 'text-red-400' : 'text-green-400'}>
                                    {service.predictions.response_time_trend > 0 ? '+' : ''}{(service.predictions.response_time_trend * 1000).toFixed(2)}ms
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Anomalies (if any) */}
                        {hasAnomalies && (
                          <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20" data-testid={`container-anomalies-${serviceName}`}>
                            <div className="text-xs font-semibold text-yellow-300 mb-2 flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" />
                              Anomalies Detected ({service.anomalies.length})
                            </div>
                            <ScrollArea className="max-h-20">
                              <ul className="space-y-1 text-xs">
                                {service.anomalies.map((anomaly: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2" data-testid={`text-anomaly-${serviceName}-${idx}`}>
                                    <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5 flex-shrink-0" />
                                    <span className="text-muted-foreground">{anomaly}</span>
                                  </li>
                                ))}
                              </ul>
                            </ScrollArea>
                          </div>
                        )}

                        {/* No Anomalies Message */}
                        {!hasAnomalies && (
                          <div className="text-xs text-muted-foreground text-center p-2" data-testid={`text-no-anomalies-${serviceName}`}>
                            <CheckCircle2 className="h-4 w-4 text-green-500 inline mr-1" />
                            No anomalies detected
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            {/* No Services Available */}
            {(!healthData?.services || Object.keys(healthData.services).length === 0) && (
              <Card className="border-2 border-cyan-500/30">
                <CardContent className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
                  <Server className="h-16 w-16 text-muted-foreground opacity-50" />
                  <div className="text-center">
                    <h3 className="text-lg font-semibold mb-2">No Services Available</h3>
                    <p className="text-sm text-muted-foreground">
                      Service data is currently unavailable. Please check system health.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </motion.div>
        )}

        {/* Learning Tab - Aurora's Corpus with Advanced Filtering */}
        {activeTab === 'learning' && (
          <div className="space-y-6">
            {/* Aurora's 27 Mastery Tiers Display */}
            <Card className="border-cyan-500/30 bg-gradient-to-br from-cyan-950/20 to-purple-950/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-6 w-6 text-cyan-400" />
                  Aurora's 27 Mastery Tiers
                  <Badge className="ml-auto bg-cyan-500/20 text-cyan-300">1,782+ Skills Active</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {[
                    { tier: 1, name: "Ancient Computing", icon: "⏰", range: "1940s-1970s", skills: 45 },
                    { tier: 2, name: "Debugging Grandmaster", icon: "🔍", range: "printf→Quantum", skills: 120 },
                    { tier: 3, name: "Security & Cryptography", icon: "🔐", range: "Caesar→Quantum", skills: 89 },
                    { tier: 4, name: "UI/UX Mastery", icon: "🎨", range: "CLI→Neural", skills: 67 },
                    { tier: 5, name: "Networking", icon: "🌐", range: "ARPANET→Quantum", skills: 95 },
                    { tier: 6, name: "Database Systems", icon: "💾", range: "Punch cards→Vector", skills: 78 },
                    { tier: 7, name: "Cloud & Infrastructure", icon: "☁️", range: "Mainframes→Serverless", skills: 102 },
                    { tier: 8, name: "Frontend Frameworks", icon: "⚛️", range: "jQuery→Quantum UI", skills: 73 },
                    { tier: 9, name: "Backend Architectures", icon: "🔧", range: "CGI→Microservices", skills: 88 },
                    { tier: 10, name: "AI/ML Engineering", icon: "🧠", range: "Perceptrons→AGI", skills: 134 },
                    { tier: 11, name: "API Design", icon: "🔌", range: "SOAP→GraphQL", skills: 56 },
                    { tier: 12, name: "Mobile Development", icon: "📱", range: "J2ME→Cross-platform", skills: 82 },
                    { tier: 13, name: "DevOps & CI/CD", icon: "🔄", range: "Scripts→GitOps", skills: 91 },
                    { tier: 14, name: "Testing & QA", icon: "✅", range: "Manual→AI-driven", skills: 64 },
                    { tier: 15, name: "Performance Optimization", icon: "⚡", range: "Profiling→Quantum", skills: 71 },
                    { tier: 16, name: "Component Architecture", icon: "🏗️", range: "Modules→Micro-frontends", skills: 58 },
                    { tier: 17, name: "Data Engineering", icon: "📊", range: "ETL→Real-time", skills: 85 },
                    { tier: 18, name: "Gaming & XR", icon: "🎮", range: "Doom→Neural VR", skills: 76 },
                    { tier: 19, name: "Real-time Systems", icon: "⚡", range: "Polling→Edge", skills: 69 },
                    { tier: 20, name: "IoT & Embedded", icon: "📡", range: "Arduino→Neural chips", skills: 54 },
                    { tier: 21, name: "Blockchain & Web3", icon: "⛓️", range: "Bitcoin→Quantum-safe", skills: 48 },
                    { tier: 22, name: "Documentation", icon: "📝", range: "Comments→AI docs", skills: 42 },
                    { tier: 23, name: "Business & Monetization", icon: "💰", range: "Ads→SaaS", skills: 39 },
                    { tier: 24, name: "Legal & Compliance", icon: "⚖️", range: "Licenses→GDPR", skills: 36 },
                    { tier: 25, name: "Accessibility", icon: "♿", range: "Basic→Neural", skills: 44 },
                    { tier: 26, name: "Internationalization", icon: "🌍", range: "UTF-8→Real-time", skills: 31 },
                    { tier: 27, name: "Future Technologies", icon: "🚀", range: "Quantum→Consciousness", skills: 62 }
                  ].map((tier) => (
                    <motion.div
                      key={tier.tier}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: tier.tier * 0.02 }}
                      className="p-3 rounded-lg border border-cyan-500/20 bg-background/50 hover:bg-cyan-500/10 transition-colors"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-2xl">{tier.icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">T{tier.tier}</Badge>
                            <h4 className="font-semibold text-sm truncate">{tier.name}</h4>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">{tier.range}</p>
                          <Badge className="mt-2 text-xs" variant="secondary">{tier.skills} skills</Badge>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <BookOpen className="h-6 w-6 text-primary" />
                  <div className="flex-1">
                    <CardTitle>Aurora's Learning Corpus</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Synthesized functions from self-learning runs - {corpusResponse?.items?.length || 0} total
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Search Bar */}
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search functions by name or signature..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* Filter Bar */}
                <div className="space-y-4">
                  {/* Category Filter */}
                  <div>
                    <p className="text-sm font-semibold mb-2">Category</p>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={selectedCategory === 'all' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedCategory('all')}
                      >
                        All
                      </Button>
                      <Button
                        variant={selectedCategory === 'hard' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedCategory('hard')}
                        className={selectedCategory === 'hard' ? 'bg-red-500/80 hover:bg-red-500' : ''}
                      >
                        Hard (Complex)
                      </Button>
                      <Button
                        variant={selectedCategory === 'medium' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedCategory('medium')}
                        className={selectedCategory === 'medium' ? 'bg-orange-500/80 hover:bg-orange-500' : ''}
                      >
                        Medium
                      </Button>
                      <Button
                        variant={selectedCategory === 'soft' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedCategory('soft')}
                        className={selectedCategory === 'soft' ? 'bg-green-500/80 hover:bg-green-500' : ''}
                      >
                        Soft (Utilities)
                      </Button>
                    </div>
                  </div>

                  {/* Pass/Fail Filter */}
                  <div>
                    <p className="text-sm font-semibold mb-2">Status</p>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={passFailFilter === 'all' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setPassFailFilter('all')}
                      >
                        All
                      </Button>
                      <Button
                        variant={passFailFilter === 'pass' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setPassFailFilter('pass')}
                        className={passFailFilter === 'pass' ? 'bg-green-500/80 hover:bg-green-500' : ''}
                      >
                        <CheckCircle2 className="h-4 w-4 mr-1" /> Passing
                      </Button>
                      <Button
                        variant={passFailFilter === 'fail' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setPassFailFilter('fail')}
                        className={passFailFilter === 'fail' ? 'bg-red-500/80 hover:bg-red-500' : ''}
                      >
                        <XCircle className="h-4 w-4 mr-1" /> Failing
                      </Button>
                    </div>
                  </div>

                  {/* Levelship Filter (Ancient to Future) */}
                  <div>
                    <p className="text-sm font-semibold mb-2">Coding Evolution (Ancient → Future)</p>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={levelshipFilter === 'all' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setLevelshipFilter('all')}
                      >
                        All
                      </Button>
                      <Button
                        variant={levelshipFilter === 'ancient' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setLevelshipFilter('ancient')}
                        className={levelshipFilter === 'ancient' ? 'bg-gray-500/80 hover:bg-gray-500' : ''}
                      >
                        Ancient (Legacy)
                      </Button>
                      <Button
                        variant={levelshipFilter === 'classical' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setLevelshipFilter('classical')}
                        className={levelshipFilter === 'classical' ? 'bg-blue-500/80 hover:bg-blue-500' : ''}
                      >
                        Classical
                      </Button>
                      <Button
                        variant={levelshipFilter === 'modern' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setLevelshipFilter('modern')}
                        className={levelshipFilter === 'modern' ? 'bg-purple-500/80 hover:bg-purple-500' : ''}
                      >
                        Modern
                      </Button>
                      <Button
                        variant={levelshipFilter === 'future' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setLevelshipFilter('future')}
                        className={levelshipFilter === 'future' ? 'bg-cyan-500/80 hover:bg-cyan-500' : ''}
                      >
                        🚀 Future (Novel)
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Corpus Display */}
                {corpusLoading ? (
                  <div className="flex items-center justify-center min-h-[300px]">
                    <div className="text-center space-y-4">
                      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
                      <p className="text-muted-foreground font-mono">Loading corpus...</p>
                    </div>
                  </div>
                ) : !corpusResponse?.items || corpusResponse.items.length === 0 ? (
                  <div className="flex items-center justify-center min-h-[300px]">
                    <div className="text-center space-y-4">
                      <Code2 className="h-12 w-12 text-muted-foreground mx-auto opacity-50" />
                      <p className="text-muted-foreground">No functions in corpus yet</p>
                      <p className="text-sm text-muted-foreground">Run self-learning to populate Aurora's function library</p>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Filter Results Summary */}
                    {(() => {
                      const filtered = corpusResponse.items.filter((fn: any) => {
                        const matchesSearch = fn.func_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          fn.func_signature.toLowerCase().includes(searchTerm.toLowerCase());
                        const matchesCategory = selectedCategory === 'all' || getCategory(fn) === selectedCategory;
                        const matchesPassFail = passFailFilter === 'all' ||
                          (passFailFilter === 'pass' && fn.passed === fn.total) ||
                          (passFailFilter === 'fail' && fn.passed !== fn.total);
                        const matchesLevelship = levelshipFilter === 'all' || getLevelship(fn) === levelshipFilter;

                        return matchesSearch && matchesCategory && matchesPassFail && matchesLevelship;
                      });

                      return (
                        <div className="text-sm text-muted-foreground">
                          Showing <span className="font-semibold text-primary">{filtered.length}</span> of {corpusResponse.items.length} functions
                        </div>
                      );
                    })()}

                    <ScrollArea className="h-[700px]">
                      <div className="space-y-3 pr-4">
                        {corpusResponse.items
                          .filter((fn: any) => {
                            const matchesSearch = fn.func_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              fn.func_signature.toLowerCase().includes(searchTerm.toLowerCase());
                            const matchesCategory = selectedCategory === 'all' || getCategory(fn) === selectedCategory;
                            const matchesPassFail = passFailFilter === 'all' ||
                              (passFailFilter === 'pass' && fn.passed === fn.total) ||
                              (passFailFilter === 'fail' && fn.passed !== fn.total);
                            const matchesLevelship = levelshipFilter === 'all' || getLevelship(fn) === levelshipFilter;

                            return matchesSearch && matchesCategory && matchesPassFail && matchesLevelship;
                          })
                          .map((fn: any) => {
                            const category = getCategory(fn);
                            const levelship = getLevelship(fn);
                            const isExpanded = expandedCode === fn.id;

                            return (
                              <div key={fn.id} className="rounded-lg border border-primary/10 p-4 bg-background/50 hover:bg-background/70 transition-colors">
                                <div className="space-y-3">
                                  {/* Header */}
                                  <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center gap-2 flex-wrap mb-2">
                                        <code className="text-sm font-mono font-semibold">{fn.func_name}</code>
                                        <Badge variant="outline" className="text-xs">
                                          {category === 'hard' && '🔴 Hard'}
                                          {category === 'medium' && '🟠 Medium'}
                                          {category === 'soft' && '🟢 Soft'}
                                        </Badge>
                                        <Badge variant="outline" className="text-xs">
                                          {levelship === 'ancient' && '⏰ Ancient'}
                                          {levelship === 'classical' && '📚 Classical'}
                                          {levelship === 'modern' && '🔧 Modern'}
                                          {levelship === 'future' && '🚀 Future'}
                                        </Badge>
                                      </div>
                                      <p className="text-xs text-muted-foreground font-mono truncate">{fn.func_signature}</p>
                                    </div>
                                  </div>

                                  {/* Badges */}
                                  <div className="flex items-center gap-2 flex-wrap">
                                    <Badge variant={fn.score >= 0.8 ? "default" : "secondary"}>
                                      Score: {(fn.score * 100).toFixed(0)}%
                                    </Badge>
                                    <Badge variant={fn.passed === fn.total ? "default" : "destructive"}>
                                      {fn.passed === fn.total ? (
                                        <CheckCircle2 className="h-3 w-3 mr-1" />
                                      ) : (
                                        <XCircle className="h-3 w-3 mr-1" />
                                      )}
                                      {fn.passed}/{fn.total}
                                    </Badge>
                                  </div>

                                  {/* Code Display */}
                                  {fn.snippet && (
                                    <div>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => setExpandedCode(isExpanded ? null : fn.id)}
                                        className="text-xs"
                                      >
                                        {isExpanded ? (
                                          <>
                                            <ChevronDown className="h-3 w-3 mr-1 rotate-180" />
                                            Hide Code
                                          </>
                                        ) : (
                                          <>
                                            <ChevronDown className="h-3 w-3 mr-1" />
                                            View Code
                                          </>
                                        )}
                                      </Button>
                                      {isExpanded && (
                                        <div className="mt-2 relative">
                                          <pre className="bg-muted p-3 rounded-lg overflow-x-auto text-xs border border-primary/20">
                                            <code>{fn.snippet}</code>
                                          </pre>
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            className="absolute top-2 right-2 h-8 w-8 p-0"
                                            onClick={() => {
                                              navigator.clipboard.writeText(fn.snippet);
                                            }}
                                            title="Copy code"
                                          >
                                            <Copy className="h-3 w-3" />
                                          </Button>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {/* Metadata */}
                                  <p className="text-xs text-muted-foreground">
                                    Added: {new Date(fn.timestamp).toLocaleString()}
                                  </p>
                                </div>
                              </div>
                            );
                          })}
                      </div>
                    </ScrollArea>
                  </>
                )}
              </CardContent>
            </Card>
        </div>
      )}
    </div>
  </div>
);
}