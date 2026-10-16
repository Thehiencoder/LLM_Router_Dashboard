import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { PromptInput } from './components/PromptInput';
import { ModelSelector } from './components/ModelSelector';
import { ResponseCard } from './components/ResponseCard';
import { SkeletonCard } from './components/SkeletonCard';
import { compareApi } from './api/compare';
import {
  ModelInfo,
  ModelSelection,
  ProviderName,
  CompareResponse,
  HealthResponse,
} from './types/comparison';
import { Sparkles, BarChart3, AlertTriangle, Layers } from 'lucide-react';

export const App: React.FC = () => {
  const [catalog, setCatalog] = useState<ModelInfo[]>([]);
  const [selectedModels, setSelectedModels] = useState<ModelSelection[]>([
    { provider: 'openai', model: 'o3-mini' },
    { provider: 'anthropic', model: 'claude-3-7-sonnet' },
    { provider: 'gemini', model: 'gemini-3.0-flash' },
  ]);

  const [prompt, setPrompt] = useState<string>('');
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [maxTokens, setMaxTokens] = useState<number>(2048);

  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [apiError, setApiError] = useState<string | null>(null);

  // Initialize and load model catalog & health check on mount
  useEffect(() => {
    const initData = async () => {
      try {
        setLoadingHealth(true);
        const [healthRes, catalogRes] = await Promise.all([
          compareApi.fetchHealth().catch(() => null),
          compareApi.fetchModelsCatalog().catch(() => ({ models: [] })),
        ]);

        if (healthRes) {
          setHealth(healthRes);
        }
        if (catalogRes?.models?.length) {
          setCatalog(catalogRes.models);
        }
      } catch (err: any) {
        console.error('Failed to initialize dashboard:', err);
      } finally {
        setLoadingHealth(false);
      }
    };

    initData();
  }, []);

  const handleToggleModel = (provider: ProviderName, modelId: string) => {
    setSelectedModels((prev) => {
      const exists = prev.find((m) => m.provider === provider);
      if (exists) {
        return prev.filter((m) => m.provider !== provider);
      } else {
        return [...prev, { provider, model: modelId }];
      }
    });
  };

  const handleSelectSpecificModel = (provider: ProviderName, modelId: string) => {
    setSelectedModels((prev) => {
      const filtered = prev.filter((m) => m.provider !== provider);
      return [...filtered, { provider, model: modelId }];
    });
  };

  const handleCompare = async () => {
    if (!prompt.trim() || selectedModels.length === 0) return;

    setIsLoading(true);
    setApiError(null);

    try {
      const res = await compareApi.compareModels({
        prompt,
        system_prompt: systemPrompt.trim() || undefined,
        models: selectedModels,
        temperature,
        max_tokens: maxTokens,
      });
      setComparison(res);
    } catch (err: any) {
      setApiError(err.message || 'An unexpected error occurred during comparison.');
    } finally {
      setIsLoading(false);
    }
  };

  // Determine fastest and cheapest winners across successful responses
  const successfulResults = comparison?.results?.filter((r) => r.status === 'success') || [];
  const minLatency = successfulResults.length > 1
    ? Math.min(...successfulResults.map((r) => r.latency_ms))
    : -1;
  const minCost = successfulResults.length > 1
    ? Math.min(...successfulResults.map((r) => r.cost.actual_cost_usd))
    : -1;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <Header health={health} loadingHealth={loadingHealth} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Error Alert */}
        {apiError && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-center space-x-3 text-sm">
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <div className="flex-1">
              <span className="font-semibold">Benchmarking Request Failed: </span>
              <span>{apiError}</span>
            </div>
          </div>
        )}

        {/* Prompt Input Control Area */}
        <PromptInput
          prompt={prompt}
          setPrompt={setPrompt}
          systemPrompt={systemPrompt}
          setSystemPrompt={setSystemPrompt}
          temperature={temperature}
          setTemperature={setTemperature}
          maxTokens={maxTokens}
          setMaxTokens={setMaxTokens}
          onSubmit={handleCompare}
          isLoading={isLoading}
          selectedCount={selectedModels.length}
        />

        {/* Next-Gen Model Selector Chips */}
        <div>
          <div className="flex items-center justify-between mb-3 px-1">
            <h2 className="text-sm font-bold text-slate-300 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Select Models to Benchmark (GPT &gt; 4o, Claude &gt; 3.5, Gemini ≥ 3.0)</span>
            </h2>
            <span className="text-xs text-slate-400">
              {selectedModels.length} of 3 providers active
            </span>
          </div>

          <ModelSelector
            catalog={catalog}
            selectedModels={selectedModels}
            onToggleModel={handleToggleModel}
            onSelectSpecificModel={handleSelectSpecificModel}
          />
        </div>

        {/* Comparison Results Section */}
        <div className="pt-4">
          <div className="flex items-center justify-between mb-4 px-1">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-bold text-slate-300">Side-by-Side Comparison</h2>
            </div>
            {comparison && (
              <span className="text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full">
                Total turnaround:{' '}
                <strong className="text-indigo-400 font-mono">
                  {Math.round(comparison.total_latency_ms)}ms
                </strong>
              </span>
            )}
          </div>

          {/* Skeletons while loading */}
          {isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {selectedModels.map((sm) => (
                <SkeletonCard
                  key={`${sm.provider}-${sm.model}`}
                  provider={sm.provider}
                  modelName={sm.model}
                />
              ))}
            </div>
          )}

          {/* Render Active Responses */}
          {!isLoading && comparison && comparison.results.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {comparison.results.map((result) => (
                <ResponseCard
                  key={`${result.provider}-${result.model}`}
                  result={result}
                  isFastest={result.status === 'success' && minLatency > 0 && result.latency_ms === minLatency}
                  isCheapest={result.status === 'success' && minCost >= 0 && result.cost.actual_cost_usd === minCost}
                />
              ))}
            </div>
          )}

          {/* Initial Clean Empty State */}
          {!isLoading && !comparison && (
            <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center backdrop-blur-sm">
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="text-base font-bold text-slate-200 mb-1">Ready for Multi-Model Inference</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Select your prompt above or click one of the presets to compare responses, token counts, latency, and estimated cost across GPT, Claude, and Gemini concurrently.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600">
        <p>LLM Router Dashboard — Built with React, TypeScript, FastAPI, and Python 3.13 Concurrency.</p>
      </footer>
    </div>
  );
};

export default App;
