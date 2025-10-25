import { MessageSquare, Code2, Activity, Database, Settings, Zap } from "lucide-react";
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
  SidebarFooter,
} from "@/components/ui/sidebar";
import { useLocation, Link } from "wouter";

const menuItems = [
  {
    title: "Chat",
    url: "/",
    icon: MessageSquare,
  },
  {
    title: "Code Library",
    url: "/library",
    icon: Code2,
  },
  {
    title: "Aurora Dashboard",
    url: "/dashboard",
    icon: Activity,
  },
];

const bottomItems = [
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
];

export function AppSidebar() {
  const [location] = useLocation();

  return (
    <Sidebar className="relative overflow-hidden border-r border-primary/20 bg-gradient-to-b from-background via-background to-primary/5">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-[0.15] pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.3) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(6, 182, 212, 0.3) 1px, transparent 1px)`,
          backgroundSize: '30px 30px',
          animation: 'gridPulse 4s ease-in-out infinite'
        }} />
      </div>

      {/* Floating orbs */}
      <div className="absolute top-10 left-4 w-32 h-32 bg-primary/10 rounded-full blur-3xl animate-pulse pointer-events-none" />
      <div className="absolute bottom-20 right-4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl animate-pulse pointer-events-none" style={{ animationDelay: '1s' }} />

      <SidebarHeader className="relative border-b border-primary/20 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-3 group">
          <div className="relative">
            <Activity className="h-8 w-8 text-primary animate-pulse" />
            <Zap className="h-4 w-4 text-cyan-400 absolute -top-1 -right-1 animate-bounce" />
          </div>
          <div>
            <h2 className="text-xl font-bold bg-gradient-to-r from-primary via-cyan-400 to-primary bg-clip-text text-transparent">
              Chango
            </h2>
            <p className="text-[10px] text-muted-foreground font-mono">
              <span className="text-primary animate-pulse">●</span> Aurora-X Ultra
            </p>
          </div>
        </div>

        {/* Scan line effect */}
        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary to-transparent animate-scan" />
      </SidebarHeader>

      <SidebarContent className="relative">
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs uppercase tracking-wider text-primary/70 font-mono flex items-center gap-2">
            <div className="w-1 h-1 bg-primary rounded-full animate-ping" />
            <div className="w-1 h-1 bg-primary rounded-full animate-ping" style={{ animationDelay: '0.2s' }} />
            <div className="w-1 h-1 bg-primary rounded-full animate-ping" style={{ animationDelay: '0.4s' }} />
            <span className="ml-2">Navigation</span>
          </SidebarGroupLabel>
          <SidebarGroupContent className="mt-2">
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={location === item.url}
                    data-testid={`link-${item.title.toLowerCase().replace(' ', '-')}`}
                    className={`
                      group relative overflow-hidden transition-all duration-300
                      ${location === item.url
                        ? 'bg-gradient-to-r from-primary/20 to-cyan-500/10 border-l-2 border-primary shadow-lg shadow-primary/20'
                        : 'hover:bg-primary/5 hover:border-l-2 hover:border-primary/50'
                      }
                    `}
                  >
                    <Link to={item.url}>
                      <div className="flex items-center gap-3 relative z-10">
                        <item.icon className={`h-4 w-4 transition-all duration-300 ${
                          location === item.url
                            ? 'text-primary animate-pulse'
                            : 'text-muted-foreground group-hover:text-primary group-hover:scale-110'
                        }`} />
                        <span className={`font-mono text-sm ${
                          location === item.url
                            ? 'text-primary font-semibold'
                            : 'group-hover:text-primary'
                        }`}>
                          {item.title}
                        </span>
                      </div>
                      {location === item.url && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent animate-shimmer" />
                      )}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="relative border-t border-primary/20 p-6 backdrop-blur-sm">
        <SidebarMenu>
          {bottomItems.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton
                asChild
                isActive={location === item.url}
                data-testid={`link-${item.title.toLowerCase()}`}
                className={`
                  group relative overflow-hidden transition-all duration-300
                  ${location === item.url
                    ? 'bg-gradient-to-r from-primary/20 to-cyan-500/10 border-l-2 border-primary shadow-lg shadow-primary/20'
                    : 'hover:bg-primary/5 hover:border-l-2 hover:border-primary/50'
                  }
                `}
              >
                <Link to={item.url}>
                  <div className="flex items-center gap-3 relative z-10">
                    <item.icon className={`h-4 w-4 transition-all duration-300 ${
                      location === item.url
                        ? 'text-primary animate-pulse'
                        : 'text-muted-foreground group-hover:text-primary group-hover:scale-110'
                    }`} />
                    <span className={`font-mono text-sm ${
                      location === item.url
                        ? 'text-primary font-semibold'
                        : 'group-hover:text-primary'
                    }`}>
                      {item.title}
                    </span>
                  </div>
                  {location === item.url && (
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent animate-shimmer" />
                  )}
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>

        {/* Bottom scan line */}
        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary to-transparent animate-scan" style={{ animationDelay: '2s' }} />
      </SidebarFooter>

      <style jsx>{`
        @keyframes gridPulse {
          0%, 100% { opacity: 0.15; }
          50% { opacity: 0.25; }
        }
        @keyframes scan {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-scan {
          animation: scan 3s linear infinite;
        }
        .animate-shimmer {
          animation: shimmer 2s linear infinite;
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </Sidebar>
  );
}