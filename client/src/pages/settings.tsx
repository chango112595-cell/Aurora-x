import { useState } from 'react';
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
import { Settings, RefreshCw, Palette, Brain, Zap, Bell, Shield, Server, Save, RotateCcw, Moon, Sun, Monitor } from "lucide-react";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";

interface SettingsSection {
  id: string;
  label: string;
  icon: React.ReactNode;
}

export default function SettingsPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('appearance');
  const [theme, setTheme] = useState('dark');
  const [accentColor, setAccentColor] = useState('cyan');
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
    setAccentColor('cyan');
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
    <div className="h-full flex flex-col bg-gradient-to-br from-background via-cyan-950/5 to-purple-950/5">
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-purple-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-purple-400/50 flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                <Settings className="w-6 h-6 text-purple-400" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent" data-testid="text-page-title">
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
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500"
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
          <TabsList className="mb-4 bg-slate-900 border border-purple-500/40 shadow-lg flex-wrap justify-start gap-1" data-testid="tablist-settings">
            {sections.map((section) => (
              <TabsTrigger 
                key={section.id}
                value={section.id} 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600/70 data-[state=active]:to-pink-600/70 data-[state=active]:text-white text-purple-300"
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
                <Card className="border-purple-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-purple-500/20">
                    <CardTitle className="text-lg text-purple-300">Theme Settings</CardTitle>
                    <CardDescription className="text-purple-300/60">Customize the visual appearance</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-6">
                    <div className="space-y-3">
                      <Label className="text-purple-200">Color Theme</Label>
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
                              ? "bg-gradient-to-r from-purple-600 to-pink-600" 
                              : "border-purple-500/30 text-purple-300"}
                            data-testid={`button-theme-${option.value}`}
                          >
                            {option.icon}
                            <span className="ml-2">{option.label}</span>
                          </Button>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <Label className="text-purple-200">Accent Color</Label>
                      <Select value={accentColor} onValueChange={setAccentColor}>
                        <SelectTrigger className="bg-slate-800/50 border-purple-500/30" data-testid="select-accent-color">
                          <SelectValue placeholder="Select accent color" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cyan">Cyan</SelectItem>
                          <SelectItem value="purple">Purple</SelectItem>
                          <SelectItem value="pink">Pink</SelectItem>
                          <SelectItem value="green">Green</SelectItem>
                          <SelectItem value="blue">Blue</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-purple-200">Enable Animations</p>
                        <p className="text-xs text-purple-300/60">Smooth transitions and effects</p>
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
                <Card className="border-cyan-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-cyan-500/20">
                    <CardTitle className="text-lg text-cyan-300">AI Behavior</CardTitle>
                    <CardDescription className="text-cyan-300/60">Configure Aurora's learning and response patterns</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-6">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-cyan-200">Learning Rate</Label>
                        <span className="text-sm text-cyan-400 font-mono">{learningRate[0]}%</span>
                      </div>
                      <Slider
                        value={learningRate}
                        onValueChange={setLearningRate}
                        max={100}
                        step={5}
                        className="w-full"
                        data-testid="slider-learning-rate"
                      />
                      <p className="text-xs text-cyan-300/60">Higher values mean faster adaptation but may reduce stability</p>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-cyan-200">Memory Retention</Label>
                        <span className="text-sm text-cyan-400 font-mono">{memoryRetention[0]}%</span>
                      </div>
                      <Slider
                        value={memoryRetention}
                        onValueChange={setMemoryRetention}
                        max={100}
                        step={5}
                        className="w-full"
                        data-testid="slider-memory-retention"
                      />
                      <p className="text-xs text-cyan-300/60">Controls how long Aurora retains learned information</p>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <p className="text-sm text-cyan-200">Autonomous Mode</p>
                        <p className="text-xs text-cyan-300/60">Allow self-directed learning and optimization</p>
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
              <div className="grid gap-6">
                <Card className="border-red-500/30 bg-slate-900/50 backdrop-blur-xl">
                  <CardHeader className="border-b border-red-500/20">
                    <CardTitle className="text-lg text-red-300">Security Settings</CardTitle>
                    <CardDescription className="text-red-300/60">Manage security and privacy options</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-4">
                    <div className="p-4 bg-slate-800/50 rounded-lg border border-red-500/20">
                      <div className="flex items-center gap-3 mb-2">
                        <Shield className="w-5 h-5 text-green-400" />
                        <span className="text-sm text-red-200 font-semibold">Security Status</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="bg-green-500/20 text-green-300 border-green-500/30">
                          Protected
                        </Badge>
                        <span className="text-xs text-red-300/60">All security measures active</span>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-sm text-red-200 mb-2">API Key Management</p>
                      <p className="text-xs text-red-300/60 mb-3">Securely stored and encrypted</p>
                      <Button variant="outline" size="sm" className="border-red-500/30 text-red-300">
                        Manage API Keys
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
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
