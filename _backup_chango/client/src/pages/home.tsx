import { ChatInterface } from "@/components/chat-interface";
import { Card } from "@/components/ui/card";
import backgroundImage from "@assets/generated_images/Holographic_AI_neural_network_background_9dd21e33.png";

export default function Home() {
  return (
    <div className="h-full flex flex-col relative">
      <div 
        className="absolute inset-0 opacity-10 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: `url(${backgroundImage})` }}
      />
      
      <div className="relative z-10 flex flex-col h-full">
        <div className="border-b border-border p-6">
          <h1 className="text-2xl font-bold" data-testid="text-page-title">Chat with Chango</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Request code generation powered by Aurora-X synthesis engine
          </p>
        </div>
        
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </div>
    </div>
  );
}
