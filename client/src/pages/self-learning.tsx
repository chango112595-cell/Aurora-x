import { useQuery, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, Zap, Play, Square, RefreshCw, Database, Settings, Clock, Moon, Sun } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

interface SelfLearningStatus {
  running: boolean;
  message?: string;
  stats?: {
    started_at: string | null;
    last_activity: string | null;
    run_count: number;
  };
}

interface RecentRun {
  run_id: string;
  timestamp: string;
  score: number;
  passed: number;
  total: number;
}

interface LearningSettings {
  autoStart: boolean;
  sleepInterval: number; // minutes
  wakeTime: string; // HH:MM format
  sleepTime: string; // HH:MM format
  enableSchedule: boolean;
}

const DEFAULT_SETTINGS: LearningSettings = {
  autoStart: true, // Always auto-start
  sleepInterval: 15, // Default: 15 seconds. UI allows minimum interval down to 5 seconds.
  wakeTime: "00:00", // Run 24/7
  sleepTime: "23:59", // Run 24/7
  enableSchedule: false, // Disabled - run continuously
};

export default function SelfLearning() {
  const { toast } = useToast();
  const [statusPolling, setStatusPolling] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [manualStop, setManualStop] = useState(false);
  const manualStopRef = useRef(false); // Use ref to track manual stop immediately
  const [settings, setSettings] = useState<LearningSettings>(() => {
    const saved = localStorage.getItem("aurora-learning-settings");
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("aurora-learning-settings", JSON.stringify(settings));
  }, [settings]);

  // Query for self-learning status
  const { data: status, isLoading, refetch } = useQuery<SelfLearningStatus>({
    queryKey: ["/api/self-learning/status"],
    refetchInterval: statusPolling ? 5000 : false,
    retry: 1,
  });

  // Auto-start on mount and keep running continuously
  useEffect(() => {
    // Always try to start if not running (unless user manually stopped it)
    // Use ref to avoid race conditions with state updates
    if (status && !status.running && !isLoading && !manualStopRef.current) {
      // Check if we're within wake hours if schedule is enabled
      if (settings.enableSchedule) {
        const now = new Date();
        const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

        if (currentTime >= settings.wakeTime && currentTime < settings.sleepTime) {
          startMutation.mutate();
        }
      } else {
        // Run continuously by default
        startMutation.mutate();
      }
    }
  }, [status, isLoading, settings.enableSchedule, settings.wakeTime, settings.sleepTime]);

  // Schedule-based sleep/wake cycle
  useEffect(() => {
    if (!settings.enableSchedule || !status?.running) return;

    const checkSchedule = () => {
      const now = new Date();
      const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

      // Stop if past sleep time
      if (currentTime >= settings.sleepTime || currentTime < settings.wakeTime) {
        if (status.running) {
          stopMutation.mutate();
          toast({
            title: "Aurora is Sleeping",
            description: `Stopped for the night. Will resume at ${settings.wakeTime}`,
          });
        }
      }
    };

    const interval = setInterval(checkSchedule, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [settings.enableSchedule, settings.sleepTime, settings.wakeTime, status]);

  // Query for recent runs
  const { data: recentRuns } = useQuery<{ runs: RecentRun[] }>({
    queryKey: ["/api/corpus/recent?limit=10"],
    refetchInterval: 10000,
  });

  // Start mutation
  const startMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/self-learning/start", {
        sleepInterval: settings.sleepInterval,
      });
      
      // Handle "already running" error gracefully - return success without throwing
      if (response.status === 400) {
        const data = await response.json();
        if (data.error === "Already running") {
          // Treat "already running" as success - just return a flag
          return { status: "started", message: "Self-learning daemon is already running", alreadyRunning: true };
        }
      }
      
      // For other errors or success, parse normally
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || "Failed to start learning");
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      // Clear manual stop flag and update UI (both ref and state)
      manualStopRef.current = false;
      setManualStop(false);
      updateSetting("autoStart", true);
      queryClient.invalidateQueries({ queryKey: ["/api/self-learning/status"] });
      
      // Only show toast for actual starts, not for "already running"
      if (!data.alreadyRunning) {
        toast({
          title: "Self-Learning Started",
          description: data.message || "Aurora is now learning autonomously",
        });
      }
    },
    onError: (error: any) => {
      // Only show error for actual failures
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
      // Set BOTH ref and state immediately to prevent race conditions
      manualStopRef.current = true;
      setManualStop(true);
      updateSetting("autoStart", false);
      
      const response = await apiRequest("POST", "/api/self-learning/stop", {});
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Self-Learning Stopped",
        description: data.message || "Aurora has stopped learning",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/self-learning/status"] });
      // Flags already set in mutationFn
    },
    onError: (error: any) => {
      // If stop failed, revert the flags
      manualStopRef.current = false;
      setManualStop(false);
      updateSetting("autoStart", true);
      
      toast({
        title: "Failed to Stop",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleStart = () => {
    // Update auto-start setting immediately when user clicks start/resume
    manualStopRef.current = false;
    setSettings((prev) => ({ ...prev, autoStart: true }));
    startMutation.mutate();
  };
  const handleStop = () => stopMutation.mutate();

  const updateSetting = <K extends keyof LearningSettings>(
    key: K,
    value: LearningSettings[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

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

        {/* Settings Card */}
        <Card className="mb-6 border-primary/10">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg">Learning Settings</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
              >
                {showSettings ? "Hide" : "Show"}
              </Button>
            </div>
          </CardHeader>
          {showSettings && (
            <CardContent className="space-y-6">
              {/* Auto-Start */}
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">Auto-Start Learning</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically start Aurora when the page loads
                  </p>
                </div>
                <Switch
                  checked={settings.autoStart}
                  onCheckedChange={(checked) => {
                    updateSetting("autoStart", checked);
                    // Clear manual stop flag when user changes auto-start setting
                    if (checked) {
                      manualStopRef.current = false;
                      setManualStop(false);
                    }
                  }}
                />
              </div>

              <Separator />

              {/* Sleep Interval */}
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Sleep Interval (seconds)
                </Label>
                <Input
                  type="number"
                  min="5"
                  max="3600"
                  value={settings.sleepInterval}
                  onChange={(e) => updateSetting("sleepInterval", parseInt(e.target.value) || 15)}
                  className="max-w-xs"
                />
                <p className="text-xs text-muted-foreground">
                  Time between learning runs (minimum 5 seconds)
                </p>
              </div>

              <Separator />

              {/* Wake/Sleep Schedule */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">Enable Sleep Schedule</Label>
                    <p className="text-sm text-muted-foreground">
                      Aurora will only run during specified hours
                    </p>
                  </div>
                  <Switch
                    checked={settings.enableSchedule}
                    onCheckedChange={(checked) => updateSetting("enableSchedule", checked)}
                  />
                </div>

                {settings.enableSchedule && (
                  <div className="grid grid-cols-2 gap-4 pl-4 border-l-2 border-primary/20">
                    <div className="space-y-2">
                      <Label className="flex items-center gap-2">
                        <Sun className="h-4 w-4 text-yellow-500" />
                        Wake Time
                      </Label>
                      <Input
                        type="time"
                        value={settings.wakeTime}
                        onChange={(e) => updateSetting("wakeTime", e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="flex items-center gap-2">
                        <Moon className="h-4 w-4 text-purple-500" />
                        Sleep Time
                      </Label>
                      <Input
                        type="time"
                        value={settings.sleepTime}
                        onChange={(e) => updateSetting("sleepTime", e.target.value)}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Current Status */}
              {settings.enableSchedule && (
                <div className="p-3 rounded-lg bg-secondary/30 text-sm">
                  <p className="text-muted-foreground">
                    <strong>Active Hours:</strong> {settings.wakeTime} - {settings.sleepTime}
                  </p>
                  {(() => {
                    const now = new Date();
                    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                    const isActive = currentTime >= settings.wakeTime && currentTime < settings.sleepTime;
                    return (
                      <p className="mt-1">
                        <strong>Status:</strong>{" "}
                        <Badge variant={isActive ? "default" : "secondary"} className="ml-1">
                          {isActive ? "Active Period" : "Sleep Period"}
                        </Badge>
                      </p>
                    );
                  })()}
                </div>
              )}
            </CardContent>
          )}
        </Card>

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
                  <CardDescription className="flex flex-col gap-1">
                    <span>Current state of the self-learning daemon</span>
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
                {startMutation.isPending ? 'Starting...' : (manualStop ? 'Resume Learning' : (status?.running ? 'Running...' : 'Start Learning'))}
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
            {status?.stats && status.running && (
              <div className="mt-4 p-3 rounded-lg bg-secondary/30 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Started:</span>
                  <span className="font-mono">{new Date(status.stats.started_at || '').toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Last Activity:</span>
                  <span className="font-mono">{status.stats.last_activity ? new Date(status.stats.last_activity).toLocaleTimeString() : 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Runs Completed:</span>
                  <span className="font-mono font-bold text-primary">{status.stats.run_count}</span>
                </div>
              </div>
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