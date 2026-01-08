import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getRoadmapProgress, getRoadmapSummary, getEvolutionLog, getQueuedApprovals, runNextPhase, approveChange } from "@/lib/roadmap-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, RefreshCw, Check, AlertCircle, Loader2, Activity, Layers, Users } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ProgressData {
  phase: number;
  status: string;
  last_update?: string;
}

interface SummaryData {
  current_phase: number;
  status: string;
  modules_count: number;
  knowledge_snapshot: boolean;
  evolution_log_entries: number;
  timestamp?: string;
}

interface EvolutionEntry {
  timestamp: string;
  reason?: string;
  metrics?: Record<string, unknown>;
  queued?: Array<{ target: string; proposal: string; requires_approval: boolean }>;
}

interface QueuedApproval {
  target: string;
  proposal: string;
  requires_approval: boolean;
}

export default function RoadmapPage() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [isRunning, setIsRunning] = useState(false);
  const [queued, setQueued] = useState<QueuedApproval[]>([]);

  const { data: progressRes, isLoading: progressLoading } = useQuery({
    queryKey: ["roadmap", "progress"],
    queryFn: getRoadmapProgress,
    refetchInterval: 5000
  });

  const { data: summaryRes, isLoading: summaryLoading } = useQuery({
    queryKey: ["roadmap", "summary"],
    queryFn: getRoadmapSummary,
    refetchInterval: 15000
  });

  const { data: evoRes, isLoading: evoLoading } = useQuery({
    queryKey: ["evolution", "log"],
    queryFn: getEvolutionLog,
    refetchInterval: 15000
  });

  useEffect(() => {
    getQueuedApprovals().then(r => setQueued(r.queued || [])).catch(() => {});
  }, []);


  const onRunNext = async () => {
    setIsRunning(true);
    try {
      const result = await runNextPhase();
      if (result.ok) {
        toast({ title: "Phase Triggered", description: "Running next roadmap phase..." });
        qc.invalidateQueries({ queryKey: ["roadmap", "progress"] });
      } else {
        toast({ title: "Error", description: result.error || "Failed to trigger phase", variant: "destructive" });
      }
    } catch {
      toast({ title: "Error", description: "Failed to connect to server", variant: "destructive" });
    }
    setIsRunning(false);
  };

  const onApprove = async (target: string) => {
    try {
      const result = await approveChange(target);
      if (result.ok) {
        toast({ title: "Approved", description: `Applied: ${target}` });
        setQueued(prev => prev.filter(q => q.target !== target));
        qc.invalidateQueries({ queryKey: ["evolution", "log"] });
      } else {
        toast({ title: "Error", description: result.error || "Failed to approve", variant: "destructive" });
      }
    } catch {
      toast({ title: "Error", description: "Failed to approve change", variant: "destructive" });
    }
  };

  const progress: ProgressData = progressRes?.data || { phase: 0, status: "unknown" };
  const summary: SummaryData = summaryRes?.data || { current_phase: 0, status: "unknown", modules_count: 0, knowledge_snapshot: false, evolution_log_entries: 0 };
  const entries: EvolutionEntry[] = evoRes?.entries || [];

  const getStatusBadge = (status: string) => {
    if (status === "complete") return <Badge variant="default" className="bg-green-600" data-testid="badge-status-complete">Complete</Badge>;
    if (status === "pending") return <Badge variant="secondary" data-testid="badge-status-pending">Pending</Badge>;
    return <Badge variant="outline" data-testid="badge-status-unknown">{status}</Badge>;
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Aurora Roadmap Dashboard</h1>
          <p className="text-muted-foreground">Autonomous progress tracking and phase management</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => qc.invalidateQueries({ queryKey: ["roadmap"] })}
            data-testid="button-refresh"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button
            onClick={onRunNext}
            disabled={isRunning}
            data-testid="button-run-next"
          >
            {isRunning ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
            Run Next Phase
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card data-testid="card-phase">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Phase</CardTitle>
            <Activity className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {progressLoading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <>
                <div className="text-3xl font-bold" data-testid="text-phase-number">{progress.phase}</div>
                <div className="flex items-center gap-2 mt-1">
                  {getStatusBadge(progress.status)}
                  {progress.last_update && (
                    <span className="text-xs text-muted-foreground">
                      Updated: {new Date(progress.last_update).toLocaleTimeString()}
                    </span>
                  )}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card data-testid="card-modules">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Modules</CardTitle>
            <Layers className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <>
                <div className="text-3xl font-bold" data-testid="text-modules-count">{summary.modules_count}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Knowledge: {summary.knowledge_snapshot ? "Active" : "Pending"}
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card data-testid="card-workers">
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Workers</CardTitle>
            <Users className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" data-testid="text-workers-count">400</div>
            <p className="text-xs text-muted-foreground mt-1">300 tasks / 100 healers</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card data-testid="card-evolution-log">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Evolution Log
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {evoLoading ? (
                <div className="flex justify-center p-4">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
              ) : entries.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">No evolution entries yet</p>
              ) : (
                entries.slice().reverse().slice(0, 20).map((e, idx) => (
                  <div key={idx} className="p-3 border rounded-md hover-elevate" data-testid={`evolution-entry-${idx}`}>
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-xs text-muted-foreground">
                        {e.timestamp ? new Date(e.timestamp).toLocaleString() : "—"}
                      </span>
                      {e.reason && <Badge variant="outline">{e.reason}</Badge>}
                    </div>
                    {e.metrics && (
                      <pre className="text-xs mt-2 p-2 bg-muted rounded overflow-x-auto">
                        {JSON.stringify(e.metrics, null, 2)}
                      </pre>
                    )}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card data-testid="card-approvals">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Queued Approvals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {queued.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                  <Check className="w-8 h-8 mb-2" />
                  <p>No pending approvals</p>
                </div>
              ) : (
                queued.map((q, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border rounded-md" data-testid={`approval-item-${i}`}>
                    <div className="flex-1">
                      <div className="font-medium">{q.target}</div>
                      {q.proposal && <p className="text-sm text-muted-foreground">{q.proposal}</p>}
                    </div>
                    <Button
                      size="sm"
                      onClick={() => onApprove(q.target)}
                      data-testid={`button-approve-${i}`}
                    >
                      <Check className="w-4 h-4 mr-1" />
                      Approve
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card data-testid="card-phase-timeline">
        <CardHeader>
          <CardTitle>Phase Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 flex-wrap">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(phase => (
              <div
                key={phase}
                className={`flex items-center justify-center w-12 h-12 rounded-full border-2 font-bold ${
                  phase < progress.phase
                    ? "bg-green-600 border-green-600 text-white"
                    : phase === progress.phase
                    ? "bg-primary border-primary text-primary-foreground"
                    : "bg-muted border-muted-foreground/30 text-muted-foreground"
                }`}
                data-testid={`phase-indicator-${phase}`}
              >
                {phase < progress.phase ? <Check className="w-5 h-5" /> : phase}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
