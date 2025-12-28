import React from "react";

export default function AuroraSplash({ statusText = "Initializing holographic interface…" }: { statusText?: string }) {
  return (
    <div className="h-screen w-screen bg-black relative overflow-hidden flex items-center justify-center">
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/30 via-black to-purple-900/40 animate-pulse" />
      <div className="absolute w-96 h-96 rounded-full blur-3xl bg-cyan-500/20 animate-ping" />
      <div className="absolute w-64 h-64 rounded-full blur-3xl bg-purple-500/20 animate-pulse" />

      <div className="relative flex flex-col items-center gap-6">
        <div className="relative">
          <div className="w-32 h-32 rounded-full bg-gradient-to-tr from-cyan-500 via-purple-500 to-indigo-500 animate-spin-slow shadow-2xl shadow-cyan-500/40" />
          <div className="absolute inset-4 rounded-full bg-black/60 backdrop-blur-sm border border-cyan-400/30 flex items-center justify-center text-5xl font-black text-cyan-200 tracking-widest">
            A
          </div>
        </div>
        <div className="text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-200/80">Aurora System</p>
          <p className="text-xl text-white font-semibold mt-2">{statusText}</p>
        </div>
      </div>
    </div>
  );
}
