import React, { useState, KeyboardEvent } from 'react';
import { Send, SlidersHorizontal, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface PromptInputProps {
  prompt: string;
  setPrompt: (value: string) => void;
  systemPrompt: string;
  setSystemPrompt: (value: string) => void;
  temperature: number;
  setTemperature: (value: number) => void;
  maxTokens: number;
  setMaxTokens: (value: number) => void;
  onSubmit: () => void;
  isLoading: boolean;
  selectedCount: number;
}

const PRESETS = [
  {
    label: "Algorithm & Code",
    prompt: "Write a thread-safe LRU Cache in Python with O(1) get and put operations, including unit tests.",
  },
  {
    label: "Complex Reasoning",
    prompt: "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show your step-by-step mathematical reasoning.",
  },
  {
    label: "Creative Analogy",
    prompt: "Explain how transformer self-attention mechanisms work to a 12-year-old using a bustling library metaphor.",
  },
];

export const PromptInput: React.FC<PromptInputProps> = ({
  prompt,
  setPrompt,
  systemPrompt,
  setSystemPrompt,
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
  onSubmit,
  isLoading,
  selectedCount,
}) => {
  const [showSettings, setShowSettings] = useState(false);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (prompt.trim() && !isLoading && selectedCount > 0) {
        onSubmit();
      }
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-2xl backdrop-blur-xl">
      {/* Preset Pills */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <span className="text-xs font-semibold text-slate-400 flex items-center space-x-1 mr-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Presets:</span>
        </span>
        {PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => setPrompt(p.prompt)}
            className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 transition-colors"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Main Prompt Textarea */}
      <div className="relative">
        <textarea
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter a prompt to benchmark across GPT, Claude, and Gemini side-by-side... (Press Ctrl + Enter to run)"
          className="w-full rounded-xl bg-slate-950/80 border border-slate-800/90 p-4 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/80 text-sm transition-all resize-y min-h-[90px]"
        />
      </div>

      {/* Advanced Settings Toggle & Submit Row */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 pt-2">
        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Inference Parameters</span>
          {showSettings ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-400 hidden sm:inline">
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">Enter</kbd>
          </span>

          <button
            type="button"
            onClick={onSubmit}
            disabled={!prompt.trim() || isLoading || selectedCount === 0}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 via-indigo-600 to-purple-600 text-white font-semibold text-xs shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
          >
            <Send className="w-4 h-4" />
            <span>{isLoading ? 'Benchmarking...' : `Compare (${selectedCount} Models)`}</span>
          </button>
        </div>
      </div>

      {/* Collapsible Advanced Parameters */}
      {showSettings && (
        <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs animate-fadeIn">
          {/* System Prompt */}
          <div className="md:col-span-3">
            <label className="block text-slate-400 font-medium mb-1">System Instruction (Optional)</label>
            <input
              type="text"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="e.g. You are an expert distributed systems engineer. Be concise and precise."
              className="w-full rounded-lg bg-slate-950/80 border border-slate-800 px-3 py-2 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* Temperature */}
          <div>
            <div className="flex justify-between text-slate-400 mb-1">
              <span>Temperature</span>
              <span className="text-slate-200 font-mono">{temperature}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.5"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <span className="text-[10px] text-slate-500">Note: Reasoning models (o1/o3-mini) use fixed sampling</span>
          </div>

          {/* Max Tokens */}
          <div>
            <div className="flex justify-between text-slate-400 mb-1">
              <span>Max Completion Tokens</span>
              <span className="text-slate-200 font-mono">{maxTokens}</span>
            </div>
            <input
              type="range"
              min="256"
              max="8192"
              step="256"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value, 10))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
};
