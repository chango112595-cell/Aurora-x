import { Switch, Route } from "wouter";
import { useEffect, useState } from "react";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import { AppSidebar } from "@/components/app-sidebar";
import { ErrorBoundary } from "@/components/error-boundary";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import NotFound from "@/pages/not-found";
import Home from "@/pages/home";
import Dashboard from "@/pages/dashboard";
import Library from "@/pages/library";
import Corpus from "@/pages/corpus";
import Settings from "@/pages/settings";
import SelfLearning from "@/pages/self-learning";
import ComparisonDashboard from "@/pages/ComparisonDashboard";
import LuminarNexus from "@/pages/luminar-nexus";
import ServerControl from "@/pages/server-control";
import ChatPage from "@/pages/chat";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/comparison" component={ComparisonDashboard} />
      <Route path="/luminar" component={LuminarNexus} />
      <Route path="/servers" component={ServerControl} />
      <Route path="/library" component={Library} />
      <Route path="/corpus" component={Corpus} />
      <Route path="/self-learning" component={SelfLearning} />
      <Route path="/settings" component={Settings} />
      <Route path="/chat" component={ChatPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showInstallButton, setShowInstallButton] = useState(false);
  const { toast } = useToast();
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected');

  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  useEffect(() => {
    // Service worker disabled - was caching old UI and blocking updates
    // Unregister existing service worker if present
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        for (let registration of registrations) {
          registration.unregister();
          console.log('🌟 Aurora: Unregistered service worker to allow updates');
        }
      });
    }

    // Original service worker code commented out - it was blocking UI updates
    /*
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker
          .register('/sw.js')
          .then((registration) => {
            console.log('Service Worker registered:', registration);

            // Check for updates periodically
            setInterval(() => {
              registration.update();
            }, 60000); // Check every minute

            // Handle service worker updates
            registration.addEventListener('updatefound', () => {
              const newWorker = registration.installing;
              if (newWorker) {
                newWorker.addEventListener('statechange', () => {
                  if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    toast({
                      title: "Update Available",
                      description: "A new version of Aurora-X is available. Reload to update.",
                      action: (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.location.reload()}
                        >
                          Reload
                        </Button>
                      ),
                    });
                  }
                });
              }
            });
          })
          .catch((error) => {
            console.error('Service Worker registration failed:', error);
          });
      });
    }
    */

    // Handle PWA install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallButton(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Handle app installed
    window.addEventListener('appinstalled', () => {
      setShowInstallButton(false);
      setDeferredPrompt(null);
      toast({
        title: "App Installed",
        description: "Aurora-X has been installed successfully!",
      });
    });

    // Monitor WebSocket connection status in development
    if (import.meta.env.DEV) {
      const checkConnection = () => {
        fetch('/api/health')
          .then(res => res.ok ? setConnectionStatus('connected') : setConnectionStatus('disconnected'))
          .catch(() => setConnectionStatus('disconnected'));
      };

      checkConnection();
      const interval = setInterval(checkConnection, 10000);

      return () => {
        clearInterval(interval);
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      };
    } else {
      return () => {
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      };
    }
  }, [toast]);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }

    setDeferredPrompt(null);
    setShowInstallButton(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <SidebarProvider style={style as React.CSSProperties} defaultOpen={true}>
            <div className="flex h-screen w-full">
              <AppSidebar />
              <div className="flex flex-col flex-1">
                <header className="flex items-center justify-between p-4 border-b border-border">
                  <div className="flex items-center gap-2">
                    <SidebarTrigger data-testid="button-sidebar-toggle" />
                    {showInstallButton && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleInstallClick}
                        className="gap-2"
                        data-testid="button-install-pwa"
                      >
                        <Download className="h-4 w-4" />
                        Install App
                      </Button>
                    )}
                  </div>
                  <ThemeToggle />
                </header>
                <main className="flex-1 overflow-hidden">
                  {import.meta.env.DEV && connectionStatus === 'disconnected' && (
                    <div className="bg-yellow-500 text-black px-4 py-2 text-sm text-center">
                      ⚠️ Server connection lost. Attempting to reconnect...
                    </div>
                  )}
                  <ErrorBoundary>
                    <Router />
                  </ErrorBoundary>
                </main>
              </div>
            </div>
          </SidebarProvider>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;