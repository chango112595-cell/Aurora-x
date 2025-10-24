import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Code2, Clock, Download, Zap, Terminal } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

interface FunctionItem {
  id: string;
  name: string;
  description: string;
  language: string;
  createdAt: string;
  code: string;
}

export function FunctionLibrary() {
  const [searchTerm, setSearchTerm] = useState("");

  const { data, isLoading, error } = useQuery<{ items: FunctionItem[], hasMore: boolean }>({
    queryKey: ['/api/corpus'],
    queryFn: async () => {
      const response = await fetch('/api/corpus');
      if (!response.ok) throw new Error('Failed to fetch corpus');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-muted-foreground font-mono">Loading corpus...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <p className="text-destructive font-mono">Error loading corpus</p>
          <p className="text-sm text-muted-foreground">{String(error)}</p>
        </div>
      </div>
    );
  }

  // Extract functions array from API response
  const functions = Array.isArray(data) ? data : (data?.items || []);

  const filteredFunctions = functions.filter((fn: any) =>
    fn.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    fn.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Futuristic search bar */}
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-cyan-500/50 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-300" />
        <div className="relative">
          <Search className="absolute left-4 top-4 h-5 w-5 text-primary" />
          <Terminal className="absolute right-4 top-4 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Initialize search protocol..."
            className="pl-12 pr-12 h-14 bg-background/80 backdrop-blur-sm border-primary/30 focus:border-primary transition-all font-mono text-base"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Function grid with futuristic cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredFunctions.map((fn, index) => (
          <Card
            key={fn.id}
            className="group relative overflow-hidden border-primary/20 bg-gradient-to-br from-card via-card to-card/80 hover:border-primary/50 transition-all duration-300 hover-elevate"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Animated border glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/20 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            {/* Corner accent */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-primary/10 blur-2xl rounded-full -translate-y-10 translate-x-10 group-hover:bg-primary/20 transition-colors" />

            <CardHeader className="relative">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                    <Code2 className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg font-mono bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
                    {fn.name}
                  </CardTitle>
                </div>
                <Badge
                  variant="secondary"
                  className="bg-primary/10 text-primary border-primary/30 font-mono text-xs"
                >
                  {fn.language}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="relative">
              <p className="text-sm text-muted-foreground mb-6 line-clamp-2 font-mono">
                {fn.description}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
                  <Clock className="h-3 w-3 text-primary" />
                  <span className="text-primary">:</span>
                  {new Date(fn.createdAt).toLocaleDateString()}
                </div>

                <Button
                  size="sm"
                  variant="ghost"
                  className="hover:bg-primary/10 hover:text-primary transition-colors group/btn"
                >
                  <Download className="h-4 w-4 group-hover/btn:animate-bounce" />
                </Button>
              </div>

              {/* Scan line animation */}
              <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-primary to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-scan" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Enhanced empty state */}
      {filteredFunctions.length === 0 && (
        <div className="text-center py-16">
          <div className="relative inline-block">
            <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
            <Zap className="relative h-16 w-16 text-primary/50 mx-auto mb-4 animate-pulse" />
          </div>
          <p className="text-muted-foreground font-mono text-lg">
            {'>'} No synthesis records found
          </p>
          <p className="text-muted-foreground/60 font-mono text-sm mt-2">
            Run Aurora-X synthesis to populate the library
          </p>
          <p className="text-muted-foreground/60 font-mono text-xs mt-1">
            Try: python3 -m aurora_x.main --nl "create a function"
          </p>
        </div>
      )}
    </div>
  );
}