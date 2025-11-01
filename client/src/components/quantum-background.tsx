import { ReactNode } from 'react';

interface QuantumBackgroundProps {
  children: ReactNode;
  className?: string;
}

export function QuantumBackground({ children, className = '' }: QuantumBackgroundProps) {
  return (
    <div className={`relative min-h-screen ${className}`}>
      {/* Quantum field background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-purple-950/50 to-cyan-950/50" />
        
        {/* Animated particles */}
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'particleFloat 20s linear infinite'
        }} />
        
        {/* Neural grid */}
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.3) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(6, 182, 212, 0.3) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          animation: 'gridPulse 4s ease-in-out infinite'
        }} />
        
        {/* Glowing orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}} />
      </div>
      
      {children}
      
      <style jsx global>{`
        @keyframes particleFloat {
          0%, 100% { transform: translateY(0) translateX(0); }
          50% { transform: translateY(-20px) translateX(10px); }
        }
        
        @keyframes gridPulse {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}
