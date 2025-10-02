import { FunctionLibrary } from "@/components/function-library";

export default function Library() {
  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Code Library</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse and search synthesized functions
          </p>
        </div>

        <FunctionLibrary />
      </div>
    </div>
  );
}
