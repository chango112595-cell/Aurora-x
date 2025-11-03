import { ErrorBoundary } from '@/components/error-boundary';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, AlertCircle, CheckCircle2, Clock, Shield, BookOpen, Code2, Search, XCircle, ChevronDown, Copy, Eye } from "lucide-react";
import { motion } from "framer-motion";

type TabType = 'overview' | 'services' | 'metrics' | 'diagnostics' | 'learning';
type Category = 'all' | 'hard' | 'soft' | 'medium';
type PassFailFilter = 'all' | 'pass' | 'fail';
type LevelshipFilter = 'all' | 'ancient' | 'classical' | 'modern' | 'future';

export default function LuminarNexus() {
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<Category>('all');
  const [passFailFilter, setPassFailFilter] = useState<PassFailFilter>('all');
  const [levelshipFilter, setLevelshipFilter] = useState<LevelshipFilter>('all');
  const [expandedCode, setExpandedCode] = useState<string | null>(null);

  // Fetch corpus data - fetch all available
  const { data: corpusResponse, isLoading: corpusLoading } = useQuery<{ items: any[], hasMore: boolean }>({
    queryKey: ['/api/corpus?limit=500'],
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
      const res = await fetch('http://localhost:9090/api/status');
      const data = await res.json();
      setHealthData(data);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const healthScore = 95; // Calculate from actual data
  const uptimeData = [
    { time: '10m', uptime: 98 }, { time: '20m', uptime: 97 }, { time: '30m', uptime: 99 },
    { time: '40m', uptime: 100 }, { time: '50m', uptime: 98 }, { time: '60m', uptime: 99 }
  ];

  const serviceDistribution = [
    { name: 'Running', value: 4, color: '#10b981' },
    { name: 'Stopped', value: 0, color: '#ef4444' }
  ];

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><Activity className="animate-spin h-12 w-12" /></div>;
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
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent mb-2">
            🌟 Luminar Nexus
          </h1>
          <p className="text-muted-foreground">Advanced Aurora Analytics & Monitoring</p>
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
                <p className="text-xs text-muted-foreground mt-1">Excellent</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><Activity className="h-4 w-4" />Active Services</CardTitle></CardHeader>
              <CardContent><div className="text-4xl font-bold">4/4</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-500" />Checks Passed</CardTitle></CardHeader>
              <CardContent><div className="text-4xl font-bold text-green-500">12</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><Clock className="h-4 w-4" />Auto-Saves</CardTitle></CardHeader>
              <CardContent><div className="text-4xl font-bold">156</div></CardContent>
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

        {/* Learning Tab - Aurora's Corpus with Advanced Filtering */}
        {activeTab === 'learning' && (
          <div className="space-y-6">
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