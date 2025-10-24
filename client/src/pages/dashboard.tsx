import { useQuery, useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import {
  CheckCircle,
  Loader2,
  Wrench,
  Circle,
  TrendingUp,
  Activity,
  Zap,
  RefreshCw,
  WifiOff,
  Wifi,
  Database,
  AlertCircle,
  FileCode2,
  Sparkles,
  Rocket,
  Download,
  Package,
  Terminal,
  Copy,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Task {
  id: string;
  name: string;
  status: string;
  percent: number;
  category: string;
  notes: string[];
}

interface ProgressData {
  version: string;
  updated_utc: string;
  tasks: Task[];
  active: string[];
  rules: string[];
  overall_percent?: number;
}

// Synthesis/Generation interfaces
interface GenerationRequest {
  prompt: string;
}

interface GenerationResponse {
  status: "success" | "error";
  run_id?: string;
  files?: string[];
  project_type?: string;
  zip_path?: string;
  framework?: string;
  language?: string;
  features?: string[];
  message?: string;
  error?: string;
  details?: string;
}

interface GeneratedProject {
  run_id: string;
  prompt: string;
  project_type: string;
  files_count: number;
  framework?: string;
  language?: string;
  timestamp: Date;
}

// Solver interfaces
interface SolverRequest {
  q: string;  // API expects 'q' not 'query'
}

interface SolverResponse {
  ok: boolean;
  formatted?: string;
  error?: string;
  message?: string;
}

// Status mapping for cleaner processing
const parseStatus = (status: string) => {
  if (status.includes("complete")) return "complete";
  if (status.includes("in-progress")) return "in-progress";
  if (status.includes("in-development")) return "in-development";
  return "pending";
};

// Parse percentage - handles both number and string formats
const parsePercent = (percent: number | string): number => {
  if (typeof percent === 'number') return percent;
  return parseInt(percent.replace('%', '')) || 0;
};

// Color mapping for status
const getStatusColor = (status: string) => {
  const cleanStatus = parseStatus(status);
  switch(cleanStatus) {
    case "complete": return "#10b981"; // Green
    case "in-progress": return "#3b82f6"; // Blue
    case "in-development": return "#f59e0b"; // Amber
    default: return "#6b7280"; // Gray
  }
};

// Get status icon
const StatusIcon = ({ status }: { status: string }) => {
  const cleanStatus = parseStatus(status);
  const iconClass = "h-5 w-5";

  switch(cleanStatus) {
    case "complete":
      return <CheckCircle className={iconClass} style={{ color: "#10b981" }} data-testid="icon-complete" />;
    case "in-progress":
      return <Loader2 className={`${iconClass} animate-spin`} style={{ color: "#3b82f6" }} data-testid="icon-in-progress" />;
    case "in-development":
      return <Wrench className={iconClass} style={{ color: "#f59e0b" }} data-testid="icon-in-development" />;
    default:
      return <Circle className={iconClass} style={{ color: "#6b7280" }} data-testid="icon-pending" />;
  }
};

// Progress bar component with animation
const AnimatedProgress = ({ value, color }: { value: number; color: string }) => {
  return (
    <div className="relative w-full h-2 bg-secondary/50 rounded-full overflow-hidden">
      <motion.div
        className="absolute top-0 left-0 h-full rounded-full"
        style={{ backgroundColor: color }}
        initial={{ width: "0%" }}
        animate={{ width: `${value}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        data-testid="progress-bar"
      />
    </div>
  );
};

// Task card component
const TaskCard = ({ task, isActive }: { task: Task; isActive: boolean }) => {
  const status = parseStatus(task.status);
  const percent = parsePercent(task.percent);
  const color = getStatusColor(task.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02, y: -4 }}
      data-testid={`card-task-${task.id}`}
    >
      <Card className={`h-full relative overflow-hidden ${
        isActive
          ? 'border-primary/50 bg-gradient-to-br from-primary/10 via-background to-background'
          : 'border-primary/10 bg-gradient-to-br from-background to-secondary/5'
      }`}>
        {isActive && (
          <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-cyan-500/5 to-transparent animate-pulse" />
        )}
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-3 relative">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-background to-secondary/30 border border-primary/10">
              <StatusIcon status={task.status} />
            </div>
            <div>
              <CardTitle className="text-lg" data-testid={`text-task-name-${task.id}`}>
                {task.name}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-xs bg-primary/10 border-primary/20" data-testid={`badge-task-id-${task.id}`}>
                  {task.id}
                </Badge>
                <Badge variant="outline" className="text-xs border-primary/20" data-testid={`badge-category-${task.id}`}>
                  {task.category}
                </Badge>
              </div>
            </div>
          </div>
          <div className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent" data-testid={`text-percent-${task.id}`}>
            {task.percent}%
          </div>
        </CardHeader>
        <CardContent className="relative">
          <AnimatedProgress value={percent} color={color} />
          <div className="mt-3 space-y-1">
            {task.notes.map((note, idx) => (
              <div key={idx} className="text-xs text-muted-foreground flex items-start gap-1" data-testid={`text-note-${task.id}-${idx}`}>
                <span className="inline-block mt-0.5">•</span>
                <span>{note}</span>
              </div>
            ))}
          </div>
          {isActive && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3"
            >
              <Badge className="bg-gradient-to-r from-primary/20 to-cyan-500/20 text-primary border-primary/30" data-testid={`badge-active-${task.id}`}>
                <Activity className="h-3 w-3 mr-1 animate-pulse" />
                Active Now
              </Badge>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Overall progress component
const OverallProgress = ({ tasks, isRefetching, lastUpdated }: { tasks: Task[]; isRefetching: boolean; lastUpdated: Date }) => {
  // Add defensive checks
  if (!tasks || tasks.length === 0) {
    return null;
  }

  const totalPercent = tasks.reduce((acc, task) => acc + (task.percent || 0), 0) / tasks.length;
  const completedTasks = tasks.filter(t => parseStatus(t.status || "") === "complete").length;
  const inProgressTasks = tasks.filter(t => parseStatus(t.status || "") === "in-progress").length;
  const inDevelopmentTasks = tasks.filter(t => parseStatus(t.status || "") === "in-development").length;

  return (
    <Card className="mb-6 border-primary/20 bg-gradient-to-br from-primary/10 via-background to-cyan-500/5 relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,white,transparent)]" />
      <CardHeader className="relative">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/20 border border-primary/30">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl" data-testid="text-overall-title">
              Aurora-X Project Progress
            </CardTitle>
          </div>
          <div className="text-4xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent" data-testid="text-overall-percent">
            {totalPercent.toFixed(1)}%
          </div>
        </div>
        <div className="flex items-center gap-2">
          <CardDescription data-testid="text-last-updated">
            Last updated: {lastUpdated ? lastUpdated.toLocaleString() : 'Loading...'}
          </CardDescription>
          <AnimatePresence mode="wait">
            {isRefetching && (
              <motion.div
                initial={{ opacity: 0, rotate: 0 }}
                animate={{ opacity: 1, rotate: 360 }}
                exit={{ opacity: 0 }}
                transition={{
                  opacity: { duration: 0.2 },
                  rotate: { duration: 1, repeat: Infinity, ease: "linear" }
                }}
              >
                <RefreshCw className="h-4 w-4 text-muted-foreground" data-testid="icon-refreshing" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </CardHeader>
      <CardContent className="relative">
        <div className="space-y-4">
          <div className="relative w-full h-6 bg-secondary/30 rounded-full overflow-hidden border border-primary/20">
            <motion.div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary via-cyan-500 to-purple-500 rounded-full"
              initial={{ width: "0%" }}
              animate={{ width: `${totalPercent}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              data-testid="progress-overall"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
          </div>
          <div className="flex justify-between text-sm">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20" data-testid="text-completed-count">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="font-medium">{completedTasks} Completed</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20" data-testid="text-in-progress-count">
              <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
              <span className="font-medium">{inProgressTasks} In Progress</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20" data-testid="text-in-development-count">
              <Wrench className="h-5 w-5 text-amber-500" />
              <span className="font-medium">{inDevelopmentTasks} In Development</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Corpus Explorer Component with full inline content
const CorpusExplorerSection = () => {
  const [funcFilter, setFuncFilter] = useState("");
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [perfectOnly, setPerfectOnly] = useState(false);
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [maxScore, setMaxScore] = useState<number | undefined>(undefined);
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const { toast } = useToast();

  // Fetch latest run metadata
  const { data: metaData } = useQuery<{ meta: any }>({
    queryKey: ["/api/run-meta/latest"],
  });

  const buildQueryString = () => {
    const params = new URLSearchParams();
    if (funcFilter) params.set("func", funcFilter);
    params.set("limit", limit.toString());
    params.set("offset", offset.toString());
    if (perfectOnly) params.set("perfectOnly", "true");
    if (minScore !== undefined) params.set("minScore", minScore.toString());
    if (maxScore !== undefined) params.set("maxScore", maxScore.toString());
    if (startDate) {
      const normalized = new Date(startDate).toISOString();
      params.set("startDate", normalized);
    }
    if (endDate) {
      const normalized = new Date(endDate).toISOString();
      params.set("endDate", normalized);
    }
    return params.toString();
  };

  const { data: corpusData, isLoading } = useQuery<{
    items: any[];
    hasMore: boolean;
  }>({
    queryKey: [`/api/corpus?${buildQueryString()}`],
  });

  const entries = corpusData?.items || [];
  const hasMore = corpusData?.hasMore || false;
  const totalRecords = entries.length;
  const perfectRuns = entries.filter((e) => e.passed === e.total).length;
  const avgScore = entries.length > 0
    ? (entries.reduce((sum, e) => sum + e.score, 0) / entries.length).toFixed(2)
    : "0";

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

  const nextPage = () => setOffset(offset + limit);
  const prevPage = () => setOffset(Math.max(0, offset - limit));

  const resetFilters = () => {
    setFuncFilter("");
    setPerfectOnly(false);
    setMinScore(undefined);
    setMaxScore(undefined);
    setStartDate("");
    setEndDate("");
    setOffset(0);
  };

  return (
    <>
      {/* Latest Run Status */}
      {metaData?.meta && (
        <Card className="mb-6 border-primary/10 bg-gradient-to-br from-primary/5 via-background to-background">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Activity className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Latest Run</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Most recent synthesis run metadata
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <div className="text-sm text-muted-foreground">Run ID</div>
                <div className="font-mono text-sm mt-1">{metaData.meta.run_id}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Timestamp</div>
                <div className="text-sm mt-1">
                  {new Date(metaData.meta.timestamp).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Seed Bias</div>
                <div className="text-sm mt-1">{metaData.meta.seed_bias.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Max Iterations</div>
                <div className="text-sm mt-1">{metaData.meta.max_iters}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Seeding</div>
                <Badge variant={metaData.meta.seeding_enabled ? "default" : "secondary"}>
                  {metaData.meta.seeding_enabled ? "Enabled" : "Disabled"}
                </Badge>
              </div>
              {metaData.meta.beam && (
                <div>
                  <div className="text-sm text-muted-foreground">Beam Width</div>
                  <div className="text-sm mt-1">{metaData.meta.beam}</div>
                </div>
              )}
            </div>
            {metaData.meta.notes && (
              <div className="mt-4 pt-4 border-t border-primary/10">
                <div className="text-sm text-muted-foreground mb-2">Notes</div>
                <p className="text-sm">{metaData.meta.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card className="bg-secondary/30 border-primary/10">
          <CardContent className="pt-6">
            <div className="text-center">
              <Database className="h-8 w-8 mx-auto mb-2 text-chart-1" />
              <div className="text-2xl font-bold">{totalRecords}</div>
              <div className="text-xs text-muted-foreground">Total Records</div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-secondary/30 border-primary/10">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-chart-2" />
              <div className="text-2xl font-bold">{perfectRuns}</div>
              <div className="text-xs text-muted-foreground">Perfect Runs</div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-secondary/30 border-primary/10">
          <CardContent className="pt-6">
            <div className="text-center">
              <Zap className="h-8 w-8 mx-auto mb-2 text-chart-3" />
              <div className="text-2xl font-bold">{avgScore}</div>
              <div className="text-xs text-muted-foreground">Avg Score</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Corpus Records Card */}
      <Card className="mb-6 border-primary/10 bg-gradient-to-br from-primary/5 via-background to-background">
        <CardHeader>
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Database className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Synthesis Records</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Aurora's learning corpus and synthesis history
                </p>
              </div>
            </div>
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
                  className="pl-8 bg-background/50"
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setShowFilters(!showFilters)}
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
                        setMinScore(e.target.value ? Number(e.target.value) : undefined);
                        setOffset(0);
                      }}
                      className="w-24"
                      step="0.01"
                    />
                    <span className="text-muted-foreground">to</span>
                    <Input
                      type="number"
                      placeholder="Max"
                      value={maxScore ?? ""}
                      onChange={(e) => {
                        setMaxScore(e.target.value ? Number(e.target.value) : undefined);
                        setOffset(0);
                      }}
                      className="w-24"
                      step="0.01"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Date Range</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="datetime-local"
                      value={startDate}
                      onChange={(e) => {
                        setStartDate(e.target.value);
                        setOffset(0);
                      }}
                      className="flex-1"
                    />
                    <span className="text-muted-foreground">to</span>
                    <Input
                      type="datetime-local"
                      value={endDate}
                      onChange={(e) => {
                        setEndDate(e.target.value);
                        setOffset(0);
                      }}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : entries.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No synthesis records found. Adjust your filters or start a synthesis run.
            </div>
          ) : (
            <>
              <div className="space-y-3">
                {entries.map((entry) => (
                  <div
                    key={entry.id}
                    className="rounded-lg border border-primary/10 p-4 space-y-3 bg-background/50 hover:bg-background/70 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <code className="text-sm font-mono font-semibold">{entry.func_name}</code>
                          <Badge variant="secondary">
                            {entry.passed}/{entry.total} ({passPercentage(entry.passed, entry.total)})
                          </Badge>
                          <Badge variant="outline">Score: {entry.score.toFixed(4)}</Badge>
                          {entry.complexity !== undefined && entry.complexity >= 0 && (
                            <Badge variant="outline">AST: {entry.complexity}</Badge>
                          )}
                          {entry.calls_functions && entry.calls_functions.length > 0 && (
                            <Badge variant="outline">Calls: {entry.calls_functions.length}</Badge>
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
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
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

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-primary/10">
                <div className="text-sm text-muted-foreground">
                  Showing {offset + 1} - {offset + entries.length}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={prevPage}
                    disabled={offset === 0}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={nextPage}
                    disabled={!hasMore}
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
    </>
  );
};

// Removed ProjectGenerationSection - now available via chat commands

// Removed SolverSection - now available via chat commands

// Removed BridgeSection - now available via chat commands

// Removed RollbackSection - now available via chat commands

// Project Generation Component with Aurora-X Theme (REMOVED)
const ProjectGenerationSection_REMOVED = () => {
  const [prompt, setPrompt] = useState("");
  const [recentProjects, setRecentProjects] = useState<GeneratedProject[]>([]);
  const { toast } = useToast();

  // Mutation for generating projects
  const generateMutation = useMutation<GenerationResponse, Error, GenerationRequest>({
    mutationFn: async (data) => {
      const response = await apiRequest("POST", "/api/nl/compile_full", data);
      return response.json();
    },
    onSuccess: (data) => {
      if (data.status === "success") {
        toast({
          title: "Project Generated Successfully!",
          description: data.message || `Generated ${data.project_type} with ${data.files?.length || 0} files`,
        });

        // Add to recent projects
        if (data.run_id) {
          const newProject: GeneratedProject = {
            run_id: data.run_id,
            prompt: prompt.substring(0, 100),
            project_type: data.project_type || "unknown",
            files_count: data.files?.length || 0,
            framework: data.framework,
            language: data.language,
            timestamp: new Date()
          };
          setRecentProjects(prev => [newProject, ...prev.slice(0, 4)]);
          setPrompt(""); // Clear the prompt
        }
      } else {
        toast({
          title: "Generation Failed",
          description: data.error || "Failed to generate project",
          variant: "destructive"
        });
      }
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "An unexpected error occurred",
        variant: "destructive"
      });
    }
  });

  // Function to download project
  const downloadProject = (run_id: string) => {
    const downloadUrl = `/api/projects/${run_id}/download`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${run_id}-project.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast({
      title: "Download Started",
      description: `Downloading ${run_id} project...`
    });
  };

  const handleGenerate = () => {
    if (!prompt.trim()) {
      toast({
        title: "Prompt Required",
        description: "Please enter a description of the project you want to generate",
        variant: "destructive"
      });
      return;
    }

    generateMutation.mutate({ prompt: prompt.trim() });
  };

  return (
    <div className="space-y-6 mb-8">
      {/* Generation Card with Aurora-X Styling */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="relative overflow-hidden border-primary/20 bg-gradient-to-br from-primary/5 via-background to-secondary/5">
          {/* Animated Background Gradient */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10 animate-pulse" />

          <CardHeader className="relative">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl" data-testid="text-generation-title">
                  Generate Project with AI
                </CardTitle>
                <CardDescription data-testid="text-generation-description">
                  Describe your project in natural language and let Aurora-X build it for you
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="relative space-y-4">
            <Textarea
              placeholder="Describe your project... e.g., 'Create a React dashboard with user authentication and real-time data visualization'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[120px] bg-background/50 border-primary/20 focus:border-primary/40 transition-colors"
              disabled={generateMutation.isPending}
              data-testid="input-generation-prompt"
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileCode2 className="h-4 w-4" />
                <span>Supports: React, Vue, Flask, FastAPI, AI/ML, and more</span>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={generateMutation.isPending || !prompt.trim()}
                className="relative group"
                data-testid="button-generate"
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Rocket className="mr-2 h-4 w-4 group-hover:animate-pulse" />
                    Generate Project
                  </>
                )}
                {/* Hover Effect */}
                <div className="absolute inset-0 rounded-md bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              </Button>
            </div>

            {/* Generation Result */}
            {generateMutation.isSuccess && generateMutation.data?.status === "success" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-4 rounded-lg bg-green-500/10 border border-green-500/20"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <div>
                      <p className="font-medium text-green-600 dark:text-green-400">
                        Project Generated Successfully!
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {generateMutation.data.project_type} • {generateMutation.data.files?.length || 0} files
                      </p>
                    </div>
                  </div>
                  {generateMutation.data.run_id && (
                    <Button
                      onClick={() => downloadProject(generateMutation.data.run_id!)}
                      variant="outline"
                      size="sm"
                      className="border-green-500/20 hover:bg-green-500/10"
                      data-testid="button-download-latest"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  )}
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Generations */}
      {recentProjects.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="border-primary/10">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Package className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg" data-testid="text-recent-title">
                  Recent Generations
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentProjects.map((project, index) => (
                  <motion.div
                    key={project.run_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors"
                    data-testid={`item-recent-${project.run_id}`}
                  >
                    <div className="flex items-center gap-3">
                      <FileCode2 className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium text-sm" data-testid={`text-recent-prompt-${project.run_id}`}>
                          {project.prompt}...
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {project.project_type}
                          </Badge>
                          {project.framework && (
                            <Badge variant="secondary" className="text-xs">
                              {project.framework}
                            </Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {project.files_count} files • {new Date(project.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => downloadProject(project.run_id)}
                      variant="ghost"
                      size="sm"
                      className="hover:bg-primary/10"
                      data-testid={`button-download-${project.run_id}`}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

// Math & Physics Solver Component
const SolverSection = () => {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const { toast } = useToast();

  // Mutation for solving queries
  const solveMutation = useMutation<SolverResponse, Error, SolverRequest>({
    mutationFn: async (data) => {
      const response = await apiRequest("POST", "/api/solve/pretty", data);
      return response.json();
    },
    onSuccess: (data) => {
      if (data.ok && data.formatted) {
        setResult(data.formatted);
        setErrorMessage("");
      } else {
        const error = data.error || "Could not process the query. Please try a different format.";
        toast({
          title: "Unable to solve",
          description: error,
          variant: "destructive"
        });
        setResult("");
        setErrorMessage(error);
      }
    },
    onError: (error) => {
      const errorMsg = error.message || "An unexpected error occurred while processing your query";
      toast({
        title: "Error",
        description: errorMsg,
        variant: "destructive"
      });
      setResult("");
      setErrorMessage(errorMsg);
    }
  });

  const handleSolve = () => {
    if (!query.trim()) {
      toast({
        title: "Query Required",
        description: "Please enter a math or physics problem to solve",
        variant: "destructive"
      });
      return;
    }

    solveMutation.mutate({ q: query.trim() });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !solveMutation.isPending) {
      handleSolve();
    }
  };

  // Example queries for quick selection
  const exampleQueries = [
    { label: "Arithmetic", query: "2 + 3 * 4" },
    { label: "Differentiation", query: "differentiate x^3 - 2x^2 + x" },
    { label: "Orbital Period", query: "orbital period a=7e6 M=5.972e24" },
    { label: "Integration", query: "integrate x^2 + 3x + 2" },
    { label: "Quadratic", query: "solve x^2 - 5x + 6 = 0" }
  ];

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
    setResult("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="mb-8"
    >
      <Card className="relative overflow-hidden border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 via-background to-emerald-500/5">
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-transparent to-emerald-500/5 animate-pulse" />

        <CardHeader className="relative">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10">
              <Terminal className="h-6 w-6 text-cyan-500" />
            </div>
            <div>
              <CardTitle className="text-xl" data-testid="text-solver-title">
                Math & Physics Solver
              </CardTitle>
              <CardDescription data-testid="text-solver-description">
                Solve complex mathematical and physics problems instantly
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="relative space-y-4">
          {/* Input and Button */}
          <div className="flex gap-2">
            <Input
              placeholder="Try: 2+3*4 or differentiate x^3-2x^2+x or orbital period a=7e6 M=5.972e24"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 bg-background/50 border-cyan-500/20 focus:border-cyan-500/40 transition-colors"
              disabled={solveMutation.isPending}
              data-testid="input-solver-query"
            />

            <Button
              onClick={handleSolve}
              disabled={solveMutation.isPending || !query.trim()}
              className="relative group bg-cyan-500 hover:bg-cyan-600 text-white"
              data-testid="button-solve"
            >
              {solveMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Solving...
                </>
              ) : (
                <>
                  <Terminal className="mr-2 h-4 w-4 group-hover:animate-pulse" />
                  Solve
                </>
              )}
            </Button>
          </div>

          {/* Example Queries */}
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Quick examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example) => (
                <Badge
                  key={example.label}
                  variant="outline"
                  className="cursor-pointer hover:bg-cyan-500/10 hover:border-cyan-500/40 transition-colors"
                  onClick={() => handleExampleClick(example.query)}
                  data-testid={`badge-example-${example.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  {example.label}: {example.query}
                </Badge>
              ))}
            </div>
          </div>

          {/* Results Display */}
          {(result || solveMutation.isPending) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-cyan-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-cyan-600 dark:text-cyan-400 mb-2">
                      Solution:
                    </p>
                    {solveMutation.isPending ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-cyan-500" />
                        <span className="text-sm text-muted-foreground">Processing your query...</span>
                      </div>
                    ) : (
                      <p className="text-lg font-mono text-foreground" data-testid="text-solver-result">
                        {result}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Error Display */}
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div
                className="p-4 rounded-lg bg-red-500/10 border border-red-500/20"
                role="alert"
                aria-live="assertive"
                data-testid="alert-solver-error"
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-red-600 dark:text-red-400 mb-2">
                      Error:
                    </p>
                    <p className="text-sm text-foreground" data-testid="text-solver-error">
                      {errorMessage}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Capabilities Info */}
          <div className="text-xs text-muted-foreground space-y-1">
            <p>• Supports arithmetic operations, algebra, calculus, and physics calculations</p>
            <p>• Try differentiation, integration, equation solving, and orbital mechanics</p>
            <p>• Use standard mathematical notation: x^2, sqrt(x), sin(x), etc.</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Rollback Section Component for PR management
const RollbackSection = () => {
  const [response, setResponse] = useState<string>("");
  const [isLoading, setIsLoading] = useState<{ open: boolean; merged: boolean }>({ open: false, merged: false });
  const [errorMessage, setErrorMessage] = useState<string>("");
  const { toast } = useToast();

  // Handle rollback of open PR
  const handleRollbackOpen = async () => {
    setIsLoading({ ...isLoading, open: true });
    setResponse("");
    setErrorMessage("");

    try {
      const res = await apiRequest("POST", "/api/bridge/rollback/open", {});
      const data = await res.json();

      if (res.ok && data.status === "ok") {
        const message = `Successfully closed PR #${data.closed} and deleted branch ${data.deleted_branch}`;
        setResponse(JSON.stringify(data, null, 2));
        toast({
          title: "Rollback Complete",
          description: message
        });
      } else {
        const error = data.message || data.error || "Failed to rollback open PR";
        setErrorMessage(error);
        toast({
          title: "Rollback Failed",
          description: error,
          variant: "destructive"
        });
      }
    } catch (error: any) {
      const errorMsg = error.message || "Failed to connect to server";
      setErrorMessage(errorMsg);
      toast({
        title: "Connection Error",
        description: errorMsg,
        variant: "destructive"
      });
    } finally {
      setIsLoading({ ...isLoading, open: false });
    }
  };

  // Handle revert of merged PR
  const handleRollbackMerged = async () => {
    setIsLoading({ ...isLoading, merged: true });
    setResponse("");
    setErrorMessage("");

    try {
      const res = await apiRequest("POST", "/api/bridge/rollback/merged", { base: "main" });
      const data = await res.json();

      if (res.ok && (data.status === "ok" || data.revert_pr)) {
        const message = data.revert_pr
          ? `Successfully created revert PR #${data.revert_pr}`
          : "Revert PR created successfully";
        setResponse(JSON.stringify(data, null, 2));
        toast({
          title: "Revert Complete",
          description: message
        });
      } else {
        const error = data.message || data.error || "Failed to revert merged PR";
        setErrorMessage(error);
        toast({
          title: "Revert Failed",
          description: error,
          variant: "destructive"
        });
      }
    } catch (error: any) {
      const errorMsg = error.message || "Failed to connect to server";
      setErrorMessage(errorMsg);
      toast({
        title: "Connection Error",
        description: errorMsg,
        variant: "destructive"
      });
    } finally {
      setIsLoading({ ...isLoading, merged: false });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="mb-8"
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-5 w-5 text-cyan-500" />
              <CardTitle data-testid="text-rollback-title">PR Rollback Controls</CardTitle>
            </div>
            <Badge variant="outline" className="text-xs">
              GitHub Integration
            </Badge>
          </div>
          <CardDescription>
            Manage Aurora-generated pull requests - close open PRs or revert merged changes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Button
              onClick={handleRollbackOpen}
              disabled={isLoading.open || isLoading.merged}
              className="flex-1"
              variant="outline"
              data-testid="button-rollback-open"
            >
              {isLoading.open ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Rolling Back...
                </>
              ) : (
                <>
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Rollback Open PR
                </>
              )}
            </Button>

            <Button
              onClick={handleRollbackMerged}
              disabled={isLoading.open || isLoading.merged}
              className="flex-1"
              variant="outline"
              data-testid="button-revert-merged"
            >
              {isLoading.merged ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Reverting...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Revert Last Merged PR
                </>
              )}
            </Button>
          </div>

          {/* Response Display */}
          {response && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              transition={{ duration: 0.3 }}
            >
              <div className="bg-muted/50 rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Response:</span>
                  <Badge variant="secondary" className="text-xs">
                    Success
                  </Badge>
                </div>
                <pre className="text-xs text-muted-foreground overflow-x-auto" data-testid="text-rollback-response">
                  {response}
                </pre>
              </div>
            </motion.div>
          )}

          {/* Error Display */}
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              transition={{ duration: 0.3 }}
            >
              <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3">
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="h-4 w-4 text-destructive" />
                  <span className="text-sm font-medium text-destructive">Error</span>
                </div>
                <p className="text-xs text-muted-foreground" data-testid="text-rollback-error">
                  {errorMessage}
                </p>
              </div>
            </motion.div>
          )}

          {/* Help Text */}
          <div className="text-xs text-muted-foreground space-y-1">
            <p>• <strong>Rollback Open PR:</strong> Closes the latest open PR with 'aurora' label and deletes its branch</p>
            <p>• <strong>Revert Merged PR:</strong> Creates a revert PR for the latest merged PR with 'aurora' label</p>
            <p>• Requires AURORA_GH_TOKEN environment variable with repo permissions</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Loading skeleton
const DashboardSkeleton = () => {
  return (
    <div className="space-y-6">
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-32 w-full" />
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {[...Array(12)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [connectionError, setConnectionError] = useState(false);

  const { data, isLoading, error, isRefetching, refetch, isSuccess, isError } = useQuery<ProgressData>({
    queryKey: ['/api/progress'],
    refetchInterval: 10000, // Refresh every 10 seconds instead of 5
    refetchIntervalInBackground: false, // Don't poll when tab is inactive
    staleTime: 8000, // Cache data for 8 seconds
    cacheTime: 30000, // Keep cache for 30 seconds
    retry: 2, // Reduce retry attempts to speed up failure detection
    retryDelay: 1000, // Faster retry delay
    initialData: () => ({
      tasks: [],
      updated_utc: new Date().toISOString(),
      // ui_thresholds: { ok: 90, warn: 60 } // This property is not defined in ProgressData
    }), // Provide initial data to prevent loading state
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: true, // Only refetch on mount
  });

  // Watch query state and update connection status
  useEffect(() => {
    if (isSuccess && data) {
      setLastUpdated(new Date());
      setConnectionError(false);
    }
  }, [isSuccess, data]);

  useEffect(() => {
    if (isError) {
      setConnectionError(true);
    }
  }, [isError]);

  // Auto-recover when connection is restored
  useEffect(() => {
    if (connectionError) {
      const retryTimer = setTimeout(() => {
        refetch();
      }, 10000); // Retry after 10 seconds

      return () => clearTimeout(retryTimer);
    }
  }, [connectionError, refetch]);

  if (isLoading) {
    return (
      <div className="h-full overflow-auto">
        <div className="p-6">
          <h1 className="text-3xl font-bold mb-2" data-testid="text-page-title">Aurora-X Dashboard</h1>
          <p className="text-muted-foreground mb-6" data-testid="text-page-description">
            Loading task progress...
          </p>
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-full overflow-auto">
        <div className="p-6">
          <h1 className="text-3xl font-bold mb-2" data-testid="text-page-title">Aurora-X Dashboard</h1>
          <Card className="p-6 border-destructive/20">
            <div className="flex items-center gap-3 mb-4">
              <WifiOff className="h-5 w-5 text-destructive" data-testid="icon-connection-error" />
              <p className="text-destructive" data-testid="text-error">
                Connection lost. Retrying in 10 seconds...
              </p>
            </div>
            <p className="text-sm text-muted-foreground" data-testid="text-error-details">
              Unable to fetch progress data. The connection will automatically recover when restored.
            </p>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <div className="p-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 relative"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-cyan-500/10 to-purple-500/10 blur-3xl -z-10" />
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent" data-testid="text-page-title">
                Aurora-X Dashboard
              </h1>
              <p className="text-muted-foreground flex items-center gap-2" data-testid="text-page-description">
                <Activity className="h-4 w-4 text-primary animate-pulse" />
                Real-time monitoring of autonomous code synthesis
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Task Graph Link */}
              <a
                href="/dashboard/graph"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary/10 to-cyan-500/10 hover:from-primary/20 hover:to-cyan-500/20 text-primary rounded-lg transition-all border border-primary/20 hover:border-primary/40"
                data-testid="link-task-graph"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="3" />
                  <circle cx="6" cy="6" r="2" />
                  <circle cx="18" cy="6" r="2" />
                  <circle cx="6" cy="18" r="2" />
                  <circle cx="18" cy="18" r="2" />
                  <line x1="9" y1="9" x2="10.5" y2="10.5" />
                  <line x1="15" y1="9" x2="13.5" y2="10.5" />
                  <line x1="9" y1="15" x2="10.5" y2="13.5" />
                  <line x1="15" y1="15" x2="13.5" y2="13.5" />
                </svg>
                <span className="font-medium">Task Graph</span>
              </a>
              {/* Connection status indicator */}
              <AnimatePresence mode="wait">
              {connectionError ? (
                <motion.div
                  key="offline"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-2 px-3 py-2 rounded-full bg-destructive/10 border border-destructive/20"
                  data-testid="badge-connection-error"
                >
                  <WifiOff className="h-4 w-4 text-destructive" />
                  <span className="text-sm font-medium text-destructive">Offline</span>
                </motion.div>
              ) : (
                <motion.div
                  key="online"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-2 px-3 py-2 rounded-full bg-green-500/10 border border-green-500/20"
                  data-testid="badge-connection-ok"
                >
                  <Wifi className="h-4 w-4 text-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">Live</span>
                </motion.div>
              )}
            </AnimatePresence>
            </div>
          </div>
        </motion.div>

        <OverallProgress tasks={data.tasks} isRefetching={isRefetching} lastUpdated={lastUpdated} />

        {/* PR Rollback Controls Section */}
        <RollbackSection />

        {/* Corpus Explorer Section - Embedded */}
        <CorpusExplorerSection />

        {/* Active Now Section */}
        {data.active && data.active.length > 0 && (
          <Card className="mb-6 border-primary/20 bg-gradient-to-br from-primary/5 via-background to-background">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary animate-pulse" />
                <CardTitle data-testid="text-active-title">Active Now</CardTitle>
              </div>
              <CardDescription data-testid="text-active-description">
                Tasks currently being worked on
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {data.tasks.filter(t => data.active?.includes(t.id)).map((task) => (
                  <motion.div
                    key={task.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-background/50 hover:bg-background/70 transition-colors border border-primary/10"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    whileHover={{ x: 5 }}
                    data-testid={`item-active-${task.id}`}
                  >
                    <div className="flex items-center gap-3">
                      <StatusIcon status={task.status} />
                      <div>
                        <div className="font-medium" data-testid={`text-active-name-${task.id}`}>{task.name}</div>
                        <div className="text-xs text-muted-foreground" data-testid={`text-active-category-${task.id}`}>{task.category}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold" style={{ color: getStatusColor(task.status) }} data-testid={`text-active-percent-${task.id}`}>
                        {task.percent}%
                      </span>
                      <TrendingUp className="h-4 w-4 text-primary animate-pulse" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {data.tasks.map((task, index) => (
            <TaskCard
              key={task.id}
              task={task}
              isActive={data.active?.includes(task.id) || false}
            />
          ))}
        </div>
      </div>
    </div>
  );
}