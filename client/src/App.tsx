import { Route, Switch } from "wouter";
import AuroraFuturisticLayout from "./components/AuroraFuturisticLayout";
import Dashboard from "./pages/dashboard";
import ChatPage from "./pages/chat";
import TasksPage from "./pages/tasks";
import TiersPage from "./pages/tiers";
import IntelligencePage from "./pages/intelligence";
import EvolutionPage from "./pages/evolution";
import AutonomousPage from "./pages/autonomous";
import MonitoringPage from "./pages/monitoring";
import DatabasePage from "./pages/database";
import SettingsPage from "./pages/settings";

function App() {
  return (
    <AuroraFuturisticLayout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/chat" component={ChatPage} />
        <Route path="/tasks" component={TasksPage} />
        <Route path="/tiers" component={TiersPage} />
        <Route path="/intelligence" component={IntelligencePage} />
        <Route path="/evolution" component={EvolutionPage} />
        <Route path="/autonomous" component={AutonomousPage} />
        <Route path="/monitoring" component={MonitoringPage} />
        <Route path="/database" component={DatabasePage} />
        <Route path="/settings" component={SettingsPage} />
        <Route>
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
                404 - Quantum Path Not Found
              </h1>
              <p className="text-purple-400">This neural pathway doesn't exist yet.</p>
            </div>
          </div>
        </Route>
      </Switch>
    </AuroraFuturisticLayout>
  );
}

export default App;
