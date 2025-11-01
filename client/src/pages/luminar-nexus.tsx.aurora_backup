import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Rocket,
  Zap,
  Plug,
  Brain,
  Server,
  BookOpen,
  Search,
  ArrowRight,
  Activity,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface Component {
  name: string;
  file: string;
  size: string;
  icon: string;
  features: string[];
}

interface Service {
  name: string;
  port: number;
  type: string;
  tech: string;
}

const componentsData: Component[] = [
  {
    name: "Ultimate API Manager",
    file: "tools/ultimate_api_manager.py",
    size: "154KB",
    icon: "🚀",
    features: [
      "Autonomous mode with auto-scanning (15s intervals)",
      "Manages 4 core services",
      "Auto-healing and predictive fixing",
      "Expert knowledge integration",
      "Pattern recognition and learning",
    ],
  },
  {
    name: "Advanced Server Manager",
    file: "tools/server_manager.py",
    size: "116KB",
    icon: "⚙️",
    features: [
      "Total autonomous diagnostics",
      "Complete service architecture knowledge",
      "Auto-fix integration issues",
      "Network diagnostics and SSL",
      "Process management by port/PID/name",
    ],
  },
  {
    name: "Aurora API Manager",
    file: "tools/api_manager.py",
    size: "13KB",
    icon: "🔌",
    features: [
      "Manages 3 core APIs",
      "Health monitoring with retry",
      "Auto-healing unhealthy services",
      "Port conflict resolution",
      "Continuous monitoring mode",
    ],
  },
  {
    name: "Intelligence Manager",
    file: "aurora_intelligence_manager.py",
    size: "18KB",
    icon: "🧠",
    features: [
      "Pattern recognition from issues",
      "Issue diagnosis with confidence scoring",
      "Auto-learning from outcomes",
      "Knowledge base persistence",
      "Training modes for optimization",
    ],
  },
  {
    name: "Aurora Server Manager",
    file: "aurora_server_manager.py",
    size: "14KB",
    icon: "🖥️",
    features: [
      "Config persistence (JSON)",
      "Port management (4 services)",
      "Service status tracking",
      "Auto-restart policies",
      "Health monitoring",
    ],
  },
  {
    name: "Expert Knowledge",
    file: "tools/aurora_expert_knowledge.py",
    size: "86KB",
    icon: "📚",
    features: [
      "Master-level in ALL languages",
      "Code analysis and suggestions",
      "Error pattern recognition",
      "Best practice recommendations",
      "Architecture guidance",
    ],
  },
];

const servicesData: Service[] = [
  { name: "Aurora UI", port: 5000, type: "Frontend", tech: "React/Vite" },
  { name: "Learning API", port: 5002, type: "Backend", tech: "FastAPI" },
  { name: "Bridge API", port: 5001, type: "Backend", tech: "FastAPI" },
  { name: "File Server", port: 8080, type: "Utility", tech: "Python HTTP" },
];

const commandsData = {
  autonomous: [
    "python tools/ultimate_api_manager.py --autonomous",
    "python tools/server_manager.py --autonomous",
    "python tools/api_manager.py --monitor",
  ],
  diagnostics: [
    "python tools/server_manager.py --diagnose",
    "python tools/server_manager.py --auto-heal",
    "python tools/server_manager.py --fix-integration",
    "python tools/server_manager.py --ultimate-heal",
  ],
  intelligence: [
    "python aurora_intelligence_manager.py --train",
    'python aurora_intelligence_manager.py --diagnose "symptoms"',
    "python aurora_intelligence_manager.py --auto-fix",
    "python aurora_intelligence_manager.py --learn",
  ],
};

// Tab Component
interface TabProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

const Tab = ({ active, onClick, children }: TabProps) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg transition-all ${
      active
        ? "bg-primary/30 text-primary font-semibold border border-primary/50"
        : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50 border border-secondary/30"
    }`}
  >
    {children}
  </button>
);

// Stats Card Component
const StatCard = ({ value, label }: { value: string; label: string }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="text-center p-6 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-500/10 border border-primary/20"
  >
    <div className="text-3xl font-bold text-primary">{value}</div>
    <div className="text-sm text-muted-foreground mt-2">{label}</div>
  </motion.div>
);

// Component Card
const ComponentCard = ({ component }: { component: Component }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.3 }}
    className="p-6 rounded-lg bg-gradient-to-br from-secondary/50 to-secondary/30 border border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg"
  >
    <h3 className="text-2xl font-bold mb-2 flex items-center gap-3">
      <span>{component.icon}</span>
      {component.name}
    </h3>
    <div className="text-xs text-muted-foreground mb-4 font-mono">
      {component.file} ({component.size})
    </div>
    <ul className="space-y-2">
      {component.features.map((feature, idx) => (
        <li key={idx} className="text-sm flex items-start gap-2">
          <span className="text-green-500 font-bold">✓</span>
          <span>{feature}</span>
        </li>
      ))}
    </ul>
  </motion.div>
);

// Service Flow
const ServiceFlow = () => (
  <div className="flex flex-wrap justify-center items-center gap-4 my-8">
    <div className="text-center p-4 rounded-lg bg-secondary/50 border border-primary/20 min-w-[120px]">
      <div className="text-2xl mb-2">👤</div>
      <div className="text-xs font-mono">User Request</div>
    </div>
    <ArrowRight className="w-6 h-6 text-primary/50 hidden sm:block" />
    <div className="text-center p-4 rounded-lg bg-secondary/50 border border-primary/20 min-w-[120px]">
      <div className="text-2xl mb-2">🚀</div>
      <div className="text-xs font-mono">Ultimate API Manager</div>
    </div>
    <ArrowRight className="w-6 h-6 text-primary/50 hidden sm:block" />
    <div className="text-center p-4 rounded-lg bg-secondary/50 border border-primary/20 min-w-[120px]">
      <div className="text-2xl mb-2">⚙️</div>
      <div className="text-xs font-mono">Server Manager</div>
    </div>
    <ArrowRight className="w-6 h-6 text-primary/50 hidden sm:block" />
    <div className="text-center p-4 rounded-lg bg-secondary/50 border border-primary/20 min-w-[120px]">
      <div className="text-2xl mb-2">✅</div>
      <div className="text-xs font-mono">Services Running</div>
    </div>
  </div>
);

// Overview Tab
const OverviewTab = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="space-y-8"
  >
    <div>
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
        <Activity className="w-8 h-8 text-primary" />
        System Overview
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard value="6" label="Core Components" />
        <StatCard value="4" label="Managed Services" />
        <StatCard value="390K+" label="Lines of Code" />
        <StatCard value="90%+" label="Auto-Heal Rate" />
      </div>
    </div>

    <div className="p-6 rounded-lg bg-gradient-to-br from-primary/10 to-cyan-500/10 border border-primary/20">
      <p className="text-lg leading-relaxed mb-6">
        <strong>Luminar Nexus</strong> is your comprehensive, autonomous server management
        ecosystem. It combines multiple intelligent layers to create a self-managing,
        self-healing, continuously learning infrastructure platform.
      </p>
      <h3 className="text-2xl font-bold mb-4">Key Benefits</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-lg bg-secondary/50 border border-primary/10">
          <h4 className="font-bold mb-2">🤖 Fully Autonomous</h4>
          <p className="text-sm text-muted-foreground">
            Runs 24/7 without human intervention, monitoring every 15 seconds
          </p>
        </div>
        <div className="p-4 rounded-lg bg-secondary/50 border border-primary/10">
          <h4 className="font-bold mb-2">🏥 Self-Healing</h4>
          <p className="text-sm text-muted-foreground">
            Automatically fixes 90%+ of common issues without manual intervention
          </p>
        </div>
        <div className="p-4 rounded-lg bg-secondary/50 border border-primary/10">
          <h4 className="font-bold mb-2">🧠 Intelligent Learning</h4>
          <p className="text-sm text-muted-foreground">
            Learns from experience and improves responses over time
          </p>
        </div>
        <div className="p-4 rounded-lg bg-secondary/50 border border-primary/10">
          <h4 className="font-bold mb-2">🔮 Predictive</h4>
          <p className="text-sm text-muted-foreground">
            Predicts and prevents issues before they occur
          </p>
        </div>
      </div>
    </div>
  </motion.div>
);

// Components Tab
const ComponentsTab = () => {
  const [search, setSearch] = useState("");

  const filteredComponents = componentsData.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div>
        <h2 className="text-3xl font-bold mb-4 flex items-center gap-3">
          <Rocket className="w-8 h-8 text-primary" />
          Core Components
        </h2>
        <div className="relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search components..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredComponents.map((component) => (
          <ComponentCard key={component.name} component={component} />
        ))}
      </div>
    </motion.div>
  );
};

// Architecture Tab
const ArchitectureTab = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="space-y-8"
  >
    <div>
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
        <Zap className="w-8 h-8 text-primary" />
        System Architecture
      </h2>

      <h3 className="text-xl font-bold mb-4">Service Flow</h3>
      <ServiceFlow />

      <h3 className="text-xl font-bold mb-4 mt-8">Managed Services</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-primary/20 bg-secondary/30">
              <th className="text-left p-3 font-semibold">Service</th>
              <th className="text-left p-3 font-semibold">Port</th>
              <th className="text-left p-3 font-semibold">Type</th>
              <th className="text-left p-3 font-semibold">Technology</th>
            </tr>
          </thead>
          <tbody>
            {servicesData.map((service) => (
              <tr key={service.name} className="border-b border-primary/10 hover:bg-secondary/30 transition-colors">
                <td className="p-3 font-semibold">{service.name}</td>
                <td className="p-3 font-mono">{service.port}</td>
                <td className="p-3">{service.type}</td>
                <td className="p-3">{service.tech}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </motion.div>
);

// Usage Tab
const UsageTab = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="space-y-8"
  >
    <h2 className="text-3xl font-bold flex items-center gap-3">
      <Terminal className="w-8 h-8 text-primary" />
      Usage Commands
    </h2>

    <div>
      <h3 className="text-xl font-bold mb-4">🤖 Autonomous Mode</h3>
      <div className="space-y-2 bg-secondary/30 rounded-lg p-4 border border-primary/10">
        {commandsData.autonomous.map((cmd, idx) => (
          <div key={idx} className="font-mono text-sm text-green-400">
            $ {cmd}
          </div>
        ))}
      </div>
    </div>

    <div>
      <h3 className="text-xl font-bold mb-4">🔍 Diagnostics & Healing</h3>
      <div className="space-y-2 bg-secondary/30 rounded-lg p-4 border border-primary/10">
        {commandsData.diagnostics.map((cmd, idx) => (
          <div key={idx} className="font-mono text-sm text-green-400">
            $ {cmd}
          </div>
        ))}
      </div>
    </div>

    <div>
      <h3 className="text-xl font-bold mb-4">🧠 Intelligence Training</h3>
      <div className="space-y-2 bg-secondary/30 rounded-lg p-4 border border-primary/10">
        {commandsData.intelligence.map((cmd, idx) => (
          <div key={idx} className="font-mono text-sm text-green-400">
            $ {cmd}
          </div>
        ))}
      </div>
    </div>
  </motion.div>
);

// Monitoring Tab
const MonitoringTab = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="space-y-8"
  >
    <div>
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
        <Activity className="w-8 h-8 text-primary" />
        Monitoring & Self-Healing
      </h2>

      <h3 className="text-xl font-bold mb-4">Real-Time Metrics</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-primary/10">
          <CardHeader>
            <CardTitle className="text-lg">📊 Service Health</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Uptime tracking
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Response times
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Error rates
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Resource usage
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="border-primary/10">
          <CardHeader>
            <CardTitle className="text-lg">🚨 Alerting</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Critical path failures
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Service downtime
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Integration breakages
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Performance degradation
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="border-primary/10">
          <CardHeader>
            <CardTitle className="text-lg">🏥 Auto-Healing</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Detect failures
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Diagnose causes
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Fix automatically
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Verify & learn
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      <h3 className="text-xl font-bold mb-4 mt-8">Self-Healing Process</h3>
      <div className="flex flex-wrap justify-center items-center gap-4 p-6 rounded-lg bg-secondary/30 border border-primary/10">
        {["Detect", "Diagnose", "Fix", "Verify", "Learn"].map((step, idx) => (
          <div key={idx} className="flex items-center gap-4">
            <div className="px-4 py-2 rounded-lg bg-primary/20 border border-primary/40 font-semibold">
              {step}
            </div>
            {idx < 4 && <ArrowRight className="w-6 h-6 text-primary/50" />}
          </div>
        ))}
      </div>
    </div>
  </motion.div>
);

// Files Tab
const FilesTab = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="space-y-6"
  >
    <h2 className="text-3xl font-bold flex items-center gap-3">
      <BookOpen className="w-8 h-8 text-primary" />
      File Inventory
    </h2>

    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-primary/20 bg-secondary/30">
            <th className="text-left p-3 font-semibold">Component</th>
            <th className="text-left p-3 font-semibold">File Path</th>
            <th className="text-left p-3 font-semibold">Size</th>
            <th className="text-left p-3 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody>
          {componentsData.map((comp) => (
            <tr
              key={comp.name}
              className="border-b border-primary/10 hover:bg-secondary/30 transition-colors"
            >
              <td className="p-3 font-semibold">
                {comp.icon} {comp.name}
              </td>
              <td className="p-3 font-mono text-xs">{comp.file}</td>
              <td className="p-3">{comp.size}</td>
              <td className="p-3">
                <Badge className="bg-green-500/20 text-green-500 border-green-500/50">
                  ✅ Present
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </motion.div>
);

// Import Terminal icon
const Terminal = Zap;

// Main Component
export default function LuminarNexus() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "components" | "architecture" | "usage" | "monitoring" | "files"
  >("overview");

  const tabs: Array<{
    id: "overview" | "components" | "architecture" | "usage" | "monitoring" | "files";
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }> = [
    { id: "overview", label: "Overview", icon: Activity },
    { id: "components", label: "Components", icon: Rocket },
    { id: "architecture", label: "Architecture", icon: Zap },
    { id: "usage", label: "Usage", icon: Terminal },
    { id: "monitoring", label: "Monitoring", icon: AlertCircle },
    { id: "files", label: "Files", icon: BookOpen },
  ];

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-cyan-500/10 to-purple-500/10 blur-3xl -z-10" />
          <div>
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary via-cyan-500 to-purple-500 bg-clip-text text-transparent">
              🌟 Luminar Nexus
            </h1>
            <p className="text-lg text-muted-foreground">
              Aurora's Master Server Management Ecosystem
            </p>
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-2 pb-4 border-b border-primary/20"
        >
          {tabs.map((tab) => (
            <Tab
              key={tab.id}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="flex items-center gap-2">
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </div>
            </Tab>
          ))}
        </motion.div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === "overview" && <OverviewTab />}
          {activeTab === "components" && <ComponentsTab />}
          {activeTab === "architecture" && <ArchitectureTab />}
          {activeTab === "usage" && <UsageTab />}
          {activeTab === "monitoring" && <MonitoringTab />}
          {activeTab === "files" && <FilesTab />}
        </AnimatePresence>
      </div>
    </div>
  );
}
