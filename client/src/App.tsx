'use client';

import { Route, Switch } from "wouter";
import AuroraFuturisticLayout from "./components/AuroraFuturisticLayout";
import Dashboard from "./pages/dashboard";
import Home from "./pages/home";
import Chat from "./pages/chat";
import Corpus from "./pages/corpus";
import SelfLearning from "./pages/self-learning";
import ServerControl from "./pages/server-control";
import Library from "./pages/library";
import Settings from "./pages/settings";
import AuroraUI from "./pages/aurora-ui";
import ComparisonDashboard from "./pages/ComparisonDashboard";
import LuminarNexus from "./pages/luminar-nexus";
import Autonomous from "./pages/autonomous";
import Monitoring from "./pages/monitoring";
import Database from "./pages/database";
import Evolution from "./pages/evolution";
import Tasks from "./pages/tasks";
import Tiers from "./pages/tiers";
import Intelligence from "./pages/intelligence";
import NotFound from "./pages/not-found";

function App() {
  return (
    <AuroraFuturisticLayout>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/chat" component={Chat} />
        <Route path="/library" component={Library} />
        <Route path="/comparison" component={ComparisonDashboard} />
        <Route path="/luminar-nexus" component={LuminarNexus} />
        <Route path="/servers" component={ServerControl} />
        <Route path="/self-learning" component={SelfLearning} />
        <Route path="/corpus" component={Corpus} />
        <Route path="/autonomous" component={Autonomous} />
        <Route path="/monitoring" component={Monitoring} />
        <Route path="/database" component={Database} />
        <Route path="/settings" component={Settings} />
        <Route path="/tasks" component={Tasks} />
        <Route path="/tiers" component={Tiers} />
        <Route path="/evolution" component={Evolution} />
        <Route path="/intelligence" component={Intelligence} />
        <Route path="/aurora-ui" component={AuroraUI} />
        <Route component={NotFound} />
      </Switch>
    </AuroraFuturisticLayout>
  );
}

export default App;
