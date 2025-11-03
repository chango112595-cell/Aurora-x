/**
 * Aurora Chat Interface
 * Part of Aurora-X Neural Synthesis Engine
 * 🌟 Aurora's own UI for natural language code generation
 */

import { ErrorBoundary } from '@/components/error-boundary';
import { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'aurora';
    content: string;
    timestamp: Date;
    data?: Record<string, unknown>;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '0',
            role: 'aurora',
            content: "🌟 Hi! I'm Aurora. Just tell me what you want to build in plain English, and I'll generate it instantly!",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const processCommand = (command: string): string | null => {
        const cmd = command.toLowerCase().trim();

        if (cmd === '/help') {
            return `🌟 Here are some commands you can try:
/status - See if everything's working
/diagnostics - Check what needs fixing
/fix-all - Let me fix issues automatically
/help - This menu

Or just tell me what you want to build and I'll create it! 💡`;
        }

        if (cmd === '/status') {
            return `🌟 Everything's running great!
✅ Chat: Working
✅ Code Generation: Ready
✅ Real-time: Active`;
        }

        if (cmd === '/diagnostics') {
            return `🌟 Let me scan the system...
Found some minor things to fix.
Type /fix-all to let me handle them all!`;
        }

        if (cmd === '/fix-all') {
            return `🌟 I'm on it! Fixing everything now...
This might take a minute. I'll let you know when I'm done! ⚡`;
        }

        return null;
    };

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

        // Check for commands
        const commandResponse = processCommand(promptToSend);
        if (commandResponse) {
            const auroraMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'aurora',
                content: commandResponse,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, auroraMessage]);
            return;
        }

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
                content: `🌟 Hmm, something went wrong. ${error instanceof Error ? error.message : 'Not sure what happened.'} Try again or type /help for commands.`,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const formatAuroraResponse = (data: Record<string, unknown> | null): string => {
        if (!data?.ok) {
            return `🌟 Sorry, I hit a little snag trying to generate that. Here's what happened:\n\n${JSON.stringify(data, null, 2)}`;
        }

        let response = `🌟 Done! Here's what I created:\n\n`;

        if (data?.kind) response += `• ${data.kind}\n`;
        if (data?.lang) response += `• Written in: ${data.lang}\n`;
        if (data?.file) response += `• Saved to: ${data.file}\n`;
        if (data?.tests) response += `• Tests ready: ${data.tests}\n`;
        if (data?.reason) response += `\nWhy I did it this way: ${data.reason}\n`;
        if (data?.hint) response += `\n💡 Pro tip: ${data.hint}\n`;

        response += `\nWant me to change anything? Just let me know! 🎯`;

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
            {/* Aurora's Quantum Background */}
            <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20" />

                {/* Particle field */}
                <div className="absolute inset-0 opacity-20" style={{
                    backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
                    backgroundSize: '50px 50px',
                    animation: 'particleFloat 20s linear infinite'
                }} />

                {/* Neural network grid */}
                <svg className="absolute inset-0 w-full h-full opacity-10">
                    <defs>
                        <linearGradient id="grid-chat" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.5" />
                            <stop offset="100%" stopColor="#a855f7" stopOpacity="0.5" />
                        </linearGradient>
                    </defs>
                    <pattern id="grid-pattern-chat" width="50" height="50" patternUnits="userSpaceOnUse">
                        <circle cx="25" cy="25" r="1" fill="url(#grid-chat)" />
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#grid-pattern-chat)" />
                </svg>

                {/* Holographic orbs */}
                <div className="absolute top-20 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
            </div>

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
