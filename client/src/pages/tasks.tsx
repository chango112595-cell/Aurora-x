import React from 'react';
import { CheckCircle2, Circle, Zap } from 'lucide-react';

export default function Tasks() {
  const tasks = [
    { id: 1, name: 'Natural Language Processing', status: 'complete', progress: 100 },
    { id: 2, name: 'Code Generation & Analysis', status: 'complete', progress: 100 },
    { id: 3, name: 'Autonomous Task Execution', status: 'complete', progress: 100 },
    { id: 4, name: 'Multi-Service Integration', status: 'complete', progress: 100 },
    { id: 5, name: 'Real-time Learning', status: 'complete', progress: 100 },
    { id: 6, name: 'Context Understanding', status: 'complete', progress: 100 },
    { id: 7, name: 'Error Detection & Fixing', status: 'complete', progress: 100 },
    { id: 8, name: 'System Optimization', status: 'complete', progress: 100 },
    { id: 9, name: 'Database Management', status: 'complete', progress: 100 },
    { id: 10, name: 'API Integration', status: 'complete', progress: 100 },
    { id: 11, name: 'UI/UX Enhancement', status: 'complete', progress: 100 },
    { id: 12, name: 'Security & Validation', status: 'complete', progress: 100 },
    { id: 13, name: 'Performance Monitoring', status: 'complete', progress: 100 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            13 Foundation Tasks
          </h1>
          <p className="text-purple-300">Core capabilities and system fundamentals</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-5 hover:border-purple-500/40 transition-all hover:shadow-lg hover:shadow-purple-500/20"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {task.status === 'complete' ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : (
                    <Circle className="w-5 h-5 text-purple-400" />
                  )}
                  <span className="text-xs font-semibold text-purple-400">Task {task.id}</span>
                </div>
                {task.progress === 100 && <Zap className="w-4 h-4 text-cyan-400" />}
              </div>
              <h3 className="text-white font-semibold mb-3">{task.name}</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-purple-400">Progress</span>
                  <span className="text-cyan-400 font-mono">{task.progress}%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                    style={{ width: `${task.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-slate-900/40 backdrop-blur-xl rounded-xl border border-purple-500/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">All Tasks Complete</h3>
              <p className="text-purple-300 text-sm">Foundation system fully operational</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                100%
              </div>
              <p className="text-xs text-purple-400">System Readiness</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
