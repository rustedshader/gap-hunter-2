"""Centralized LLM factory for local llama.cpp or remote Ollama."""

from __future__ import annotations

import multiprocessing
import os
import logging
from pathlib import Path
from typing import Any

from langchain_community.chat_models import ChatLlamaCpp

try:
    from langchain_ollama import ChatOllama
except Exception:  # pragma: no cover - optional dependency at runtime
    ChatOllama = None

logger = logging.getLogger(__name__)

# Suppress noisy llama.cpp stderr logs
os.environ.setdefault("LLAMA_CPP_LOG_LEVEL", "0")

# Default GGUF model path — set GGUF_MODEL_PATH or pass model_path.
_DEFAULT_MODEL_PATH: str | None = None

# Singleton to avoid reloading the model for every call
_llm_cache: dict[str, Any] = {}


def _resolve_provider(provider: str | None, ollama_url: str | None) -> str:
    explicit = (provider or os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if explicit:
        return explicit
    if ollama_url or os.environ.get("OLLAMA_URL") or os.environ.get("OLLAMA_HOST"):
        return "ollama"
    return "llamacpp"


def create_llm(
    model_path: str | None = None,
    n_ctx: int = 32000,
    max_tokens: int = 2048,
    temperature: float = 0,
    model_name: str | None = None,
    provider: str | None = None,
    ollama_url: str | None = None,
) -> Any:
    """
    Create (or return cached) LLM instance.

    Provider resolution:
      - If provider is "ollama" (or OLLAMA_URL/OLLAMA_HOST is set), use ChatOllama
      - Otherwise, use ChatLlamaCpp with a local GGUF path

    Args:
        model_path: Path to GGUF weights (llama.cpp only).
        n_ctx: Context window size.
        max_tokens: Max tokens to generate.
        temperature: Sampling temperature.
        model_name: Model name (Ollama) or display name.
        provider: "ollama" or "llamacpp" (optional).
        ollama_url: Base URL for Ollama (optional).

    Returns:
        LLM instance ready for .invoke() or .with_structured_output().
    """
    resolved_provider = _resolve_provider(provider, ollama_url)
    resolved_model = (
        model_name
        or os.environ.get("LLM_MODEL")
        or os.environ.get("OLLAMA_MODEL")
        or "gemma4:e2b"
    )

    if resolved_provider == "ollama":
        if ChatOllama is None:
            raise RuntimeError("langchain-ollama is required for Ollama support")

        base_url = (
            ollama_url
            or os.environ.get("OLLAMA_URL")
            or os.environ.get("OLLAMA_HOST")
        )
        if not base_url:
            raise ValueError("OLLAMA_URL is required when using provider=ollama")

        cache_key = f"ollama:{base_url}:{resolved_model}:{n_ctx}:{max_tokens}:{temperature}"
        if cache_key in _llm_cache:
            return _llm_cache[cache_key]

        logger.info("Using Ollama at %s (model=%s)", base_url, resolved_model)
        llm = ChatOllama(
            model=resolved_model,
            base_url=base_url,
            temperature=temperature,
            num_ctx=n_ctx,
            num_predict=max_tokens,
        )
        _llm_cache[cache_key] = llm
        return llm

    # Default: llama.cpp
    path = model_path or os.environ.get("GGUF_MODEL_PATH") or _DEFAULT_MODEL_PATH
    if not path:
        raise ValueError(
            "GGUF_MODEL_PATH is required when using provider=llamacpp"
        )

    model_file = Path(path)
    if not model_file.exists():
        raise FileNotFoundError(f"GGUF model not found: {model_file}")

    cache_key = f"llamacpp:{model_file}:{n_ctx}:{max_tokens}:{temperature}"
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    logger.info("Loading llama.cpp model from %s (n_ctx=%d)", model_file, n_ctx)

    llm = ChatLlamaCpp(
        model_path=str(model_file),
        n_ctx=n_ctx,
        n_gpu_layers=8,
        n_batch=300,
        max_tokens=max_tokens,
        n_threads=max(1, multiprocessing.cpu_count() - 1),
        temperature=temperature,
        repeat_penalty=1.5,
        top_p=0.5,
        verbose=False,
    )

    _llm_cache[cache_key] = llm
    return llm
