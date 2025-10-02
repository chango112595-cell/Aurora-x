import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Search, CheckCircle2, XCircle } from "lucide-react";
import { useState } from "react";

interface FunctionItem {
  name: string;
  args: string;
  returns: string;
  passRate: number;
  complexity: number;
  status: "passed" | "failed";
}

export function FunctionLibrary() {
  const [search, setSearch] = useState("");
  
  const functions: FunctionItem[] = [
    { name: "normalize_spaces", args: "s:str", returns: "str", passRate: 100, complexity: 8, status: "passed" },
    { name: "tokenize", args: "s:str", returns: "list[str]", passRate: 100, complexity: 12, status: "passed" },
    { name: "safe_int", args: "s:str, default:int", returns: "int", passRate: 95, complexity: 15, status: "passed" },
    { name: "clamp", args: "x:int, lo:int, hi:int", returns: "int", passRate: 100, complexity: 10, status: "passed" },
    { name: "score_keyword", args: "s:str, kw:str", returns: "int", passRate: 90, complexity: 18, status: "passed" },
  ];

  const filtered = functions.filter(f => 
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card data-testid="card-function-library">
      <CardHeader>
        <CardTitle>Function Library</CardTitle>
        <div className="relative mt-2">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search functions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8"
            data-testid="input-search"
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {filtered.map((func) => (
            <div
              key={func.name}
              className="flex items-center justify-between rounded-lg border border-border p-3 hover-elevate"
              data-testid={`function-${func.name}`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono font-semibold">{func.name}</code>
                  {func.status === "passed" ? (
                    <CheckCircle2 className="h-4 w-4 text-chart-2" />
                  ) : (
                    <XCircle className="h-4 w-4 text-destructive" />
                  )}
                </div>
                <p className="mt-1 text-xs text-muted-foreground font-mono">
                  ({func.args}) → {func.returns}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Pass: {func.passRate}%</Badge>
                <Badge variant="outline">AST: {func.complexity}</Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
