import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Code2, Sparkles, Zap, Rocket, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { SynthesisProgress } from "@/components/synthesis-progress";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  code?: string;
  language?: string;
  synthesisId?: string;
  isProcessing?: boolean;
}

interface ExamplePrompt {
  icon: any;
  title: string;
  prompt: string;
}

const examplePrompts: ExamplePrompt[] = [
  {
    icon: Code2,
    title: "String Reversal",
    prompt: "reverse a string (unicode safe)"
  },
  {
    icon: Zap,
    title: "Factorial Function",
    prompt: "write factorial(n) with unit tests"
  },
  {
    icon: Sparkles,
    title: "Creative Haiku",
    prompt: "generate a random haiku about coding"
  },
  {
    icon: Rocket,
    title: "LRU Cache",
    prompt: "build a tiny LRU cache class with get/put and capacity"
  },
  {
    icon: Shield,
    title: "Email Validation",
    prompt: "validate an email with regex + tests"
  }
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hi! I'm Chango, powered by Aurora-X synthesis. I can turn any English request into working Python code - from algorithms to creative text generation. What would you like to build?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [showExamples, setShowExamples] = useState(true);
  const [activeSynthesisId, setActiveSynthesisId] = useState<string | null>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await apiRequest("POST", "/api/chat", { message: message.trim() });

      const data = await response.json();

      if (!response.ok) {
        console.error('Chat API error:', data);
        throw new Error(data.error || data.message || 'Failed to send message');
      }

      console.log('Chat API response:', data);
      return data;
    },
    onSuccess: (data: any) => {
      if (data.synthesis_id) {
        // Initial response with synthesis ID
        setActiveSynthesisId(data.synthesis_id);

        // Add a processing message with synthesis ID
        const processingMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: "Processing your request...",
          synthesisId: data.synthesis_id,
          isProcessing: true,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, processingMessage]);
      } else {
        // Fallback for direct response (shouldn't happen with new system)
        // Show the synthesis result
        const resultMessage = data.message || 
          (data.code_file ? `✅ Generated: ${data.code_file}` : 'Code generated successfully');

        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: resultMessage,
        }]);
      }
    },
    onError: (error: any) => {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `I encountered an error while processing your request: ${error?.message || "Unknown error"}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setActiveSynthesisId(null);
    }
  });

  // Poll for synthesis result when complete
  const { data: synthesisResult } = useQuery({
    queryKey: [`/api/synthesis/result/${activeSynthesisId}`],
    enabled: false, // We'll handle completion through progress component
    refetchInterval: false,
  });

  const handleSynthesisComplete = (progressData: any) => {
    // Extract the synthesized code from the progress data result
    const result = progressData.result;
    const code = result?.code || `# Synthesis completed but no code was generated\n# Synthesis ID: ${progressData.id}`;
    const language = result?.language || "python";
    const functionName = result?.functionName || "synthesized_function";
    const description = result?.description || progressData.message || "Aurora-X has successfully synthesized your code!";

    const completedMessage: Message = {
      id: Date.now().toString(),
      role: "assistant",
      content: description,
      code: code,
      language: language,
      timestamp: new Date(),
    };

    // Replace the processing message with the completed one
    setMessages((prev) => {
      const updated = [...prev];
      const processingIndex = updated.findIndex(m => m.synthesisId === progressData.id);
      if (processingIndex !== -1) {
        updated[processingIndex] = completedMessage;
      } else {
        updated.push(completedMessage);
      }
      return updated;
    });

    setActiveSynthesisId(null);
  };

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
              <div className="mt-4 animate-in fade-in duration-500">
                <p className="text-sm text-muted-foreground mb-3 font-medium">Try these examples:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
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
                  {/* Show synthesis progress for processing messages */}
                  {message.synthesisId && message.isProcessing && (
                    <SynthesisProgress
                      synthesisId={message.synthesisId}
                      onComplete={handleSynthesisComplete}
                      className="mt-2"
                    />
                  )}
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