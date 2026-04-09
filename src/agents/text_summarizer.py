"""
Shared LLM text summarizer with a strong validation loop.

Used everywhere in the pipeline where large raw text would otherwise be
fed directly into an LLM prompt. The summarizer produces a dense, lossless
compressed version of the text plus an exhaustive key_points checklist.
The validator then independently verifies every key point is present in the
summary — catching any hallucinated omissions before the summary is used.

Design:
  - SUMMARIZE: LLM reads full text → produces TextSummary (summary + key_points)
  - VALIDATE:  LLM reads key_points + summary → produces SummaryLossCheck
               If any key_points are missing → SUMMARIZE again with feedback
               Loop up to MAX_RETRIES

The validation is deliberately strict (see TEXT_SUMMARY_VALIDATOR_SYSTEM prompt):
a vague general sentence does NOT cover a specific requirement. This is by design
— a messed-up summary will corrupt every downstream step that relies on it.

Usage:
    from agents.text_summarizer import summarize_lossless

    # Only compresses if text exceeds the threshold
    compact = summarize_lossless(
        text=full_report,
        context_hint="NIST Govern function gap analysis report",
        threshold=800,   # chars — below this, returns text as-is
    )
"""

from __future__ import annotations

import logging

from llm import create_llm
from agents.policy_revision_schema import TextSummary, SummaryLossCheck
from prompts.policy_revision_prompt import (
    TEXT_SUMMARIZER_SYSTEM,
    TEXT_SUMMARY_VALIDATOR_SYSTEM,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
LLM_INVOKE_RETRIES = 3

# Default character threshold above which summarization is triggered.
# Below this, the text is returned as-is (no LLM call needed).
# gemma4:e2b has n_ctx=32 000 (≈128K chars); 4 000 chars ≈ 1K tokens — well
# within capacity, so there is no benefit to summarising shorter texts.
DEFAULT_THRESHOLD = 4_000


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _invoke_with_retries(
    structured_llm, messages: list[dict], retries: int = LLM_INVOKE_RETRIES
):
    """Invoke structured LLM with retries for transient parsing failures."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                logger.warning(
                    "    [Summarizer] LLM invoke attempt %d/%d failed: %s — retrying",
                    attempt,
                    retries,
                    exc,
                )
            else:
                logger.error(
                    "    [Summarizer] LLM invoke failed after %d attempts: %s",
                    retries,
                    exc,
                )
    raise last_exc


def _run_summarize(
    text: str,
    context_hint: str,
    missing_points: list[str] | None = None,
) -> TextSummary:
    """
    Single summarization pass.

    Args:
        text: The full source text to compress.
        context_hint: One-line description of what this text is.
        missing_points: Key points missing in a prior attempt (max 15 passed back).

    Returns:
        TextSummary with summary, key_points (≤15), and source_char_count.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(TextSummary)

    prompt = (
        f"Source text type: {context_hint}\n\n"
        f"Source text ({len(text)} chars):\n\n"
        f"{text}"
    )

    if missing_points:
        # Cap feedback to 15 items to avoid ballooning the retry prompt.
        # If >15 were missing, the summarizer was catastrophically wrong —
        # sending all of them back just causes the same JSON truncation error.
        # Send the top 15 most specific ones (they are already ranked by importance
        # since the validator lists failures in order).
        capped = missing_points[:15]
        missing_text = "\n".join(f"  - {p}" for p in capped)
        prompt += (
            f"\n\n### IMPORTANT — Previous summary missed these topics. "
            f"You MUST cover all of them (grouped where related):\n\n{missing_text}"
        )

    logger.info(
        "  [Summarizer] Compressing %d chars (%s)",
        len(text),
        context_hint,
    )

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": TEXT_SUMMARIZER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    # Hard guard: truncate runaway summaries before they corrupt downstream JSON.
    # This should not normally fire given the 2000-char instruction in the prompt,
    # but is a safety net for models that ignore length instructions.
    if len(result.summary) > 2200:
        logger.warning(
            "  [Summarizer] Summary exceeded 2200 chars (%d) — truncating at sentence boundary",
            len(result.summary),
        )
        # Truncate at the last sentence boundary before 2000 chars
        truncated = result.summary[:2000]
        last_period = truncated.rfind(".")
        if last_period > 1500:
            truncated = truncated[: last_period + 1]
        result = TextSummary(
            summary=truncated,
            key_points=result.key_points[:15],
            source_char_count=result.source_char_count,
        )

    # Hard guard: cap key_points at 15.
    if len(result.key_points) > 15:
        logger.warning(
            "  [Summarizer] key_points exceeded 15 (%d) — capping",
            len(result.key_points),
        )
        result = TextSummary(
            summary=result.summary,
            key_points=result.key_points[:15],
            source_char_count=result.source_char_count,
        )

    logger.info(
        "  [Summarizer] Produced summary: %d chars, %d key points",
        len(result.summary),
        len(result.key_points),
    )
    return result


def _run_validate(summary: TextSummary) -> SummaryLossCheck:
    """
    Validate that the summary covers every key point.

    The validator receives only the key_points list + the summary — it does NOT
    re-read the full original text. This keeps the validation prompt small and
    forces the model to reason about concrete checklist items rather than
    doing a vague "does this look complete?" judgment.

    Args:
        summary: The TextSummary to validate.

    Returns:
        SummaryLossCheck with is_lossless and missing_points.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(SummaryLossCheck)

    key_points_text = "\n".join(
        f"  {i + 1}. {p}" for i, p in enumerate(summary.key_points)
    )

    prompt = (
        f"Key points that MUST appear in the summary ({len(summary.key_points)} total):\n\n"
        f"{key_points_text}\n\n"
        f"---\n\n"
        f"Summary to validate:\n\n"
        f"{summary.summary}\n\n"
        f"---\n\n"
        f"Check every key point. List any that are absent or materially distorted."
    )

    logger.info(
        "  [Summarizer Validator] Checking %d key points against summary",
        len(summary.key_points),
    )

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": TEXT_SUMMARY_VALIDATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    if result.is_lossless:
        logger.info("  [Summarizer Validator] LOSSLESS ✓")
    else:
        logger.warning(
            "  [Summarizer Validator] LOSSY — %d key points missing:",
            len(result.missing_points),
        )
        for mp in result.missing_points:
            logger.warning("    - %s", mp)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def summarize_lossless(
    text: str,
    context_hint: str,
    threshold: int = DEFAULT_THRESHOLD,
) -> str:
    """
    Compress text using a validated summarization loop.

    If the text is shorter than `threshold` characters, it is returned as-is
    with no LLM call — there is no benefit to summarizing short text and it
    only adds latency.

    The summarizer loop:
      1. Generate TextSummary (summary + key_points)
      2. Validate: does every key_point appear in summary?
      3. If missing points found → regenerate with missing_points as feedback
      4. Repeat up to MAX_RETRIES
      5. If still lossy after MAX_RETRIES → return original text (never corrupt)

    Args:
        text: The full source text to compress.
        context_hint: One-line description of the text's purpose, e.g.
                      "NIST Govern gap analysis report" or
                      "policy section blocks for integration".
                      Used in the summarizer prompt so the model knows what to preserve.
        threshold: Minimum char count to trigger summarization (default 800).
                   Texts shorter than this are returned as-is.

    Returns:
        The validated summary string, or the original text if summarization
        was not needed or failed to produce a lossless result.
    """
    if len(text) <= threshold:
        logger.debug(
            "  [Summarizer] Text (%d chars) below threshold (%d) — skipping",
            len(text),
            threshold,
        )
        return text

    logger.info(
        "  [Summarizer] Text (%d chars) exceeds threshold (%d) — summarizing",
        len(text),
        threshold,
    )

    missing_points: list[str] | None = None
    last_summary: TextSummary | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            summary = _run_summarize(text, context_hint, missing_points)
        except Exception as exc:
            logger.warning(
                "  [Summarizer] Summarization failed on attempt %d/%d: %s — "
                "returning original text",
                attempt,
                MAX_RETRIES,
                exc,
            )
            return text

        try:
            check = _run_validate(summary)
        except Exception as exc:
            logger.warning(
                "  [Summarizer] Validation failed on attempt %d/%d: %s — "
                "accepting summary as-is",
                attempt,
                MAX_RETRIES,
                exc,
            )
            return summary.summary

        if check.is_lossless:
            logger.info(
                "  [Summarizer] Lossless summary accepted on attempt %d ✓ "
                "(%d → %d chars, %.0f%% reduction)",
                attempt,
                len(text),
                len(summary.summary),
                (1 - len(summary.summary) / len(text)) * 100,
            )
            return summary.summary

        # Prepare for retry with the missing points as feedback
        missing_points = check.missing_points
        last_summary = summary
        logger.warning(
            "  [Summarizer] Attempt %d/%d lossy — retrying with %d missing points",
            attempt,
            MAX_RETRIES,
            len(missing_points),
        )

    # Max retries exhausted — safety fallback: return original text
    # A lossy summary would corrupt all downstream steps that rely on it.
    # Returning raw text is always safer than returning a bad summary.
    logger.warning(
        "  [Summarizer] Max retries (%d) reached — summary still lossy. "
        "Returning original text to prevent data loss downstream.",
        MAX_RETRIES,
    )
    return text


def summarize_blocks(
    blocks_text: str,
    block_ids: list[str],
    context_hint: str,
    threshold: int = DEFAULT_THRESHOLD,
) -> str:
    """
    Summarize a concatenated blocks string, but guarantee that every block ID
    appears in the summary.

    This is a specialised wrapper for the Integration Editor's blocks_text.
    After summarization, a code check verifies all block IDs are present —
    if any are missing, the original blocks_text is returned for that block.

    Args:
        blocks_text: Full concatenated block content.
        block_ids: List of subcategory IDs that MUST appear in the summary.
        context_hint: Description for the summarizer prompt.
        threshold: Character threshold (default 800).

    Returns:
        Validated summary string, or original if summarization fails or is lossy.
    """
    result = summarize_lossless(blocks_text, context_hint, threshold)

    # Code check: every block ID must survive summarization
    missing_ids = [bid for bid in block_ids if bid not in result]
    if missing_ids:
        logger.warning(
            "  [Summarizer] Block IDs missing from summary after validation: %s "
            "— returning original blocks text",
            ", ".join(missing_ids),
        )
        return blocks_text

    return result
