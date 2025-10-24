import { FunctionLibrary } from "@/components/function-library";

export default function Library() {
  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
      <div className="p-6 space-y-6 relative">
        {/* Futuristic grid background overlay */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(6, 182, 212, 0.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }} />
        </div>

        {/* Animated glow orbs */}
        <div className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse pointer-events-none" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: '1s' }} />

        <div className="relative z-10">
          <div className="mb-8 border-l-4 border-primary pl-6 py-4 bg-gradient-to-r from-primary/10 via-primary/5 to-transparent rounded-r-lg backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-ping" />
              <div className="w-2 h-2 bg-primary rounded-full animate-ping" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-primary rounded-full animate-ping" style={{ animationDelay: '0.4s' }} />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary via-cyan-400 to-primary bg-clip-text text-transparent" data-testid="text-page-title">
              Code Library
            </h1>
            <p className="text-sm text-muted-foreground mt-2 font-mono">
              <span className="text-primary">{'>'}</span> Browse and search synthesized functions
            </p>
          </div>

          <FunctionLibrary />
        </div>
      </div>
    </div>
  );
}
