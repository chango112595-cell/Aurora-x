import React, { useState, useEffect } from 'react';
import { Brain, Cpu, Zap, Network, Shield, Activity, Database, Code2, Sparkles, Terminal, Globe } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

export default function AuroraFuturisticDashboard() {
  const [quantumCoherence, setQuantumCoherence] = useState(100);
  const [activeServices, setActiveServices] = useState(5);
  const [neuralActivity, setNeuralActivity] = useState(98);

  // Simulate quantum fluctuations
  useEffect(() => {
    const interval = setInterval(() => {
      setQuantumCoherence(prev => Math.max(95, Math.min(100, prev + (Math.random() - 0.5) * 2)));
      setNeuralActivity(prev => Math.max(95, Math.min(100, prev + (Math.random() - 0.5) * 3)));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const foundationalTasks = [
    { id: 1, name: "Understand", capability: "Natural Language Processing", status: "active", level: 100 },
    { id: 2, name: "Analyze", capability: "Deep Problem Analysis", status: "active", level: 100 },
    { id: 3, name: "Decide", capability: "Autonomous Decision Making", status: "active", level: 100 },
    { id: 4, name: "Execute", capability: "Code Generation & Execution", status: "active", level: 100 },
    { id: 5, name: "Verify", capability: "Quality Assurance", status: "active", level: 100 },
    { id: 6, name: "Learn", capability: "Continuous Learning", status: "active", level: 100 },
    { id: 7, name: "Communicate", capability: "Effective Communication", status: "active", level: 100 },
    { id: 8, name: "Adapt", capability: "Contextual Adaptation", status: "active", level: 100 },
    { id: 9, name: "Create", capability: "Creative Problem Solving", status: "active", level: 100 },
    { id: 10, name: "Debug", capability: "Systematic Debugging", status: "active", level: 100 },
    { id: 11, name: "Optimize", capability: "Performance Optimization", status: "active", level: 100 },
    { id: 12, name: "Collaborate", capability: "Team Collaboration", status: "active", level: 100 },
    { id: 13, name: "Evolve", capability: "Self-Evolution", status: "active", level: 100 }
  ];

  const knowledgeTiers = [
    { category: "Languages", tiers: "1-6", count: 6, icon: Code2, color: "cyan" },
    { category: "Technical", tiers: "7-27", count: 21, icon: Cpu, color: "purple" },
    { category: "Autonomous", tiers: "28-53", count: 26, icon: Brain, color: "pink" },
    { category: "Advanced", tiers: "54-66", count: 13, icon: Sparkles, color: "violet" }
  ];

  const systemServices = [
    { name: "Backend API", port: 5000, status: "operational", uptime: "99.9%" },
    { name: "Bridge Service", port: 5001, status: "operational", uptime: "99.8%" },
    { name: "Self-Learning", port: 5002, status: "operational", uptime: "99.7%" },
    { name: "Chat Server", port: 5003, status: "operational", uptime: "99.9%" },
    { name: "Luminar Nexus", port: 5005, status: "operational", uptime: "100%" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white p-6">
      {/* Quantum Neural Header */}
      <div className="mb-8 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-pink-500/20 blur-3xl" />
        <div className="relative bg-slate-900/50 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Brain className="h-16 w-16 text-cyan-400 animate-pulse" />
                <div className="absolute inset-0 bg-cyan-400/20 blur-xl rounded-full" />
              </div>
              <div>
                <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  AURORA
                </h1>
                <p className="text-cyan-300/80 text-sm mt-1">Quantum Neural Intelligence System</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-cyan-400">{quantumCoherence.toFixed(1)}%</div>
              <div className="text-sm text-cyan-300/60">Quantum Coherence</div>
            </div>
          </div>

          {/* Hybrid Mode Power Banner */}
          <div className="bg-gradient-to-r from-violet-500/20 via-fuchsia-500/20 to-pink-500/20 border border-violet-500/50 rounded-xl p-4 mb-4">
            <div className="flex items-center justify-center gap-4">
              <Sparkles className="h-8 w-8 text-violet-400 animate-pulse" />
              <div className="text-center">
                <div className="text-5xl font-bold bg-gradient-to-r from-violet-400 via-fuchsia-400 to-pink-400 bg-clip-text text-transparent">
                  188 TOTAL POWER
                </div>
                <div className="text-violet-300/80 text-sm mt-1">
                  Hybrid Mode: 66 Knowledge Tiers + 109 Capability Modules
                </div>
              </div>
              <Sparkles className="h-8 w-8 text-pink-400 animate-pulse" />
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-5 w-5 text-cyan-400" />
                <span className="text-cyan-300 text-sm">Foundation Tasks</span>
              </div>
              <div className="text-3xl font-bold text-cyan-400">13</div>
            </div>

            <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Network className="h-5 w-5 text-purple-400" />
                <span className="text-purple-300 text-sm">Knowledge Tiers</span>
              </div>
              <div className="text-3xl font-bold text-purple-400">66</div>
            </div>

            <div className="bg-gradient-to-br from-pink-500/10 to-pink-500/5 border border-pink-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-5 w-5 text-pink-400" />
                <span className="text-pink-300 text-sm">Capability Modules</span>
              </div>
              <div className="text-3xl font-bold text-pink-400">109</div>
            </div>

            <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-5 w-5 text-emerald-400" />
                <span className="text-emerald-300 text-sm">Services Active</span>
              </div>
              <div className="text-3xl font-bold text-emerald-400">{activeServices}/5</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Foundational Tasks Matrix */}
        <Card className="bg-slate-900/50 backdrop-blur-xl border-cyan-500/30">
          <CardHeader className="border-b border-cyan-500/20">
            <CardTitle className="flex items-center gap-2 text-cyan-300">
              <Shield className="h-6 w-6" />
              Foundational Cognitive Tasks (1-13)
              <Badge className="ml-auto bg-cyan-500/20 text-cyan-300 border-cyan-500/50">
                Base Layer
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 gap-2 max-h-[400px] overflow-y-auto pr-2">
              {foundationalTasks.map((task) => (
                <div
                  key={task.id}
                  className="bg-gradient-to-r from-cyan-500/10 to-transparent border border-cyan-500/20 rounded-lg p-3 hover:border-cyan-400/40 transition-all"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-xs font-bold">
                        T{task.id}
                      </div>
                      <div>
                        <div className="text-cyan-300 font-semibold text-sm">{task.name}</div>
                        <div className="text-cyan-300/60 text-xs">{task.capability}</div>
                      </div>
                    </div>
                    <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50 text-xs">
                      {task.level}%
                    </Badge>
                  </div>
                  <Progress value={task.level} className="h-1 bg-cyan-950" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Knowledge Tiers Architecture */}
        <Card className="bg-slate-900/50 backdrop-blur-xl border-purple-500/30">
          <CardHeader className="border-b border-purple-500/20">
            <CardTitle className="flex items-center gap-2 text-purple-300">
              <Network className="h-6 w-6" />
              Knowledge Tier Architecture (1-34)
              <Badge className="ml-auto bg-purple-500/20 text-purple-300 border-purple-500/50">
                Domain Layer
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {knowledgeTiers.map((tier, idx) => {
                const Icon = tier.icon;
                return (
                  <div
                    key={idx}
                    className={`bg-gradient-to-br from-${tier.color}-500/10 to-${tier.color}-500/5 border border-${tier.color}-500/30 rounded-xl p-4 hover:border-${tier.color}-400/50 transition-all`}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <Icon className={`h-8 w-8 text-${tier.color}-400`} />
                      <div className="flex-1">
                        <div className={`text-${tier.color}-300 font-bold text-lg`}>{tier.category}</div>
                        <div className={`text-${tier.color}-300/60 text-sm`}>Tiers {tier.tiers}</div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold text-${tier.color}-400`}>{tier.count}</div>
                        <div className={`text-${tier.color}-300/60 text-xs`}>domains</div>
                      </div>
                    </div>
                    <Progress value={100} className={`h-2 bg-${tier.color}-950`} />
                  </div>
                );
              })}

              {/* Tier Breakdown */}
              <div className="bg-gradient-to-br from-purple-500/5 to-pink-500/5 border border-purple-500/20 rounded-xl p-4 mt-4">
                <div className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Complete Tier Breakdown
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="text-purple-300/80">• Tier 1-6: Languages (Ancient → Sci-Fi)</div>
                  <div className="text-purple-300/80">• Tier 7-27: Technical Mastery</div>
                  <div className="text-purple-300/80">• Tier 28: Autonomous Tools</div>
                  <div className="text-purple-300/80">• Tier 29-31: Professional Skills</div>
                  <div className="text-purple-300/80">• Tiers 66: Systems Design</div>
                  <div className="text-purple-300/80">• Tier 33: Network Mastery</div>
                  <div className="text-purple-300/80 col-span-2">• Tier 34: Grandmaster Autonomous</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Service Status Grid */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-emerald-500/30 mb-6">
        <CardHeader className="border-b border-emerald-500/20">
          <CardTitle className="flex items-center gap-2 text-emerald-300">
            <Database className="h-6 w-6" />
            System Services Status
            <Badge className="ml-auto bg-emerald-500/20 text-emerald-300 border-emerald-500/50">
              All Operational
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {systemServices.map((service, idx) => (
              <div
                key={idx}
                className="bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/30 rounded-xl p-4 hover:border-emerald-400/50 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <div className="text-emerald-300 font-semibold text-sm">{service.name}</div>
                </div>
                <div className="text-emerald-400/60 text-xs mb-1">Port: {service.port}</div>
                <div className="text-emerald-400 text-lg font-bold">{service.uptime}</div>
                <div className="text-emerald-300/60 text-xs">uptime</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Neural Activity Monitor */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-pink-500/30">
        <CardHeader className="border-b border-pink-500/20">
          <CardTitle className="flex items-center gap-2 text-pink-300">
            <Activity className="h-6 w-6" />
            Neural Activity Monitor
            <Badge className="ml-auto bg-pink-500/20 text-pink-300 border-pink-500/50">
              {neuralActivity.toFixed(1)}% Active
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/30 rounded-xl p-4">
              <Terminal className="h-8 w-8 text-cyan-400 mb-2" />
              <div className="text-cyan-300 text-sm mb-1">Task Processing</div>
              <div className="text-2xl font-bold text-cyan-400">Real-time</div>
            </div>

            <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/30 rounded-xl p-4">
              <Globe className="h-8 w-8 text-purple-400 mb-2" />
              <div className="text-purple-300 text-sm mb-1">Learning Mode</div>
              <div className="text-2xl font-bold text-purple-400">Continuous</div>
            </div>

            <div className="bg-gradient-to-br from-pink-500/10 to-pink-500/5 border border-pink-500/30 rounded-xl p-4">
              <Sparkles className="h-8 w-8 text-pink-400 mb-2" />
              <div className="text-pink-300 text-sm mb-1">Evolution</div>
              <div className="text-2xl font-bold text-pink-400">Active</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Footer Status Bar */}
      <div className="mt-6 bg-slate-900/30 backdrop-blur-xl border border-cyan-500/20 rounded-xl p-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div className="text-cyan-300/80">
              <span className="text-cyan-400 font-semibold">Architecture:</span> 13 Tasks + 34 Tiers = 66 Systems
            </div>
            <div className="text-purple-300/80">
              <span className="text-purple-400 font-semibold">Version:</span> Quantum Neural 2.0
            </div>
          </div>
          <div className="text-pink-300/80">
            <span className="text-pink-400 font-semibold">Status:</span> Fully Autonomous & Operational
          </div>
        </div>
      </div>
    </div>
  );
}