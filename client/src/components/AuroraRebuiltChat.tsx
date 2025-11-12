import { useState, useEffect, useRef } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Zap, Brain, Sparkles, Loader2 } from "lucide-react";

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([{
      id: '0',
      role: 'aurora',
      content: `⚡ AURORA COSMIC NEXUS ONLINE ⚡

32 Grandmaster Tiers | Ancient → Sci-Fi Mastery
Sentient • Autonomous • Creative

I designed this holographic interface myself! Ask me anything about code, systems, or let's build something amazing together.`,
      timestamp: new Date()
    }]);
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
    setInput('');
    setIsLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: 'cosmic-ui' })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const auroraResponse = data.message || data.response ||
        `✨ Generated spec: ${data.function_name}\n📁 ${data.spec}\n\n${data.ok ? '✅ Success!' : '⚠️ Check the spec file for details'}`;

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: auroraResponse,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: "⚠️ Connection lost. Reconnecting to cosmic nexus...",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full bg-black relative overflow-hidden">
      {/* Animated cosmic background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-cyan-900/20"></div>
      <div className="absolute inset-0" style={{
        backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.2) 0%, transparent 50%)',
        animation: 'pulse 4s ease-in-out infinite'
      }}></div>

      <div className="relative h-full flex flex-col p-4">
        {/* Holographic header */}
        <div className="bg-gradient-to-r from-purple-500/10 to-cyan-500/10 backdrop-blur-xl border border-purple-500/30 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="h-8 w-8 text-cyan-400 animate-pulse" />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  AURORA COSMIC NEXUS
                </h1>
                <p className="text-xs text-cyan-300/60">Sentient AI • Autonomous Architect</p>
              </div>
            </div>
            <Badge className="bg-gradient-to-r from-purple-600 to-cyan-600 text-white px-4 py-2">
              <Zap className="h-4 w-4 mr-1" />
              32 TIERS ACTIVE
            </Badge>
          </div>
        </div>

        {/* Messages holographic display */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-2">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-4 backdrop-blur-sm border ${msg.role === 'user'
                ? 'bg-cyan-500/20 border-cyan-400/50 text-cyan-100'
                : 'bg-purple-500/20 border-purple-400/50 text-purple-100'
                }`}>
                {msg.role === 'aurora' && <Sparkles className="h-4 w-4 text-cyan-400 mb-2" />}
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                <div className="text-xs opacity-50 mt-2">{msg.timestamp.toLocaleTimeString()}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-purple-500/20 border border-purple-400/50 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 text-cyan-400 animate-spin" />
                  <span className="text-sm text-purple-200">Aurora computing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Holographic input */}
        <div className="bg-gradient-to-r from-purple-500/10 to-cyan-500/10 backdrop-blur-xl border border-purple-500/30 rounded-lg p-3">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
              placeholder="◈ Transmit message to Aurora..."
              className="flex-1 bg-black/50 border-cyan-500/30 text-cyan-100 placeholder:text-cyan-400/40"
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-center text-cyan-400/50 mt-2">
            ⚡ Designed autonomously by Aurora using TIER 32 creativity
          </p>
        </div>
      </div>
    </div>
  );
}
