"""
model_factory.py

Model factory for building OpenRouter models with prompt caching support.
Supports both MiniMax (auto-cached) and Anthropic (explicit cache_control) models.
"""

import os
import json
import re
from typing import Any
from dotenv import load_dotenv
from agno.models.openrouter import OpenRouter

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ── JSON Parsing Utilities for MiniMax Free-Form Output ───────────────────────

_FENCE_OPEN = re.compile(r"^```(?:json|JSON)?\s*\n", re.MULTILINE)
_FENCE_CLOSE = re.compile(r"\n```\s*$")


def extract_json(text: str) -> dict | list:
    """
    Parse JSON from MiniMax's free-form text response.
    Handles markdown fences and finds the first JSON object or array.
    """
    text = text.strip()
    text = _FENCE_OPEN.sub("", text, count=1)
    text = _FENCE_CLOSE.sub("", text)
    text = text.strip()

    # Find the first { or [
    start = min(
        (i for i, c in enumerate(text) if c in ("{", "[")),
        default=-1
    )
    if start == -1:
        raise ValueError("No JSON object or array found in response")

    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def validate_bare_list(content: dict | list, response_model: type) -> Any:
    """
    Auto-wrap bare list responses if the response model has a single list field.
    MiniMax often returns [...] instead of {"field": [...]}.
    """
    if isinstance(content, dict):
        return content

    if not isinstance(content, list):
        return content

    # Check if response model has exactly one list field
    fields = getattr(response_model, "model_fields", {})
    if len(fields) != 1:
        return content

    (name, info), = fields.items()
    # Check if the field type is a list
    if hasattr(info.annotation, "__origin__") and info.annotation.__origin__ is list:
        return {name: content}

    return content


# ── CachingOpenRouter Wrapper (Anthropic Only) ────────────────────────────────

class CachingOpenRouter(OpenRouter):
    """
    Injects cache_control: ephemeral on system messages.
    ONLY used when enable_caching=True (Anthropic primary).
    MiniMax ignores these markers and caches automatically at the provider level.
    """

    def _format_message(self, message: Any, compress_tool_results: bool = False) -> dict:
        d = super()._format_message(message, compress_tool_results=compress_tool_results)
        if d.get("role") == "system" and isinstance(d.get("content"), str):
            d["content"] = [
                {
                    "type": "text",
                    "text": d["content"],
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        return d


# ── Model Factory ─────────────────────────────────────────────────────────────

def _build_extra_body(
    primary_model: str,
    fallback_models: list[str],
    pin_anthropic: bool,
) -> dict:
    """
    Build the extra_body dict for OpenRouter API.
    Handles provider pinning and fallback model chain.
    """
    body = {}

    # Only pin Anthropic when it's the PRIMARY model
    # On MiniMax primary, pinning would fight routing
    if pin_anthropic:
        body["provider"] = {
            "order": ["Anthropic"],
            "allow_fallbacks": False,
        }

    # Cross-model fallback chain (max 3 entries per OpenRouter)
    chain = [primary_model]
    seen = {primary_model}
    for m in fallback_models:
        if m and m not in seen:
            chain.append(m)
            seen.add(m)
        if len(chain) >= 3:
            break

    if len(chain) > 1:
        body["models"] = chain

    return body


def build_model(
    *,
    model_id: str,
    enable_caching: bool = False,
    fallback_models: list[str] | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> OpenRouter:
    """
    Build an OpenRouter model with optional caching and fallback chain.

    Args:
        model_id: Primary model ID (e.g., "minimax/minimax-m2.5" or "anthropic/claude-sonnet-4.6")
        enable_caching: If True, uses CachingOpenRouter for Anthropic cache_control injection.
                      Set to False for MiniMax (auto-cached at provider level).
        fallback_models: List of fallback model IDs (max 3 total including primary)
        temperature: Model temperature
        max_tokens: Max tokens for response

    Returns:
        Configured OpenRouter model instance
    """
    if fallback_models is None:
        fallback_models = []

    # Determine if we should pin Anthropic provider
    pin_anthropic = model_id.startswith("anthropic/")

    # Select wrapper class
    model_cls = CachingOpenRouter if enable_caching else OpenRouter

    # Build extra_body for provider pinning and fallback chain
    extra_body = _build_extra_body(model_id, fallback_models, pin_anthropic)

    return model_cls(
        id=model_id,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body if extra_body else None,
    )


# ── Helper Functions ───────────────────────────────────────────────────────────

def _parse_fallback_models(env_var: str) -> list[str]:
    """Parse comma-separated fallback models from env var."""
    value = os.getenv(env_var, "").strip()
    if not value:
        return []
    return [m.strip() for m in value.split(",") if m.strip()]


def _parse_bool(env_var: str, default: bool = False) -> bool:
    """Parse boolean from env var."""
    value = os.getenv(env_var, "").strip().lower()
    if not value:
        return default
    return value in ("true", "1", "yes", "on")


def get_model_config(agent_type: str) -> dict:
    """
    Get model configuration for a specific agent type from environment.

    Args:
        agent_type: One of "parser", "triage", "reply"

    Returns:
        Dict with keys: model_id, enable_caching, fallback_models
    """
    prefix = agent_type.upper()
    model_id = os.getenv(f"{prefix}_MODEL_ID", "minimax/minimax-m2.5")
    enable_caching = _parse_bool(f"{prefix}_ENABLE_CACHING", default=False)
    fallback_models = _parse_fallback_models(f"{prefix}_FALLBACK_MODELS")

    return {
        "model_id": model_id,
        "enable_caching": enable_caching,
        "fallback_models": fallback_models,
    }
