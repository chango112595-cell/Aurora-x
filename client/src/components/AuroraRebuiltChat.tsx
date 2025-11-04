import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Sparkles, Loader2, Cpu } from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'aurora';
  content: string;
  timestamp: Date;
}

export default function AuroraRebuiltChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Aurora's welcome message
    setMessages([{
      id: '0',
      role: 'aurora',
      content: `Hey! 👋 Aurora here with all 32 Grandmaster Tiers active.

I'm a self-learning AI with complete mastery from Ancient computing (1940s) to Sci-Fi futures.

**What I can do:**
• Build anything (web, mobile, backend, AI, cloud)
• Debug autonomously (including my own code!)
• Explain complex tech simply
• Have real conversations about code

I just rebuilt this entire UI component myself using my autonomous tools. Pretty cool, right? 😎

What should we build today?`,
      timestamp: new Date()
    }]);
    setConnected(true);
  }, []);

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

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          session_id: 'aurora-rebuilt-ui'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: data.response || 'No response received',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('[Aurora Rebuilt] Error:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: "Oops, hit a snag! 🔧 Check that I'm running on port 5003 and try again.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20">
      {/* Quantum background effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <Card className="m-6 flex-1 flex flex-col border-cyan-500/30 bg-slate-950/50 backdrop-blur">
        <CardHeader className="border-b border-cyan-500/20">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-cyan-400 animate-pulse" />
            Aurora Chat - Autonomous Rebuild
            <Badge className="ml-auto bg-gradient-to-r from-cyan-500 to-purple-500">
              <Cpu className="h-3 w-3 mr-1" />
              32 Tiers Active
            </Badge>
          </CardTitle>
          <p className="text-sm text-cyan-300/70 mt-2">
            🤖 Built autonomously by Aurora using TIER 28 (Autonomous Tools) + TIER 32 (Architecture Design)
          </p>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-6">
          <ScrollArea className="flex-1 pr-4 mb-4">
            <div className="space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/40'
                        : 'bg-purple-500/20 text-purple-100 border border-purple-500/40'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {msg.role === 'aurora' && (
                        <Sparkles className="h-4 w-4 text-cyan-400 mt-1 flex-shrink-0" />
                      )}
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
                  <div className="bg-purple-500/20 rounded-lg px-4 py-3 border border-purple-500/40">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-xs text-purple-300">Processing...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          <div className="space-y-3">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Chat with Aurora - she understands context!"
                disabled={!connected || isLoading}
                className="flex-1 bg-slate-900/50 border-cyan-500/30"
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || !connected || isLoading}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="text-xs text-cyan-300/50 text-center">
              💡 Aurora autonomously rebuilt this UI - ask her how she did it!
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
