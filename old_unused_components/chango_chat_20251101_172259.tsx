/**
 * Aurora Chat Interface
 * Created by Aurora autonomously to fix response display issue
 * 
 * Aurora's personality: 🌟 Fast, smart, friendly, proactive
 */

import { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '0',
            role: 'assistant',
            content: "🌟 Hi! I'm Aurora. I can understand natural language and generate code for you instantly! Just tell me what you want to build.",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
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

        // Add user message immediately
        setMessages((prev) => {
            console.log('🌟 Aurora: Adding user message to state');
            return [...prev, userMessage];
        });

        const promptToSend = input;  // Save before clearing
        setInput('');
        setIsLoading(true);

        try {
            console.log('🌟 Aurora: Calling endpoint with:', promptToSend);

            // Call Aurora's chat endpoint
            const response = await fetch('http://localhost:5001/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: promptToSend,
                }),
            });

            console.log('🌟 Aurora: Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('🌟 Aurora: Response data:', data);

            // Aurora's response
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: formatAuroraResponse(data),
                timestamp: new Date(),
            };

            console.log('🌟 Aurora: Formatted response:', assistantMessage.content);

            // Add Aurora's response to chat
            setMessages((prev) => {
                console.log('🌟 Aurora: Adding assistant message to state, current messages:', prev.length);
                const newMessages = [...prev, assistantMessage];
                console.log('🌟 Aurora: New messages count:', newMessages.length);
                return newMessages;
            });

            console.log('✅ Aurora: Message added successfully!');
        } catch (error) {
            console.error('❌ Aurora chat error:', error);

            // Error message with Aurora's personality
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `🌟 Oops! I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Let me try to help anyway!`,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const formatAuroraResponse = (data: any): string => {
        // Aurora formats her responses with personality
        if (!data.ok) {
            return `🌟 I couldn't generate that right now, but here's what I found: ${JSON.stringify(data, null, 2)}`;
        }

        let response = `🌟 I've got it! Here's what I created:\n\n`;

        if (data.kind) {
            response += `**Type:** ${data.kind}\n`;
        }
        if (data.lang) {
            response += `**Language:** ${data.lang}\n`;
        }
        if (data.file) {
            response += `**File:** ${data.file}\n`;
        }
        if (data.tests) {
            response += `**Tests:** ${data.tests}\n`;
        }
        if (data.reason) {
            response += `\n**Aurora's reasoning:** ${data.reason}\n`;
        }

        response += `\nLet me know if you'd like me to adjust anything! ⚡`;

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
                        <h1 className="text-2xl font-bold text-cyan-400">
                            Chat with Aurora
                        </h1>
                        <div className="ml-auto">
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-sm">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
                                </span>
                                Aurora-X Neural Synthesis Engine • Status: ACTIVE
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
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                    }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg px-4 py-3 ${message.role === 'user'
                                        ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/30'
                                        : 'bg-gray-800/50 text-gray-100 border border-gray-700'
                                        }`}
                                >
                                    <div className="flex items-start gap-3">
                                        {message.role === 'assistant' && (
                                            <Sparkles className="h-5 w-5 text-cyan-400 mt-1 flex-shrink-0" />
                                        )}
                                        <div className="flex-1">
                                            <div className="whitespace-pre-wrap break-words">
                                                {message.content}
                                            </div>
                                            <div className="text-xs text-gray-500 mt-2">
                                                {message.timestamp.toLocaleTimeString()}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {/* Typing indicator */}
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
                                        <span className="text-gray-400 text-sm">Aurora is thinking...</span>
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
                            placeholder="Just type what you want in natural language – I'll understand and generate it for you! 🌟"
                            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
                            rows={3}
                            disabled={isLoading}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!input.trim() || isLoading}
                            className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
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
                        🌟 Aurora can generate CLI tools, web apps, libraries, and more – just describe what you want!
                    </div>
                </div>
            </div>
        </div>
    );
}
