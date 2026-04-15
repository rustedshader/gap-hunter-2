"""
Centralized LLM factory — creates ChatLlamaCpp instances for all agents.

Replaces ChatOllama throughout the codebase. Ollama's structured output
breaks above ~19K prompt chars; llama.cpp handles arbitrary sizes correctly.

Model: gemma-4-E2B-it-Q8_0 (gemma4:e2b)
  - 2.3B effective parameters (5.1B with per-layer embeddings)
  - 128K token context window with 512-token sliding window attention
  - n_ctx=65536 used here: covers all realistic policy documents while
    keeping KV-cache RAM consumption manageable on local hardware
  - Thinking mode (<|think|>) is NOT enabled: it prepends a reasoning
    channel block that breaks with_structured_output() JSON parsing
"""

from __future__ import annotations

import multiprocessing
import os
import logging

from langchain_community.chat_models import ChatLlamaCpp

logger = logging.getLogger(__name__)

# Suppress noisy llama.cpp stderr logs
os.environ.setdefault("LLAMA_CPP_LOG_LEVEL", "0")

# Default GGUF model path — override via GGUF_MODEL_PATH env var or create_llm(model_path=...)
_DEFAULT_MODEL_PATH = (
    "/Users/shubhang/.cache/huggingface/hub/"
    "models--unsloth--gemma-4-E2B-it-GGUF/snapshots/"
    "e18a8a48038a5da3e89c1152441ab57546a70873/"
    "gemma-4-E2B-it-Q8_0.gguf"
)

# Singleton to avoid reloading the model for every call
_llm_cache: dict[str, ChatLlamaCpp] = {}


def create_llm(
    model_path: str | None = None,
    n_ctx: int = 65536,
    max_tokens: int = 2048,
    temperature: float = 0,
) -> ChatLlamaCpp:
    """
    Create (or return cached) ChatLlamaCpp instance.

    Args:
        model_path: Path to GGUF weights. Defaults to _DEFAULT_MODEL_PATH
                    or GGUF_MODEL_PATH env var.
        n_ctx: Context window size. Default 65536 (64K tokens) — uses half
               of gemma4:e2b's 128K capacity; comfortably fits any policy
               document while keeping KV-cache RAM manageable.
        max_tokens: Max tokens to generate.
        temperature: Sampling temperature.

    Returns:
        ChatLlamaCpp instance ready for .invoke() or .with_structured_output().
    """
    path = model_path or os.environ.get("GGUF_MODEL_PATH", _DEFAULT_MODEL_PATH)
    cache_key = f"{path}:{n_ctx}:{max_tokens}:{temperature}"

    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    logger.info("Loading LLM from %s (n_ctx=%d)", path, n_ctx)

    llm = ChatLlamaCpp(
        model_path=path,
        n_ctx=n_ctx,
        n_gpu_layers=8,
        # n_batch=512 aligns with gemma4:e2b's 512-token sliding window;
        # faster prompt prefill vs the old n_batch=300.
        n_batch=512,
        max_tokens=max_tokens,
        n_threads=multiprocessing.cpu_count() - 1,
        temperature=temperature,
        # repeat_penalty=1.1: the old 1.5 was too aggressive and caused the
        # model to avoid repeating JSON keys and common policy-domain terms,
        # degrading structured output quality.
        repeat_penalty=1.1,
        top_p=0.5,
        verbose=False,
    )

    _llm_cache[cache_key] = llm
    return llm
