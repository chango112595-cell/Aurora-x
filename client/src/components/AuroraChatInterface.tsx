import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Sparkles, Loader2 } from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'aurora' | 'system';
  content: string;
  timestamp: Date;
}
interface AuroraChatProps {
  compact?: boolean;
}

export default function AuroraChatInterface({ compact = false }: AuroraChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Aurora welcome message with conversational style
    setMessages([
      {
        id: '0',
        role: 'aurora',
        content: compact
          ? "Hey — I'm Aurora. Chat with me quickly from the sidebar. Ask anything!"
          : "Hey! 👋 Aurora here with all 27 mastery tiers active.\n\nI can help you:\n• Build anything (web, mobile, cloud, AI)\n• Debug any issue\n• Explain complex concepts\n• Review and optimize code\n\nJust chat naturally with me - I understand context! What's on your mind?",
        timestamp: new Date(),
      },
    ]);
    setConnected(true);

    // Auto-scroll
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [compact]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    console.log('[Aurora Chat] Starting request, isLoading=true');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          session_id: 'web-ui-session'
        })
      });

      console.log('[Aurora Chat] Got response:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[Aurora Chat] Parsed JSON, adding message');

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: data.response || 'No response',
        timestamp: new Date()
      }]);

      console.log('[Aurora Chat] Message added, clearing loading');
    } catch (error) {
      console.error('[Aurora Chat] Error:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: "Hmm, I hit a snag there. Mind trying that again? 🔧",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      console.log('[Aurora Chat] isLoading=false (finally block)');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={compact ? "h-full flex flex-col" : "h-full flex flex-col bg-gradient-to-br from-background via-background to-primary/5"}>
      {/* Aurora's Quantum Background - hidden in compact mode */}
      {!compact && (
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20" />

          {/* Particle field */}
          <div className="absolute inset-0 opacity-20" style={{
            backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
            backgroundSize: '50px 50px',
            animation: 'particleFloat 20s linear infinite'
          }} />

          {/* Holographic orbs */}
          <div className="absolute top-20 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        </div>
      )}

      <Card className={compact ? "m-3 flex-none h-64 border-cyan-500/20" : "m-6 flex-1 flex flex-col border-cyan-500/20"}>
        <CardHeader className="border-b border-cyan-500/20">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-cyan-400" />
            Chat with Aurora
            <Badge variant={connected ? "default" : "secondary"} className="ml-auto bg-cyan-500/20 text-cyan-300">
              {connected ? (compact ? '🌌 Sidebar' : '🌌 27 Tiers Active') : '○ Offline'}
            </Badge>
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-2">
            {compact ? 'Compact sidebar chat — quick context and replies.' : 'Conversational AI with complete mastery across all domains - just like Copilot!'}
          </p>
        </CardHeader>

        <CardContent className={`${compact ? 'flex-none h-[calc(100%-80px)] p-3' : 'flex-1 flex flex-col p-6'}`}>
          <ScrollArea className="flex-1 pr-4 mb-4">
            <div className="space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg px-4 py-3 ${msg.role === 'user'
                      ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/30'
                      : msg.role === 'aurora'
                        ? 'bg-purple-500/20 text-purple-100 border border-purple-500/30'
                        : 'bg-muted/50 text-muted-foreground border border-muted'
                      }`}
                  >
                    <div className="flex items-start gap-2">
                      {msg.role === 'aurora' && <Sparkles className="h-4 w-4 text-cyan-400 mt-1 flex-shrink-0" />}
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap break-words text-sm">
                          {msg.content}
                        </div>
                        <div className="text-xs opacity-60 mt-1">
                          {msg.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-purple-500/20 rounded-lg px-4 py-3 border border-purple-500/30">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-xs text-purple-300">Aurora is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          <div className={`${compact ? 'space-y-2' : 'space-y-3'}`}>
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={compact ? "Quick ask Aurora..." : "Chat naturally with Aurora - ask anything! 💬"}
                disabled={!connected || isLoading}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || !connected || isLoading}
                className="bg-cyan-500 hover:bg-cyan-600 gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    {compact ? '...' : 'Thinking'}
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    {compact ? 'Send' : 'Send'}
                  </>
                )}
              </Button>
            </div>
            {!compact && (
              <div className="text-xs text-muted-foreground text-center">
                💡 I understand context and have real conversations - try asking me anything!
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
