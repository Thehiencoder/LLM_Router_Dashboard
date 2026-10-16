import React from 'react';
import { Layers, Sparkles, ShieldCheck } from 'lucide-react';
import { HealthResponse } from '../types/comparison';

interface HeaderProps {
  health: HealthResponse | null;
  loadingHealth: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, loadingHealth }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-tight">LLM Router Dashboard</h1>
              <span className="text-[10px] font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full">
                Next-Gen
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Side-by-side inference, token count, cost, and latency benchmarking
            </p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center space-x-3 text-xs">
          {health?.mock_mode && (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 font-medium">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Mock Mode Active</span>
            </div>
          )}

          <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300">
            <div className={`w-2 h-2 rounded-full ${loadingHealth ? 'bg-amber-400 animate-ping' : health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            <span className="font-medium">
              {loadingHealth ? 'Connecting...' : health?.status === 'healthy' ? 'Backend Ready' : 'Backend Offline'}
            </span>
          </div>

          <div className="hidden md:flex items-center space-x-2 text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Python 3.13 Concurrency</span>
          </div>
        </div>
      </div>
    </header>
  );
};
