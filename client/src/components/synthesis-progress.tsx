import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface SynthesisStage {
  name: string;
  status: "completed" | "in-progress" | "pending";
  description: string;
}

export function SynthesisProgress() {
  const stages: SynthesisStage[] = [
    { name: "Spec Parsing", status: "completed", description: "Analyzed function requirements" },
    { name: "Test Generation", status: "completed", description: "Created validation tests" },
    { name: "Beam Search", status: "in-progress", description: "Exploring candidate solutions" },
    { name: "Symbolic Optimization", status: "pending", description: "Applying heuristics" },
    { name: "Sandbox Testing", status: "pending", description: "Running safety checks" },
  ];

  const progress = (stages.filter(s => s.status === "completed").length / stages.length) * 100;

  return (
    <Card data-testid="card-synthesis-progress">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Synthesis Progress</CardTitle>
          <Badge variant="secondary" className="gap-1">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="font-medium" data-testid="text-progress-percentage">{progress.toFixed(0)}%</span>
          </div>
          <Progress value={progress} className="h-2" data-testid="progress-bar" />
        </div>

        <div className="space-y-3">
          {stages.map((stage, index) => (
            <div key={stage.name} className="flex items-start gap-3" data-testid={`stage-${stage.name.toLowerCase().replace(' ', '-')}`}>
              <div className="mt-0.5">
                {stage.status === "completed" && (
                  <CheckCircle2 className="h-5 w-5 text-chart-2" />
                )}
                {stage.status === "in-progress" && (
                  <Loader2 className="h-5 w-5 animate-spin text-chart-1" />
                )}
                {stage.status === "pending" && (
                  <Circle className="h-5 w-5 text-muted-foreground" />
                )}
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium">{stage.name}</p>
                <p className="text-xs text-muted-foreground">{stage.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
