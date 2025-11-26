import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Zap, Code, CheckCircle2, AlertCircle } from 'lucide-react';
import { ErrorBoundary } from './error-boundary';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'thinking' | 'executing' | 'complete' | 'error';
}

export default function AuroraFuturisticChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hey! I'm Aurora. What would you like to work on today? I can help you code, debug, analyze, or build anything you need.",
      timestamp: new Date(),
      status: 'complete'
    }
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(() => `chat-${Date.now()}`); // Persistent session ID
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

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    // Add thinking message
    const thinkingMessage: Message = {
      role: 'assistant',
      content: 'Analyzing your request...',
      timestamp: new Date(),
      status: 'thinking'
    };
    setMessages(prev => [...prev, thinkingMessage]);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });

      const data = await response.json();

      // Aurora's autonomous null check
      if (!data || !data.response) {
        throw new Error('Invalid response from Aurora');
      }

      // Update with response
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;

        // If response indicates execution
        if (data.executing) {
          newMessages[lastIndex] = {
            role: 'assistant',
            content: data.response,
            timestamp: new Date(),
            status: 'executing'
          };
        } else {
          newMessages[lastIndex] = {
            role: 'assistant',
            content: data.response,
            timestamp: new Date(),
            status: 'complete'
          };
        }

        return newMessages;
      });
    } catch (error) {
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: 'Oops, something went wrong. Let me try that again.',
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
        return <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />;
      case 'executing':
        return <Zap className="w-4 h-4 text-purple-400 animate-pulse" />;
      case 'complete':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return null;
    }
  };

  const formatMessage = (content: string) => {
    // Aurora's autonomous error detection: null safety + type coercion
    if (!content) return <span className="text-slate-500">Empty message</span>;

    // Ensure content is a string (Aurora's autonomous type safety)
    const safeContent = typeof content === 'string' ? content : String(content);

    try {
      // Format code blocks
      const parts = safeContent.split('```');
      return parts.map((part, i) => {
        if (i % 2 === 1) {
          // Code block
          const lines = part.split('\n');
          const language = lines[0] || 'code';
          const code = lines.slice(1).join('\n');

          return (
            <div key={`code-${i}`} className="my-3 rounded-lg bg-slate-900/80 border border-purple-500/20 overflow-hidden">
              <div className="px-3 py-1 bg-purple-500/10 border-b border-purple-500/20 flex items-center gap-2">
                <Code className="w-3 h-3 text-purple-400" />
                <span className="text-xs text-purple-400 font-mono">{language}</span>
              </div>
              <pre className="p-3 overflow-x-auto">
                <code className="text-sm text-cyan-300 font-mono">{code}</code>
              </pre>
            </div>
          );
        }

        // Regular text - make it more natural with proper formatting
        return (
          <div key={`text-${i}`} className="whitespace-pre-wrap leading-relaxed">
            {part.split('\n').map((line, j) => {
              // Bold text
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
              // Bullet points
              if (line.trim().startsWith('- ')) {
                return (
                  <li key={j} className="ml-4 mb-1 text-purple-200">
                    {line.replace('- ', '')}
                  </li>
                );
              }
              return line.trim() ? <p key={j} className="mb-2">{line}</p> : <br key={j} />;
            })}
          </div>
        );
      });
    } catch (error) {
      // Aurora's autonomous error handler
      console.error('[AURORA] Format error:', error);
      return <span className="text-red-400">Error formatting message</span>;
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-6 text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              Neural Chat
            </h1>
            <p className="text-purple-300 text-sm">Natural conversation with Aurora</p>
          </div>

          {/* Chat Container */}
          <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-purple-500/20 shadow-2xl overflow-hidden">
            {/* Messages Area */}
            <div className="h-[600px] overflow-y-auto p-6 space-y-4">
              {messages?.map((msg, idx) => (
                <div
                  key={`msg-${idx}-${msg.timestamp.getTime()}`}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                      ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30'
                      : 'bg-slate-800/50 border border-purple-500/20'
                      }`}
                  >
                    {/* Message Header */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs font-semibold ${msg.role === 'user' ? 'text-cyan-400' : 'text-purple-400'
                        }`}>
                        {msg.role === 'user' ? 'You' : 'Aurora'}
                      </span>
                      {msg.status && getStatusIcon(msg.status)}
                      <span className="text-xs text-slate-500 ml-auto">
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    {/* Message Content */}
                    <div className={`text-sm ${msg.role === 'user' ? 'text-cyan-100' : 'text-purple-100'
                      }`}>
                      {formatMessage(msg.content)}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-purple-500/20 bg-slate-900/60 p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Ask Aurora anything... (natural language works best)"
                  className="flex-1 bg-slate-800/50 border border-purple-500/30 rounded-xl px-4 py-3 text-purple-100 placeholder-purple-400/50 focus:outline-none focus:border-purple-500/60 focus:ring-2 focus:ring-purple-500/20"
                  disabled={isProcessing}
                />
                <button
                  onClick={sendMessage}
                  disabled={isProcessing || !input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-xl font-semibold text-white hover:shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
              <p className="text-xs text-purple-400/60 mt-2 text-center">
                Pro tip: Be specific and natural - I understand context and nuance
              </p>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
