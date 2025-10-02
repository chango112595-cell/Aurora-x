import { AuroraStatus } from "@/components/aurora-status";
import { SynthesisProgress } from "@/components/synthesis-progress";
import { CodePreview } from "@/components/code-preview";

export default function Dashboard() {
  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Aurora Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor synthesis engine status and real-time code generation
          </p>
        </div>

        <AuroraStatus />

        <div className="grid gap-6 lg:grid-cols-2">
          <SynthesisProgress />
          <CodePreview />
        </div>
      </div>
    </div>
  );
}
