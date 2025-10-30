
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Settings as SettingsIcon, Zap, Cpu, Activity } from "lucide-react";

export default function Settings() {
  const [autoSynth, setAutoSynth] = useState(true);
  const [noveltyCache, setNoveltyCache] = useState(true);
  const [beamWidth, setBeamWidth] = useState(20);
  const [maxIters, setMaxIters] = useState(1000);
  const { toast } = useToast();

  // Fetch current T08 status on page load
  const { data: t08Status, isLoading: isLoadingT08 } = useQuery<{ t08_enabled: boolean }>({
    queryKey: ["/api/t08/activate"],
    refetchOnMount: true,
  });

  // Update local state when T08 status is fetched
  useEffect(() => {
    if (t08Status) {
      setAutoSynth(t08Status.t08_enabled);
    }
  }, [t08Status]);

  // Mutation to toggle T08 activation
  const toggleT08Mutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      const response = await apiRequest("POST", "/api/t08/activate", { on: enabled });
      return response.json();
    },
    onSuccess: (data) => {
      setAutoSynth(data.t08_enabled);
      toast({
        title: "Success",
        description: data.t08_enabled 
          ? "T08 natural language synthesis activated" 
          : "T08 natural language synthesis deactivated",
      });
      // Invalidate query to ensure data stays in sync
      queryClient.invalidateQueries({ queryKey: ["/api/t08/activate"] });
    },
    onError: (error: Error) => {
      // Revert the switch state on error
      setAutoSynth(!autoSynth);
      toast({
        title: "Error",
        description: `Failed to update T08 status: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  // Handle switch toggle
  const handleAutoSynthToggle = (checked: boolean) => {
    // Immediately update the UI (optimistic update)
    setAutoSynth(checked);
    // Make the API call
    toggleT08Mutation.mutate(checked);
  };

  // Save settings function
  const handleSaveSettings = () => {
    // Save to localStorage
    const settings = {
      autoSynth,
      noveltyCache,
      beamWidth,
      maxIters,
      timestamp: Date.now()
    };
    localStorage.setItem("aurora-settings", JSON.stringify(settings));
    
    toast({
      title: "Settings Saved",
      description: "Your Aurora configuration has been saved successfully.",
    });
  };

  // Load settings from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("aurora-settings");
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        setAutoSynth(settings.autoSynth ?? true);
        setNoveltyCache(settings.noveltyCache ?? true);
        setBeamWidth(settings.beamWidth ?? 20);
        setMaxIters(settings.maxIters ?? 1000);
      } catch (error) {
        console.warn("Failed to load settings:", error);
      }
    }
  }, []);

  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
      <div className="p-6 space-y-6">
        {/* Futuristic Header */}
        <div className="relative overflow-hidden rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/20 via-primary/10 to-background p-8 shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-cyan-500/10 to-transparent animate-pulse" />
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl" />
          
          <div className="relative flex items-center gap-4">
            <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/30 to-cyan-500/30 border border-primary/40 shadow-lg">
              <SettingsIcon className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-primary bg-clip-text text-transparent" data-testid="text-page-title">
                Settings
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Configure Aurora-X synthesis parameters
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Aurora Configuration Card */}
          <Card 
            className="relative overflow-hidden border-primary/30 bg-gradient-to-br from-card via-card to-primary/5 shadow-xl hover:shadow-2xl hover:shadow-primary/20 transition-all duration-300" 
            data-testid="card-aurora-settings"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-cyan-500/5" />
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-2xl" />
            
            <CardHeader className="relative">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/20 border border-primary/30">
                  <Cpu className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-xl bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
                    Aurora Configuration
                  </CardTitle>
                  <CardDescription>Synthesis engine parameters</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 relative">
              <div className="space-y-2">
                <Label htmlFor="beam-width" className="flex items-center gap-2 font-semibold">
                  <Zap className="h-4 w-4 text-primary" />
                  Beam Width
                </Label>
                <Input
                  id="beam-width"
                  type="number"
                  min="1"
                  max="100"
                  value={beamWidth}
                  onChange={(e) => setBeamWidth(parseInt(e.target.value) || 20)}
                  className="border-primary/30 bg-background/50 backdrop-blur-sm focus:border-primary focus:ring-primary/50 transition-all"
                  data-testid="input-beam-width"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max-iters" className="flex items-center gap-2 font-semibold">
                  <Activity className="h-4 w-4 text-cyan-500" />
                  Max Iterations
                </Label>
                <Input
                  id="max-iters"
                  type="number"
                  min="10"
                  max="10000"
                  value={maxIters}
                  onChange={(e) => setMaxIters(parseInt(e.target.value) || 1000)}
                  className="border-primary/30 bg-background/50 backdrop-blur-sm focus:border-cyan-500 focus:ring-cyan-500/50 transition-all"
                  data-testid="input-max-iterations"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ast-budget" className="flex items-center gap-2 font-semibold">
                  <Cpu className="h-4 w-4 text-primary" />
                  AST Budget
                </Label>
                <Input
                  id="ast-budget"
                  type="number"
                  defaultValue="64"
                  className="border-primary/30 bg-background/50 backdrop-blur-sm focus:border-primary focus:ring-primary/50 transition-all"
                  data-testid="input-ast-budget"
                />
              </div>
            </CardContent>
          </Card>

          {/* Feature Toggles Card */}
          <Card 
            className="relative overflow-hidden border-primary/30 bg-gradient-to-br from-card via-card to-cyan-500/5 shadow-xl hover:shadow-2xl hover:shadow-cyan-500/20 transition-all duration-300"
            data-testid="card-feature-settings"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-primary/5" />
            <div className="absolute top-0 left-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl" />
            
            <CardHeader className="relative">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
                  <Zap className="h-5 w-5 text-cyan-500" />
                </div>
                <div>
                  <CardTitle className="text-xl bg-gradient-to-r from-foreground to-cyan-500 bg-clip-text text-transparent">
                    Feature Toggles
                  </CardTitle>
                  <CardDescription>Enable or disable features</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6 relative">
              <div className="flex items-center justify-between p-4 rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 to-transparent hover:from-primary/10 transition-all">
                <div className="space-y-0.5">
                  <Label htmlFor="auto-synth" className="font-semibold text-base">Auto Synthesis</Label>
                  <p className="text-xs text-muted-foreground">
                    Automatically synthesize on chat requests
                  </p>
                </div>
                <Switch
                  id="auto-synth"
                  checked={autoSynth}
                  onCheckedChange={handleAutoSynthToggle}
                  disabled={isLoadingT08 || toggleT08Mutation.isPending}
                  data-testid="switch-auto-synthesis"
                  className="data-[state=checked]:bg-primary"
                />
              </div>
              <div className="flex items-center justify-between p-4 rounded-xl border border-cyan-500/20 bg-gradient-to-r from-cyan-500/5 to-transparent hover:from-cyan-500/10 transition-all">
                <div className="space-y-0.5">
                  <Label htmlFor="novelty-cache" className="font-semibold text-base">Novelty Cache</Label>
                  <p className="text-xs text-muted-foreground">
                    Use global novelty cache (TTL+LRU)
                  </p>
                </div>
                <Switch
                  id="novelty-cache"
                  checked={noveltyCache}
                  onCheckedChange={setNoveltyCache}
                  data-testid="switch-novelty-cache"
                  className="data-[state=checked]:bg-cyan-500"
                />
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-primary to-cyan-500 hover:from-primary/90 hover:to-cyan-500/90 shadow-lg hover:shadow-xl hover:shadow-primary/30 transition-all text-white font-semibold" 
                data-testid="button-save-settings"
                onClick={handleSaveSettings}
              >
                <Zap className="mr-2 h-4 w-4" />
                Save Settings
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
