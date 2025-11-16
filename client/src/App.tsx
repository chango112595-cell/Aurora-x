import { Route, Switch } from "wouter";
import AuroraFuturisticLayout from "./components/AuroraFuturisticLayout";
import Dashboard from "./pages/dashboard";
import ChatPage from "./pages/chat";
import Tasks from "./pages/tasks";
import Tiers from "./pages/tiers";
import Intelligence from "./pages/intelligence";
import Evolution from "./pages/evolution";
import Autonomous from "./pages/autonomous";
import Monitoring from "./pages/monitoring";
import Database from "./pages/database";
import Settings from "./pages/settings";

function App() {
  return (
    <AuroraFuturisticLayout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/chat" component={ChatPage} />
        <Route path="/tasks" component={Tasks} />
        <Route path="/tiers" component={Tiers} />
        <Route path="/intelligence" component={Intelligence} />
        <Route path="/evolution" component={Evolution} />
        <Route path="/autonomous" component={Autonomous} />
        <Route path="/monitoring" component={Monitoring} />
        <Route path="/database" component={Database} />
        <Route path="/settings" component={Settings} />
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
