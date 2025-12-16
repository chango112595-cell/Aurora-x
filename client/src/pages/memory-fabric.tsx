import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";
import { Brain, Database, Clock, Zap, FileText, Search, RefreshCw, Layers, MessageSquare, Lightbulb, History, Target, Network, Server, Activity } from "lucide-react";
import { motion } from "framer-motion";

interface MemoryEntry {
  id: string;
  content: string;
  role: string;
  timestamp: string;
  layer: string;
  importance: number;
  tags: string[];
  metadata: Record<string, unknown>;
}

interface MemoryStats {
  shortTermCount: number;
  midTermCount: number;
  longTermCount: number;
  semanticCount: number;
  factCount: number;
  eventCount: number;
  totalMemories: number;
  activeProject: string;
  sessionId: string;
}

interface MemoryData {
  stats: MemoryStats;
  facts: Record<string, unknown>;
  shortTerm: MemoryEntry[];
  midTerm: MemoryEntry[];
  longTerm: MemoryEntry[];
  semantic: MemoryEntry[];
  events: Array<{ timestamp: string; event: string; details?: Record<string, unknown> }>;
  conversations: string[];
}

interface NexusStatus {
  v2: {
    connected: boolean;
    port: number;
    status: string;
    chatResponses?: number;
  };
  v3: {
    connected: boolean;
    status: string;
    workers?: number | { total: number; active: number; idle: number };
    tiers?: number;
    aems?: number;
    modules?: number;
    hybridMode?: boolean;
  };
}

export default function MemoryFabric() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);

  const { data: memoryData, isLoading, refetch, isRefetching } = useQuery<MemoryData>({
    queryKey: ['/api/memory-fabric/status'],
    refetchInterval: 30000,
  });

  const { data: conversationData } = useQuery<{ messages: MemoryEntry[] }>({
    queryKey: ['/api/memory-fabric/conversation', selectedConversation],
    enabled: !!selectedConversation,
  });

  const { data: nexusStatus } = useQuery<NexusStatus>({
    queryKey: ['/api/nexus/status'],
    refetchInterval: 86400000, // 24 hours
  });

  const stats = memoryData?.stats;

  const renderMemoryCard = (entry: MemoryEntry, index: number) => (
    <motion.div
      key={entry.id || index}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className="mb-3 border-cyan-500/20 bg-gradient-to-br from-cyan-950/20 to-purple-950/20">
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-2 mb-2">
            <Badge variant={entry.role === 'user' ? 'outline' : 'default'} className="text-xs" data-testid={`badge-role-${index}`}>
              {entry.role}
            </Badge>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs" data-testid={`badge-layer-${index}`}>
                {entry.layer}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
          <p className="text-sm text-foreground/90 whitespace-pre-wrap" data-testid={`text-content-${index}`}>
            {entry.content}
          </p>
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {entry.tags.map((tag, i) => (
                <Badge key={i} variant="outline" className="text-xs text-cyan-400/80">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 h-1 bg-cyan-950/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500" 
                style={{ width: `${(entry.importance || 0.5) * 100}%` }} 
              />
            </div>
            <span className="text-xs text-cyan-400/60 font-mono">
              {((entry.importance || 0.5) * 100).toFixed(0)}%
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderFactsCard = (facts: Record<string, unknown>) => {
    const entries = Object.entries(facts);
    return (
      <div className="space-y-2">
        {entries.length === 0 ? (
          <p className="text-muted-foreground text-sm">No facts stored yet.</p>
        ) : (
          entries.map(([key, factData], index) => {
            const factObj = factData as { value?: string; category?: string; timestamp?: string; importance?: number };
            const displayValue = factObj?.value !== undefined ? String(factObj.value) : String(factData);
            const category = factObj?.category || 'general';
            const importance = factObj?.importance || 0.5;
            
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="border-cyan-500/20 bg-gradient-to-br from-cyan-950/10 to-purple-950/10">
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Lightbulb className="w-4 h-4 text-yellow-400" />
                        <span className="font-mono text-sm text-cyan-300">{key}</span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {category}
                      </Badge>
                    </div>
                    <p className="text-sm text-foreground/90 font-mono mb-2" data-testid={`text-fact-${key}`}>
                      {displayValue}
                    </p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1 bg-cyan-950/50 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-yellow-500 to-cyan-500" 
                          style={{ width: `${importance * 100}%` }} 
                        />
                      </div>
                      <span className="text-xs text-yellow-400/60 font-mono">
                        {(importance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })
        )}
      </div>
    );
  };

  const renderEventsLog = (events: Array<{ timestamp: string; event: string; details?: Record<string, unknown> }>) => (
    <div className="space-y-2" data-testid="list-events">
      {(!events || events.length === 0) ? (
        <p className="text-muted-foreground text-sm" data-testid="text-no-events">No events logged yet.</p>
      ) : (
        events.slice(-50).reverse().map((event, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: index * 0.02 }}
          >
            <Card className="border-purple-500/20 bg-gradient-to-br from-purple-950/10 to-cyan-950/10" data-testid={`card-event-${index}`}>
              <CardContent className="p-3">
                <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
                  <Badge variant="outline" className="text-xs" data-testid={`badge-event-type-${index}`}>
                    {event.event}
                  </Badge>
                  <span className="text-xs text-muted-foreground" data-testid={`text-event-time-${index}`}>
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                {event.details && (
                  <pre className="text-xs text-muted-foreground mt-1 overflow-x-auto" data-testid={`text-event-details-${index}`}>
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))
      )}
    </div>
  );

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-cyan-400/50 flex items-center justify-center bg-gradient-to-br from-cyan-500/20 to-purple-500/20">
                <Brain className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent" data-testid="text-page-title">
                Memory Fabric
              </h1>
              <p className="text-sm text-muted-foreground">
                Aurora's Neural Memory System - What She Remembers
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
            <Brain className="w-12 h-12 text-cyan-400 animate-pulse mx-auto mb-4" />
            <p className="text-muted-foreground">Loading Aurora's memories...</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="border-cyan-500/20 bg-gradient-to-br from-cyan-950/20 to-transparent" data-testid="card-stat-short-term">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Zap className="w-8 h-8 text-yellow-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Short-Term</p>
                    <p className="text-2xl font-bold text-cyan-400" data-testid="text-short-term-count">
                      {stats?.shortTermCount || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-purple-500/20 bg-gradient-to-br from-purple-950/20 to-transparent" data-testid="card-stat-mid-term">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Mid-Term</p>
                    <p className="text-2xl font-bold text-purple-400" data-testid="text-mid-term-count">
                      {stats?.midTermCount || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/20 to-transparent" data-testid="card-stat-long-term">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Database className="w-8 h-8 text-blue-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Long-Term</p>
                    <p className="text-2xl font-bold text-blue-400" data-testid="text-long-term-count">
                      {stats?.longTermCount || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-green-500/20 bg-gradient-to-br from-green-950/20 to-transparent" data-testid="card-stat-total">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Layers className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Total</p>
                    <p className="text-2xl font-bold text-green-400" data-testid="text-total-count">
                      {stats?.totalMemories || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <Card className="border-purple-500/30 bg-slate-900/80" data-testid="card-active-project">
              <CardContent className="p-3 flex items-center justify-between gap-2 flex-wrap">
                <span className="text-sm text-purple-200">Active Project</span>
                <Badge variant="outline" className="font-mono bg-purple-900/50 text-purple-100 border-purple-400/50" data-testid="text-active-project">
                  {stats?.activeProject || 'None'}
                </Badge>
              </CardContent>
            </Card>
            <Card className="border-purple-500/30 bg-slate-900/80" data-testid="card-facts-stored">
              <CardContent className="p-3 flex items-center justify-between gap-2 flex-wrap">
                <span className="text-sm text-purple-200">Facts Stored</span>
                <Badge variant="outline" className="font-mono bg-purple-900/50 text-purple-100 border-purple-400/50" data-testid="text-fact-count">
                  {stats?.factCount || 0}
                </Badge>
              </CardContent>
            </Card>
            <Card className="border-purple-500/30 bg-slate-900/80" data-testid="card-events-logged">
              <CardContent className="p-3 flex items-center justify-between gap-2 flex-wrap">
                <span className="text-sm text-purple-200">Events Logged</span>
                <Badge variant="outline" className="font-mono bg-purple-900/50 text-purple-100 border-purple-400/50" data-testid="text-event-count">
                  {stats?.eventCount || 0}
                </Badge>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <Card className="border-cyan-500/40 bg-gradient-to-br from-slate-900 to-cyan-950/50" data-testid="card-nexus-v2">
              <CardContent className="p-4">
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${nexusStatus?.v2?.connected ? 'bg-cyan-500/30' : 'bg-slate-700/50'}`}>
                      <MessageSquare className={`w-5 h-5 ${nexusStatus?.v2?.connected ? 'text-cyan-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-cyan-100">Luminar Nexus V2</h3>
                      <p className="text-xs text-cyan-300/70">Chat & ML Pattern Learning</p>
                    </div>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`${nexusStatus?.v2?.connected ? 'bg-green-900/50 text-green-300 border-green-500/50' : 'bg-red-900/50 text-red-300 border-red-500/50'}`}
                    data-testid="badge-nexus-v2-status"
                  >
                    {nexusStatus?.v2?.connected ? 'Connected' : 'Offline'}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded">
                    <span className="text-cyan-300/70">Port</span>
                    <span className="font-mono text-cyan-200">{nexusStatus?.v2?.port || 8000}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded">
                    <span className="text-cyan-300/70">Responses</span>
                    <span className="font-mono text-cyan-200">{nexusStatus?.v2?.chatResponses || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-500/40 bg-gradient-to-br from-slate-900 to-purple-950/50" data-testid="card-nexus-v3">
              <CardContent className="p-4">
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${nexusStatus?.v3?.connected ? 'bg-purple-500/30' : 'bg-slate-700/50'}`}>
                      <Network className={`w-5 h-5 ${nexusStatus?.v3?.connected ? 'text-purple-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-purple-100">Aurora Nexus V3</h3>
                      <p className="text-xs text-purple-300/70">Universal Consciousness</p>
                    </div>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`${nexusStatus?.v3?.connected ? 'bg-green-900/50 text-green-300 border-green-500/50' : 'bg-red-900/50 text-red-300 border-red-500/50'}`}
                    data-testid="badge-nexus-v3-status"
                  >
                    {nexusStatus?.v3?.connected ? 'Connected' : 'Offline'}
                  </Badge>
                </div>
                <div className="grid grid-cols-4 gap-2 text-xs">
                  <div className="flex flex-col items-center p-2 bg-slate-800/50 rounded">
                    <span className="text-purple-300/70 text-[10px]">Workers</span>
                    <span className="font-mono text-purple-200 font-bold">
                      {typeof nexusStatus?.v3?.workers === 'object' 
                        ? nexusStatus.v3.workers.total 
                        : (nexusStatus?.v3?.workers || 300)}
                    </span>
                  </div>
                  <div className="flex flex-col items-center p-2 bg-slate-800/50 rounded">
                    <span className="text-purple-300/70 text-[10px]">Tiers</span>
                    <span className="font-mono text-purple-200 font-bold">{nexusStatus?.v3?.tiers || 188}</span>
                  </div>
                  <div className="flex flex-col items-center p-2 bg-slate-800/50 rounded">
                    <span className="text-purple-300/70 text-[10px]">AEMs</span>
                    <span className="font-mono text-purple-200 font-bold">{nexusStatus?.v3?.aems || 66}</span>
                  </div>
                  <div className="flex flex-col items-center p-2 bg-slate-800/50 rounded">
                    <span className="text-purple-300/70 text-[10px]">Modules</span>
                    <span className="font-mono text-purple-200 font-bold">{nexusStatus?.v3?.modules || 550}</span>
                  </div>
                </div>
                {nexusStatus?.v3?.hybridMode && (
                  <div className="mt-2 flex items-center gap-2 p-2 bg-green-900/30 rounded border border-green-500/30">
                    <Activity className="w-4 h-4 text-green-400 animate-pulse" />
                    <span className="text-xs text-green-300">Hybrid Mode Active - Brain Bridge Connected</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1" data-testid="tabs-memory-fabric">
            <TabsList className="mb-4 bg-slate-900 border border-purple-500/40 shadow-lg" data-testid="tablist-memory">
              <TabsTrigger value="overview" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-purple-300" data-testid="tab-trigger-overview">
                <Target className="w-4 h-4 mr-2" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="facts" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-purple-300" data-testid="tab-trigger-facts">
                <Lightbulb className="w-4 h-4 mr-2" />
                Facts
              </TabsTrigger>
              <TabsTrigger value="memories" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-purple-300" data-testid="tab-trigger-memories">
                <Brain className="w-4 h-4 mr-2" />
                Memories
              </TabsTrigger>
              <TabsTrigger value="conversations" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-purple-300" data-testid="tab-trigger-conversations">
                <MessageSquare className="w-4 h-4 mr-2" />
                Conversations
              </TabsTrigger>
              <TabsTrigger value="events" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-purple-300" data-testid="tab-trigger-events">
                <History className="w-4 h-4 mr-2" />
                Events
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="h-[calc(100%-60px)]" data-testid="tab-content-overview">
              <ScrollArea className="h-full">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-overview-facts">
                    <CardHeader className="border-b border-cyan-500/20">
                      <CardTitle className="flex items-center gap-2 text-lg text-cyan-300">
                        <Lightbulb className="w-5 h-5 text-yellow-400" />
                        Key Facts Aurora Knows
                      </CardTitle>
                      <CardDescription className="text-cyan-300/60">Important information stored in memory</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-4">
                      {renderFactsCard(memoryData?.facts || {})}
                    </CardContent>
                  </Card>

                  <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-overview-short-term">
                    <CardHeader className="border-b border-purple-500/20">
                      <CardTitle className="flex items-center gap-2 text-lg text-purple-300">
                        <Zap className="w-5 h-5 text-yellow-400" />
                        Recent Short-Term Memories
                      </CardTitle>
                      <CardDescription className="text-purple-300/60">Current session context</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <ScrollArea className="h-[300px]">
                        {(memoryData?.shortTerm || []).length === 0 ? (
                          <p className="text-purple-300/50 text-sm" data-testid="text-no-short-term-overview">No short-term memories in current session.</p>
                        ) : (
                          memoryData?.shortTerm.slice(-5).map((entry, i) => renderMemoryCard(entry, i))
                        )}
                      </ScrollArea>
                    </CardContent>
                  </Card>
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="facts" className="h-[calc(100%-60px)]" data-testid="tab-content-facts">
              <ScrollArea className="h-full">
                <Card className="border-cyan-500/20" data-testid="card-all-facts">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-yellow-400" />
                      All Stored Facts
                    </CardTitle>
                    <CardDescription>Persistent facts Aurora remembers about you and the project</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {renderFactsCard(memoryData?.facts || {})}
                  </CardContent>
                </Card>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="memories" className="h-[calc(100%-60px)]" data-testid="tab-content-memories">
              <ScrollArea className="h-full">
                <div className="space-y-6">
                  <Card className="border-yellow-500/20" data-testid="card-short-term-memories">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Zap className="w-5 h-5 text-yellow-400" />
                        Short-Term Memory ({memoryData?.shortTerm?.length || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {(memoryData?.shortTerm || []).length === 0 ? (
                        <p className="text-muted-foreground text-sm" data-testid="text-no-short-term">No short-term memories.</p>
                      ) : (
                        memoryData?.shortTerm.map((entry, i) => renderMemoryCard(entry, i))
                      )}
                    </CardContent>
                  </Card>

                  <Card className="border-purple-500/20" data-testid="card-mid-term-memories">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Clock className="w-5 h-5 text-purple-400" />
                        Mid-Term Memory ({memoryData?.midTerm?.length || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {(memoryData?.midTerm || []).length === 0 ? (
                        <p className="text-muted-foreground text-sm" data-testid="text-no-mid-term">No mid-term memories.</p>
                      ) : (
                        memoryData?.midTerm.map((entry, i) => renderMemoryCard(entry, i))
                      )}
                    </CardContent>
                  </Card>

                  <Card className="border-blue-500/20" data-testid="card-long-term-memories">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Database className="w-5 h-5 text-blue-400" />
                        Long-Term Memory ({memoryData?.longTerm?.length || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {(memoryData?.longTerm || []).length === 0 ? (
                        <p className="text-muted-foreground text-sm">No long-term memories.</p>
                      ) : (
                        memoryData?.longTerm.map((entry, i) => renderMemoryCard(entry, i))
                      )}
                    </CardContent>
                  </Card>
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="conversations" className="h-[calc(100%-60px)]" data-testid="tab-content-conversations">
              <ScrollArea className="h-full">
                <Card className="border-cyan-500/20" data-testid="card-conversations">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="w-5 h-5 text-cyan-400" />
                      Conversation History
                    </CardTitle>
                    <CardDescription>Past conversations stored in memory</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(memoryData?.conversations || []).length === 0 ? (
                      <p className="text-muted-foreground text-sm" data-testid="text-no-conversations">No conversation history found.</p>
                    ) : (
                      <div className="space-y-2" data-testid="list-conversations">
                        {memoryData?.conversations.map((conv, index) => (
                          <Card 
                            key={index} 
                            className={`cursor-pointer transition-all hover:border-cyan-400/50 ${selectedConversation === conv ? 'border-cyan-400/50 bg-cyan-500/10' : 'border-cyan-500/20'}`}
                            onClick={() => setSelectedConversation(conv)}
                            data-testid={`card-conversation-${index}`}
                          >
                            <CardContent className="p-3 flex items-center justify-between gap-2 flex-wrap">
                              <div className="flex items-center gap-2">
                                <FileText className="w-4 h-4 text-cyan-400" />
                                <span className="text-sm font-mono" data-testid={`text-conversation-name-${index}`}>{conv}</span>
                              </div>
                              <Badge variant="outline" className="text-xs" data-testid={`button-view-conversation-${index}`}>
                                View
                              </Badge>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}

                    {selectedConversation && conversationData?.messages && (
                      <div className="mt-6 pt-6 border-t border-cyan-500/20" data-testid="section-conversation-messages">
                        <h4 className="text-sm font-medium mb-4 flex items-center gap-2">
                          <MessageSquare className="w-4 h-4" />
                          {selectedConversation}
                        </h4>
                        {conversationData.messages.map((msg, i) => renderMemoryCard(msg, i))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="events" className="h-[calc(100%-60px)]" data-testid="tab-content-events">
              <ScrollArea className="h-full">
                <Card className="border-purple-500/20" data-testid="card-events">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <History className="w-5 h-5 text-purple-400" />
                      Event Log
                    </CardTitle>
                    <CardDescription>System events and actions recorded by Aurora</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {renderEventsLog(memoryData?.events || [])}
                  </CardContent>
                </Card>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}