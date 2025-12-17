import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Zap, Code, CheckCircle2, AlertCircle } from 'lucide-react';
import { ErrorBoundary } from './error-boundary';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'thinking' | 'executing' | 'complete' | 'error';
  aemUsed?: { id: number; name: string };
}

export default function AuroraFuturisticChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "**Aurora Quantum Neural Intelligence System - Online**\n\n**Active Systems:**\n- 188 Knowledge Tiers\n- 66 Advanced Execution Methods (my hands)\n- 550 Active Modules\n- 300 Parallel Workers\n- 100 Self-Healers\n- Hyperspeed Mode: ACTIVE\n\n**What I can do with my hands:**\n\n• **Code Operations (AEM 7-12):** Write, debug, review code; read/write files\n• **Analysis (AEM 15-17):** Analyze codebase, check integrations, recognize patterns\n• **Synthesis (AEM 18-22):** Design architectures, create documentation, build APIs\n• **System (AEM 14, 32-35):** Check status, git operations, deployment planning\n\nTry saying: \"Status\", \"List files\", \"Analyze codebase\", or describe what you need built.\n\n**What would you like me to execute?**",
      timestamp: new Date(),
      status: 'complete',
      aemUsed: { id: 14, name: 'System Status' }
    }
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(() => `chat-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
      status: 'complete'
    };

    const userInput = input;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    const thinkingMessage: Message = {
      role: 'assistant',
      content: 'Selecting optimal AEM and executing with 300 parallel workers...',
      timestamp: new Date(),
      status: 'thinking'
    };
    setMessages(prev => [...prev, thinkingMessage]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userInput, 
          session_id: sessionId,
          context: messages.slice(-4) // Send last 4 messages as context
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (!data || !data.response) {
        throw new Error('Invalid response from Aurora');
      }

      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;

        newMessages[lastIndex] = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          status: 'complete',
          aemUsed: data.aemUsed
        };

        return newMessages;
      });
    } catch (error) {
      console.error('[Aurora Chat] Error:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: `I encountered an issue processing your request. You asked: "${userInput}"\n\nLet me provide you with information on that topic or try a different approach. What aspect would you like to explore?`,
          timestamp: new Date(),
          status: 'error'
        };
        return newMessages;
      });
    }

    setIsProcessing(false);
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'thinking':
        return <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />;
      case 'executing':
        return <Zap className="w-4 h-4 text-sky-400 animate-pulse" />;
      case 'complete':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return null;
    }
  };

  const formatMessage = (content: string) => {
    if (!content) return <span className="text-slate-500">Empty message</span>;

    const safeContent = typeof content === 'string' ? content : String(content);

    try {
      // Format code blocks
      const parts = safeContent.split('```');
      return parts.map((part, i) => {
        if (i % 2 === 1) {
          // Code block
          const lines = part.split('\n');
          const language = lines[0]?.trim() || 'code';
          const code = lines.slice(1).join('\n');

          return (
            <div key={`code-${i}`} className="my-3 rounded-lg bg-slate-900/80 border border-sky-500/20 overflow-hidden">
              <div className="px-3 py-2 bg-sky-500/10 border-b border-sky-500/20 flex items-center gap-2">
                <Code className="w-3 h-3 text-sky-400" />
                <span className="text-xs text-sky-400 font-mono">{language}</span>
              </div>
              <pre className="p-3 overflow-x-auto text-xs sm:text-sm">
                <code className="text-emerald-300 font-mono">{code}</code>
              </pre>
            </div>
          );
        }

        // Regular text - enhanced formatting
        return (
          <div key={`text-${i}`} className="whitespace-pre-wrap leading-relaxed">
            {part.split('\n').map((line, j) => {
              const trimmed = line.trim();
              
              // Skip empty lines for cleaner display
              if (!trimmed) return <br key={j} />;
              
              // Bold text with ** markers
              if (line.includes('**')) {
                const boldParts = line.split('**');
                return (
                  <p key={`line-${j}`} className="mb-2">
                    {boldParts.map((p, k) =>
                      k % 2 === 1 ? <strong key={k} className="text-white font-semibold">{p}</strong> : p
                    )}
                  </p>
                );
              }
              
              // Numbered lists
              if (/^\d+\.\s/.test(trimmed)) {
                return (
                  <p key={j} className="ml-4 mb-1 text-sky-200">
                    {trimmed}
                  </p>
                );
              }
              
              // Bullet points
              if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
                const content = trimmed.replace(/^[•-]\s+/, '');
                return (
                  <li key={j} className="ml-4 mb-1 text-sky-200">
                    {content}
                  </li>
                );
              }
              
              // Links and emphasis
              if (line.includes('http')) {
                return (
                  <p key={j} className="mb-2 break-words">
                    {line.split(/(\bhttps?:\/\/[^\s]+)/g).map((segment, idx) => 
                      segment.startsWith('http') ? 
                        <a key={idx} href={segment} target="_blank" rel="noopener" className="text-emerald-400 hover:text-emerald-300 underline">{segment}</a> :
                        segment
                    )}
                  </p>
                );
              }
              
              return <p key={j} className="mb-2">{line}</p>;
            })}
          </div>
        );
      });
    } catch (error) {
      console.error('[Aurora] Format error:', error);
      return <span className="text-red-400">Error formatting message</span>;
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-sky-950 to-slate-900 p-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-6 text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 via-sky-400 to-amber-400 bg-clip-text text-transparent mb-2">
              Neural Chat
            </h1>
            <p className="text-sky-300 text-sm">Natural conversation with Aurora</p>
          </div>

          {/* Chat Container */}
          <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-sky-500/20 shadow-2xl overflow-hidden">
            {/* Messages Area */}
            <div className="h-[600px] overflow-y-auto p-6 space-y-4">
              {messages?.map((msg, idx) => (
                <div
                  key={`msg-${idx}-${msg.timestamp.getTime()}`}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                      ? 'bg-gradient-to-br from-emerald-500/20 to-sky-500/20 border border-emerald-500/30'
                      : 'bg-slate-800/50 border border-sky-500/20'
                      }`}
                  >
                    {/* Message Header */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs font-semibold ${msg.role === 'user' ? 'text-emerald-400' : 'text-sky-400'
                        }`}>
                        {msg.role === 'user' ? 'You' : 'Aurora'}
                      </span>
                      {msg.status && getStatusIcon(msg.status)}
                      <span className="text-xs text-slate-500 ml-auto">
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    {/* Message Content */}
                    <div className={`text-sm ${msg.role === 'user' ? 'text-emerald-100' : 'text-sky-100'
                      }`}>
                      {formatMessage(msg.content)}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-sky-500/20 bg-slate-900/60 p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Ask Aurora anything... (natural language works best)"
                  className="flex-1 bg-slate-800/50 border border-sky-500/30 rounded-xl px-4 py-3 text-sky-100 placeholder-sky-400/50 focus:outline-none focus:border-sky-500/60 focus:ring-2 focus:ring-sky-500/20"
                  disabled={isProcessing}
                />
                <button
                  onClick={sendMessage}
                  disabled={isProcessing || !input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-sky-500 rounded-xl font-semibold text-white hover:shadow-lg hover:shadow-sky-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <Sparkles className="w-5 h-5 animate-spin" />
                      <span>Thinking...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span>Send</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-xs text-sky-400/60 mt-2 text-center">
                Pro tip: Be specific and natural - I understand context and nuance
              </p>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
