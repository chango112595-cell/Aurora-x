import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Code2, Sparkles, Zap, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  code?: string;
  language?: string;
}

interface ExamplePrompt {
  icon: any;
  title: string;
  prompt: string;
}

const examplePrompts: ExamplePrompt[] = [
  {
    icon: Code2,
    title: "RESTful API",
    prompt: "Generate a RESTful API with CRUD operations for a task management system"
  },
  {
    icon: Sparkles,
    title: "Data Processor",
    prompt: "Create a data processing pipeline that validates, transforms, and aggregates CSV data"
  },
  {
    icon: Zap,
    title: "Authentication",
    prompt: "Build a secure JWT authentication system with refresh tokens"
  },
  {
    icon: Rocket,
    title: "WebSocket Server",
    prompt: "Implement a real-time WebSocket server with room management"
  }
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hi! I'm Chango, powered by Aurora-X synthesis. What would you like to build?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [showExamples, setShowExamples] = useState(true);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await apiRequest("POST", "/api/chat", { message });
      return response.json();
    },
    onSuccess: (data: any) => {
      const aiMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.message || "I've generated the code for you. Here's the result:",
        code: data.code,
        language: data.language || "python",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    },
    onError: () => {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  });

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setShowExamples(false);
    chatMutation.mutate(input);
  };

  const handleExampleClick = (prompt: string) => {
    setInput(prompt);
    setShowExamples(false);
  };

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="flex-1 overflow-hidden" ref={scrollAreaRef}>
        <ScrollArea className="h-full">
          <div className="p-6 space-y-6">
            {/* Example prompts - show when chat is empty except for initial message */}
            {showExamples && messages.length === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4 animate-in fade-in duration-500">
                {examplePrompts.map((example, idx) => (
                  <Card
                    key={idx}
                    className="p-4 cursor-pointer hover-elevate transition-all border-muted"
                    onClick={() => handleExampleClick(example.prompt)}
                    data-testid={`example-prompt-${idx}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-md bg-primary/10">
                        <example.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-medium mb-1">{example.title}</h4>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {example.prompt}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Messages */}
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
                style={{ animationDelay: `${index * 50}ms` }}
                data-testid={`message-${message.role}-${message.id}`}
              >
                {message.role === "assistant" && (
                  <Avatar className="h-10 w-10 border-2 border-primary/20">
                    <AvatarFallback className="bg-primary text-primary-foreground font-bold">
                      C
                    </AvatarFallback>
                  </Avatar>
                )}
                <div className={`max-w-[70%] space-y-2`}>
                  <div
                    className={`rounded-lg px-4 py-3 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted/50 border border-border"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  {message.code && (
                    <Card className="p-4 bg-muted/30 border-muted">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-muted-foreground">
                          {message.language || "python"}
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 text-xs"
                          onClick={() => navigator.clipboard.writeText(message.code!)}
                          data-testid="button-copy-code"
                        >
                          Copy
                        </Button>
                      </div>
                      <pre className="overflow-x-auto">
                        <code className="text-xs font-mono text-foreground">
                          {message.code}
                        </code>
                      </pre>
                    </Card>
                  )}
                  <p className="text-xs text-muted-foreground px-1">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                {message.role === "user" && (
                  <Avatar className="h-10 w-10 border-2 border-primary/20">
                    <AvatarFallback className="bg-primary text-primary-foreground font-bold">
                      U
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {chatMutation.isPending && (
              <div className="flex gap-3 justify-start animate-in fade-in duration-300" data-testid="loading-indicator">
                <Avatar className="h-10 w-10 border-2 border-primary/20">
                  <AvatarFallback className="bg-primary text-primary-foreground font-bold">
                    C
                  </AvatarFallback>
                </Avatar>
                <div className="flex items-center gap-2 rounded-lg bg-muted/50 border border-border px-4 py-3">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span className="text-sm">Analyzing request...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input area */}
      <div className="border-t border-border bg-background/95 backdrop-blur-sm p-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask Chango to generate code..."
            className="min-h-[56px] max-h-32 resize-none bg-muted/50"
            data-testid="input-chat"
          />
          <Button
            onClick={handleSend}
            size="icon"
            disabled={!input.trim() || chatMutation.isPending}
            className="h-[56px] w-[56px]"
            data-testid="button-send"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
