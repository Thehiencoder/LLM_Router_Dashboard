import React from 'react';
import { Loader2 } from 'lucide-react';

interface SkeletonCardProps {
  modelName: string;
  provider: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({ modelName, provider }) => {
  const providerColor =
    provider === 'openai'
      ? 'border-emerald-500/30'
      : provider === 'anthropic'
      ? 'border-amber-500/30'
      : 'border-sky-500/30';

  return (
    <div className={`rounded-2xl border ${providerColor} bg-slate-900/60 p-5 flex flex-col justify-between shadow-xl backdrop-blur-md animate-pulse`}>
      {/* Header skeleton */}
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-slate-800" />
            <div>
              <div className="font-semibold text-xs text-slate-300">{modelName}</div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">{provider}</div>
            </div>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
            <span>Streaming...</span>
          </div>
        </div>

        {/* Content body skeleton */}
        <div className="py-4 space-y-2.5">
          <div className="h-3.5 bg-slate-800/70 rounded w-11/12" />
          <div className="h-3.5 bg-slate-800/70 rounded w-full" />
          <div className="h-3.5 bg-slate-800/70 rounded w-4/5" />
          <div className="h-20 bg-slate-800/40 rounded-xl w-full border border-slate-800 mt-3" />
          <div className="h-3.5 bg-slate-800/70 rounded w-9/12 mt-3" />
        </div>
      </div>

      {/* Metrics footer skeleton */}
      <div className="pt-4 border-t border-slate-800 grid grid-cols-3 gap-2">
        <div className="h-10 bg-slate-800/50 rounded-lg" />
        <div className="h-10 bg-slate-800/50 rounded-lg" />
        <div className="h-10 bg-slate-800/50 rounded-lg" />
      </div>
    </div>
  );
};
