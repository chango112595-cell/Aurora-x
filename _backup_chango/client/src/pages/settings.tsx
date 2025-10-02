import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Settings() {
  const [autoSynth, setAutoSynth] = useState(true);
  const [noveltyCache, setNoveltyCache] = useState(true);

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
                  onCheckedChange={setAutoSynth}
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
