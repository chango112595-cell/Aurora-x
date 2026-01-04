import { useEffect, useRef, useState, useCallback } from "react";
import { Send, Sparkles, Code, CheckCircle2, AlertCircle, Activity, Wifi, WifiOff, Settings2, BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AuroraMetricsOverlay } from "@/components/aurora-metrics";

type MessageStatus = "pending" | "processing" | "complete" | "error";

interface Message {
  id: string;
  role: "user" | "aurora";
  text: string;
  timestamp: Date;
  status: MessageStatus;
}

interface SystemMetrics {
  services: {
    luminar: boolean;
    memory: boolean;
    nexus: boolean;
    auroraX: boolean;
  };
  consciousness?: {
    state: string;
    workers: { total: number; idle: number };
  };
  turnContextSize?: number;
}

export default function AuroraChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/synthesis`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("[AuroraChat] Connected to WebSocket");
      setIsConnected(true);
      ws.send(JSON.stringify({ type: "subscribe_chat" }));
    };

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        handleWebSocketMessage(data);
      } catch (err) {
        console.error("[AuroraChat] Failed to parse message:", err);
      }
    };

    ws.onclose = () => {
      console.log("[AuroraChat] Disconnected from WebSocket");
      setIsConnected(false);
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error("[AuroraChat] WebSocket error:", error);
    };

    setSocket(ws);

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      ws.close();
    };
  }, []);

  useEffect(() => {
    const cleanup = connectWebSocket();
    fetchSystemMetrics();
    const metricsInterval = setInterval(fetchSystemMetrics, 30000);

    return () => {
      cleanup();
      clearInterval(metricsInterval);
    };
  }, [connectWebSocket]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSystemMetrics = async () => {
    try {
      const res = await fetch("/api/auroraai/status");
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error("[AuroraChat] Failed to fetch metrics:", err);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case "connected":
      case "chat_subscribed":
        console.log("[AuroraChat]", data.message);
        break;

      case "chat_processing":
        setMessages((prev) =>
          prev.map((m) =>
            m.id === data.messageId ? { ...m, status: "processing" as MessageStatus } : m
          )
        );
        break;

      case "chat_response":
        setIsProcessing(false);
        setMessages((prev) => [
          ...prev.map((m) =>
            m.id === data.messageId
              ? { ...m, status: "complete" as MessageStatus }
              : m
          ),
          {
            id: `aurora_${Date.now()}`,
            role: "aurora" as const,
            text: data.response,
            timestamp: new Date(),
            status: "complete" as MessageStatus,
          },
        ]);
        break;

      case "chat_error":
        setIsProcessing(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === data.messageId
              ? { ...m, status: "error" as MessageStatus, text: data.error || "Error processing message" }
              : m
          )
        );
        break;

      case "chat_broadcast":
        setMessages((prev) => [
          ...prev,
          {
            id: `broadcast_${Date.now()}`,
            role: "aurora",
            text: data.response,
            timestamp: new Date(),
            status: "complete" as MessageStatus,
          },
        ]);
        break;
    }
  };

  const sendMessage = () => {
    if (!input.trim() || !socket || socket.readyState !== WebSocket.OPEN || isProcessing) return;

    const messageId = `msg_${Date.now()}`;
    const userMessage: Message = {
      id: messageId,
      role: "user",
      text: input.trim(),
      timestamp: new Date(),
      status: "pending",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsProcessing(true);

    socket.send(
      JSON.stringify({
        type: "chat",
        message: input.trim(),
        messageId,
      })
    );
  };

  const getStatusIcon = (status: MessageStatus) => {
    switch (status) {
      case "pending":
        return <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" data-testid="icon-pending" />;
      case "processing":
        return <Activity className="w-4 h-4 text-purple-400 animate-pulse" data-testid="icon-processing" />;
      case "complete":
        return <CheckCircle2 className="w-4 h-4 text-green-400" data-testid="icon-complete" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-400" data-testid="icon-error" />;
    }
  };

  const formatMessage = (text: string) => {
    if (!text) return <span className="text-muted-foreground">Empty message</span>;

    const parts = text.split("```");
    return parts.map((part, i) => {
      if (i % 2 === 1) {
        const lines = part.split("\n");
        const language = lines[0]?.trim() || "code";
        const code = lines.slice(1).join("\n");

        return (
          <div key={`code-${i}`} className="my-3 rounded-lg bg-muted/80 border overflow-hidden">
            <div className="px-3 py-2 bg-primary/10 border-b flex items-center gap-2">
              <Code className="w-3 h-3 text-primary" />
              <span className="text-xs text-primary font-mono">{language}</span>
            </div>
            <pre className="p-3 overflow-x-auto text-xs sm:text-sm">
              <code className="text-foreground font-mono">{code}</code>
            </pre>
          </div>
        );
      }

      return (
        <div key={`text-${i}`} className="whitespace-pre-wrap leading-relaxed">
          {part.split("\n").map((line, j) => {
            if (!line.trim()) return <br key={j} />;
            if (line.startsWith("•") || line.startsWith("-")) {
              return (
                <li key={j} className="ml-4 mb-1">
                  {line.replace(/^[•-]\s*/, "")}
                </li>
              );
            }
            return <p key={j} className="mb-1">{line}</p>;
          })}
        </div>
      );
    });
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4" data-testid="aurora-chat-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Aurora WebSocket Chat</h1>
          <Badge
            variant={isConnected ? "default" : "destructive"}
            className="flex items-center gap-1"
            data-testid="badge-connection-status"
          >
            {isConnected ? (
              <>
                <Wifi className="w-3 h-3" />
                Connected
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3" />
                Disconnected
              </>
            )}
          </Badge>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowMetrics(!showMetrics)}
          data-testid="button-toggle-metrics"
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Metrics
        </Button>
      </div>

      {showMetrics && metrics && (
        <Card className="bg-card/50" data-testid="card-metrics">
          <CardHeader className="py-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Settings2 className="w-4 h-4" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent className="py-2">
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Luminar:</span>
                <Badge variant={metrics.services?.luminar ? "default" : "destructive"}>
                  {metrics.services?.luminar ? "Online" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Memory:</span>
                <Badge variant={metrics.services?.memory ? "default" : "destructive"}>
                  {metrics.services?.memory ? "Online" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Nexus:</span>
                <Badge variant={metrics.services?.nexus ? "default" : "destructive"}>
                  {metrics.services?.nexus ? "Online" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Aurora-X:</span>
                <Badge variant={metrics.services?.auroraX ? "default" : "destructive"}>
                  {metrics.services?.auroraX ? "Online" : "Offline"}
                </Badge>
              </div>
              {metrics.consciousness && (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">State:</span>
                    <Badge variant="outline">{metrics.consciousness.state}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Workers:</span>
                    <Badge variant="outline">
                      {metrics.consciousness.workers.idle}/{metrics.consciousness.workers.total}
                    </Badge>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="flex-1 flex flex-col overflow-hidden" data-testid="card-chat">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-12" data-testid="text-empty-state">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Start a conversation with Aurora</p>
                <p className="text-sm mt-2">Connected via WebSocket for real-time responses</p>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                data-testid={`message-${msg.role}-${msg.id}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold">
                      {msg.role === "user" ? "You" : "Aurora"}
                    </span>
                    {getStatusIcon(msg.status)}
                    <span className="text-xs opacity-70 ml-auto">
                      {msg.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <div className="text-sm">{formatMessage(msg.text)}</div>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>

        <div className="border-t p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder={isConnected ? "Talk to Aurora..." : "Connecting..."}
              className="flex-1 bg-muted rounded-lg px-4 py-3 text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              disabled={!isConnected || isProcessing}
              data-testid="input-message"
            />
            <Button
              onClick={sendMessage}
              disabled={!isConnected || isProcessing || !input.trim()}
              className="px-6"
              data-testid="button-send"
            >
              {isProcessing ? (
                <>
                  <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                  Thinking...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Send
                </>
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Real-time WebSocket connection to Aurora AI orchestrator
          </p>
        </div>
      </Card>

      {/* Real-time system metrics overlay */}
      <AuroraMetricsOverlay refreshInterval={5000} />
    </div>
  );
}
