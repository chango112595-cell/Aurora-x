import { Activity, Zap, Database, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function AuroraStatus() {
  const statusItems = [
    {
      title: "Aurora Engine",
      status: "Active",
      icon: Zap,
      color: "text-chart-2",
      value: "Running",
    },
    {
      title: "Sandbox Security",
      status: "Secure",
      icon: Shield,
      color: "text-chart-2",
      value: "Isolated",
    },
    {
      title: "Novelty Cache",
      status: "Healthy",
      icon: Activity,
      color: "text-chart-1",
      value: "45.2K entries",
    },
    {
      title: "Corpus Size",
      status: "Growing",
      icon: Database,
      color: "text-chart-3",
      value: "12.8K records",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {statusItems.map((item) => (
        <Card key={item.title} className="hover-elevate" data-testid={`card-status-${item.title.toLowerCase().replace(' ', '-')}`}>
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
            <item.icon className={`h-4 w-4 ${item.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" data-testid={`text-value-${item.title.toLowerCase().replace(' ', '-')}`}>{item.value}</div>
            <Badge variant="secondary" className="mt-2">
              {item.status}
            </Badge>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
