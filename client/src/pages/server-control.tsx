import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { Zap, Square, RotateCw, Power, ChevronDown, Shield, Clock, AlertTriangle, Activity } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { motion } from "framer-motion";
import { Link } from "wouter";

interface Service {
    name: string;
    status: string;
    port: number;
    restart_count: number;
    uptime_seconds: number;
}

interface ServicesData {
    services: Record<string, Service>;
}

type ShutdownType = 'graceful' | 'emergency' | 'scheduled';

export default function ServerControl() {
    const [services, setServices] = useState<ServicesData | null>(null);
    const [loading, setLoading] = useState(true);
    const [shutdownDialogOpen, setShutdownDialogOpen] = useState(false);
    const [shutdownType, setShutdownType] = useState<ShutdownType>('graceful');
    const { toast } = useToast();

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey) {
                if (e.key === 'S') { e.preventDefault(); startAllServices(); }
                else if (e.key === 'Q') { e.preventDefault(); setShutdownType('graceful'); setShutdownDialogOpen(true); }
                else if (e.key === 'E') { e.preventDefault(); setShutdownType('emergency'); setShutdownDialogOpen(true); }
            }
        };
        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch('http://localhost:9090/api/status');
            const data = await res.json();
            setServices(data);
            setLoading(false);
        } catch (error) {
            setLoading(false);
        }
    };

    const controlService = async (service: string, action: string) => {
        try {
            await fetch('http://localhost:9090/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service, action })
            });
            toast({ title: "Action Sent", description: `${action} command sent to ${service}` });
            setTimeout(fetchStatus, 2000);
        } catch (error) {
            toast({ title: "Error", description: `Failed to ${action} ${service}`, variant: "destructive" });
        }
    };

    const startAllServices = async () => {
        if (!services) return;
        toast({ title: "Starting All Services", description: "Launching all Aurora services..." });
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
        toast({ title: `${type.charAt(0).toUpperCase() + type.slice(1)} Shutdown Initiated`, description: descriptions[type] });
        if (type === 'scheduled') await new Promise(resolve => setTimeout(resolve, 30000));
        for (const serviceName of Object.keys(services.services)) {
            await controlService(serviceName, 'stop');
        }
    };

    const restartAllServices = async () => {
        if (!services) return;
        toast({ title: "Restarting All Services", description: "Bouncing all Aurora services..." });
        for (const serviceName of Object.keys(services.services)) {
            await controlService(serviceName, 'restart');
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center h-screen"><Activity className="animate-spin h-12 w-12 text-primary" /></div>;
    }

    const allRunning = services && Object.values(services.services).every(s => s.status === 'running');
    const anyRunning = services && Object.values(services.services).some(s => s.status === 'running');
    const runningCount = services ? Object.values(services.services).filter(s => s.status === 'running').length : 0;
    const totalCount = services ? Object.values(services.services).length : 0;

    return (
        <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
            <div className="container mx-auto p-6 space-y-8 max-w-7xl">
                <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center space-y-3 pt-6">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent">
                        Aurora Control Center
                    </h1>
                    <p className="text-muted-foreground text-lg">Manage all Aurora services from one powerful interface</p>
                    <Badge variant={anyRunning ? "default" : "secondary"} className="gap-2">
                        <div className={`h-2 w-2 rounded-full ${anyRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                        {runningCount}/{totalCount} Services Active
                    </Badge>
                </motion.div>

                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="relative">
                    <Card className="border-2 border-primary/30 shadow-2xl">
                        <CardContent className="p-8">
                            {!anyRunning ? (
                                <Button onClick={startAllServices} size="lg" className="w-full h-24 text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 gap-4">
                                    <Zap className="h-10 w-10" /> START ALL SERVERS
                                </Button>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Button onClick={startAllServices} disabled={allRunning} size="lg" variant={allRunning ? "secondary" : "default"} className="h-16 text-lg font-semibold gap-3">
                                        <Zap className="h-6 w-6" /> {allRunning ? 'All Running' : 'Start All'}
                                    </Button>
                                    <Button onClick={restartAllServices} size="lg" variant="outline" className="h-16 text-lg font-semibold gap-3 border-2">
                                        <RotateCw className="h-6 w-6" /> Restart All
                                    </Button>
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button size="lg" variant="destructive" className="h-16 text-lg font-semibold gap-3">
                                                <Square className="h-6 w-6" /> Shutdown <ChevronDown className="h-5 w-5 ml-auto" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end" className="w-64">
                                            <DropdownMenuItem onClick={() => { setShutdownType('graceful'); setShutdownDialogOpen(true); }} className="py-3 cursor-pointer">
                                                <Shield className="mr-3 h-5 w-5 text-blue-500" />
                                                <div><div className="font-semibold">Graceful Shutdown</div><div className="text-xs text-muted-foreground">Save state & diagnostics</div></div>
                                            </DropdownMenuItem>
                                            <DropdownMenuItem onClick={() => { setShutdownType('scheduled'); setShutdownDialogOpen(true); }} className="py-3 cursor-pointer">
                                                <Clock className="mr-3 h-5 w-5 text-yellow-500" />
                                                <div><div className="font-semibold">Scheduled Shutdown</div><div className="text-xs text-muted-foreground">Shutdown in 30 seconds</div></div>
                                            </DropdownMenuItem>
                                            <DropdownMenuSeparator />
                                            <DropdownMenuItem onClick={() => { setShutdownType('emergency'); setShutdownDialogOpen(true); }} className="py-3 cursor-pointer text-red-500">
                                                <AlertTriangle className="mr-3 h-5 w-5" />
                                                <div><div className="font-semibold">Emergency Shutdown</div><div className="text-xs text-muted-foreground">Immediate stop</div></div>
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </div>
                            )}
                            <div className="mt-4 pt-4 border-t border-border">
                                <p className="text-xs text-muted-foreground text-center font-mono">
                                    Shortcuts: Ctrl+Shift+S (Start) • Ctrl+Shift+Q (Graceful) • Ctrl+Shift+E (Emergency)
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {services && Object.values(services.services).map((service: Service) => (
                        <Card key={service.name} className="hover:shadow-lg transition-shadow">
                            <CardHeader>
                                <CardTitle className="flex justify-between">
                                    {service.name}
                                    <Badge className={service.status === 'running' ? 'bg-green-500' : 'bg-red-500'}>
                                        {service.status}
                                    </Badge>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="text-sm"><span className="text-muted-foreground">Port:</span> {service.port}</div>
                                {service.uptime_seconds > 0 && <div className="text-sm"><span className="text-muted-foreground">Uptime:</span> {Math.floor(service.uptime_seconds / 60)}m</div>}
                                <div className="flex gap-2">
                                    {service.status === 'running' ? (
                                        <>
                                            <Button size="sm" variant="destructive" className="flex-1" onClick={() => controlService(service.name, 'stop')}>
                                                <Square className="mr-1 h-3 w-3" /> Stop
                                            </Button>
                                            <Button size="sm" variant="outline" className="flex-1" onClick={() => controlService(service.name, 'restart')}>
                                                <RotateCw className="mr-1 h-3 w-3" /> Restart
                                            </Button>
                                        </>
                                    ) : (
                                        <Button size="sm" className="flex-1" onClick={() => controlService(service.name, 'start')}>
                                            <Power className="mr-1 h-3 w-3" /> Start
                                        </Button>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <AlertDialog open={shutdownDialogOpen} onOpenChange={setShutdownDialogOpen}>
                    <AlertDialogContent>
                        <AlertDialogHeader>
                            <AlertDialogTitle>Confirm {shutdownType.charAt(0).toUpperCase() + shutdownType.slice(1)} Shutdown</AlertDialogTitle>
                            <AlertDialogDescription>
                                This will shutdown all services. Are you sure?
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={() => stopAllServices(shutdownType)} className={shutdownType === 'emergency' ? 'bg-red-600' : ''}>
                                Confirm
                            </AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>
            </div>
        </div>
    );
}