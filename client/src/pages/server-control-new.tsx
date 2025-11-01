import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { RefreshCw, Power, RotateCw, Square, ExternalLink, Zap, ChevronDown, AlertTriangle, Shield, Clock, Activity, TrendingUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { motion } from "framer-motion";
import { Link } from "wouter";

interface Service {
    name: string;
    status: string;
    port: number;
    restart_count: number;
    uptime_seconds: number;
    health_status: string;
    paused?: boolean;
}

interface ServicesData {
    timestamp: string;
    services: Record<string, Service>;
}

type ShutdownType = 'graceful' | 'emergency' | 'scheduled';

export default function ServerControl() {
    const [services, setServices] = useState<ServicesData | null>(null);
    const [loading, setLoading] = useState(true);
    const [shutdownDialogOpen, setShutdownDialogOpen] = useState(false);
    const [shutdownType, setShutdownType] = useState<ShutdownType>('graceful');
    const { toast } = useToast();

    const fetchStatus = async () => {
        try {
            const res = await fetch('http://localhost:9090/api/status');
            const data = await res.json();
            setServices(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch service status:', error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey) {
                if (e.key === 'S') {
                    e.preventDefault();
                    startAllServices();
                } else if (e.key === 'Q') {
                    e.preventDefault();
                    setShutdownType('graceful');
                    setShutdownDialogOpen(true);
                } else if (e.key === 'E') {
                    e.preventDefault();
                    setShutdownType('emergency');
                    setShutdownDialogOpen(true);
                }
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, []);

    const controlService = async (service: string, action: string) => {
        try {
            await fetch('http://localhost:9090/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service, action })
            });

            toast({
                title: "Action Sent",
                description: `${action} command sent to ${service}`,
            });

            setTimeout(fetchStatus, 2000);
        } catch (error) {
            toast({
                title: "Error",
                description: `Failed to ${action} ${service}`,
                variant: "destructive"
            });
        }
    };

    const startAllServices = async () => {
        if (!services) return;

        toast({
            title: "Starting All Services",
            description: "Launching all Aurora services...",
        });

        for (const serviceName of Object.keys(services.services)) {
            await controlService(serviceName, 'start');
        }
    };

    const stopAllServices = async (type: ShutdownType) => {
        if (!services) return;

        const descriptions = {
            graceful: "Services will shutdown cleanly after saving all state",
            emergency: "Immediate shutdown - Use only in emergencies",
            scheduled: "Services will shutdown in 30 seconds"
        };

        toast({
            title: `${type.charAt(0).toUpperCase() + type.slice(1)} Shutdown Initiated`,
            description: descriptions[type],
        });

        if (type === 'scheduled') {
            await new Promise(resolve => setTimeout(resolve, 30000));
        }

        for (const serviceName of Object.keys(services.services)) {
            await controlService(serviceName, 'stop');
        }

        toast({
            title: "Shutdown Complete",
            description: "All services stopped successfully",
        });
    };

    const restartAllServices = async () => {
        if (!services) return;

        toast({
            title: "Restarting All Services",
            description: "Bouncing all Aurora services...",
        });

        for (const serviceName of Object.keys(services.services)) {
            await controlService(serviceName, 'restart');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'running':
                return 'bg-green-500';
            case 'stopped':
            case 'paused':
                return 'bg-red-500';
            case 'starting':
                return 'bg-yellow-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusBadge = (status: string) => {
        const color = getStatusColor(status);
        return (
            <Badge className={`${color} text-white`}>
                {status}
            </Badge>
        );
    };

    const formatUptime = (seconds: number) => {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gradient-to-br from-background via-background to-primary/5">
                <div className="text-center space-y-4">
                    <RefreshCw className="animate-spin h-12 w-12 mx-auto text-primary" />
                    <p className="text-muted-foreground">Loading Aurora Control Center...</p>
                </div>
            </div>
        );
    }

    const allServicesRunning = services && Object.values(services.services).every(s => s.status === 'running');
    const anyServiceRunning = services && Object.values(services.services).some(s => s.status === 'running');
    const runningCount = services ? Object.values(services.services).filter(s => s.status === 'running').length : 0;
    const totalCount = services ? Object.values(services.services).length : 0;

    return (
        <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
            <div className="container mx-auto p-6 space-y-8 max-w-7xl">

                {/* Hero Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center space-y-3 pt-6"
                >
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent">
                        Aurora Control Center
                    </h1>
                    <p className="text-muted-foreground text-lg">
                        Manage all Aurora services from one powerful interface
                    </p>
                    <div className="flex items-center justify-center gap-3 text-sm">
                        <Badge variant={anyServiceRunning ? "default" : "secondary"} className="gap-2">
                            <div className={`h-2 w-2 rounded-full ${anyServiceRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                            {runningCount}/{totalCount} Services Active
                        </Badge>
                        <Badge variant="outline" className="gap-2">
                            <Clock className="h-3 w-3" />
                            Last updated: {new Date().toLocaleTimeString()}
                        </Badge>
                    </div>
                </motion.div>

                {/* Hero Power Button */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="relative"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-cyan-500/20 to-purple-500/20 blur-3xl -z-10" />

                    <Card className="border-2 border-primary/30 shadow-2xl">
                        <CardContent className="p-8">
                            {!anyServiceRunning ? (
                                // START ALL - Big Hero Button
                                <Button
                                    onClick={startAllServices}
                                    size="lg"
                                    className="w-full h-24 text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-lg hover:shadow-xl transition-all gap-4"
                                >
                                    <Zap className="h-10 w-10" />
                                    START ALL SERVERS
                                </Button>
                            ) : (
                                // Context-Aware Control Panel
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Button
                                        onClick={startAllServices}
                                        disabled={allServicesRunning}
                                        size="lg"
                                        variant={allServicesRunning ? "secondary" : "default"}
                                        className="h-16 text-lg font-semibold gap-3"
                                    >
                                        <Zap className="h-6 w-6" />
                                        {allServicesRunning ? 'All Running' : 'Start All'}
                                    </Button>

                                    <Button
                                        onClick={restartAllServices}
                                        size="lg"
                                        variant="outline"
                                        className="h-16 text-lg font-semibold gap-3 border-2"
                                    >
                                        <RotateCw className="h-6 w-6" />
                                        Restart All
                                    </Button>

                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button
                                                size="lg"
                                                variant="destructive"
                                                className="h-16 text-lg font-semibold gap-3"
                                            >
                                                <Square className="h-6 w-6" />
                                                Shutdown
                                                <ChevronDown className="h-5 w-5 ml-auto" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end" className="w-64">
                                            <DropdownMenuItem
                                                onClick={() => {
                                                    setShutdownType('graceful');
                                                    setShutdownDialogOpen(true);
                                                }}
                                                className="py-3 cursor-pointer"
                                            >
                                                <Shield className="mr-3 h-5 w-5 text-blue-500" />
                                                <div>
                                                    <div className="font-semibold">Graceful Shutdown</div>
                                                    <div className="text-xs text-muted-foreground">Save state & diagnostics</div>
                                                </div>
                                            </DropdownMenuItem>

                                            <DropdownMenuItem
                                                onClick={() => {
                                                    setShutdownType('scheduled');
                                                    setShutdownDialogOpen(true);
                                                }}
                                                className="py-3 cursor-pointer"
                                            >
                                                <Clock className="mr-3 h-5 w-5 text-yellow-500" />
                                                <div>
                                                    <div className="font-semibold">Scheduled Shutdown</div>
                                                    <div className="text-xs text-muted-foreground">Shutdown in 30 seconds</div>
                                                </div>
                                            </DropdownMenuItem>

                                            <DropdownMenuSeparator />

                                            <DropdownMenuItem
                                                onClick={() => {
                                                    setShutdownType('emergency');
                                                    setShutdownDialogOpen(true);
                                                }}
                                                className="py-3 cursor-pointer text-red-500"
                                            >
                                                <AlertTriangle className="mr-3 h-5 w-5" />
                                                <div>
                                                    <div className="font-semibold">Emergency Shutdown</div>
                                                    <div className="text-xs text-muted-foreground">Immediate stop</div>
                                                </div>
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </div>
                            )}

                            {/* Keyboard Shortcuts Hint */}
                            <div className="mt-4 pt-4 border-t border-border">
                                <p className="text-xs text-muted-foreground text-center font-mono">
                                    Shortcuts: Ctrl+Shift+S (Start) • Ctrl+Shift+Q (Graceful) • Ctrl+Shift+E (Emergency)
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Quick Access Links */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="flex justify-center gap-4"
                >
                    <Link href="/luminar">
                        <Button variant="outline" className="gap-2">
                            <TrendingUp className="h-4 w-4" />
                            Luminar Nexus Analytics
                        </Button>
                    </Link>
                    <Button
                        onClick={() => window.open('http://localhost:9090', '_blank')}
                        variant="outline"
                        className="gap-2"
                    >
                        <ExternalLink className="h-4 w-4" />
                        Full Health Dashboard
                    </Button>
                    <Button
                        onClick={fetchStatus}
                        variant="ghost"
                        size="sm"
                        className="gap-2"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Refresh
                    </Button>
                </motion.div>

                {/* Individual Service Cards - 2x2 Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <Activity className="h-6 w-6 text-primary" />
                        Individual Services
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {services && Object.values(services.services).map((service: Service, index) => (
                            <motion.div
                                key={service.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 + index * 0.1 }}
                            >
                                <Card className="relative hover:shadow-lg transition-shadow border-primary/20">
                                    <CardHeader>
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <CardTitle className="text-xl">{service.name}</CardTitle>
                                                <CardDescription>Port {service.port}</CardDescription>
                                            </div>
                                            <div className="absolute top-4 right-4">
                                                <div className={`h-3 w-3 rounded-full ${getStatusColor(service.status)} ${service.status === 'running' ? 'animate-pulse' : ''}`} />
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-muted-foreground">Status</span>
                                            {getStatusBadge(service.status)}
                                        </div>

                                        {service.uptime_seconds > 0 && (
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm text-muted-foreground">Uptime</span>
                                                <span className="text-sm font-mono font-semibold">
                                                    {formatUptime(service.uptime_seconds)}
                                                </span>
                                            </div>
                                        )}

                                        {service.restart_count > 0 && (
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm text-muted-foreground">Restarts</span>
                                                <Badge variant="secondary">{service.restart_count}</Badge>
                                            </div>
                                        )}

                                        <div className="flex gap-2 pt-2">
                                            {service.status === 'running' ? (
                                                <>
                                                    <Button
                                                        size="sm"
                                                        variant="destructive"
                                                        className="flex-1"
                                                        onClick={() => controlService(service.name, 'stop')}
                                                    >
                                                        <Square className="mr-1 h-3 w-3" />
                                                        Stop
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="flex-1"
                                                        onClick={() => controlService(service.name, 'restart')}
                                                    >
                                                        <RotateCw className="mr-1 h-3 w-3" />
                                                        Restart
                                                    </Button>
                                                </>
                                            ) : (
                                                <Button
                                                    size="sm"
                                                    className="flex-1"
                                                    onClick={() => controlService(service.name, 'start')}
                                                >
                                                    <Power className="mr-1 h-3 w-3" />
                                                    Start
                                                </Button>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>

                {/* Shutdown Confirmation Dialog */}
                <AlertDialog open={shutdownDialogOpen} onOpenChange={setShutdownDialogOpen}>
                    <AlertDialogContent>
                        <AlertDialogHeader>
                            <AlertDialogTitle className="flex items-center gap-2">
                                {shutdownType === 'emergency' ? (
                                    <AlertTriangle className="h-5 w-5 text-red-500" />
                                ) : shutdownType === 'scheduled' ? (
                                    <Clock className="h-5 w-5 text-yellow-500" />
                                ) : (
                                    <Shield className="h-5 w-5 text-blue-500" />
                                )}
                                Confirm {shutdownType.charAt(0).toUpperCase() + shutdownType.slice(1)} Shutdown
                            </AlertDialogTitle>
                            <AlertDialogDescription>
                                {shutdownType === 'graceful' && (
                                    <>
                                        This will cleanly shutdown all services after:
                                        <ul className="list-disc ml-6 mt-2 space-y-1">
                                            <li>Saving all system state</li>
                                            <li>Running diagnostics</li>
                                            <li>Creating shutdown report</li>
                                        </ul>
                                        <p className="mt-2 font-semibold">All work will be saved.</p>
                                    </>
                                )}
                                {shutdownType === 'scheduled' && (
                                    <>
                                        Services will shutdown in 30 seconds. This gives time to:
                                        <ul className="list-disc ml-6 mt-2 space-y-1">
                                            <li>Complete ongoing operations</li>
                                            <li>Save state automatically</li>
                                            <li>Close connections gracefully</li>
                                        </ul>
                                    </>
                                )}
                                {shutdownType === 'emergency' && (
                                    <p className="text-red-500 font-semibold">
                                        ⚠️ This will immediately stop all services. Use only if services are unresponsive.
                                        State will be saved but operations may be interrupted.
                                    </p>
                                )}
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                                onClick={() => stopAllServices(shutdownType)}
                                className={shutdownType === 'emergency' ? 'bg-red-600 hover:bg-red-700' : ''}
                            >
                                Confirm Shutdown
                            </AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>
            </div>
        </div>
    );
}
