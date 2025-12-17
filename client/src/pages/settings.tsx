import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Settings, RefreshCw, Palette, Brain, Zap, Bell, Shield, Server, Save, RotateCcw, Moon, Sun, Monitor, Key, Plus, Trash2, Lock, Eye, EyeOff } from "lucide-react";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";

interface SettingsSection {
  id: string;
  label: string;
  icon: React.ReactNode;
}

function SecurityApiKeyManager() {
  const { toast } = useToast();
  const [adminKey, setAdminKey] = useState(() => localStorage.getItem("aurora_admin_key") || "");
  const [newAlias, setNewAlias] = useState("");
  const [newValue, setNewValue] = useState("");
  const [showValue, setShowValue] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (adminKey) {
      localStorage.setItem("aurora_admin_key", adminKey);
    }
  }, [adminKey]);

  const aliasesQuery = useQuery<{ ok: boolean; aliases: string[] }>({
    queryKey: ["/api/vault/aliases"],
    enabled: isAuthenticated,
    queryFn: async () => {
      const res = await fetch("/api/vault/aliases", {
        headers: { "x-api-key": adminKey }
      });
      if (!res.ok) throw new Error("Unauthorized");
      return res.json();
    }
  });

  const healthQuery = useQuery<{ ok: boolean; configured: boolean; hasMasterPassphrase: boolean; hasAdminKey: boolean }>({
    queryKey: ["/api/vault/health"]
  });

  const addSecretMutation = useMutation({
    mutationFn: async (data: { alias: string; value: string }) => {
      const res = await fetch("/api/vault/secrets", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "x-api-key": adminKey 
        },
        body: JSON.stringify(data)
      });
      return res.json();
    },
    onSuccess: (data) => {
      if (data.ok) {
        toast({ title: "API Key Added", description: `${data.alias} stored securely in vault.` });
        setNewAlias("");
        setNewValue("");
        queryClient.invalidateQueries({ queryKey: ["/api/vault/aliases"] });
      } else {
        toast({ title: "Error", description: data.error || "Failed to add key", variant: "destructive" });
      }
    },
    onError: () => {
      toast({ title: "Error", description: "Failed to add API key", variant: "destructive" });
    }
  });

  const deleteSecretMutation = useMutation({
    mutationFn: async (alias: string) => {
      const res = await fetch(`/api/vault/secrets/${alias}`, {
        method: "DELETE",
        headers: { "x-api-key": adminKey }
      });
      return res.json();
    },
    onSuccess: (data) => {
      if (data.ok) {
        toast({ title: "API Key Deleted", description: `${data.alias} removed from vault.` });
        queryClient.invalidateQueries({ queryKey: ["/api/vault/aliases"] });
      } else {
        toast({ title: "Error", description: data.error || "Failed to delete key", variant: "destructive" });
      }
    },
    onError: () => {
      toast({ title: "Error", description: "Failed to delete API key", variant: "destructive" });
    }
  });

  const handleAuthenticate = () => {
    if (!adminKey.trim()) {
      toast({ title: "Admin Key Required", description: "Please enter your admin API key.", variant: "destructive" });
      return;
    }
    setIsAuthenticated(true);
  };

  const handleAddSecret = () => {
    if (!newAlias.trim() || !newValue.trim()) {
      toast({ title: "Missing Fields", description: "Please enter both alias and value.", variant: "destructive" });
      return;
    }
    addSecretMutation.mutate({ alias: newAlias.trim(), value: newValue.trim() });
  };

  return (
    <div className="grid gap-6">
      <Card className="border-red-500/30 bg-slate-900/50 backdrop-blur-xl">
        <CardHeader className="border-b border-red-500/20">
          <CardTitle className="text-lg text-red-300 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            ASE-Infinity Vault - API Key Management
          </CardTitle>
          <CardDescription className="text-red-300/60">Securely store and manage API keys with 22-layer encryption</CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div className="p-4 bg-slate-800/50 rounded-lg border border-red-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Lock className="w-5 h-5 text-green-400" />
              <span className="text-sm text-red-200 font-semibold">Vault Status</span>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {healthQuery.data?.configured ? (
                <Badge variant="outline" className="bg-green-500/20 text-green-300 border-green-500/30">Configured</Badge>
              ) : (
                <Badge variant="outline" className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">Not Configured</Badge>
              )}
              {healthQuery.data?.hasMasterPassphrase && (
                <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-500/30">Master Key Set</Badge>
              )}
              <span className="text-xs text-red-300/60">22-layer AES encryption active</span>
            </div>
          </div>

          {!isAuthenticated ? (
            <div className="p-4 bg-slate-800/50 rounded-lg border border-red-500/20">
              <Label className="text-red-200 mb-2 block">Admin API Key</Label>
              <div className="flex gap-2">
                <Input
                  type="password"
                  placeholder="Enter admin key to manage secrets"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  className="flex-1 bg-slate-700/50 border-red-500/30"
                  data-testid="input-admin-key"
                />
                <Button onClick={handleAuthenticate} className="bg-red-600 hover:bg-red-500" data-testid="button-authenticate">
                  <Key className="w-4 h-4 mr-2" />
                  Unlock
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                <Label className="text-green-200 mb-3 block flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add New API Key
                </Label>
                <div className="space-y-3">
                  <Input
                    placeholder="Alias (e.g., discord_webhook, openai_key)"
                    value={newAlias}
                    onChange={(e) => setNewAlias(e.target.value)}
                    className="bg-slate-700/50 border-green-500/30"
                    data-testid="input-new-alias"
                  />
                  <div className="relative">
                    <Input
                      type={showValue ? "text" : "password"}
                      placeholder="API Key / Secret Value"
                      value={newValue}
                      onChange={(e) => setNewValue(e.target.value)}
                      className="bg-slate-700/50 border-green-500/30 pr-10"
                      data-testid="input-new-value"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                      onClick={() => setShowValue(!showValue)}
                    >
                      {showValue ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                  <Button 
                    onClick={handleAddSecret} 
                    disabled={addSecretMutation.isPending}
                    className="w-full bg-green-600 hover:bg-green-500"
                    data-testid="button-add-secret"
                  >
                    {addSecretMutation.isPending ? (
                      <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Encrypting...</>
                    ) : (
                      <><Lock className="w-4 h-4 mr-2" />Store in Vault</>
                    )}
                  </Button>
                </div>
              </div>

              <div className="p-4 bg-slate-800/50 rounded-lg border border-emerald-500/20">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-emerald-200 flex items-center gap-2">
                    <Key className="w-4 h-4" />
                    Stored API Keys ({aliasesQuery.data?.aliases?.length || 0})
                  </Label>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => aliasesQuery.refetch()}
                    data-testid="button-refresh-keys"
                  >
                    <RefreshCw className={`w-4 h-4 ${aliasesQuery.isFetching ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {aliasesQuery.isLoading ? (
                    <div className="text-center py-4 text-emerald-300/60">Loading...</div>
                  ) : aliasesQuery.data?.aliases?.length === 0 ? (
                    <div className="text-center py-4 text-emerald-300/60">No API keys stored yet</div>
                  ) : (
                    aliasesQuery.data?.aliases?.map((alias, i) => (
                      <div key={alias} className="flex items-center justify-between p-2 bg-slate-700/30 rounded" data-testid={`row-key-${i}`}>
                        <div className="flex items-center gap-2">
                          <Lock className="w-4 h-4 text-emerald-400" />
                          <span className="text-sm text-emerald-200 font-mono">{alias}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-red-400 hover:text-red-300 hover:bg-red-500/20"
                          onClick={() => deleteSecretMutation.mutate(alias)}
                          disabled={deleteSecretMutation.isPending}
                          data-testid={`button-delete-${i}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function SettingsPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('appearance');
  const [theme, setTheme] = useState('dark');
  const [accentColor, setAccentColor] = useState('emerald');
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [learningRate, setLearningRate] = useState([75]);
  const [memoryRetention, setMemoryRetention] = useState([85]);
  const [autonomousMode, setAutonomousMode] = useState(true);
  const [debugMode, setDebugMode] = useState(false);
  const [apiTimeout, setApiTimeout] = useState('30');
  const [maxWorkers, setMaxWorkers] = useState('300');

  const sections: SettingsSection[] = [
    { id: 'appearance', label: 'Appearance', icon: <Palette className="w-4 h-4" /> },
    { id: 'ai', label: 'AI Settings', icon: <Brain className="w-4 h-4" /> },
    { id: 'performance', label: 'Performance', icon: <Zap className="w-4 h-4" /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
    { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" /> },
    { id: 'advanced', label: 'Advanced', icon: <Server className="w-4 h-4" /> },
  ];

  const handleSave = () => {
    toast({
      title: "Settings Saved",
      description: "Your preferences have been updated successfully.",
    });
  };

  const handleReset = () => {
    setTheme('dark');
    setAccentColor('emerald');
    setAnimationsEnabled(true);
    setAutoSaveEnabled(true);
    setNotificationsEnabled(true);
    setSoundEnabled(false);
    setLearningRate([75]);
    setMemoryRetention([85]);
    setAutonomousMode(true);
    setDebugMode(false);
    setApiTimeout('30');
    setMaxWorkers('300');
    toast({
      title: "Settings Reset",
      description: "All settings have been restored to defaults.",
    });
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-emerald-950/5 to-sky-950/5">
      <div className="p-6 border-b border-emerald-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-sky-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-sky-400/50 flex items-center justify-center bg-gradient-to-br from-sky-500/20 to-amber-500/20">
                <Settings className="w-6 h-6 text-sky-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-400 via-amber-400 to-sky-400 bg-clip-text text-transparent" data-testid="text-page-title">
                Configuration
              </h1>
              <p className="text-sm text-muted-foreground">
                System Settings & Preferences
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleReset}
              className="border-slate-500/30 hover:border-slate-400/50"
              data-testid="button-reset"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </Button>
            <Button 
              size="sm" 
              onClick={handleSave}
              className="bg-gradient-to-r from-sky-600 to-amber-600 hover:from-sky-500 hover:to-amber-500"
              data-testid="button-save"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col" data-testid="tabs-settings">
          <TabsList className="mb-4 bg-slate-900 border border-sky-500/40 shadow-lg flex-wrap justify-start gap-1" data-testid="tablist-settings">
            {sections.map((section) => (
              <TabsTrigger 
                key={section.id}
                value={section.id} 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-sky-600/70 data-[state=active]:to-amber-600/70 data-[state=active]:text-white text-sky-300"
                data-testid={`tab-trigger-${section.id}`}
              >
                {section.icon}
                <span className="ml-2 hidden sm:inline">{section.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <ScrollArea className="flex-1">
            <TabsContent value="appearance" className="mt-0" data-testid="tab-content-appearance">
              <div className="grid gap-6">
                <Card className="border-sky-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-sky-500/20">
                    <CardTitle className="text-lg text-sky-300">Theme Settings</CardTitle>
                    <CardDescription className="text-sky-300/60">Customize the visual appearance</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-6">
                    <div className="space-y-3">
                      <Label className="text-sky-200">Color Theme</Label>
                      <div className="flex gap-3">
                        {[
                          { value: 'light', icon: <Sun className="w-4 h-4" />, label: 'Light' },
                          { value: 'dark', icon: <Moon className="w-4 h-4" />, label: 'Dark' },
                          { value: 'system', icon: <Monitor className="w-4 h-4" />, label: 'System' },
                        ].map((option) => (
                          <Button
                            key={option.value}
                            variant={theme === option.value ? "default" : "outline"}
                            size="sm"
                            onClick={() => setTheme(option.value)}
                            className={theme === option.value 
                              ? "bg-gradient-to-r from-sky-600 to-amber-600" 
                              : "border-sky-500/30 text-sky-300"}
                            data-testid={`button-theme-${option.value}`}
                          >
                            {option.icon}
                            <span className="ml-2">{option.label}</span>
                          </Button>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <Label className="text-sky-200">Accent Color</Label>
                      <Select value={accentColor} onValueChange={setAccentColor}>
                        <SelectTrigger className="bg-slate-800/50 border-sky-500/30" data-testid="select-accent-color">
                          <SelectValue placeholder="Select accent color" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="emerald">Cyan</SelectItem>
                          <SelectItem value="sky">Purple</SelectItem>
                          <SelectItem value="amber">Pink</SelectItem>
                          <SelectItem value="green">Green</SelectItem>
                          <SelectItem value="blue">Blue</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-sky-200">Enable Animations</p>
                        <p className="text-xs text-sky-300/60">Smooth transitions and effects</p>
                      </div>
                      <Switch 
                        checked={animationsEnabled} 
                        onCheckedChange={setAnimationsEnabled}
                        data-testid="switch-animations"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="ai" className="mt-0" data-testid="tab-content-ai">
              <div className="grid gap-6">
                <Card className="border-emerald-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-emerald-500/20">
                    <CardTitle className="text-lg text-emerald-300">AI Behavior</CardTitle>
                    <CardDescription className="text-emerald-300/60">Configure Aurora's learning and response patterns</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-6">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-emerald-200">Learning Rate</Label>
                        <span className="text-sm text-emerald-400 font-mono">{learningRate[0]}%</span>
                      </div>
                      <Slider
                        value={learningRate}
                        onValueChange={setLearningRate}
                        max={100}
                        step={5}
                        className="w-full"
                        data-testid="slider-learning-rate"
                      />
                      <p className="text-xs text-emerald-300/60">Higher values mean faster adaptation but may reduce stability</p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-emerald-200">Memory Retention</Label>
                        <span className="text-sm text-emerald-400 font-mono">{memoryRetention[0]}%</span>
                      </div>
                      <Slider
                        value={memoryRetention}
                        onValueChange={setMemoryRetention}
                        max={100}
                        step={5}
                        className="w-full"
                        data-testid="slider-memory-retention"
                      />
                      <p className="text-xs text-emerald-300/60">Controls how long Aurora retains learned information</p>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-emerald-200">Autonomous Mode</p>
                        <p className="text-xs text-emerald-300/60">Allow self-directed learning and optimization</p>
                      </div>
                      <Switch 
                        checked={autonomousMode} 
                        onCheckedChange={setAutonomousMode}
                        data-testid="switch-autonomous"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="performance" className="mt-0" data-testid="tab-content-performance">
              <div className="grid gap-6">
                <Card className="border-green-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-green-500/20">
                    <CardTitle className="text-lg text-green-300">Performance Settings</CardTitle>
                    <CardDescription className="text-green-300/60">Optimize system resources and speed</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label className="text-green-200">API Timeout (seconds)</Label>
                        <Input
                          type="number"
                          value={apiTimeout}
                          onChange={(e) => setApiTimeout(e.target.value)}
                          className="bg-slate-800/50 border-green-500/30"
                          data-testid="input-api-timeout"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-green-200">Max Workers</Label>
                        <Input
                          type="number"
                          value={maxWorkers}
                          onChange={(e) => setMaxWorkers(e.target.value)}
                          className="bg-slate-800/50 border-green-500/30"
                          data-testid="input-max-workers"
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-green-200">Auto-Save</p>
                        <p className="text-xs text-green-300/60">Automatically save changes</p>
                      </div>
                      <Switch 
                        checked={autoSaveEnabled} 
                        onCheckedChange={setAutoSaveEnabled}
                        data-testid="switch-auto-save"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="notifications" className="mt-0" data-testid="tab-content-notifications">
              <div className="grid gap-6">
                <Card className="border-yellow-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-yellow-500/20">
                    <CardTitle className="text-lg text-yellow-300">Notification Preferences</CardTitle>
                    <CardDescription className="text-yellow-300/60">Control alerts and notifications</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-4">
                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-yellow-200">Enable Notifications</p>
                        <p className="text-xs text-yellow-300/60">Receive system alerts and updates</p>
                      </div>
                      <Switch 
                        checked={notificationsEnabled} 
                        onCheckedChange={setNotificationsEnabled}
                        data-testid="switch-notifications"
                      />
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-yellow-200">Sound Effects</p>
                        <p className="text-xs text-yellow-300/60">Play sounds for notifications</p>
                      </div>
                      <Switch 
                        checked={soundEnabled} 
                        onCheckedChange={setSoundEnabled}
                        data-testid="switch-sound"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="security" className="mt-0" data-testid="tab-content-security">
              <SecurityApiKeyManager />
            </TabsContent>

            <TabsContent value="advanced" className="mt-0" data-testid="tab-content-advanced">
              <div className="grid gap-6">
                <Card className="border-slate-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-slate-500/20">
                    <CardTitle className="text-lg text-slate-300">Advanced Settings</CardTitle>
                    <CardDescription className="text-slate-300/60">Developer and debug options</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-4">
                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-slate-200">Debug Mode</p>
                        <p className="text-xs text-slate-300/60">Enable verbose logging and diagnostics</p>
                      </div>
                      <Switch 
                        checked={debugMode} 
                        onCheckedChange={setDebugMode}
                        data-testid="switch-debug"
                      />
                    </div>

                    <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-500/20">
                      <p className="text-sm text-slate-200 mb-2">System Information</p>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Version:</span>
                          <span className="text-slate-300 font-mono">3.1.0</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Build:</span>
                          <span className="text-slate-300 font-mono">Peak Autonomy</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Workers:</span>
                          <span className="text-slate-300 font-mono">300</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Modules:</span>
                          <span className="text-slate-300 font-mono">550</span>
                        </div>
                      </div>
                    </div>

                    <Button variant="outline" size="sm" className="border-slate-500/30 text-slate-300 w-full">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Clear Cache & Restart
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </div>
    </div>
  );
}
