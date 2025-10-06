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
import { useLocation } from "wouter";

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
  {
    title: "Corpus Explorer",
    url: "/corpus",
    icon: Database,
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
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <Zap className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-sidebar-foreground">Chango</h2>
            <p className="text-xs text-muted-foreground">Aurora-X Ultra</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={location === item.url}
                    data-testid={`link-${item.title.toLowerCase().replace(' ', '-')}`}
                  >
                    <a href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border p-2">
        <SidebarMenu>
          {bottomItems.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton
                asChild
                isActive={location === item.url}
                data-testid={`link-${item.title.toLowerCase()}`}
              >
                <a href={item.url}>
                  <item.icon className="h-4 w-4" />
                  <span>{item.title}</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
