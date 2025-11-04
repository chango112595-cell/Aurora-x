import { ErrorBoundary } from '@/components/error-boundary';
import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { BookOpen, Search, Code2, CheckCircle2, XCircle, Clock, Sparkles } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export default function Library() {
  const [searchTerm, setSearchTerm] = useState("");
  
  // Fetch Aurora's learned code from corpus
  const { data: corpusData, isLoading } = useQuery<{ items: any[] }>({
    queryKey: ['/api/corpus?limit=100'],
  });

  const filteredFunctions = corpusData?.items.filter(fn => 
    fn.func_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    fn.func_signature.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const stats = {
    total: corpusData?.items.length || 0,
    passed: corpusData?.items.filter(fn => fn.score === 1).length || 0,
    recent: corpusData?.items.filter(fn => {
      const date = new Date(fn.timestamp);
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return date > dayAgo;
    }).length || 0
  };

  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
      {/* Quantum background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20" />
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'particleFloat 20s linear infinite'
        }} />
      </div>

      <div className="p-6 space-y-6 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent flex items-center gap-3">
              <BookOpen className="h-10 w-10 text-cyan-400" />
              Aurora's Code Library
            </h1>
            <p className="text-muted-foreground mt-2">
              Functions Aurora has learned and synthesized through self-learning
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-cyan-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Functions</p>
                  <p className="text-3xl font-bold text-cyan-400">{stats.total}</p>
                </div>
                <Code2 className="h-12 w-12 text-cyan-400/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-green-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Passing Tests</p>
                  <p className="text-3xl font-bold text-green-400">{stats.passed}</p>
                </div>
                <CheckCircle2 className="h-12 w-12 text-green-400/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-purple-500/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Learned Today</p>
                  <p className="text-3xl font-bold text-purple-400">{stats.recent}</p>
                </div>
                <Sparkles className="h-12 w-12 text-purple-400/50 animate-pulse" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <Card className="border-cyan-500/20">
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search functions by name or signature..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Functions List */}
        <Card className="border-cyan-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5 text-cyan-400" />
              Learned Functions ({filteredFunctions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px]">
              {isLoading ? (
                <div className="flex items-center justify-center h-32">
                  <Sparkles className="h-8 w-8 animate-spin text-cyan-400" />
                  <span className="ml-2 text-muted-foreground">Loading Aurora's library...</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredFunctions.map((fn) => (
                    <Card key={fn.id} className="border-cyan-500/10 hover:border-cyan-500/30 transition-colors">
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-mono text-cyan-400 font-semibold">{fn.func_name}</h3>
                            <p className="text-xs text-muted-foreground mt-1">{fn.func_signature}</p>
                          </div>
                          <div className="flex gap-2">
                            {fn.score === 1 ? (
                              <Badge className="bg-green-500/20 text-green-400">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Passing
                              </Badge>
                            ) : (
                              <Badge variant="destructive">
                                <XCircle className="h-3 w-3 mr-1" />
                                {fn.passed}/{fn.total}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(fn.timestamp).toLocaleString()}
                          </span>
                          <span>Iteration: {fn.iteration}</span>
                          <span>Complexity: {fn.complexity}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
