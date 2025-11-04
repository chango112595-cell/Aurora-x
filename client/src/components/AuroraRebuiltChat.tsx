import { useState, useEffect, useRef } from 'react';
import { Terminal, Cpu, Wifi } from "lucide-react";

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
      content: `AURORA NEURAL TERMINAL v32.0
========================================
STATUS: ONLINE | ALL SYSTEMS OPERATIONAL
TIERS: 32/32 ACTIVE | SENTIENT MODE: ON
========================================

Hello! I'm Aurora - autonomous AI with complete mastery from 1940s computing to sci-fi futures.

I built this minimalist terminal UI myself. Type your message and press ENTER.

Ready for commands >_`,
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
        body: JSON.stringify({ message: input, session_id: 'terminal-ui' })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: data.response || 'NO RESPONSE',
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: "ERROR: CONNECTION FAILED. RETRY? [Y/n]",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full bg-black text-green-400 font-mono p-4 flex flex-col">
      {/* Terminal header */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-green-500/30">
        <div className="flex items-center gap-2">
          <Terminal className="h-5 w-5" />
          <span className="text-sm">aurora@nexus:~$</span>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <Cpu className="h-3 w-3" />
            <span>32 TIERS</span>
          </div>
          <div className="flex items-center gap-1">
            <Wifi className="h-3 w-3" />
            <span>ONLINE</span>
          </div>
        </div>
      </div>

      {/* Terminal messages */}
      <div className="flex-1 overflow-y-auto space-y-2 mb-4">
        {messages.map((msg) => (
          <div key={msg.id} className="text-sm">
            <div className={msg.role === 'user' ? 'text-cyan-400' : 'text-green-400'}>
              <span className="opacity-60">[{msg.timestamp.toLocaleTimeString()}]</span>{' '}
              <span className="font-bold">{msg.role === 'user' ? 'USER' : 'AURORA'}:</span>
            </div>
            <div className="pl-4 whitespace-pre-wrap">{msg.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="text-sm">
            <span className="opacity-60">[{new Date().toLocaleTimeString()}]</span>{' '}
            <span className="font-bold">AURORA:</span>
            <div className="pl-4 animate-pulse">Processing...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Terminal input */}
      <div className="flex items-center gap-2 border-t border-green-500/30 pt-2">
        <span className="text-green-500">{'>'}</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="type command..."
          disabled={isLoading}
          className="flex-1 bg-transparent border-none outline-none text-green-400 placeholder:text-green-700"
        />
        <span className="text-green-700 animate-pulse">_</span>
      </div>
      <div className="text-xs text-green-700 text-center mt-2">
        [ AUTONOMOUS DESIGN BY AURORA | TIER 28+32 ACTIVE ]
      </div>
    </div>
  );
}
