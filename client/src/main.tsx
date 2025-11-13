import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { Route, Switch } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import Home from "@/pages/home";
import Dashboard from "@/pages/dashboard";
import Chat from "@/pages/chat";
import Corpus from "@/pages/corpus";
import SelfLearning from "@/pages/self-learning";
import ServerControl from "@/pages/server-control";
import Library from "@/pages/library";
import Settings from "@/pages/settings";
import AuroraUI from "@/pages/aurora-ui";
import ComparisonDashboard from "@/pages/ComparisonDashboard";
import LuminarNexus from "@/pages/luminar-nexus";

console.log('🌟 Aurora: Starting React app...');

const rootElement = document.getElementById("root");

if (!rootElement) {
  console.error('❌ Aurora: Root element not found! Cannot mount React app.');
  document.body.innerHTML = '<h1>ERROR: React root element not found</h1>';
} else {
  try {
    console.log('🌟 Aurora: Mounting React app to root element...');
    createRoot(rootElement).render(
      <QueryClientProvider client={queryClient}>
        <App>
          <Switch>
            <Route path="/" component={Home} />
            <Route path="/dashboard" component={Dashboard} />
            <Route path="/chat" component={Chat} />
            <Route path="/corpus" component={Corpus} />
            <Route path="/self-learning" component={SelfLearning} />
            <Route path="/server-control" component={ServerControl} />
            <Route path="/library" component={Library} />
            <Route path="/settings" component={Settings} />
            <Route path="/aurora-ui" component={AuroraUI} />
            <Route path="/comparison" component={ComparisonDashboard} />
            <Route path="/luminar-nexus" component={LuminarNexus} />
            <Route component={NotFound} />
          </Switch>
        </App>
        <Toaster />
      </QueryClientProvider>
    );
    console.log('✅ Aurora: React app mounted successfully!');
  } catch (error) {
    console.error('❌ Aurora: Failed to render app:', error);
    rootElement.innerHTML = `<div style="padding: 20px; color: red;"><h1>Application Error</h1><p>${error instanceof Error ? error.message : 'Unknown error'}</p></div>`;
  }
}