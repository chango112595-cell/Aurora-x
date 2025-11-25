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
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Knowledge</p>
                            <p className="text-3xl font-bold text-purple-600">{status.knowledgeCapabilities}</p>
                            <p className="text-xs text-muted-foreground mt-1">Capabilities</p>
                        </div>
                        <div className="text-4xl">🧠</div>
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Execution</p>
                            <p className="text-3xl font-bold text-blue-600">{status.executionModes}</p>
                            <p className="text-xs text-muted-foreground mt-1">Modes</p>
                        </div>
                        <div className="text-4xl">⚡</div>
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Systems</p>
                            <p className="text-3xl font-bold text-green-600">{status.systemComponents}</p>
                            <p className="text-xs text-muted-foreground mt-1">Components</p>
                        </div>
                        <div className="text-4xl">🔧</div>
                    </div>
                </Card>

                <Card className="p-6 bg-gradient-to-br from-orange-500/10 to-orange-500/5 border-orange-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Modules</p>
                            <p className="text-3xl font-bold text-orange-600">{status.totalModules}</p>
                            <p className="text-xs text-muted-foreground mt-1">Active</p>
                        </div>
                        <div className="text-4xl">📦</div>
                    </div>
                </Card>
            </div>

            {/* 100-Worker Autofixer Status */}
            <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">100-Worker Autofixer Pool</h2>
                    <Badge variant="outline">
                        {status.autofixer.active}/{status.autofixer.workers} Active
                    </Badge>
                </div>

                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-muted-foreground">Workers Active</span>
                            <span className="font-medium">{status.autofixer.active}</span>
                        </div>
                        <Progress value={(status.autofixer.active / status.autofixer.workers) * 100} />
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                            <p className="text-2xl font-bold text-green-600">{status.autofixer.workers}</p>
                            <p className="text-xs text-muted-foreground">Total Workers</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-blue-600">{status.autofixer.queued}</p>
                            <p className="text-xs text-muted-foreground">Queued Jobs</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-purple-600">{status.autofixer.completed}</p>
                            <p className="text-xs text-muted-foreground">Completed</p>
                        </div>
                    </div>
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
