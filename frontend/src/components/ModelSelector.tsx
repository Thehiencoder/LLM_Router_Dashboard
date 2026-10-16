import React from 'react';
import { ModelInfo, ModelSelection, ProviderName } from '../types/comparison';
import { Check } from 'lucide-react';

interface ModelSelectorProps {
  catalog: ModelInfo[];
  selectedModels: ModelSelection[];
  onToggleModel: (provider: ProviderName, modelId: string) => void;
  onSelectSpecificModel: (provider: ProviderName, modelId: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  catalog,
  selectedModels,
  onToggleModel,
  onSelectSpecificModel,
}) => {
  const providers: { key: ProviderName; label: string; accent: string; badge: string }[] = [
    {
      key: 'openai',
      label: 'OpenAI',
      accent: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400',
      badge: 'Paid Credits',
    },
    {
      key: 'anthropic',
      label: 'Anthropic',
      accent: 'border-amber-500/40 bg-amber-950/20 text-amber-400',
      badge: 'Paid Credits',
    },
    {
      key: 'gemini',
      label: 'Google Gemini',
      accent: 'border-sky-500/40 bg-sky-950/20 text-sky-400',
      badge: 'Free Tier ($0.00)',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {providers.map((p) => {
        const providerModels = catalog.filter((m) => m.provider === p.key);
        const selected = selectedModels.find((sm) => sm.provider === p.key);
        const isChecked = Boolean(selected);
        const currentModel = providerModels.find((m) => m.id === selected?.model) || providerModels[0];

        return (
          <div
            key={p.key}
            className={`rounded-2xl border transition-all p-4 flex flex-col justify-between ${
              isChecked
                ? `${p.accent} shadow-lg shadow-black/40`
                : 'border-slate-800 bg-slate-900/40 opacity-70 hover:opacity-100'
            }`}
          >
            <div>
              {/* Card Header: Checkbox + Provider Name + Free Tier Badge */}
              <div className="flex items-center justify-between mb-3">
                <button
                  type="button"
                  onClick={() => onToggleModel(p.key, currentModel?.id || '')}
                  className="flex items-center space-x-2 text-left"
                >
                  <div
                    className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${
                      isChecked
                        ? 'bg-indigo-600 border-indigo-500 text-white'
                        : 'border-slate-700 bg-slate-900'
                    }`}
                  >
                    {isChecked && <Check className="w-3.5 h-3.5" />}
                  </div>
                  <span className="font-bold text-sm text-slate-100">{p.label}</span>
                </button>

                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                    p.key === 'gemini'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}
                >
                  {p.badge}
                </span>
              </div>

              {/* Model Dropdown Selector */}
              <div className="mt-2">
                <label className="text-[11px] text-slate-400 mb-1 block">Active Benchmark Model</label>
                <select
                  disabled={!isChecked}
                  value={selected?.model || currentModel?.id || ''}
                  onChange={(e) => onSelectSpecificModel(p.key, e.target.value)}
                  className="w-full rounded-xl bg-slate-950/90 border border-slate-700/80 px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {providerModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.category})
                    </option>
                  ))}
                </select>
              </div>

              {/* Pricing breakdown caption */}
              {currentModel && (
                <div className="mt-3 text-[11px] text-slate-400 bg-slate-950/40 rounded-lg p-2 border border-slate-800/60">
                  <div className="flex justify-between">
                    <span>Input / 1M:</span>
                    <span className="font-mono text-slate-200">${currentModel.pricing.input_price_per_million.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between mt-0.5">
                    <span>Output / 1M:</span>
                    <span className="font-mono text-slate-200">${currentModel.pricing.output_price_per_million.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>

            <p className="text-[11px] text-slate-400 mt-3 line-clamp-2">
              {currentModel?.description}
            </p>
          </div>
        );
      })}
    </div>
  );
};
