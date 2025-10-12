import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

export default function Settings() {
  const [autoSynth, setAutoSynth] = useState(false);
  const [noveltyCache, setNoveltyCache] = useState(true);
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

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Settings</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configure Aurora-X synthesis parameters
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card data-testid="card-aurora-settings">
            <CardHeader>
              <CardTitle>Aurora Configuration</CardTitle>
              <CardDescription>Synthesis engine parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="beam-width">Beam Width</Label>
                <Input
                  id="beam-width"
                  type="number"
                  defaultValue="120"
                  data-testid="input-beam-width"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max-iters">Max Iterations</Label>
                <Input
                  id="max-iters"
                  type="number"
                  defaultValue="20"
                  data-testid="input-max-iterations"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ast-budget">AST Budget</Label>
                <Input
                  id="ast-budget"
                  type="number"
                  defaultValue="64"
                  data-testid="input-ast-budget"
                />
              </div>
            </CardContent>
          </Card>

          <Card data-testid="card-feature-settings">
            <CardHeader>
              <CardTitle>Feature Toggles</CardTitle>
              <CardDescription>Enable or disable features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="auto-synth">Auto Synthesis</Label>
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
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="novelty-cache">Novelty Cache</Label>
                  <p className="text-xs text-muted-foreground">
                    Use global novelty cache (TTL+LRU)
                  </p>
                </div>
                <Switch
                  id="novelty-cache"
                  checked={noveltyCache}
                  onCheckedChange={setNoveltyCache}
                  data-testid="switch-novelty-cache"
                />
              </div>
              <Button className="w-full" data-testid="button-save-settings">Save Settings</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}