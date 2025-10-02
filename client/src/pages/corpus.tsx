import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Database, TrendingUp, Zap, Search, Copy, CheckCircle2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

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
  failing_tests?: string;
  complexity?: number;
  iteration?: number;
};

export default function Corpus() {
  const [funcFilter, setFuncFilter] = useState("");
  const [limit, setLimit] = useState(50);
  const { toast } = useToast();

  const { data: corpusData, isLoading } = useQuery<{ items: CorpusEntry[] }>({
    queryKey: ["/api/corpus", { func: funcFilter || undefined, limit }],
  });

  const entries = corpusData?.items || [];
  const totalRecords = entries.length;
  const perfectRuns = entries.filter((e) => e.passed === e.total).length;
  const avgScore = entries.length > 0
    ? (entries.reduce((sum, e) => sum + e.score, 0) / entries.length).toFixed(2)
    : "0";

  const stats = [
    { label: "Total Records", value: totalRecords.toString(), icon: Database, color: "text-chart-1" },
    { label: "Perfect Runs", value: perfectRuns.toString(), icon: CheckCircle2, color: "text-chart-2" },
    { label: "Avg Score", value: avgScore, icon: Zap, color: "text-chart-3" },
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

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Corpus Explorer</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Explore Aurora's learning corpus and synthesis history
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {stats.map((stat) => (
            <Card key={stat.label} className="hover-elevate" data-testid={`card-${stat.label.toLowerCase().replace(' ', '-')}`}>
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold" data-testid={`text-${stat.label.toLowerCase().replace(' ', '-')}`}>{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card data-testid="card-corpus-data">
          <CardHeader>
            <div className="flex items-center justify-between gap-4">
              <CardTitle>Synthesis Records</CardTitle>
              <div className="flex items-center gap-2">
                <div className="relative flex-1 min-w-60">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Filter by function name"
                    value={funcFilter}
                    onChange={(e) => setFuncFilter(e.target.value)}
                    className="pl-8"
                    data-testid="input-filter-func"
                  />
                </div>
                <select
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
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
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : entries.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No synthesis records yet. Start a synthesis run to populate the corpus.
              </div>
            ) : (
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
                          <code className="text-sm font-mono font-semibold">{entry.func_name}</code>
                          <Badge variant="secondary" data-testid={`badge-pass-${entry.func_name}`}>
                            {entry.passed}/{entry.total} ({passPercentage(entry.passed, entry.total)})
                          </Badge>
                          <Badge variant="outline">Score: {entry.score.toFixed(4)}</Badge>
                          {entry.complexity !== undefined && entry.complexity >= 0 && (
                            <Badge variant="outline">AST: {entry.complexity}</Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 font-mono">
                          {entry.func_signature}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(entry.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => copySnippet(entry.snippet)}
                        data-testid={`button-copy-${entry.func_name}`}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="relative">
                      <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-h-60 overflow-y-auto">
                        {entry.snippet}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
