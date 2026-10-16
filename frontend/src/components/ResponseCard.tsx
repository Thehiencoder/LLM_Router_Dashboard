import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, Check, AlertCircle, Bot, Maximize2, Minimize2 } from 'lucide-react';
import { LLMResult } from '../types/comparison';
import { MetricsPanel } from './MetricsPanel';

interface ResponseCardProps {
  result: LLMResult;
  isFastest?: boolean;
  isCheapest?: boolean;
}

export const ResponseCard: React.FC<ResponseCardProps> = ({
  result,
  isFastest,
  isCheapest,
}) => {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = async () => {
    if (result.text) {
      await navigator.clipboard.writeText(result.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const providerStyles = {
    openai: {
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      glow: 'shadow-emerald-500/5',
      name: 'OpenAI',
    },
    anthropic: {
      border: 'border-amber-500/30',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      glow: 'shadow-amber-500/5',
      name: 'Anthropic',
    },
    gemini: {
      border: 'border-sky-500/30',
      badge: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
      glow: 'shadow-sky-500/5',
      name: 'Google Gemini',
    },
  }[result.provider] || {
    border: 'border-slate-800',
    badge: 'bg-slate-800 text-slate-400 border-slate-700',
    glow: '',
    name: result.provider,
  };

  return (
    <div
      className={`rounded-2xl border ${providerStyles.border} bg-slate-900/60 p-5 flex flex-col justify-between shadow-2xl backdrop-blur-xl ${providerStyles.glow} transition-all ${
        isExpanded ? 'fixed inset-4 z-50 overflow-y-auto bg-slate-950/95 max-w-5xl mx-auto' : ''
      }`}
    >
      <div>
        {/* Top Header */}
        <div className="flex items-center justify-between pb-3.5 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center">
              <Bot className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-sm text-slate-100">{result.model}</span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${providerStyles.badge}`}>
                  {providerStyles.name}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1.5">
            {result.text && (
              <>
                <button
                  type="button"
                  onClick={handleCopy}
                  title="Copy response markdown"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
                <button
                  type="button"
                  onClick={() => setIsExpanded(!isExpanded)}
                  title={isExpanded ? "Collapse" : "Expand"}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                >
                  {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Content Body */}
        <div className="py-4 text-sm text-slate-200 leading-relaxed overflow-x-auto min-h-[160px]">
          {result.status === 'error' ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 space-y-2">
              <div className="flex items-center space-x-2 font-semibold text-xs">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>Inference Error</span>
              </div>
              <p className="text-xs font-mono text-rose-200/90 break-words">{result.error}</p>
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-code:font-mono">
              <ReactMarkdown>{result.text || ''}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* Metrics Footer */}
      <MetricsPanel
        latencyMs={result.latency_ms}
        tokens={result.tokens}
        cost={result.cost}
        isFastest={isFastest}
        isCheapest={isCheapest}
      />
    </div>
  );
};
