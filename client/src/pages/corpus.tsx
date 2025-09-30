import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, TrendingUp, Zap } from "lucide-react";

export default function Corpus() {
  const stats = [
    { label: "Total Records", value: "12,847", icon: Database, color: "text-chart-1" },
    { label: "Learning Rate", value: "+15.3%", icon: TrendingUp, color: "text-chart-2" },
    { label: "Best Snippets", value: "3,241", icon: Zap, color: "text-chart-3" },
  ];

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Corpus Explorer</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Explore Aurora's learning corpus and synthesis history
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {stats.map((stat) => (
            <Card key={stat.label} className="hover-elevate" data-testid={`card-${stat.label.toLowerCase().replace(' ', '-')}`}>
              <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold" data-testid={`text-${stat.label.toLowerCase().replace(' ', '-')}`}>{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card data-testid="card-corpus-data">
          <CardHeader>
            <CardTitle>Recent Synthesis Records</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { func: "normalize_spaces", score: 0.98, timestamp: "2 min ago" },
                { func: "tokenize", score: 0.95, timestamp: "5 min ago" },
                { func: "safe_int", score: 0.92, timestamp: "8 min ago" },
                { func: "clamp", score: 0.97, timestamp: "12 min ago" },
              ].map((record, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-lg border border-border p-3"
                  data-testid={`record-${record.func}`}
                >
                  <div>
                    <code className="text-sm font-mono font-semibold">{record.func}</code>
                    <p className="text-xs text-muted-foreground mt-1">{record.timestamp}</p>
                  </div>
                  <Badge className="bg-chart-2 text-white">Score: {record.score}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
