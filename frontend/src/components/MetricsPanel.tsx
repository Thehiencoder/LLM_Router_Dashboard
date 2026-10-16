import React from 'react';
import { Clock, Zap, Coins, BrainCircuit, CheckCircle2 } from 'lucide-react';
import { TokenMetrics, CostMetrics } from '../types/comparison';

interface MetricsPanelProps {
  latencyMs: number;
  tokens: TokenMetrics;
  cost: CostMetrics;
  isFastest?: boolean;
  isCheapest?: boolean;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  latencyMs,
  tokens,
  cost,
  isFastest,
  isCheapest,
}) => {
  // Latency styling
  const latencyBadgeColor =
    latencyMs < 1000
      ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
      : latencyMs < 2500
      ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
      : 'text-rose-400 bg-rose-500/10 border-rose-500/20';

  return (
    <div className="pt-4 border-t border-slate-800 space-y-2.5">
      {/* Visual Winner Highlights */}
      {(isFastest || isCheapest) && (
        <div className="flex items-center space-x-2 text-[11px] font-semibold">
          {isFastest && (
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Zap className="w-3 h-3" />
              <span>Fastest Response</span>
            </span>
          )}
          {isCheapest && (
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400">
              <Coins className="w-3 h-3" />
              <span>Lowest Cost</span>
            </span>
          )}
        </div>
      )}

      {/* Main Metric Cards Grid */}
      <div className="grid grid-cols-3 gap-2">
        {/* Latency */}
        <div className={`p-2.5 rounded-xl bg-slate-950/60 border ${latencyBadgeColor} flex flex-col justify-between`}>
          <div className="flex items-center space-x-1.5 text-[11px]">
            <Clock className="w-3.5 h-3.5" />
            <span>Latency</span>
          </div>
          <div className="mt-1 flex items-baseline space-x-1">
            <span className="text-sm font-bold">{Math.round(latencyMs)}</span>
            <span className="text-[10px]">ms</span>
          </div>
        </div>

        {/* Tokens */}
        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <BrainCircuit className="w-3.5 h-3.5 text-purple-400" />
            <span>Tokens</span>
          </div>
          <div className="mt-1 flex items-baseline space-x-1">
            <span className="text-sm font-bold text-slate-100">{tokens.total_tokens.toLocaleString()}</span>
            <span className="text-[10px] text-slate-400" title={`In: ${tokens.input_tokens} | Out: ${tokens.output_tokens}`}>
              ({tokens.input_tokens}/{tokens.output_tokens})
            </span>
          </div>
        </div>

        {/* Cost */}
        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
            <Coins className="w-3.5 h-3.5 text-amber-400" />
            <span>Cost</span>
          </div>
          <div className="mt-1">
            {cost.is_free_tier ? (
              <div>
                <span className="text-xs font-bold text-emerald-400 flex items-center space-x-1">
                  <span>$0.00</span>
                  <span className="text-[9px] font-normal uppercase bg-emerald-500/10 px-1 rounded border border-emerald-500/20">Free</span>
                </span>
                <span className="text-[9px] text-slate-500 block truncate" title={`Estimated list value: $${cost.estimated_list_cost_usd.toFixed(5)}`}>
                  ${cost.estimated_list_cost_usd.toFixed(4)} est.
                </span>
              </div>
            ) : (
              <div>
                <span className="text-sm font-bold text-slate-100">
                  ${cost.actual_cost_usd < 0.01 ? cost.actual_cost_usd.toFixed(5) : cost.actual_cost_usd.toFixed(4)}
                </span>
                <span className="text-[9px] text-slate-500 block">Actual billed</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Internal Reasoning/Thinking Tokens Notice */}
      {Boolean(tokens.reasoning_tokens && tokens.reasoning_tokens > 0) && (
        <div className="text-[10px] text-purple-300/80 bg-purple-500/10 border border-purple-500/20 px-2 py-1 rounded-md flex items-center justify-between">
          <span>Includes {tokens.reasoning_tokens} internal reasoning/thinking tokens</span>
          <CheckCircle2 className="w-3 h-3 text-purple-400" />
        </div>
      )}
    </div>
  );
};
