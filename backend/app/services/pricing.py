from typing import Dict, List, Optional
from app.schemas.comparison import CostMetrics, ModelInfo, ModelPricingRates


class PricingService:
    """
    Dedicated Token Pricing and Cost Estimation Service.
    
    Formula:
      Cost = (T_in * P_in + T_out * P_out) / 1,000,000
    """

    # Official pricing catalog per 1 Million tokens
    CATALOG: Dict[str, Dict] = {
        # Google Gemini (Free tier eligible via Google AI Studio)
        "gemini-3.0-flash": {
            "name": "Gemini 3.0 Flash",
            "provider": "gemini",
            "category": "High Speed / Cost Efficient",
            "description": "Next-gen lightning fast multimodal model with standard 1M token context",
            "input_price_per_million": 0.15,
            "output_price_per_million": 0.60,
            "is_free_tier_eligible": True,
            "is_default": True,
        },
        "gemini-3.0-pro": {
            "name": "Gemini 3.0 Pro",
            "provider": "gemini",
            "category": "Frontier Multimodal",
            "description": "Frontier reasoning model for advanced multimodal and coding tasks",
            "input_price_per_million": 1.25,
            "output_price_per_million": 5.00,
            "is_free_tier_eligible": True,
            "is_default": False,
        },
        "gemini-3.8-flash": {
            "name": "Gemini 3.8 Flash (High)",
            "provider": "gemini",
            "category": "Ultra Fast Reasoning",
            "description": "Enhanced high-throughput flash architecture with expanded reasoning headroom",
            "input_price_per_million": 0.20,
            "output_price_per_million": 0.80,
            "is_free_tier_eligible": True,
            "is_default": False,
        },

        # Anthropic Claude (Paid Only - requires credits)
        "claude-3-7-sonnet": {
            "name": "Claude 3.7 Sonnet",
            "provider": "anthropic",
            "category": "Hybrid Reasoning Flagship",
            "description": "Leading hybrid model offering instantaneous response or extended thinking",
            "input_price_per_million": 3.00,
            "output_price_per_million": 15.00,
            "is_free_tier_eligible": False,
            "is_default": True,
        },
        "claude-3-7-sonnet-thought": {
            "name": "Claude 3.7 Sonnet (Thinking)",
            "provider": "anthropic",
            "category": "Extended Thinking",
            "description": "Claude 3.7 Sonnet configured with active thinking tokens for deep problem solving",
            "input_price_per_million": 3.00,
            "output_price_per_million": 15.00,
            "is_free_tier_eligible": False,
            "is_default": False,
        },
        "claude-4-sonnet": {
            "name": "Claude 4 Sonnet",
            "provider": "anthropic",
            "category": "Frontier Reasoning",
            "description": "Next-generation high capability frontier reasoning from Anthropic",
            "input_price_per_million": 4.00,
            "output_price_per_million": 20.00,
            "is_free_tier_eligible": False,
            "is_default": False,
        },

        # OpenAI (Paid Only - requires credits)
        "gpt-4.5-preview": {
            "name": "GPT-4.5 Preview",
            "provider": "openai",
            "category": "Frontier General Intelligence",
            "description": "Massive scale OpenAI model with unprecedented depth of world knowledge and intuition",
            "input_price_per_million": 75.00,
            "output_price_per_million": 150.00,
            "is_free_tier_eligible": False,
            "is_default": False,
        },
        "o3-mini": {
            "name": "o3-mini",
            "provider": "openai",
            "category": "High-Speed Math & Code",
            "description": "Fast and cost-efficient reasoning model optimized for STEM, coding, and structured logic",
            "input_price_per_million": 1.10,
            "output_price_per_million": 4.40,
            "is_free_tier_eligible": False,
            "is_default": True,
        },
        "o1": {
            "name": "o1",
            "provider": "openai",
            "category": "Deep Multi-step Reasoning",
            "description": "Full-size OpenAI reasoning model for hardest competitive math, science, and coding",
            "input_price_per_million": 15.00,
            "output_price_per_million": 60.00,
            "is_free_tier_eligible": False,
            "is_default": False,
        },
    }

    # Fallback rates if a model identifier is not in the static catalog
    DEFAULT_RATES: Dict[str, Dict[str, float]] = {
        "gemini": {"in": 0.20, "out": 0.80, "free_tier": True},
        "anthropic": {"in": 3.00, "out": 15.00, "free_tier": False},
        "openai": {"in": 2.50, "out": 10.00, "free_tier": False},
    }

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        reasoning_tokens: int = 0,
        force_paid_tier: bool = False,
    ) -> CostMetrics:
        """
        Calculates out-of-pocket invoice cost and estimated commercial list value.
        Reasoning tokens are billed as output tokens.
        """
        # Resolve pricing entry
        entry = self.CATALOG.get(model)
        if entry:
            p_in = entry["input_price_per_million"]
            p_out = entry["output_price_per_million"]
            is_free_tier = entry["is_free_tier_eligible"] and not force_paid_tier
        else:
            defaults = self.DEFAULT_RATES.get(provider.lower(), {"in": 1.0, "out": 3.0, "free_tier": False})
            p_in = defaults["in"]
            p_out = defaults["out"]
            is_free_tier = defaults["free_tier"] and not force_paid_tier

        total_billable_output = max(0, output_tokens)

        # Standard Cost Formula: (T_in * P_in + T_out * P_out) / 10^6
        in_cost = (max(0, input_tokens) * p_in) / 1_000_000.0
        out_cost = (total_billable_output * p_out) / 1_000_000.0
        list_cost = in_cost + out_cost

        # Out-of-pocket actual cost is $0.00 if using a Free Tier key (e.g. Gemini AI Studio)
        actual_cost = 0.0 if is_free_tier else list_cost

        return CostMetrics(
            is_free_tier=is_free_tier,
            actual_cost_usd=round(actual_cost, 6),
            estimated_list_cost_usd=round(list_cost, 6),
            input_cost_usd=round(in_cost, 6),
            output_cost_usd=round(out_cost, 6),
            total_cost_usd=round(actual_cost if not is_free_tier else list_cost, 6),
        )

    def get_models_catalog(self) -> List[ModelInfo]:
        """Returns metadata and pricing for all available models across providers."""
        catalog_list: List[ModelInfo] = []
        for model_id, data in self.CATALOG.items():
            catalog_list.append(
                ModelInfo(
                    id=model_id,
                    name=data["name"],
                    provider=data["provider"],
                    category=data["category"],
                    description=data["description"],
                    pricing=ModelPricingRates(
                        input_price_per_million=data["input_price_per_million"],
                        output_price_per_million=data["output_price_per_million"],
                        is_free_tier_eligible=data["is_free_tier_eligible"],
                    ),
                    is_default=data.get("is_default", False),
                )
            )
        return catalog_list


# Singleton instance
pricing_service = PricingService()
