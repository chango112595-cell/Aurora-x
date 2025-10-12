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
  Sparkles,
  Download,
  FileCode2,
  Rocket,
  Package,
  Terminal
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

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

// Project Generation Component with Aurora-X Theme
const ProjectGenerationSection = () => {
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
      } else {
        toast({
          title: "Unable to solve",
          description: data.error || "Could not process the query. Please try a different format.",
          variant: "destructive"
        });
        setResult("");
      }
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "An unexpected error occurred while processing your query",
        variant: "destructive"
      });
      setResult("");
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
        
        {/* Add Project Generation Section */}
        <ProjectGenerationSection />
        
        {/* Add Math & Physics Solver Section */}
        <SolverSection />
        
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