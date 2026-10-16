import {
  CompareRequest,
  CompareResponse,
  ModelsCatalogResponse,
  HealthResponse,
} from '../types/comparison';

const API_BASE = '/api';

export const compareApi = {
  /**
   * Submit prompt for concurrent multi-model benchmarking.
   */
  async compareModels(payload: CompareRequest): Promise<CompareResponse> {
    const response = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  },

  /**
   * Retrieve catalog of supported models, categories, default selections, and pricing.
   */
  async fetchModelsCatalog(): Promise<ModelsCatalogResponse> {
    const response = await fetch(`${API_BASE}/models`);
    if (!response.ok) {
      throw new Error(`Failed to load models catalog: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Check backend health and active provider key availability.
   */
  async fetchHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.statusText}`);
    }
    return response.json();
  },
};
