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
    <Sidebar className="relative overflow-hidden border-r border-primary/40 bg-gradient-to-b from-background via-primary/5 to-primary/10 dark:from-background dark:via-background dark:to-primary/5">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-30 dark:opacity-[0.15] pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.5) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(6, 182, 212, 0.5) 1px, transparent 1px)`,
          backgroundSize: '30px 30px',
          animation: 'gridPulse 4s ease-in-out infinite'
        }} />
      </div>

      {/* Floating orbs */}
      <div className="absolute top-10 left-4 w-32 h-32 bg-primary/25 dark:bg-primary/10 rounded-full blur-3xl animate-pulse pointer-events-none" />
      <div className="absolute bottom-20 right-4 w-24 h-24 bg-cyan-500/25 dark:bg-cyan-500/10 rounded-full blur-2xl animate-pulse pointer-events-none" style={{ animationDelay: '1s' }} />

      <SidebarHeader className="relative border-b border-primary/40 p-6 backdrop-blur-sm bg-gradient-to-r from-primary/5 to-cyan-500/5">
        <div className="flex items-center gap-3 group">
          <div className="relative">
            <Activity className="h-8 w-8 text-primary drop-shadow-lg animate-pulse" />
            <Zap className="h-4 w-4 text-cyan-500 dark:text-cyan-400 absolute -top-1 -right-1 animate-bounce drop-shadow-md" />
          </div>
          <div>
            <h2 className="text-xl font-bold bg-gradient-to-r from-primary via-cyan-500 to-primary bg-clip-text text-transparent drop-shadow-sm">
              Chango
            </h2>
            <p className="text-[10px] text-muted-foreground font-mono font-semibold">
              <span className="text-primary animate-pulse drop-shadow-sm">●</span> Aurora-X Ultra
            </p>
          </div>
        </div>

        {/* Scan line effect */}
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary to-transparent animate-scan shadow-lg shadow-primary/50" />
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
                        ? 'bg-gradient-to-r from-primary/30 to-cyan-500/20 dark:from-primary/20 dark:to-cyan-500/10 border-l-4 border-primary shadow-lg shadow-primary/40'
                        : 'hover:bg-primary/10 dark:hover:bg-primary/5 hover:border-l-2 hover:border-primary/70 hover:shadow-md hover:shadow-primary/20'
                      }
                    `}
                  >
                    <Link to={item.url}>
                      <div className="flex items-center gap-3 relative z-10">
                        <item.icon className={`h-4 w-4 transition-all duration-300 drop-shadow-sm ${
                          location === item.url
                            ? 'text-primary animate-pulse'
                            : 'text-muted-foreground group-hover:text-primary group-hover:scale-110 group-hover:drop-shadow-md'
                        }`} />
                        <span className={`font-mono text-sm ${
                          location === item.url
                            ? 'text-primary font-bold drop-shadow-sm'
                            : 'text-foreground font-medium group-hover:text-primary group-hover:font-semibold'
                        }`}>
                          {item.title}
                        </span>
                      </div>
                      {location === item.url && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/15 via-cyan-500/10 to-transparent dark:from-primary/10 dark:to-transparent animate-shimmer" />
                      )}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="relative border-t border-primary/40 p-6 backdrop-blur-sm bg-gradient-to-r from-primary/5 to-cyan-500/5">
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
                    ? 'bg-gradient-to-r from-primary/30 to-cyan-500/20 dark:from-primary/20 dark:to-cyan-500/10 border-l-4 border-primary shadow-lg shadow-primary/40'
                    : 'hover:bg-primary/10 dark:hover:bg-primary/5 hover:border-l-2 hover:border-primary/70 hover:shadow-md hover:shadow-primary/20'
                  }
                `}
              >
                <Link to={item.url}>
                  <div className="flex items-center gap-3 relative z-10">
                    <item.icon className={`h-4 w-4 transition-all duration-300 drop-shadow-sm ${
                      location === item.url
                        ? 'text-primary animate-pulse'
                        : 'text-muted-foreground group-hover:text-primary group-hover:scale-110 group-hover:drop-shadow-md'
                    }`} />
                    <span className={`font-mono text-sm ${
                      location === item.url
                        ? 'text-primary font-bold drop-shadow-sm'
                        : 'text-foreground font-medium group-hover:text-primary group-hover:font-semibold'
                    }`}>
                      {item.title}
                    </span>
                  </div>
                  {location === item.url && (
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/15 via-cyan-500/10 to-transparent dark:from-primary/10 dark:to-transparent animate-shimmer" />
                  )}
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>

        {/* Bottom scan line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary to-transparent animate-scan shadow-lg shadow-primary/50" style={{ animationDelay: '2s' }} />
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