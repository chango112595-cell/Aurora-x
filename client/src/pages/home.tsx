import { ChatInterface } from "@/components/chat-interface";
import { Card } from "@/components/ui/card";
import backgroundImage from "@assets/generated_images/Holographic_AI_neural_network_background_9dd21e33.png";
import { useEffect, useState } from "react";

export default function Home() {
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, delay: number}>>([]);
  
  useEffect(() => {
    // Generate floating particles for futuristic effect
    const particleArray = Array.from({ length: 20 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5
    }));
    setParticles(particleArray);
  }, []);

  return (
    <div className="h-full flex flex-col relative overflow-hidden">
      {/* Animated background with holographic effect */}
      <div 
        className="absolute inset-0 opacity-15 bg-cover bg-center pointer-events-none animate-pulse"
        style={{ 
          backgroundImage: `url(${backgroundImage})`,
          filter: 'hue-rotate(0deg)',
          animation: 'hueRotate 10s linear infinite'
        }}
      />
      
      {/* Floating particles */}
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute w-1 h-1 bg-cyan-400 rounded-full pointer-events-none opacity-60"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            animation: `float 8s ease-in-out infinite`,
            animationDelay: `${particle.delay}s`,
            boxShadow: '0 0 10px 2px rgba(6, 182, 212, 0.5)'
          }}
        />
      ))}
      
      {/* Scanning lines effect */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-20"
             style={{ animation: 'scan 3s linear infinite' }} />
      </div>
      
      {/* Holographic grid overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-5"
           style={{
             backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(6, 182, 212, 0.3) 25%, rgba(6, 182, 212, 0.3) 26%, transparent 27%, transparent 74%, rgba(6, 182, 212, 0.3) 75%, rgba(6, 182, 212, 0.3) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(6, 182, 212, 0.3) 25%, rgba(6, 182, 212, 0.3) 26%, transparent 27%, transparent 74%, rgba(6, 182, 212, 0.3) 75%, rgba(6, 182, 212, 0.3) 76%, transparent 77%, transparent)',
             backgroundSize: '50px 50px'
           }}
      />
      
      <div className="relative z-10 flex flex-col h-full">
        {/* Futuristic header with glow effect */}
        <div className="border-b border-cyan-500/30 p-6 backdrop-blur-sm bg-background/40 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-cyan-500/10 animate-pulse" />
          <div className="relative">
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 animate-gradient" 
                data-testid="text-page-title"
                style={{ animation: 'gradient 3s ease infinite' }}>
              Chat with Chango
            </h1>
            <p className="text-sm text-cyan-300/70 mt-2 font-mono">
              <span className="inline-block w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse" />
              Aurora-X Neural Synthesis Engine • Status: ACTIVE
            </p>
          </div>
        </div>
        
        <div className="flex-1 overflow-hidden relative">
          {/* Corner accents */}
          <div className="absolute top-0 left-0 w-20 h-20 border-l-2 border-t-2 border-cyan-500/30 pointer-events-none" />
          <div className="absolute top-0 right-0 w-20 h-20 border-r-2 border-t-2 border-cyan-500/30 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-20 h-20 border-l-2 border-b-2 border-cyan-500/30 pointer-events-none" />
          <div className="absolute bottom-0 right-0 w-20 h-20 border-r-2 border-b-2 border-cyan-500/30 pointer-events-none" />
          
          <ChatInterface />
        </div>
      </div>
      
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); }
          25% { transform: translateY(-20px) translateX(10px); }
          50% { transform: translateY(-40px) translateX(-10px); }
          75% { transform: translateY(-20px) translateX(10px); }
        }
        
        @keyframes scan {
          0% { top: -2px; }
          100% { top: 100%; }
        }
        
        @keyframes hueRotate {
          0% { filter: hue-rotate(0deg); }
          100% { filter: hue-rotate(360deg); }
        }
        
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
      `}</style>
    </div>
  );
}
