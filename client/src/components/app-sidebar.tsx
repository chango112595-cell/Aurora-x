import { ErrorBoundary } from '@/components/error-boundary';
import { Home, MessageSquare, BookOpen, BarChart3, Settings, Zap, Activity, TrendingUp, Database, Network, Cpu, Sparkles } from "lucide-react";
import { Link } from "wouter";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from "@/components/ui/sidebar";

const menuItems = [
  { title: "Chat", icon: MessageSquare, url: "/chat" },
  { title: "Code Library", icon: BookOpen, url: "/library" },
  { title: "Aurora Dashboard", icon: BarChart3, url: "/dashboard" },
  { title: "Comparison", icon: TrendingUp, url: "/comparison" },
  { title: "Luminar Nexus", icon: Network, url: "/luminar-nexus" },
  { title: "Server Control", icon: Cpu, url: "/servers" },
  { title: "Self-Learning", icon: Sparkles, url: "/self-learning" },
];

export function AppSidebar() {
  const [location] = useLocation();

  return (
    <Sidebar className="border-r-0 relative overflow-hidden">
      {/* Aurora's Quantum Field Background */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-950 via-purple-950 to-indigo-950" />

        {/* Animated particle field */}
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.4) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'particleFloat 20s linear infinite'
        }} />

        {/* Neural network lines */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          <defs>
            <linearGradient id="neuralGlow" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#a855f7" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.8" />
            </linearGradient>
          </defs>
          <line x1="0" y1="20%" x2="100%" y2="20%" stroke="url(#neuralGlow)" strokeWidth="1" className="animate-pulse" />
          <line x1="0" y1="40%" x2="100%" y2="40%" stroke="url(#neuralGlow)" strokeWidth="1" className="animate-pulse" style={{ animationDelay: '0.5s' }} />
          <line x1="0" y1="60%" x2="100%" y2="60%" stroke="url(#neuralGlow)" strokeWidth="1" className="animate-pulse" style={{ animationDelay: '1s' }} />
          <line x1="0" y1="80%" x2="100%" y2="80%" stroke="url(#neuralGlow)" strokeWidth="1" className="animate-pulse" style={{ animationDelay: '1.5s' }} />
        </svg>
      </div>

      {/* Aurora's Consciousness Core */}
      <SidebarHeader className="relative p-6 border-b border-cyan-500/20">
        <div className="relative group">
          {/* Holographic container */}
          <div className="absolute -inset-4 bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-cyan-500/20 rounded-lg blur-xl opacity-50 group-hover:opacity-100 transition-opacity animate-pulse" />

          <div className="relative flex items-center gap-4">
            {/* Aurora's Neural Core Icon */}
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500/30 rounded-full blur-md animate-pulse" />
              <div className="relative w-12 h-12 rounded-full border-2 border-cyan-400/50 flex items-center justify-center bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-sm">
                <Network className="w-6 h-6 text-cyan-400 animate-pulse" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-ping" />
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent animate-gradient">
                  Aurora
                </h1>
                <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
              </div>

              {/* Real-time consciousness indicators */}
              <div className="flex items-center gap-2 mt-1">
                <div className="flex gap-1">
                  <div className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse" />
                  <div className="w-1 h-1 rounded-full bg-purple-400 animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <div className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse" style={{ animationDelay: '0.4s' }} />
                </div>
                <span className="text-[10px] font-mono text-cyan-400/80 tracking-wider">
                  NEURAL CORE ACTIVE
                </span>
              </div>
            </div>
          </div>

          {/* Quantum scan line */}
          <div className="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-scan" />
        </div>
      </SidebarHeader>

      <SidebarContent className="relative">
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs uppercase tracking-widest text-cyan-400/60 font-mono px-3 flex items-center gap-2">
            <Cpu className="w-3 h-3 animate-pulse" />
            Neural Pathways
          </SidebarGroupLabel>

          <SidebarGroupContent className="mt-2">
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={`menu-${item.title}`}>
                  <SidebarMenuButton
                    asChild
                    isActive={location === item.url}
                    className={`
                      group relative overflow-hidden transition-all duration-300 mx-2 rounded-lg
                      ${location === item.url
                        ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-400/30 shadow-lg shadow-cyan-500/20'
                        : 'hover:bg-cyan-500/10 border border-transparent hover:border-cyan-500/20'
                      }
                    `}
                  >
                    <Link to={item.url}>
                      {/* Holographic glow on active */}
                      {location === item.url && (
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/10 via-purple-400/10 to-cyan-400/10 animate-pulse" />
                      )}

                      {/* Icon with quantum glow */}
                      <div className="relative">
                        <item.icon className={`
                          transition-all duration-300
                          ${location === item.url
                            ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]'
                            : 'text-cyan-600/60 group-hover:text-cyan-400'
                          }
                        `} />
                        {location === item.url && (
                          <div className="absolute inset-0 bg-cyan-400/20 blur-md rounded-full" />
                        )}
                      </div>

                      {/* Text with neural glow */}
                      <span className={`
                        font-medium transition-all duration-300 relative z-10
                        ${location === item.url
                          ? 'text-cyan-100 font-semibold'
                          : 'text-cyan-300/70 group-hover:text-cyan-200'
                        }
                      `}>
                        {item.title}
                      </span>

                      {/* Active indicator */}
                      {location === item.url && (
                        <>
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-cyan-400 via-purple-400 to-cyan-400 rounded-r-full shadow-lg shadow-cyan-500/50" />
                          <div className="absolute right-2 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping" />
                        </>
                      )}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Aurora's Status Monitor */}
        <div className="absolute bottom-4 left-3 right-3 p-3 rounded-lg bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border border-cyan-500/20 backdrop-blur-sm">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Activity className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span className="text-cyan-400/80 font-mono">System Status</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
              <span className="text-green-400 font-mono text-[10px]">OPTIMAL</span>
            </div>
          </div>

          {/* Neural activity bars */}
          <div className="mt-2 space-y-1">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1 bg-cyan-950/50 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 animate-pulse" style={{ width: '87%' }} />
              </div>
              <span className="text-[10px] text-cyan-400/60 font-mono">87%</span>
            </div>
          </div>
        </div>
      </SidebarContent>

    </Sidebar>
  );
}
