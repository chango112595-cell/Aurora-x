/**
 * Aurora Chat Interface
 * Part of Aurora-X Neural Synthesis Engine
 * 🌟 Aurora's own UI for natural language code generation and commands
 */

import { ErrorBoundary } from '@/components/error-boundary';
import { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Sparkles, Terminal, AlertCircle, CheckCircle } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'aurora';
  content: string;
  timestamp: Date;
  data?: Record<string, unknown>;
  type?: 'message' | 'command' | 'error' | 'success';
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'aurora',
      content: "🌟 Hi! I'm Aurora. You can chat with me about code, or use commands like:\n/diagnostics - Run tab diagnostics\n/fix <issue> - Fix specific issues\n/status - Check system status\n/help - Show all commands",
      timestamp: new Date(),
      type: 'message',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    console.log('🌟 Aurora: Sending message:', input);
    setMessages((prev) => [...prev, userMessage]);

    const promptToSend = input;
    setInput('');
    setIsLoading(true);

    try {
      console.log('🌟 Aurora: Calling Aurora backend API...');

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptToSend }),
      });

      console.log('🌟 Aurora: Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('🌟 Aurora: Response data:', data);

      const auroraMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: formatAuroraResponse(data),
        timestamp: new Date(),
        data: data,
      };

      setMessages((prev) => {
        console.log('🌟 Aurora: Adding response, count:', prev.length + 1);
        return [...prev, auroraMessage];
      });

      console.log('✅ Aurora: Message added!');
    } catch (error) {
      console.error('❌ Aurora error:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'aurora',
        content: `🌟 Oops! Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatAuroraResponse = (data: Record<string, unknown> | null): string => {
    if (!data?.ok) {
      return `🌟 I couldn't generate that:\n\n${JSON.stringify(data, null, 2)}`;
    }

    let response = `🌟 Got it! I've generated:\n\n`;

    if (data?.kind) response += `**Type:** ${data.kind}\n`;
    if (data?.lang) response += `**Language:** ${data.lang}\n`;
    if (data?.file) response += `**File:** \`${data.file}\`\n`;
    if (data?.tests) response += `**Tests:** \`${data.tests}\`\n`;
    if (data?.reason) response += `\n**Reasoning:** ${data.reason}\n`;
    if (data?.hint) response += `\n💡 ${data.hint}\n`;

    response += `\nNeed changes? Just ask! ⚡`;

    return response;
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950">
      {/* Header */}
      <div className="border-b border-cyan-500/20 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-cyan-400" />
            <h1 className="text-2xl font-bold text-cyan-400">Chat with Aurora</h1>
            <div className="ml-auto">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-sm">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
                </span>
                Status: ACTIVE
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${message.role === 'user'
                    ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/30'
                    : 'bg-gray-800/50 text-gray-100 border border-gray-700'
                    }`}
                >
                  <div className="flex items-start gap-3">
                    {message.role === 'aurora' && (
                      <Sparkles className="h-5 w-5 text-cyan-400 mt-1 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <div className="whitespace-pre-wrap break-words">
                        {message.content.split('\n').map((line, i) => {
                          if (line.includes('**')) {
                            const parts = line.split('**');
                            return (
                              <div key={i}>
                                {parts.map((part, j) =>
                                  j % 2 === 1 ? <strong key={j}>{part}</strong> : part
                                )}
                              </div>
                            );
                          }
                          if (line.includes('`')) {
                            const parts = line.split('`');
                            return (
                              <div key={i}>
                                {parts.map((part, j) =>
                                  j % 2 === 1 ? (
                                    <code key={j} className="bg-gray-900 px-1 rounded text-cyan-300">{part}</code>
                                  ) : part
                                )}
                              </div>
                            );
                          }
                          return <div key={i}>{line}</div>;
                        })}
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800/50 rounded-lg px-4 py-3 border border-gray-700">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-5 w-5 text-cyan-400 animate-pulse" />
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-gray-400 text-sm">Aurora is generating...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-cyan-500/20 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 max-w-4xl">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Just type what you want – I'll understand and generate it! 🌟"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 resize-none"
              rows={3}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              aria-label="action">
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Send className="h-5 w-5" />
                  Send
                </>
              )}
            </button>
          </div>

          <div className="mt-3 text-xs text-gray-500 text-center">
            🌟 Aurora generates CLI tools, web apps, libraries, and more!
          </div>
        </div>
      </div>
    </div>
  );
}
