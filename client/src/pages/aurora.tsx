/**
 * Aurora Dashboard Page
 * Phase 3: Frontend Integration
 * Displays Aurora's 188 power units in action
 */

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
    AuroraChatInterface,
    AuroraFuturisticDashboard,
    AuroraMonitor,
    UnifiedAuroraChat
} from '@/components/aurora';
import { Brain, Zap, Settings, Package, Heart, Activity } from 'lucide-react';

interface AuroraStatus {
    status: string;
    powerUnits: number;
    knowledgeCapabilities: number;
    executionModes: number;
    systemComponents: number;
    totalModules: number;
    autofixer: {
        workers: number;
        active: number;
        queued: number;
        completed: number;
    };
    selfHealers: {
        total: number;
        active: number;
        status: string;
        healsPerformed: number;
        healthyComponents?: number;
        totalComponents?: number;
    };
    packs: {
        total: number;
        loaded: number;
        active: string[];
    };
    nexusV3: {
        connected: boolean;
        version: string;
        tiers: number;
        aems: number;
        modules: number;
        hyperspeedEnabled: boolean;
    };
    uptime: number;
    version: string;
}

export default function AuroraPage() {
    const [status, setStatus] = useState<AuroraStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/aurora/status');
            const data = await res.json();
            setStatus(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch Aurora status:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center space-y-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="text-muted-foreground">Initializing Aurora...</p>
                </div>
            </div>
        );
    }

    if (!status) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Card className="p-6">
                    <p className="text-red-500">Failed to connect to Aurora</p>
                </Card>
            </div>
        );
    }

    const uptimeMinutes = Math.floor(status.uptime / 60000);
    const uptimeSeconds = Math.floor((status.uptime % 60000) / 1000);

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                        Aurora Intelligence v{status.version}
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        188 Power Units • Full Autonomous Operation
                    </p>
                </div>
                <Badge
                    variant={status.status === 'operational' ? 'default' : 'destructive'}
                    className="text-lg px-4 py-2"
                >
                    {status.status.toUpperCase()}
                </Badge>
            </div>

            {/* Power Units Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="p-6 bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20">
                    <div className="flex items-center justify-between gap-2">
                        <div>
                            <p className="text-sm text-muted-foreground">Knowledge</p>
                            <p className="text-3xl font-bold text-purple-600">{status.knowledgeCapabilities}</p>
                            <p className="text-xs text-muted-foreground mt-1">Capabilities</p>
                        </div>
                        <Brain className="w-10 h-10 text-purple-500" />
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20">
                    <div className="flex items-center justify-between gap-2">
                        <div>
                            <p className="text-sm text-muted-foreground">Execution</p>
                            <p className="text-3xl font-bold text-blue-600">{status.executionModes}</p>
                            <p className="text-xs text-muted-foreground mt-1">Modes</p>
                        </div>
                        <Zap className="w-10 h-10 text-blue-500" />
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-500/20">
                    <div className="flex items-center justify-between gap-2">
                        <div>
                            <p className="text-sm text-muted-foreground">Systems</p>
                            <p className="text-3xl font-bold text-green-600">{status.systemComponents}</p>
                            <p className="text-xs text-muted-foreground mt-1">Components</p>
                        </div>
                        <Settings className="w-10 h-10 text-green-500" />
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-orange-500/10 to-orange-500/5 border-orange-500/20">
                    <div className="flex items-center justify-between gap-2">
                        <div>
                            <p className="text-sm text-muted-foreground">Modules</p>
                            <p className="text-3xl font-bold text-orange-600">{status.totalModules}</p>
                            <p className="text-xs text-muted-foreground mt-1">Active</p>
                        </div>
                        <Package className="w-10 h-10 text-orange-500" />
                    </div>
                </Card>
            </div>

            {/* Aurora Nexus V3 Status */}
            <Card className="p-6 bg-gradient-to-br from-indigo-500/10 to-purple-500/5 border-indigo-500/20">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">Aurora Nexus V3</h2>
                    <Badge variant={status.nexusV3?.connected ? 'default' : 'destructive'}>
                        {status.nexusV3?.connected ? 'Connected' : 'Offline'} - {status.nexusV3?.version || '3.0.0'}
                    </Badge>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
                    <div>
                        <p className="text-2xl font-bold text-indigo-600">{status.nexusV3?.tiers || 188}</p>
                        <p className="text-xs text-muted-foreground">Knowledge Tiers</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-purple-600">{status.nexusV3?.aems || 66}</p>
                        <p className="text-xs text-muted-foreground">AEMs</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-blue-600">{status.nexusV3?.modules || 550}</p>
                        <p className="text-xs text-muted-foreground">Modules</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-green-600">{status.selfHealers?.total || 100}</p>
                        <p className="text-xs text-muted-foreground">Self-Healers</p>
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-amber-600">{status.packs?.total || 15}</p>
                        <p className="text-xs text-muted-foreground">Packs</p>
                    </div>
                </div>
                <div className="mt-4 flex items-center justify-center gap-2">
                    <Badge variant="outline" className={status.nexusV3?.hyperspeedEnabled ? 'border-green-500 text-green-500' : ''}>
                        Hyperspeed: {status.nexusV3?.hyperspeedEnabled ? 'ON' : 'OFF'}
                    </Badge>
                </div>
            </Card>

            {/* Self-Healers & Workers Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 100 Self-Healers Status */}
                <Card className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20">
                    <div className="flex items-center justify-between gap-2 mb-4">
                        <div className="flex items-center gap-2">
                            <Heart className="w-5 h-5 text-green-500" />
                            <h2 className="text-xl font-bold">100 Self-Healers</h2>
                        </div>
                        <Badge variant={status.selfHealers?.status === 'operational' ? 'default' : 'destructive'}>
                            {status.selfHealers?.status || 'operational'}
                        </Badge>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-muted-foreground">Active Healers</span>
                                <span className="font-medium">{status.selfHealers?.active || 100}/{status.selfHealers?.total || 100}</span>
                            </div>
                            <Progress value={((status.selfHealers?.active || 100) / (status.selfHealers?.total || 100)) * 100} className="bg-green-500/20" />
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-muted-foreground">Component Health</span>
                                <span className="font-medium">{status.selfHealers?.healthyComponents || 0}/{status.selfHealers?.totalComponents || 6}</span>
                            </div>
                            <Progress 
                                value={((status.selfHealers?.healthyComponents || 0) / (status.selfHealers?.totalComponents || 6)) * 100} 
                                className="bg-emerald-500/20" 
                            />
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">{status.selfHealers?.healsPerformed || 0}</p>
                            <p className="text-xs text-muted-foreground">Heals Performed</p>
                        </div>
                    </div>
                </Card>

                {/* 100-Worker Autofixer Status */}
                <Card className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/5 border-blue-500/20">
                    <div className="flex items-center justify-between gap-2 mb-4">
                        <div className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-500" />
                            <h2 className="text-xl font-bold">100-Worker Autofixer</h2>
                        </div>
                        <Badge variant="outline">
                            {status.autofixer?.active || 0}/{status.autofixer?.workers || 100} Active
                        </Badge>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-muted-foreground">Workers Active</span>
                                <span className="font-medium">{status.autofixer?.active || 0}</span>
                            </div>
                            <Progress value={((status.autofixer?.active || 0) / (status.autofixer?.workers || 100)) * 100} className="bg-blue-500/20" />
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                                <p className="text-2xl font-bold text-blue-600">{status.autofixer?.queued || 0}</p>
                                <p className="text-xs text-muted-foreground">Queued</p>
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-purple-600">{status.autofixer?.completed || 0}</p>
                                <p className="text-xs text-muted-foreground">Completed</p>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Pack System Status */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">Pack System</h2>
                    <Badge variant="default">
                        {status.packs?.loaded || 15}/{status.packs?.total || 15} Loaded
                    </Badge>
                </div>
                <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                    {(status.packs?.active || []).slice(0, 15).map((pack, i) => (
                        <Badge key={pack} variant="outline" className="justify-center text-xs py-1">
                            Pack {String(i + 1).padStart(2, '0')}
                        </Badge>
                    ))}
                </div>
            </Card>

            {/* System Info */}
            <Card className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                        <p className="text-sm text-muted-foreground">Total Power</p>
                        <p className="text-2xl font-bold text-purple-600">{status.powerUnits}</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Uptime</p>
                        <p className="text-2xl font-bold text-blue-600">{uptimeMinutes}m {uptimeSeconds}s</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Version</p>
                        <p className="text-2xl font-bold text-green-600">{status.version}</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Status</p>
                        <p className="text-2xl font-bold text-orange-600">{status.status}</p>
                    </div>
                </div>
            </Card>

            {/* Tabs for different views */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="chat">Chat</TabsTrigger>
                    <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                    <TabsTrigger value="monitor">Monitor</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <Card className="p-6">
                        <h3 className="text-xl font-bold mb-4">System Architecture</h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-muted rounded">
                                <span className="font-medium">Knowledge Capabilities (Tiers 1-79)</span>
                                <Badge>{status.knowledgeCapabilities}</Badge>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-muted rounded">
                                <span className="font-medium">Execution Modes (4 Categories)</span>
                                <Badge>{status.executionModes}</Badge>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-muted rounded">
                                <span className="font-medium">System Components (7 Types)</span>
                                <Badge>{status.systemComponents}</Badge>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-muted rounded">
                                <span className="font-medium">Operational Modules</span>
                                <Badge>{status.totalModules}+</Badge>
                            </div>
                        </div>
                    </Card>
                </TabsContent>

                <TabsContent value="chat">
                    <UnifiedAuroraChat />
                </TabsContent>

                <TabsContent value="dashboard">
                    <AuroraFuturisticDashboard />
                </TabsContent>

                <TabsContent value="monitor">
                    <AuroraMonitor />
                </TabsContent>
            </Tabs>
        </div>
    );
}
