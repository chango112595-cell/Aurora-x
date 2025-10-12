import { useQuery } from "@tanstack/react-query";
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
  Wifi
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface Task {
  id: string;
  name: string;
  status: string;
  percent: number;  // Changed from string to number to match API
  category: string;
  notes: string[];
}

interface ProgressData {
  version: string;
  updated_utc: string;
  tasks: Task[];
  active: string[];
  rules: string[];
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
      whileHover={{ scale: 1.02 }}
      data-testid={`card-task-${task.id}`}
    >
      <Card className={`h-full ${isActive ? 'ring-2 ring-primary' : ''}`}>
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-3">
          <div className="flex items-center gap-3">
            <StatusIcon status={task.status} />
            <div>
              <CardTitle className="text-lg" data-testid={`text-task-name-${task.id}`}>
                {task.name}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-xs" data-testid={`badge-task-id-${task.id}`}>
                  {task.id}
                </Badge>
                <Badge variant="outline" className="text-xs" data-testid={`badge-category-${task.id}`}>
                  {task.category}
                </Badge>
              </div>
            </div>
          </div>
          <div className="text-2xl font-bold" style={{ color }} data-testid={`text-percent-${task.id}`}>
            {task.percent}%
          </div>
        </CardHeader>
        <CardContent>
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
              <Badge className="bg-primary/10 text-primary border-primary/20" data-testid={`badge-active-${task.id}`}>
                <Activity className="h-3 w-3 mr-1" />
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
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-6 w-6 text-primary" />
            <CardTitle className="text-2xl" data-testid="text-overall-title">
              Aurora-X Project Progress
            </CardTitle>
          </div>
          <div className="text-3xl font-bold text-primary" data-testid="text-overall-percent">
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
      <CardContent>
        <div className="space-y-4">
          <div className="relative w-full h-4 bg-secondary/50 rounded-full overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary to-primary/70 rounded-full"
              initial={{ width: "0%" }}
              animate={{ width: `${totalPercent}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              data-testid="progress-overall"
            />
          </div>
          <div className="flex justify-between text-sm">
            <div className="flex items-center gap-1" data-testid="text-completed-count">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>{completedTasks} Completed</span>
            </div>
            <div className="flex items-center gap-1" data-testid="text-in-progress-count">
              <Loader2 className="h-4 w-4 text-blue-500" />
              <span>{inProgressTasks} In Progress</span>
            </div>
            <div className="flex items-center gap-1" data-testid="text-in-development-count">
              <Wrench className="h-4 w-4 text-amber-500" />
              <span>{inDevelopmentTasks} In Development</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Active tasks section
const ActiveTasksSection = ({ tasks, activeIds }: { tasks: Task[]; activeIds: string[] }) => {
  const activeTasks = tasks.filter(t => activeIds.includes(t.id));
  
  if (activeTasks.length === 0) return null;
  
  return (
    <Card className="mb-6 border-primary/20 bg-primary/5">
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
          {activeTasks.map((task) => (
            <motion.div
              key={task.id}
              className="flex items-center justify-between p-3 rounded-lg bg-background/50 hover:bg-background/70 transition-colors"
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
    refetchInterval: 5000, // Refresh every 5 seconds
    refetchIntervalInBackground: true, // Keep polling even when tab is not active
    staleTime: 4000, // Prevent excessive refetches
    retry: 3, // Number of retry attempts
    retryDelay: (attemptIndex: number) => {
      // Retry after 10 seconds if polling fails
      return attemptIndex === 0 ? 1000 : 10000;
    }
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
          className="mb-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2" data-testid="text-page-title">Aurora-X Dashboard</h1>
              <p className="text-muted-foreground" data-testid="text-page-description">
                Monitor Aurora-X task progress and development status
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Task Graph Link */}
              <a
                href="/dashboard/graph"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-lg transition-colors"
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
                <span className="font-medium">View Task Graph</span>
              </a>
              {/* Connection status indicator */}
              <AnimatePresence mode="wait">
              {connectionError ? (
                <motion.div
                  key="offline"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-2 px-3 py-1 rounded-full bg-destructive/10"
                  data-testid="badge-connection-error"
                >
                  <WifiOff className="h-4 w-4 text-destructive" />
                  <span className="text-sm text-destructive">Offline</span>
                </motion.div>
              ) : (
                <motion.div
                  key="online"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10"
                  data-testid="badge-connection-ok"
                >
                  <Wifi className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600 dark:text-green-400">Live</span>
                </motion.div>
              )}
            </AnimatePresence>
            </div>
          </div>
        </motion.div>

        <OverallProgress tasks={data.tasks} isRefetching={isRefetching} lastUpdated={lastUpdated} />
        
        {data.active && data.active.length > 0 && (
          <ActiveTasksSection tasks={data.tasks} activeIds={data.active} />
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