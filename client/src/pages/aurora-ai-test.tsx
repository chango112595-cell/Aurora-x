import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle2, XCircle, Loader2, Send } from "lucide-react";
import { useState } from "react";
import API_CONFIG from "@/config/api";

interface ExpressHealthResponse {
  service: string;
  uptime: number;
  status?: string;
}

interface AIBackendInfo {
  service: string;
  aurora_core: string;
}

interface AIHealthResponse {
  status: string;
  message?: string;
  aurora_ai_backend?: AIBackendInfo;
}

export default function AuroraAITest() {
  const [chatMessage, setChatMessage] = useState("");
  const [chatResponse, setChatResponse] = useState<any>(null);

  const { data: expressHealth, isLoading: expressLoading, refetch: refetchExpress } = useQuery<ExpressHealthResponse>({
    queryKey: ['/api/health'],
  });

  const { data: aiHealth, isLoading: aiLoading, refetch: refetchAI } = useQuery<AIHealthResponse>({
    queryKey: ['/api/aurora-ai/health'],
  });

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: 'test-session',
          context: {}
        })
      });
      return response.json();
    },
    onSuccess: (data) => {
      setChatResponse(data);
    }
  });

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      chatMutation.mutate(chatMessage);
    }
  };

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
            <Button onClick={() => refetchExpress()} size="sm" variant="outline">
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
            <Button onClick={() => refetchAI()} size="sm" variant="outline">
              Refresh Status
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Chat Test */}
      <Card>
        <CardHeader>
          <CardTitle>Test Chat Integration</CardTitle>
          <CardDescription>Send a message to test the full request flow</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Type a test message..."
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <Button
              onClick={handleSendMessage}
              disabled={chatMutation.isPending || !chatMessage.trim()}
            >
              {chatMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {chatResponse && (
            <Card className="bg-muted">
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant={chatResponse.ai_powered ? "default" : "secondary"}>
                      {chatResponse.ai_powered ? "AI Backend" : "Express Fallback"}
                    </Badge>
                    {chatResponse.intent && (
                      <Badge variant="outline">Intent: {chatResponse.intent}</Badge>
                    )}
                  </div>
                  <p className="text-sm">{chatResponse.response || chatResponse.message}</p>
                  {chatResponse.entities && Object.keys(chatResponse.entities).length > 0 && (
                    <div className="text-xs text-muted-foreground">
                      Entities: {JSON.stringify(chatResponse.entities)}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {chatMutation.isError && (
            <div className="text-sm text-red-600">
              Error: Failed to send message
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Request Flow</CardTitle>
          <CardDescription>How chat requests are processed</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="font-mono text-sm space-y-2">
            <div className="font-semibold">Client → Express (5000) → Aurora AI Backend (8000) → Response</div>
            <div className="text-muted-foreground pl-4">
              1. Client sends chat message to /api/chat
            </div>
            <div className="text-muted-foreground pl-4">
              2. Express proxies to Aurora AI Backend (http://0.0.0.0:8000/api/chat)
            </div>
            <div className="text-muted-foreground pl-4">
              3. Aurora AI processes with NLP intelligence
            </div>
            <div className="text-muted-foreground pl-4">
              4. Response flows back through Express to client
            </div>
            <div className="text-muted-foreground pl-4">
              5. If AI backend unavailable, Express handles with fallback
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex items-start gap-2">
            <div className="font-semibold min-w-8">1.</div>
            <div>Start the "Start Aurora AI Backend" workflow from the workflows dropdown</div>
          </div>
          <div className="flex items-start gap-2">
            <div className="font-semibold min-w-8">2.</div>
            <div>Wait for port 8000 to become available (~10-30 seconds)</div>
          </div>
          <div className="flex items-start gap-2">
            <div className="font-semibold min-w-8">3.</div>
            <div>Refresh this page to verify connectivity</div>
          </div>
          <div className="flex items-start gap-2">
            <div className="font-semibold min-w-8">4.</div>
            <div>Test the chat above - you should see "AI Backend" badge if working</div>
          </div>
          <div className="flex items-start gap-2">
            <div className="font-semibold min-w-8">5.</div>
            <div>Visit /chat to test the full chat UI with the integrated backend</div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">Configuration</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-1">
          <div><strong>Express Base:</strong> {API_CONFIG.EXPRESS_BASE}</div>
          <div><strong>AI Base:</strong> {API_CONFIG.AI_BASE}</div>
          <div><strong>WebSocket:</strong> {API_CONFIG.WS_CHAT}</div>
        </CardContent>
      </Card>
    </div>
  );
}
