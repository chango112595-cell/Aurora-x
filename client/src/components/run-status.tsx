import { ErrorBoundary } from '@/components/error-boundary';
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Activity, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { format } from "date-fns";
import type { RunMeta, UsedSeed } from "@shared/schema";

interface RunMetaResponse {
  meta: RunMeta | null;
}

interface UsedSeedsResponse {
  seeds: UsedSeed[];
}

export function RunStatus() {
  const { data: metaData, isLoading: metaLoading } = useQuery<RunMetaResponse>({
    queryKey: ["/api/run-meta/latest"],
  });

  const runId = metaData?.meta?.run_id;

  const { data: seedsData, isLoading: seedsLoading } = useQuery<UsedSeedsResponse>({
    queryKey: ["/api/used-seeds", runId],
    enabled: !!runId,
  });

  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (metaLoading) {
    return (
      <Card className="border-primary/20" data-testid="card-run-status-loading">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Aurora Run Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8" data-testid="loading-run-status">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!metaData?.meta) {
    return (
      <Card className="border-muted" data-testid="card-run-status-empty">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-muted-foreground" />
            Aurora Run Status
          </CardTitle>
          <CardDescription>No synthesis runs detected yet</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const meta = metaData.meta;
  const seeds = seedsData?.seeds || [];

  return (
    <div className="space-y-4">
      <Card className="border-primary/20" data-testid="card-run-status">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Latest Run: {meta.run_id}
          </CardTitle>
          <CardDescription>
            {format(new Date(meta.timestamp), "PPpp")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div data-testid="run-meta-seed-bias">
              <div className="text-sm text-muted-foreground">Seed Bias</div>
              <div className="text-lg font-semibold">{(meta.seed_bias * 100).toFixed(0)}%</div>
            </div>
            <div data-testid="run-meta-seeding-enabled">
              <div className="text-sm text-muted-foreground">Seeding</div>
              <div className="text-lg font-semibold">
                {meta.seeding_enabled ? (
                  <Badge variant="default" className="text-xs">Enabled</Badge>
                ) : (
                  <Badge variant="secondary" className="text-xs">Disabled</Badge>
                )}
              </div>
            </div>
            <div data-testid="run-meta-max-iters">
              <div className="text-sm text-muted-foreground">Max Iters</div>
              <div className="text-lg font-semibold">{meta.max_iters}</div>
            </div>
            {meta.beam && (
              <div data-testid="run-meta-beam">
                <div className="text-sm text-muted-foreground">Beam</div>
                <div className="text-lg font-semibold">{meta.beam}</div>
              </div>
            )}
          </div>
          {meta.notes && (
            <div className="mt-4 pt-4 border-t" data-testid="run-meta-notes">
              <div className="text-sm text-muted-foreground mb-1">Notes</div>
              <div className="text-sm">{meta.notes}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {seedsLoading ? (
        <Card data-testid="card-used-seeds-loading">
          <CardHeader>
            <CardTitle>Used Seeds</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-8" data-testid="loading-used-seeds">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      ) : seeds.length > 0 ? (
        <Card data-testid="card-used-seeds">
          <CardHeader>
            <CardTitle>Used Seeds ({seeds.length})</CardTitle>
            <CardDescription>Functions where Aurora selected seed snippets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {seeds.map((seed: any, idx: number) => (
                <div
                  key={seed.id || `seed-${idx}`}
                  className="p-3 rounded-lg border hover-elevate"
                  data-testid={`seed-${idx}`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex-1">
                      <div className="font-mono font-semibold text-sm" data-testid={`seed-function-${idx}`}>
                        {seed.function}
                      </div>
                      <div className="text-xs text-muted-foreground" data-testid={`seed-timestamp-${idx}`}>
                        {format(new Date(seed.timestamp), "PPpp")}
                      </div>
                    </div>
                    {seed.score !== null && seed.score !== undefined && (
                      <Badge variant="secondary" className="text-xs" data-testid={`seed-score-${idx}`}>
                        Score: {seed.score.toFixed(2)}
                      </Badge>
                    )}
                  </div>

                  {seed.source_id && (
                    <div className="text-xs text-muted-foreground mb-1" data-testid={`seed-source-${idx}`}>
                      Source: {seed.source_id}
                    </div>
                  )}

                  {seed.reason && (
                    <div className="text-xs mt-2 p-2 bg-muted/50 rounded" data-testid={`seed-reason-${idx}`}>
                      <span className="font-semibold">Reason:</span>{" "}
                      {JSON.stringify(seed.reason, null, 2)}
                    </div>
                  )}

                  {seed.snippet && (
                    <div className="mt-2 relative">
                      <pre className="text-xs bg-background border rounded p-2 overflow-x-auto font-mono" data-testid={`seed-snippet-${idx}`}>
                        {seed.snippet}
                      </pre>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="absolute top-1 right-1 h-6 w-6"
                        onClick={() => handleCopy(seed.snippet, `snippet-${idx}`)}
                        data-testid={`button-copy-snippet-${idx}`}
                      >
                        {copiedId === `snippet-${idx}` ? (
                          <Check className="h-3 w-3" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
