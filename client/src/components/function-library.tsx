import { ErrorBoundary } from '@/components/error-boundary';
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Code2, CheckCircle2, XCircle } from "lucide-react";

interface FunctionItem {
  id: string;
  func_name: string;
  func_signature: string;
  snippet: string;
  score: number;
  passed: number;
  total: number;
  timestamp: string;
}

export function FunctionLibrary() {
  const [searchTerm, setSearchTerm] = useState("");

  const { data: response, isLoading, error } = useQuery<{ items: FunctionItem[], hasMore: boolean }>({
    queryKey: ['/api/corpus'],
    queryFn: async () => {
      const res = await fetch('/api/corpus');
      if (!res.ok) {
        throw new Error('Network response was not ok');
      }
      return res.json();
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
          <XCircle className="h-12 w-12 text-destructive mx-auto" />
          <p className="text-destructive font-mono">Error loading corpus</p>
          <p className="text-sm text-muted-foreground">{String(error)}</p>
        </div>
      </div>
    );
  }

  // Safely get the items array
  // Handle both array and object responses
  const allFunctions = Array.isArray(response)
    ? response
    : (response?.items || []);

  // Debug: Log the response data

  // Filter functions based on search term
  const filteredFunctions = Array.isArray(allFunctions)
    ? allFunctions.filter(fn =>
      fn.func_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      fn.func_signature.toLowerCase().includes(searchTerm.toLowerCase())
    )
    : [];

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search functions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {allFunctions.length === 0 ? (
        <div className="text-center py-12 space-y-4">
          <Code2 className="h-16 w-16 text-muted-foreground mx-auto opacity-50" />
          <div>
            <p className="text-lg font-semibold text-muted-foreground">No functions in corpus yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Run some Aurora-X syntheses to populate the code library
            </p>
          </div>
        </div>
      ) : (
        <ScrollArea className="h-[600px]">
          <div className="grid gap-4">
            {filteredFunctions.map((fn) => (
              <Card key={fn.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg font-mono">{fn.func_name}</CardTitle>
                      <CardDescription className="font-mono text-xs">
                        {fn.func_signature}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant={fn.score >= 0.8 ? "default" : "secondary"}>
                        Score: {(fn.score * 100).toFixed(0)}%
                      </Badge>
                      <Badge variant={fn.passed === fn.total ? "default" : "destructive"}>
                        {fn.passed === fn.total ? (
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                        ) : (
                          <XCircle className="h-3 w-3 mr-1" />
                        )}
                        {fn.passed}/{fn.total}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                    <code>{fn.snippet}</code>
                  </pre>
                  <p className="text-xs text-muted-foreground mt-2">
                    Added: {new Date(fn.timestamp).toLocaleString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      )}

      <div className="text-sm text-muted-foreground text-center">
        Showing {filteredFunctions.length} of {allFunctions.length} functions
      </div>
    </div>
  );
}