import { ErrorBoundary } from '@/components/error-boundary';
import { useMemo, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { BookOpen, Search, Code2, CheckCircle2, XCircle, Clock, Sparkles, Copy, Check } from "lucide-react";
import { useInfiniteQuery } from "@tanstack/react-query";

type CorpusItem = {
  id: string;
  func_name: string;
  func_signature: string;
  snippet: string;
  score: number;
  passed: number;
  total: number;
  timestamp: string;
  iteration?: number;
  complexity?: number;
};

export default function Library() {
  const [searchTerm, setSearchTerm] = useState("");
  const [passingOnly, setPassingOnly] = useState(false);
  const [minScore, setMinScore] = useState<number>(0);
  const [selected, setSelected] = useState<CorpusItem | null>(null);
  const [copied, setCopied] = useState(false);

  const pageSize = 50;

  // Build query string for server-side filters we support
  const baseQuery = useMemo(() => {
    const params = new URLSearchParams();
    params.set('limit', String(pageSize));
    if (passingOnly) params.set('perfectOnly', 'true');
    if (minScore > 0) params.set('minScore', String(minScore));
    return `/api/corpus?${params.toString()}`;
  }, [passingOnly, minScore]);

  const {
    data,
    isLoading,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useInfiniteQuery<{ items: CorpusItem[]; hasMore: boolean }>({
    queryKey: ['corpus', baseQuery],
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages, lastPageParam) => {
      return lastPage?.hasMore ? (allPages.length * pageSize) : undefined;
    },
    queryFn: async ({ pageParam }) => {
      const offset = pageParam ?? 0;
      const url = `${baseQuery}&offset=${offset}`;
      const res = await fetch(url, { credentials: 'include' });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
  });

  // Flatten pages and apply client-side search filter by name/signature
  const allItems: CorpusItem[] = useMemo(() => {
    const items = data?.pages.flatMap(p => p.items) ?? [];
    if (!searchTerm) return items;
    const q = searchTerm.toLowerCase();
    return items.filter(fn =>
      fn.func_name.toLowerCase().includes(q) ||
      fn.func_signature.toLowerCase().includes(q)
    );
  }, [data, searchTerm]);

  const stats = useMemo(() => {
    const items = data?.pages.flatMap(p => p.items) ?? [];
    const total = items.length;
    const passed = items.filter(fn => fn.score === 1).length;
    const recent = items.filter(fn => {
      const date = new Date(fn.timestamp);
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return date > dayAgo;
    }).length;
    return { total, passed, recent };
  }, [data]);

  function onCopy(snippet?: string) {
    if (!snippet) return;
    navigator.clipboard.writeText(snippet).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    });
  }

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

        {/* Search + Filters */}
        <Card className="border-cyan-500/20">
          <CardContent className="pt-6 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search functions by name or signature..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 items-center gap-4">
              <div className="flex items-center gap-3">
                <Switch id="passing-only" checked={passingOnly} onCheckedChange={setPassingOnly} />
                <Label htmlFor="passing-only" className="text-sm">Passing only</Label>
              </div>
              <div className="col-span-2">
                <div className="flex items-center justify-between mb-2">
                  <Label htmlFor="score-range" className="text-sm">Minimum score</Label>
                  <span className="text-xs text-muted-foreground">{(minScore * 100).toFixed(0)}%</span>
                </div>
                <Slider id="score-range" value={[minScore]} min={0} max={1} step={0.05} onValueChange={(v) => setMinScore(v[0] ?? 0)} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Functions List */}
        <Card className="border-cyan-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5 text-cyan-400" />
              Learned Functions ({allItems.length})
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
                  {allItems.map((fn) => (
                    <Card
                      key={fn.id}
                      className="border-cyan-500/10 hover:border-cyan-500/30 transition-colors cursor-pointer"
                      onClick={() => setSelected(fn)}
                    >
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
                          {fn.iteration !== undefined && (
                            <span>Iteration: {fn.iteration}</span>
                          )}
                          {fn.complexity !== undefined && (
                            <span>Complexity: {fn.complexity}</span>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  <div className="pt-2">
                    {hasNextPage && (
                      <Button variant="outline" className="w-full" onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
                        {isFetchingNextPage ? 'Loading…' : 'Load more'}
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Code Dialog */}
        <Dialog open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle className="font-mono text-cyan-400">{selected?.func_name}</DialogTitle>
              <DialogDescription className="font-mono text-xs text-muted-foreground">
                {selected?.func_signature}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex gap-2 items-center">
                  {selected?.score === 1 ? (
                    <Badge className="bg-green-500/20 text-green-400">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> Passing
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="h-3 w-3 mr-1" /> {selected?.passed}/{selected?.total}
                    </Badge>
                  )}
                  <span>
                    <Clock className="h-3 w-3 inline mr-1" /> {selected ? new Date(selected.timestamp).toLocaleString() : ''}
                  </span>
                </div>
                <Button size="sm" variant="outline" onClick={() => onCopy(selected?.snippet)}>
                  {copied ? (<><Check className="h-4 w-4 mr-1" /> Copied</>) : (<><Copy className="h-4 w-4 mr-1" /> Copy</>)}
                </Button>
              </div>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                <code>{selected?.snippet}</code>
              </pre>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
