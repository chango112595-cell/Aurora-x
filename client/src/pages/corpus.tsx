import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Database,
  TrendingUp,
  Zap,
  Search,
  Copy,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Filter,
  Sparkles,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

type CorpusEntry = {
  id: string;
  timestamp: string;
  spec_id: string;
  func_name: string;
  func_signature: string;
  passed: number;
  total: number;
  score: number;
  snippet: string;
  failing_tests?: string[];
  calls_functions?: string[];
  complexity?: number;
  iteration?: number;
  sig_key?: string;
  post_bow?: string[];
};

type SimilarityResult = {
  entry: CorpusEntry;
  similarity: number;
  breakdown: {
    returnMatch: number;
    argMatch: number;
    jaccardScore: number;
    perfectBonus: number;
  };
};

export default function Corpus() {
  const [funcFilter, setFuncFilter] = useState("");
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [perfectOnly, setPerfectOnly] = useState(false);
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [maxScore, setMaxScore] = useState<number | undefined>(undefined);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<CorpusEntry | null>(null);
  const [showSimilarity, setShowSimilarity] = useState(false);
  const { toast } = useToast();

  const queryParams = {
    func: funcFilter || undefined,
    limit,
    offset,
    perfectOnly,
    minScore,
    maxScore,
  };

  const { data: corpusData, isLoading } = useQuery<{
    items: CorpusEntry[];
    hasMore: boolean;
  }>({
    queryKey: ["/api/corpus", queryParams],
  });

  const similarityMutation = useMutation({
    mutationFn: async (entry: CorpusEntry) => {
      const res = await fetch("/api/corpus/similar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          targetSigKey: entry.sig_key || "",
          targetPostBow: entry.post_bow || [],
          limit: 5,
        }),
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch similarity: ${res.statusText}`);
      }
      const data: { results: SimilarityResult[] } = await res.json();
      return data;
    },
  });

  const entries = corpusData?.items || [];
  const hasMore = corpusData?.hasMore || false;
  const totalRecords = entries.length;
  const perfectRuns = entries.filter((e) => e.passed === e.total).length;
  const avgScore =
    entries.length > 0
      ? (entries.reduce((sum, e) => sum + e.score, 0) / entries.length).toFixed(
          2
        )
      : "0";

  const stats = [
    {
      label: "Total Records",
      value: totalRecords.toString(),
      icon: Database,
      color: "text-chart-1",
    },
    {
      label: "Perfect Runs",
      value: perfectRuns.toString(),
      icon: CheckCircle2,
      color: "text-chart-2",
    },
    {
      label: "Avg Score",
      value: avgScore,
      icon: Zap,
      color: "text-chart-3",
    },
  ];

  const copySnippet = async (snippet: string) => {
    try {
      await navigator.clipboard.writeText(snippet);
      toast({
        title: "Copied",
        description: "Snippet copied to clipboard",
      });
    } catch {
      toast({
        title: "Error",
        description: "Failed to copy snippet",
        variant: "destructive",
      });
    }
  };

  const passPercentage = (passed: number, total: number) => {
    if (!total) return "0%";
    return `${Math.round((passed / total) * 100)}%`;
  };

  const showSimilarEntries = (entry: CorpusEntry) => {
    setSelectedEntry(entry);
    setShowSimilarity(true);
    similarityMutation.mutate(entry);
  };

  const nextPage = () => {
    setOffset(offset + limit);
  };

  const prevPage = () => {
    setOffset(Math.max(0, offset - limit));
  };

  const resetFilters = () => {
    setFuncFilter("");
    setPerfectOnly(false);
    setMinScore(undefined);
    setMaxScore(undefined);
    setOffset(0);
  };

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">
            Corpus Explorer
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Explore Aurora's learning corpus and synthesis history
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {stats.map((stat) => (
            <Card
              key={stat.label}
              className="hover-elevate"
              data-testid={`card-${stat.label.toLowerCase().replace(" ", "-")}`}
            >
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.label}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div
                  className="text-2xl font-bold"
                  data-testid={`text-${stat.label.toLowerCase().replace(" ", "-")}`}
                >
                  {stat.value}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card data-testid="card-corpus-data">
          <CardHeader>
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <CardTitle>Synthesis Records</CardTitle>
              <div className="flex items-center gap-2 flex-wrap">
                <div className="relative flex-1 min-w-60">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Filter by function name"
                    value={funcFilter}
                    onChange={(e) => {
                      setFuncFilter(e.target.value);
                      setOffset(0);
                    }}
                    className="pl-8"
                    data-testid="input-filter-func"
                  />
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowFilters(!showFilters)}
                  data-testid="button-toggle-filters"
                >
                  <Filter className="h-4 w-4" />
                </Button>
                <select
                  value={limit}
                  onChange={(e) => {
                    setLimit(Number(e.target.value));
                    setOffset(0);
                  }}
                  className="border rounded-md px-3 min-h-9 bg-background"
                  data-testid="select-limit"
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>
            </div>
            {showFilters && (
              <div className="mt-4 p-4 border rounded-lg space-y-4 bg-muted/30">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium">Advanced Filters</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetFilters}
                    data-testid="button-reset-filters"
                  >
                    Reset All
                  </Button>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="perfect-only"
                      checked={perfectOnly}
                      onCheckedChange={(checked) => {
                        setPerfectOnly(checked);
                        setOffset(0);
                      }}
                      data-testid="switch-perfect-only"
                    />
                    <Label htmlFor="perfect-only">Perfect runs only</Label>
                  </div>
                  <div className="space-y-2">
                    <Label>Score Range</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        placeholder="Min"
                        value={minScore ?? ""}
                        onChange={(e) => {
                          setMinScore(
                            e.target.value ? Number(e.target.value) : undefined
                          );
                          setOffset(0);
                        }}
                        className="w-24"
                        step="0.01"
                        data-testid="input-min-score"
                      />
                      <span className="text-muted-foreground">to</span>
                      <Input
                        type="number"
                        placeholder="Max"
                        value={maxScore ?? ""}
                        onChange={(e) => {
                          setMaxScore(
                            e.target.value ? Number(e.target.value) : undefined
                          );
                          setOffset(0);
                        }}
                        className="w-24"
                        step="0.01"
                        data-testid="input-max-score"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading...
              </div>
            ) : entries.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No synthesis records found. Adjust your filters or start a
                synthesis run.
              </div>
            ) : (
              <>
                <div className="space-y-3">
                  {entries.map((entry) => (
                    <div
                      key={entry.id}
                      className="rounded-lg border border-border p-4 space-y-3 hover-elevate"
                      data-testid={`record-${entry.func_name}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <code className="text-sm font-mono font-semibold">
                              {entry.func_name}
                            </code>
                            <Badge
                              variant="secondary"
                              data-testid={`badge-pass-${entry.func_name}`}
                            >
                              {entry.passed}/{entry.total} (
                              {passPercentage(entry.passed, entry.total)})
                            </Badge>
                            <Badge variant="outline">
                              Score: {entry.score.toFixed(4)}
                            </Badge>
                            {entry.complexity !== undefined &&
                              entry.complexity >= 0 && (
                                <Badge variant="outline">
                                  AST: {entry.complexity}
                                </Badge>
                              )}
                            {entry.calls_functions &&
                              entry.calls_functions.length > 0 && (
                                <Badge variant="outline">
                                  Calls: {entry.calls_functions.length}
                                </Badge>
                              )}
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 font-mono">
                            {entry.func_signature}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(entry.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => copySnippet(entry.snippet)}
                            data-testid={`button-copy-${entry.func_name}`}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          {entry.sig_key && (
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => showSimilarEntries(entry)}
                              data-testid={`button-similar-${entry.func_name}`}
                            >
                              <Sparkles className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      {entry.failing_tests && entry.failing_tests.length > 0 && (
                        <div className="text-xs text-destructive">
                          Failed: {entry.failing_tests.join(", ")}
                        </div>
                      )}
                      <div className="relative">
                        <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-60 overflow-y-auto">
                          {entry.snippet}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <div className="text-sm text-muted-foreground">
                    Showing {offset + 1} - {offset + entries.length}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={prevPage}
                      disabled={offset === 0}
                      data-testid="button-prev-page"
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={nextPage}
                      disabled={!hasMore}
                      data-testid="button-next-page"
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Dialog open={showSimilarity} onOpenChange={setShowSimilarity}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                Similarity Analysis for{" "}
                <code className="font-mono">{selectedEntry?.func_name}</code>
              </DialogTitle>
            </DialogHeader>
            {similarityMutation.isPending ? (
              <div className="text-center py-8 text-muted-foreground">
                Computing similarities...
              </div>
            ) : similarityMutation.data ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Top similar functions based on signature and post-conditions
                </p>
                {similarityMutation.data.results.map((result: SimilarityResult, idx: number) => (
                  <Card key={result.entry.id} className="hover-elevate">
                    <CardHeader>
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge variant="secondary">#{idx + 1}</Badge>
                            <code className="text-sm font-mono font-semibold">
                              {result.entry.func_name}
                            </code>
                            <Badge
                              variant={
                                result.similarity > 0.7 ? "default" : "outline"
                              }
                            >
                              {(result.similarity * 100).toFixed(1)}% similar
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-2">
                            {result.entry.func_signature}
                          </p>
                        </div>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => copySnippet(result.entry.snippet)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-muted-foreground">
                            Return Match:
                          </span>{" "}
                          <Badge variant="outline" className="ml-1">
                            {(result.breakdown.returnMatch * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <div>
                          <span className="text-muted-foreground">
                            Arg Match:
                          </span>{" "}
                          <Badge variant="outline" className="ml-1">
                            {(result.breakdown.argMatch * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <div>
                          <span className="text-muted-foreground">
                            Jaccard:
                          </span>{" "}
                          <Badge variant="outline" className="ml-1">
                            {(result.breakdown.jaccardScore * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Bonus:</span>{" "}
                          <Badge variant="outline" className="ml-1">
                            {(result.breakdown.perfectBonus * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                      <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-40 overflow-y-auto">
                        {result.entry.snippet}
                      </pre>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : null}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
