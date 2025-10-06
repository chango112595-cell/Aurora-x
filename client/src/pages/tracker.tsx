import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export default function Tracker() {
  const [progressData, setProgressData] = useState<any>(null);
  const [taskId, setTaskId] = useState("");
  const [taskValue, setTaskValue] = useState("");
  const { toast } = useToast();

  // Load progress data
  useEffect(() => {
    fetchProgress();
    const interval = setInterval(fetchProgress, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await fetch("/api/progress");
      if (response.ok) {
        const data = await response.json();
        setProgressData(data);
      }
    } catch (error) {
      console.error("Failed to fetch progress:", error);
    }
  };

  const updateTask = async () => {
    if (!taskId || !taskValue) {
      toast({
        title: "Error",
        description: "Please provide both Task ID and value",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch("/api/progress/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [taskId]: taskValue }),
      });
      
      if (response.ok) {
        toast({
          title: "Success",
          description: `Updated ${taskId}`,
        });
        setTaskId("");
        setTaskValue("");
        fetchProgress();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update task",
        variant: "destructive",
      });
    }
  };

  const calculatePhaseProgress = (phase: any) => {
    if (!phase.tasks) return 0;
    let totalWeight = 0;
    let weightedSum = 0;
    
    for (const task of phase.tasks) {
      const weight = task.subtasks ? task.subtasks.length : 1;
      const progress = task.subtasks 
        ? task.subtasks.reduce((sum: number, sub: any) => sum + (sub.progress || 0), 0) / task.subtasks.length
        : (task.progress || 0);
      weightedSum += progress * weight;
      totalWeight += weight;
    }
    
    return totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0;
  };

  const overallProgress = progressData?.phases 
    ? Math.round(progressData.phases.reduce((sum: number, phase: any) => {
        const weight = phase.tasks?.length || 1;
        return sum + calculatePhaseProgress(phase) * weight;
      }, 0) / progressData.phases.reduce((sum: number, phase: any) => sum + (phase.tasks?.length || 1), 0))
    : 0;

  return (
    <div className="relative min-h-screen p-8">
      {/* Floating HUD - Fixed position at top right */}
      <div className="fixed top-4 right-4 z-50">
        <Card className="p-4 bg-background/95 backdrop-blur-sm border-primary/20 shadow-lg w-80">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-lg">Aurora Tracker</h3>
              <span className="text-2xl font-bold text-primary">{overallProgress}%</span>
            </div>
            
            {/* Progress Chart SVG */}
            <div className="bg-secondary/20 p-3 rounded-md">
              <svg viewBox="0 0 160 40" width="160" height="40">
                <path
                  d={`M 0,35 ${[...Array(12)].map((_, i) => {
                    const x = i * (160 / 11);
                    const y = 35 - (Math.random() * 30);
                    return `L ${x},${y}`;
                  }).join(' ')}`}
                  fill="none"
                  stroke="hsl(var(--primary))"
                  strokeWidth="2"
                />
              </svg>
            </div>

            {/* Update Form */}
            <div className="space-y-2">
              <Input
                placeholder="Task ID (e.g., T02f)"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
                className="h-8"
                data-testid="input-task-id"
              />
              <Input
                placeholder="Value (75, auto, or +5)"
                value={taskValue}
                onChange={(e) => setTaskValue(e.target.value)}
                className="h-8"
                data-testid="input-task-value"
              />
              <Button
                onClick={updateTask}
                className="w-full h-8"
                variant="default"
                data-testid="button-update-task"
              >
                Update Task
              </Button>
            </div>

            <div className="text-xs text-muted-foreground">
              Enter task ID and value to update progress. Use 'auto' to calculate from subtasks.
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">🎯 Aurora-X Task Tracker</h1>
        
        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {progressData?.phases?.map((phase: any) => {
            const phaseProgress = calculatePhaseProgress(phase);
            const statusEmoji = phaseProgress >= 100 ? "✅" : phaseProgress > 0 ? "🚀" : "⏳";
            
            return (
              <Card key={phase.id} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">{phase.name}</h3>
                  <span className="text-2xl">{statusEmoji}</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{phase.id}</span>
                    <span className="font-bold">{phaseProgress}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary rounded-full h-2 transition-all"
                      style={{ width: `${phaseProgress}%` }}
                    />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Detailed Task List */}
        <Card className="p-6">
          <h2 className="text-2xl font-semibold mb-6">Task Breakdown</h2>
          <div className="space-y-6">
            {progressData?.phases?.map((phase: any) => (
              <div key={phase.id}>
                <h3 className="text-lg font-semibold mb-3">{phase.name}</h3>
                <div className="space-y-2 ml-4">
                  {phase.tasks?.map((task: any) => (
                    <div key={task.id} className="space-y-1">
                      <div className="flex items-center justify-between p-2 bg-secondary/20 rounded">
                        <span className="font-medium">{task.name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-muted-foreground">{task.id}</span>
                          <span className="font-bold">{task.progress || 0}%</span>
                        </div>
                      </div>
                      {task.subtasks?.map((subtask: any) => (
                        <div key={subtask.id} className="flex items-center justify-between p-2 ml-4 bg-secondary/10 rounded">
                          <span className="text-sm">{subtask.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">{subtask.id}</span>
                            <span className="text-sm font-medium">{subtask.progress || 0}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}