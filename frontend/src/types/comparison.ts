export type ProviderName = 'openai' | 'anthropic' | 'gemini';

export interface ModelSelection {
  provider: ProviderName;
  model: string;
}

export interface CompareRequest {
  prompt: string;
  system_prompt?: string;
  models: ModelSelection[];
  temperature?: number;
  max_tokens?: number;
}

export interface TokenMetrics {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  reasoning_tokens?: number;
  cached_tokens?: number;
}

export interface CostMetrics {
  is_free_tier: boolean;
  actual_cost_usd: number;
  estimated_list_cost_usd: number;
  input_cost_usd: number;
  output_cost_usd: number;
  total_cost_usd: number;
}

export interface LLMResult {
  provider: ProviderName;
  model: string;
  text?: string | null;
  tokens: TokenMetrics;
  cost: CostMetrics;
  latency_ms: number;
  error?: string | null;
  status: 'success' | 'error';
}

export interface CompareResponse {
  prompt: string;
  total_latency_ms: number;
  results: LLMResult[];
}

export interface ModelPricingRates {
  input_price_per_million: number;
  output_price_per_million: number;
  is_free_tier_eligible: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: ProviderName;
  category: string;
  description: string;
  pricing: ModelPricingRates;
  is_default: boolean;
}

export interface ModelsCatalogResponse {
  models: ModelInfo[];
}

export interface HealthResponse {
  status: string;
  mock_mode: boolean;
  providers_configured: {
    openai: boolean;
    anthropic: boolean;
    gemini: boolean;
  };
}
