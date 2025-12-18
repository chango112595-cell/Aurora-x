import { ErrorBoundary } from '@/components/error-boundary';
import { useEffect, useState, useRef } from "react";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Loader2, Clock, Zap, AlertCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

export type SynthesisStage =
  | "QUEUED"
  | "ANALYZING"
  | "GENERATING"
  | "TESTING"
  | "COMPLETE"
  | "ERROR";

interface ProgressData {
  id: string;
  stage: SynthesisStage;
  percentage: number;
  message: string;
  estimatedTimeRemaining: number;
  startedAt: string;
  updatedAt: string;
  completedAt?: string;
  error?: string;
  complexity?: "simple" | "medium" | "complex";
  actualDuration?: number;
}

interface SynthesisProgressProps {
  synthesisId: string;
  onComplete?: (data: ProgressData) => void;
  hideOnComplete?: boolean;
  className?: string;
}

export function SynthesisProgress({
  synthesisId,
  onComplete,
  hideOnComplete = false,
  className = ""
}: SynthesisProgressProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const completedRef = useRef(false);

  // Polling fallback using React Query
  const { data: polledData } = useQuery<ProgressData>({
    queryKey: [`/api/synthesis/progress/${synthesisId}`],
    refetchInterval: progressData?.stage === "COMPLETE" ? false : 2000,
    enabled: !isConnected && !!synthesisId,
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!synthesisId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/synthesis`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected for synthesis progress');
        setIsConnected(true);
        ws.send(JSON.stringify({
          type: 'subscribe',
          synthesisId
        }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'progress' && message.data) {
            setProgressData(message.data);

            if (message.data.stage === 'COMPLETE' && !completedRef.current) {
              completedRef.current = true;
              if (onComplete) {
                onComplete(message.data);
              }
            }
          }
        } catch (error) {
          console.error('[WebSocket] Error parsing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
      };

      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);

      return () => {
        clearInterval(pingInterval);
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'unsubscribe',
            synthesisId
          }));
          ws.close();
        }
        wsRef.current = null;
      };
    } catch (error) {
      console.error('[WebSocket] Failed to connect:', error);
      setIsConnected(false);
    }
  }, [synthesisId, onComplete]);

  // Use WebSocket data if available, otherwise use polled data
  const currentData = progressData || polledData;

  // Handle completion from polling
  useEffect(() => {
    if (polledData?.stage === 'COMPLETE' && !completedRef.current) {
      completedRef.current = true;
      if (onComplete) {
        onComplete(polledData);
      }
    }
  }, [polledData, onComplete]);

  if (!currentData) {
    return (
      <Card className={`${className}`} data-testid="card-synthesis-progress">
        <CardHeader>
          <CardTitle>Initializing Synthesis...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <span className="text-sm">Starting synthesis process...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (hideOnComplete && currentData.stage === "COMPLETE") {
    return null;
  }

  const getStageIcon = (stage: SynthesisStage) => {
    switch (stage) {
      case "QUEUED":
        return <Clock className="h-5 w-5 text-muted-foreground" />;
      case "ANALYZING":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      case "GENERATING":
        return <Zap className="h-5 w-5 text-yellow-500 animate-pulse" />;
      case "TESTING":
        return <Loader2 className="h-5 w-5 animate-spin text-purple-500" />;
      case "COMPLETE":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "ERROR":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const stages: Array<{ name: SynthesisStage, label: string, description: string }> = [
    { name: "QUEUED", label: "Queued", description: "Request received and queued" },
    { name: "ANALYZING", label: "Analyzing", description: "Understanding requirements" },
    { name: "GENERATING", label: "Generating", description: "Creating code solution" },
    { name: "TESTING", label: "Testing", description: "Running validation tests" },
    { name: "COMPLETE", label: "Complete", description: "Synthesis finished" },
  ];

  const getStageStatus = (stageName: SynthesisStage): "completed" | "in-progress" | "pending" => {
    const stageOrder = ["QUEUED", "ANALYZING", "GENERATING", "TESTING", "COMPLETE"];
    const currentIndex = stageOrder.indexOf(currentData.stage);
    const stageIndex = stageOrder.indexOf(stageName);

    if (stageIndex < currentIndex) return "completed";
    if (stageIndex === currentIndex) return "in-progress";
    return "pending";
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)} second${seconds !== 1 ? 's' : ''}`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (remainingSeconds === 0) {
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
    return `${minutes}m ${Math.round(remainingSeconds)}s`;
  };

  return (
    <Card className={`${className} border-cyan-500/30 bg-gradient-to-br from-background via-cyan-950/10 to-background relative overflow-hidden`} data-testid="card-synthesis-progress">
      {/* Holographic scanning effect */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent top-0 animate-scan" />
      </div>

      {/* Corner glow effects */}
      <div className="absolute top-0 left-0 w-16 h-16 bg-gradient-to-br from-cyan-500/20 to-transparent blur-xl pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-16 h-16 bg-gradient-to-tl from-purple-500/20 to-transparent blur-xl pointer-events-none" />

      <CardHeader>
        <div className="flex items-center justify-between relative z-10">
          <CardTitle className="flex items-center gap-2">
            <div className="w-1 h-6 bg-gradient-to-b from-cyan-500 to-purple-500 rounded-full animate-pulse" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400">
              Synthesis Progress
            </span>
          </CardTitle>
          <div className="flex items-center gap-2">
            {currentData.complexity && (
              <Badge variant="outline" className="text-xs border-cyan-500/50 bg-cyan-500/10 text-cyan-300">
                {currentData.complexity}
              </Badge>
            )}
            {currentData.stage === "COMPLETE" ? (
              <Badge variant="secondary" className="gap-1 bg-green-500/20 text-green-300 border-green-500/50">
                <CheckCircle2 className="h-3 w-3" />
                Complete
              </Badge>
            ) : currentData.stage === "ERROR" ? (
              <Badge variant="destructive" className="gap-1 bg-red-500/20 text-red-300 border-red-500/50">
                <AlertCircle className="h-3 w-3" />
                Error
              </Badge>
            ) : (
              <Badge variant="secondary" className="gap-1 bg-cyan-500/20 text-cyan-300 border-cyan-500/50">
                <Loader2 className="h-3 w-3 animate-spin" />
                Running
              </Badge>
            )}
            {isConnected && (
              <Badge variant="outline" className="text-xs gap-1 border-green-500/50 bg-green-500/10 text-green-300">
                <div className="w-2 h-2 bg-green-400 rounded-full shadow-lg shadow-green-500/50" style={{ animation: 'pulse 1s ease-in-out infinite' }} />
                Live
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-cyan-300/70 font-mono">Overall Progress</span>
            <div className="flex items-center gap-2">
              <span className="font-bold text-cyan-400 text-lg tabular-nums" data-testid="text-progress-percentage">
                {currentData.percentage}%
              </span>
              {currentData.estimatedTimeRemaining > 0 && currentData.stage !== "COMPLETE" && (
                <span className="text-xs text-cyan-300/50 font-mono">
                  (~{formatTime(currentData.estimatedTimeRemaining)} remaining)
                </span>
              )}
            </div>
          </div>
          <div className="relative">
            <Progress value={currentData.percentage} className="h-3 bg-cyan-950/30" data-testid="progress-bar" />
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-cyan-500 rounded-full transition-all duration-300"
              style={{
                width: `${currentData.percentage}%`,
                boxShadow: '0 0 20px rgba(6, 182, 212, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3)'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
            </div>
          </div>
        </div>

        <div className="space-y-3">
          {stages.map((stage) => {
            const status = getStageStatus(stage.name);
            return (
              <div key={`stage-${stage.name}`} className="flex items-start gap-3" data-testid={`stage-${stage.name.toLowerCase()}`}>
                <div className="mt-0.5">
                  {status === "completed" ? (
                    <CheckCircle2 className="h-5 w-5 text-chart-2" />
                  ) : status === "in-progress" ? (
                    getStageIcon(stage.name)
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium">{stage.label}</p>
                  <p className="text-xs text-muted-foreground">
                    {stage.name === currentData.stage ? currentData.message : stage.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {currentData.stage === "COMPLETE" && currentData.actualDuration && (
          <div className="text-sm text-muted-foreground pt-2 border-t">
            Completed in {formatTime(currentData.actualDuration)}
          </div>
        )}

        {currentData.stage === "ERROR" && currentData.error && (
          <div className="text-sm text-destructive pt-2 border-t">
            Error: {currentData.error}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
