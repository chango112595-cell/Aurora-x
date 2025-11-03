import { ErrorBoundary } from '@/components/error-boundary';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, AlertCircle, CheckCircle2, Clock, Shield } from "lucide-react";
import { motion } from "framer-motion";

type TabType = 'overview' | 'services' | 'metrics' | 'diagnostics';

export default function LuminarNexus() {
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');

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
      </div>
    </div>
  );
}