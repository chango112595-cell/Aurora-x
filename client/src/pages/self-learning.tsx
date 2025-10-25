
import { useQuery, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, Zap, Play, Square, RefreshCw, Database } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface SelfLearningStatus {
  running: boolean;
  message?: string;
}

interface RecentRun {
  run_id: string;
  timestamp: string;
  score: number;
  passed: number;
  total: number;
}

export default function SelfLearning() {
  const { toast } = useToast();
  const [statusPolling, setStatusPolling] = useState(true);

  // Query for self-learning status
  const { data: status, isLoading } = useQuery<SelfLearningStatus>({
    queryKey: ["/api/self-learning/status"],
    refetchInterval: statusPolling ? 5000 : false,
    retry: 1,
  });

  // Query for recent runs
  const { data: recentRuns } = useQuery<{ runs: RecentRun[] }>({
    queryKey: ["/api/corpus/recent?limit=10"],
    refetchInterval: 10000,
  });

  // Start mutation
  const startMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/self-learning/start", {});
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Self-Learning Started",
        description: data.message || "Aurora is now learning autonomously",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/self-learning/status"] });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to Start",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Stop mutation
  const stopMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/self-learning/stop", {});
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Self-Learning Stopped",
        description: data.message || "Aurora has stopped learning",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/self-learning/status"] });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to Stop",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleStart = () => startMutation.mutate();
  const handleStop = () => stopMutation.mutate();

  return (
    <div className="h-full overflow-auto">
      <div className="p-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent">
                Self-Learning Monitor
              </h1>
              <p className="text-muted-foreground flex items-center gap-2">
                <Activity className="h-4 w-4 text-primary animate-pulse" />
                Autonomous learning and improvement
              </p>
            </div>
          </div>
        </motion.div>

        {/* Status Card */}
        <Card className="mb-6 border-primary/20 bg-gradient-to-br from-primary/10 via-background to-cyan-500/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-xl">Learning Status</CardTitle>
                  <CardDescription>
                    Current state of the self-learning daemon
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isLoading ? (
                  <Badge variant="outline">
                    <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                    Checking...
                  </Badge>
                ) : status?.running ? (
                  <Badge className="bg-green-500/10 text-green-600 border-green-500/20">
                    <Activity className="h-3 w-3 mr-1 animate-pulse" />
                    Running
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <Square className="h-3 w-3 mr-1" />
                    Stopped
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Button
                onClick={handleStart}
                disabled={status?.running || startMutation.isPending}
                className="flex-1"
              >
                {startMutation.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Start Learning
                  </>
                )}
              </Button>
              <Button
                onClick={handleStop}
                disabled={!status?.running || stopMutation.isPending}
                variant="outline"
                className="flex-1"
              >
                {stopMutation.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Stopping...
                  </>
                ) : (
                  <>
                    <Square className="mr-2 h-4 w-4" />
                    Stop Learning
                  </>
                )}
              </Button>
            </div>
            {status?.message && (
              <p className="mt-4 text-sm text-muted-foreground">{status.message}</p>
            )}
          </CardContent>
        </Card>

        {/* Recent Learning Activity */}
        <Card className="border-primary/10">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Recent Learning Activity</CardTitle>
            </div>
            <CardDescription>
              Latest synthesis runs from the self-learning daemon
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentRuns?.runs && recentRuns.runs.length > 0 ? (
              <div className="space-y-3">
                {recentRuns.runs.map((run) => (
                  <div
                    key={run.run_id}
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors"
                  >
                    <div>
                      <code className="text-sm font-mono font-semibold">
                        {run.run_id}
                      </code>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(run.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={run.score === 1 ? "default" : "secondary"}>
                        {run.passed}/{run.total}
                      </Badge>
                      <Badge variant="outline">
                        Score: {run.score.toFixed(4)}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No learning activity yet. Start the self-learning daemon to begin.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
