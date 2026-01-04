import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";
import { Database, RefreshCw, Search, Lightbulb, FileText, Brain, Layers, BookOpen, Tag, Clock, Star, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

interface MemoryData {
  stats: {
    shortTermCount: number;
    midTermCount: number;
    longTermCount: number;
    semanticCount: number;
    factCount: number;
    eventCount: number;
    totalMemories: number;
  };
  facts: Record<string, unknown>;
}

interface KnowledgeEntry {
  id: string;
  title: string;
  category: string;
  content: string;
  tags: string[];
  importance: number;
  lastAccessed: string;
}

export default function DatabasePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('facts');

  const { data: memoryData, isLoading, isError, error, refetch, isRefetching } = useQuery<MemoryData>({
    queryKey: ['/api/memory-fabric/status'],
    refetchInterval: 30000,
  });

  const knowledgeEntries: KnowledgeEntry[] = [
    { id: '1', title: 'TypeScript Best Practices', category: 'programming', content: 'Use strict type checking, prefer interfaces over type aliases...', tags: ['typescript', 'coding', 'best-practices'], importance: 0.92, lastAccessed: '5 min ago' },
    { id: '2', title: 'React Component Patterns', category: 'programming', content: 'Compound components, render props, higher-order components...', tags: ['react', 'patterns', 'components'], importance: 0.88, lastAccessed: '12 min ago' },
    { id: '3', title: 'Database Optimization', category: 'databases', content: 'Index strategies, query optimization, connection pooling...', tags: ['database', 'performance', 'sql'], importance: 0.85, lastAccessed: '1 hour ago' },
    { id: '4', title: 'API Design Guidelines', category: 'architecture', content: 'RESTful conventions, error handling, versioning strategies...', tags: ['api', 'design', 'rest'], importance: 0.90, lastAccessed: '30 min ago' },
    { id: '5', title: 'Security Best Practices', category: 'security', content: 'Input validation, authentication patterns, encryption...', tags: ['security', 'auth', 'encryption'], importance: 0.95, lastAccessed: '2 min ago' },
    { id: '6', title: 'Performance Optimization', category: 'optimization', content: 'Code splitting, lazy loading, caching strategies...', tags: ['performance', 'optimization', 'web'], importance: 0.87, lastAccessed: '45 min ago' },
  ];

  const facts = memoryData?.facts || {};
  const factEntries = Object.entries(facts);

  const filteredKnowledge = knowledgeEntries.filter(entry =>
    entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'programming': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'databases': return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'architecture': return 'bg-pink-500/20 text-pink-300 border-pink-500/30';
      case 'security': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'optimization': return 'bg-green-500/20 text-green-300 border-green-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-blue-400/50 flex items-center justify-center bg-gradient-to-br from-blue-500/20 to-purple-500/20">
                <Database className="w-6 h-6 text-blue-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent" data-testid="text-page-title">
                Knowledge Base
              </h1>
              <p className="text-sm text-muted-foreground">
                Comprehensive Data Storage & Retrieval
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="border-blue-500/30 hover:border-blue-400/50"
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
            <Database className="w-12 h-12 text-blue-400 animate-pulse mx-auto mb-4" />
            <p className="text-muted-foreground">Loading knowledge base...</p>
          </div>
        </div>
      ) : isError ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-300 mb-2">Failed to load knowledge base</p>
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
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-facts">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Lightbulb className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-xs text-cyan-300/60">Facts</p>
                    <p className="text-2xl font-bold text-cyan-400" data-testid="text-fact-count">
                      {memoryData?.stats?.factCount || factEntries.length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-memories">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-purple-300/60">Memories</p>
                    <p className="text-2xl font-bold text-purple-400" data-testid="text-memory-count">
                      {memoryData?.stats?.totalMemories || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-pink-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-semantic">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                    <Layers className="w-5 h-5 text-pink-400" />
                  </div>
                  <div>
                    <p className="text-xs text-pink-300/60">Semantic</p>
                    <p className="text-2xl font-bold text-pink-400" data-testid="text-semantic-count">
                      {memoryData?.stats?.semanticCount || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-500/30 bg-slate-900/50 backdrop-blur-xl" data-testid="card-stat-events">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-xs text-green-300/60">Events</p>
                    <p className="text-2xl font-bold text-green-400" data-testid="text-event-count">
                      {memoryData?.stats?.eventCount || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="border-blue-500/30 bg-slate-900/50 backdrop-blur-xl mb-6">
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-blue-400" />
                <Input
                  placeholder="Search knowledge base..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-800/50 border-blue-500/30 focus:border-blue-400/50 text-blue-100 placeholder:text-blue-300/40"
                  data-testid="input-search"
                />
              </div>
            </CardContent>
          </Card>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1" data-testid="tabs-knowledge">
            <TabsList className="mb-4 bg-slate-900 border border-blue-500/40 shadow-lg" data-testid="tablist-knowledge">
              <TabsTrigger value="facts" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-blue-300" data-testid="tab-trigger-facts">
                <Lightbulb className="w-4 h-4 mr-2" />
                Facts
              </TabsTrigger>
              <TabsTrigger value="knowledge" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600/70 data-[state=active]:to-cyan-600/70 data-[state=active]:text-white text-blue-300" data-testid="tab-trigger-knowledge">
                <BookOpen className="w-4 h-4 mr-2" />
                Knowledge
              </TabsTrigger>
            </TabsList>

            <TabsContent value="facts" className="h-[calc(100%-120px)]" data-testid="tab-content-facts">
              <ScrollArea className="h-full">
                <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-cyan-500/20">
                    <CardTitle className="flex items-center gap-2 text-lg text-cyan-300">
                      <Lightbulb className="w-5 h-5 text-yellow-400" />
                      Stored Facts
                    </CardTitle>
                    <CardDescription className="text-cyan-300/60">
                      Key information Aurora has learned and stored
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {factEntries.length === 0 ? (
                      <p className="text-muted-foreground text-sm text-center py-8">No facts stored yet. Start a conversation to teach Aurora!</p>
                    ) : (
                      <div className="space-y-3">
                        {factEntries.map(([key, value], index) => {
                          const factObj = value as { value?: string; category?: string; importance?: number };
                          const displayValue = factObj?.value !== undefined ? String(factObj.value) : String(value);
                          const category = factObj?.category || 'general';
                          const importance = factObj?.importance || 0.5;

                          return (
                            <motion.div
                              key={key}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.05 }}
                            >
                              <Card className="border-cyan-500/20 bg-slate-800/50" data-testid={`card-fact-${index}`}>
                                <CardContent className="p-4">
                                  <div className="flex items-start justify-between gap-2 mb-2">
                                    <div className="flex items-center gap-2">
                                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                                      <span className="font-mono text-sm text-cyan-300">{key}</span>
                                    </div>
                                    <Badge variant="outline" className="text-xs bg-cyan-500/10 text-cyan-300 border-cyan-500/30">
                                      {category}
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-cyan-100 mb-2">{displayValue}</p>
                                  <div className="flex items-center gap-2">
                                    <Star className="w-3 h-3 text-yellow-400" />
                                    <span className="text-xs text-yellow-300/60">
                                      {(importance * 100).toFixed(0)}% importance
                                    </span>
                                  </div>
                                </CardContent>
                              </Card>
                            </motion.div>
                          );
                        })}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="knowledge" className="h-[calc(100%-120px)]" data-testid="tab-content-knowledge">
              <ScrollArea className="h-full">
                <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-purple-500/20">
                    <CardTitle className="flex items-center gap-2 text-lg text-purple-300">
                      <BookOpen className="w-5 h-5 text-purple-400" />
                      Knowledge Library
                    </CardTitle>
                    <CardDescription className="text-purple-300/60">
                      Curated knowledge and best practices
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {filteredKnowledge.map((entry, index) => (
                        <motion.div
                          key={entry.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Card className="border-purple-500/20 bg-slate-800/50 hover:border-purple-400/40 transition-colors" data-testid={`card-knowledge-${entry.id}`}>
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <h3 className="text-sm font-semibold text-purple-200">{entry.title}</h3>
                                <Badge variant="outline" className={`text-xs ${getCategoryColor(entry.category)}`}>
                                  {entry.category}
                                </Badge>
                              </div>
                              <p className="text-xs text-purple-300/60 mb-3 line-clamp-2">{entry.content}</p>
                              <div className="flex flex-wrap gap-1 mb-3">
                                {entry.tags.map((tag, i) => (
                                  <Badge key={i} variant="outline" className="text-xs bg-slate-700/50 text-slate-300 border-slate-500/30">
                                    <Tag className="w-3 h-3 mr-1" />
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                              <div className="flex items-center justify-between text-xs">
                                <div className="flex items-center gap-1 text-muted-foreground">
                                  <Clock className="w-3 h-3" />
                                  {entry.lastAccessed}
                                </div>
                                <div className="flex items-center gap-1 text-yellow-400">
                                  <Star className="w-3 h-3" />
                                  {(entry.importance * 100).toFixed(0)}%
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
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
