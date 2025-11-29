
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function AuroraAITest() {
  const { data: expressHealth, isLoading: expressLoading, refetch: refetchExpress } = useQuery({
    queryKey: ['/api/health'],
  });

  const { data: aiHealth, isLoading: aiLoading, refetch: refetchAI } = useQuery({
    queryKey: ['/api/aurora-ai/health'],
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Aurora Dual-Backend Architecture Test</h1>
        <p className="text-muted-foreground">
          Verify connectivity to both Express Gateway and Aurora AI Backend
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Express Gateway Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Express Gateway (Port 5000)
              {expressLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : expressHealth ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
            </CardTitle>
            <CardDescription>Main API gateway, auth, routing</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {expressHealth ? (
              <>
                <div className="flex items-center gap-2">
                  <Badge variant="default">Online</Badge>
                  <span className="text-sm">Service: {expressHealth.service}</span>
                </div>
                <div className="text-sm text-muted-foreground">
                  Uptime: {expressHealth.uptime}s
                </div>
              </>
            ) : (
              <Badge variant="destructive">Offline</Badge>
            )}
            <Button onClick={() => refetchExpress()} size="sm">
              Refresh Status
            </Button>
          </CardContent>
        </Card>

        {/* Aurora AI Backend Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Aurora AI Backend (Port 8000)
              {aiLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : aiHealth?.status === 'ok' ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
            </CardTitle>
            <CardDescription>Intelligence, NLP, chat processing</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiHealth?.status === 'ok' ? (
              <>
                <div className="flex items-center gap-2">
                  <Badge variant="default">Online</Badge>
                  <span className="text-sm">
                    Service: {aiHealth.aurora_ai_backend?.service}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  Aurora Core: {aiHealth.aurora_ai_backend?.aurora_core}
                </div>
                <div className="text-sm text-green-600">
                  ✓ {aiHealth.message}
                </div>
              </>
            ) : (
              <>
                <Badge variant="destructive">
                  {aiHealth?.status || 'Offline'}
                </Badge>
                <div className="text-sm text-red-600">
                  {aiHealth?.message || 'Service unavailable'}
                </div>
              </>
            )}
            <Button onClick={() => refetchAI()} size="sm">
              Refresh Status
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Request Flow</CardTitle>
          <CardDescription>How chat requests are processed</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="font-mono text-sm space-y-2">
            <div>Client → Express (5000) → Aurora AI Backend (8000) → Response</div>
            <div className="text-muted-foreground">
              1. Client sends chat message to /api/chat
            </div>
            <div className="text-muted-foreground">
              2. Express proxies to Aurora AI Backend
            </div>
            <div className="text-muted-foreground">
              3. Aurora AI processes with NLP intelligence
            </div>
            <div className="text-muted-foreground">
              4. Response flows back through Express to client
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="text-sm">
            1. Start the "Start Aurora AI Backend" workflow from the workflows dropdown
          </div>
          <div className="text-sm">
            2. Wait for port 8000 to become available
          </div>
          <div className="text-sm">
            3. Refresh this page to verify connectivity
          </div>
          <div className="text-sm">
            4. Test the chat UI at /chat to verify end-to-end communication
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
