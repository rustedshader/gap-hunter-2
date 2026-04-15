# Gap Hunter Technical Working In Detail

This document explains the technical working of Gap Hunter in depth, based on the current repository implementation. It is intended for technical review, hackathon jury preparation, and onboarding new contributors who need to understand the pipeline end to end.

The system is best understood as a **three-phase document intelligence pipeline**:

1. **Phase 1: Extraction**
   Convert a policy PDF into structured sections.
2. **Phase 2: Gap Analysis**
   Evaluate those sections against the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024), organized through NIST CSF functions and subcategories.
3. **Phase 3: Policy Revision and Roadmap**
   Generate a revised policy and a prioritized remediation roadmap from the structured findings.

The important architectural point is that this is **not** a single prompt over a PDF. It is an orchestrated pipeline with validation loops, structured schemas, deterministic guardrails, and intermediate artifacts persisted to disk.

## 1. System Goals

The project is built to solve a specific workflow problem:

- organizations already have policy documents
- those documents are often incomplete, inconsistent, or poorly structured
- manually comparing them against a framework template is slow
- manually rewriting them into a better policy format is slower

Gap Hunter therefore focuses on four core outcomes:

- extract a messy source policy into structured sections
- evaluate those sections against framework requirements
- explain the gaps with evidence and recommendations
- produce a revised, review-ready policy draft and roadmap

## 2. High-Level Architecture

At a high level, the pipeline looks like this:

```text
PDF Policy
  ↓
PDF-to-Markdown Conversion
  ↓
Heading Detection / LLM-Assisted Section Extraction
  ↓
sections_output.json
  ↓
Section Summarization
  ↓
master_list.json
  ↓
Policy Scope Classification
  ↓
Per-Function Gap Analysis
  ↓
assessments.json + markdown reports
  ↓
Gap Targeting and Revision Planning
  ↓
Revised Policy + Revision Report + Improvement Roadmap
```

There are three especially important design principles in this architecture:

- **Use deterministic logic wherever possible.**
- **Use LLMs only for semantic judgment tasks.**
- **Persist intermediate outputs so later phases are traceable and reusable.**

## 3. Entry Point And Runtime Flow

The main entry point is [`src/main.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/main.py).

It exposes a CLI that supports:

- full end-to-end execution
- extraction-only runs
- skip-extraction runs using a previous run directory
- revision-only runs on previously generated analysis artifacts

The CLI flow is:

1. Parse arguments.
2. Create or reuse a timestamped run directory.
3. Enable debug logging into `debug.log`.
4. Run extraction unless skipped.
5. Run gap analysis unless extraction-only.
6. Run revision unless explicitly skipped.

The run directory is a core operational concept. It stores the outputs from every phase so the system can resume or re-run downstream stages without recomputing everything.

## 4. Model And Inference Layer

The central LLM factory lives in [`src/llm.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/llm.py).

### 4.1 Why This Layer Exists

The project uses a centralized model creation function so that:

- all agents use a consistent model configuration
- model loading is cached
- structured output behavior is standardized
- performance and context window settings can be tuned in one place

### 4.2 Current Model Strategy

The current implementation uses `ChatLlamaCpp` rather than relying entirely on `ChatOllama`. The reasoning in the code is practical:

- structured output reliability was better with `llama.cpp`
- larger prompt handling became more stable
- local execution supports privacy and offline operation

The default model path points to a local GGUF version of Gemma 4 E2B. The code uses:

- large context window
- low temperature
- caching of model instances
- offline Hugging Face flags

This is important because the pipeline repeatedly depends on structured JSON-like outputs. If the model frequently breaks schema adherence, every downstream phase becomes unstable.

### 4.3 Offline Mode

Both [`src/main.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/main.py) and [`src/tools/pdf.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/tools/pdf.py) explicitly set:

- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`

This prevents unnecessary network lookups for already cached artifacts and makes the prototype more robust in offline environments.

## 5. Core Data Models

The system relies heavily on Pydantic schemas to keep agent outputs structured.

### 5.1 Extraction Models

Defined in [`src/models.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/models.py):

- `ExtractedSection`
- `IncompleteSection`
- `ChunkResult`
- `SectionSummary`

These models represent:

- section metadata
- section content
- carry-over state across overlapping windows
- summarization outputs for the master list

### 5.2 Agent Schemas For Extraction

Defined in [`src/agents/schemas.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/schemas.py):

- `SectionExtraction`
- `ExtractionResult`
- `ValidationResult`
- `SummarizationResult`

These are intentionally simpler than the main pipeline models. The extractor and corrector agents are only responsible for section boundaries, not for full final section objects.

### 5.3 Gap Analysis Schema

Defined in [`src/agents/nist_gap_agents.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/nist_gap_agents.py):

- `SubcategoryAssessment`

This is one of the most important schemas in the project. Every subcategory assessment contains:

- `subcategory_id`
- `title`
- `status`
- `evidence`
- `gap`
- `recommendation`

This schema is the structured backbone of the entire Phase 2 and Phase 3 workflow.

### 5.4 Revision Schemas

Defined in [`src/agents/policy_revision_schema.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/policy_revision_schema.py):

- `SectionRevision`
- `RevisionValidationResult`
- `AdditionBlock`
- `VerificationQuestion`
- `ClusterSummary`
- `IntegrationResult`
- `TextSummary`
- `SummaryLossCheck`

These schemas support the revision architecture, especially the RAPTOR + CoVe design used in Phase 3.

## 6. Phase 1: PDF Extraction And Section Structuring

Phase 1 is implemented mainly in [`src/extractor.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/extractor.py), with support from:

- [`src/tools/pdf.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/tools/pdf.py)
- [`src/heading_detector.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/heading_detector.py)
- [`src/agents/extractor_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/extractor_agent.py)
- [`src/agents/validator_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/validator_agent.py)
- [`src/agents/corrector_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/corrector_agent.py)
- [`src/agents/summarizer_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/summarizer_agent.py)

### 6.1 PDF To Markdown Conversion

The first step uses `docling` through [`src/tools/pdf.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/tools/pdf.py).

The process is:

1. Validate that the input file is a PDF.
2. Convert the PDF into a `DocumentConverter` object.
3. Export the parsed document to markdown.
4. Detect and decode `/MT` font encodings when they appear.

The `/MT` decoding logic is useful for malformed or custom-font PDFs where text may otherwise be unreadable. It also cleans up excessive spacing and tries to reconstruct words.

### 6.2 Document Preparation

`prepare_document()` converts the markdown text into a list of:

```text
(line_number, text)
```

This line-numbered representation is important because:

- the extractor works on line-based windows
- section boundaries are expressed in line numbers
- content extraction from the original text becomes deterministic

### 6.3 Rule-Based Heading Detection First

Before invoking any LLM, the system tries a rule-based fast path using [`src/heading_detector.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/heading_detector.py).

It checks several heading patterns:

- markdown headings
- numbered headings
- ALL CAPS headings
- bold headings
- bullet-heavy documents as a special case

This detector returns the first reliable pattern that yields a plausible number of sections. If it succeeds, the system can skip the LLM extraction pipeline entirely.

This is a strong architectural choice because many documents are structured enough to parse with pattern matching, and using an LLM in those cases would add latency and error surface for no benefit.

### 6.4 Rule-Based Section Construction

If headings are detected, `detect_rule_based_sections()`:

1. sorts headings by line number
2. uses the next heading to define each section’s end line
3. extracts content directly from source lines
4. builds `ExtractedSection` objects

This direct extraction is important. The LLM is not asked to reproduce the content; only the boundaries matter.

### 6.5 LLM Fallback Pipeline

If rule-based heading detection is insufficient, the system falls back to the multi-agent sliding-window extractor.

This uses:

- `build_windows()`
- `extract_sections_from_chunk()`

The document is processed in overlapping windows, controlled by:

- `window_size`
- `overlap`

This handles long documents and chunk boundary issues.

### 6.6 Three-Agent Extraction Loop

The extraction loop uses three roles:

1. **Extractor**
2. **Validator**
3. **Corrector**

#### Extractor

Implemented in [`src/agents/extractor_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/extractor_agent.py).

Its job is to identify section boundaries only. It does not own final content extraction. The prompt tells it:

- where the chunk begins and ends
- what numbering to continue from
- to ignore bullets and numbered paragraphs that are content, not headings
- how to handle carry-over sections from a previous chunk

#### Validator

Implemented in [`src/agents/validator_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/validator_agent.py).

Its job is to inspect the proposed boundaries and determine:

- whether the extraction is complete
- whether sections are missing
- whether boundaries are wrong
- whether titles are incorrect

It explicitly does **not** validate content text, only boundaries.

#### Corrector

Implemented in [`src/agents/corrector_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/corrector_agent.py).

If the validator rejects the extraction, the corrector receives:

- the original chunk
- the current extraction summary
- the list of issues
- missing sections if any

It then regenerates corrected section boundaries.

### 6.7 Guardrails In Extraction

The extraction phase has several practical guardrails:

- hard cap on max sections per window
- validation rounds limited by `MAX_CORRECTION_ROUNDS`
- line number clamping to valid document bounds
- invalid boundary skipping
- carry-over handling for sections that span windows
- direct content extraction from source lines after boundaries are set

These guardrails matter because they reduce a common failure mode: asking the model to both interpret and reproduce too much document structure in one step.

### 6.8 Carry-Over Sections

If a section runs until the end of a chunk, the system marks it incomplete and stores:

- section number
- title
- partial content
- original start line

That state is passed into the next chunk so the extractor can determine where the section ends.

### 6.9 Deduplication And Cleanup

After all windows are processed, the system performs three post-processing passes:

1. `_dedup_sections()`
   Uses `start_line` as a key and keeps the wider section range.
2. `_remove_overlapping_sections()`
   Removes nested or overlapping sections, favoring the earlier parent section.
3. `_renumber_sections()`
   Renumbers sections sequentially to remove LLM numbering inconsistencies.

This cleanup is essential because overlapping windows intentionally create duplicates, and raw LLM numbering cannot be trusted as final canonical numbering.

### 6.10 Serialization

The extracted sections are saved to `sections_output.json`.

This file is one of the most important artifacts in the repo because later phases can use:

- section numbers
- section titles
- section content
- line ranges

without re-parsing the PDF.

## 7. Phase 1.5: Master List Generation

After extraction, the system builds a summarized master list using `generate_master_list()` in [`src/extractor.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/extractor.py).

For each section:

1. run the summarizer agent
2. capture a concise summary or null
3. store the result alongside metadata

The summarizer agent in [`src/agents/summarizer_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/summarizer_agent.py) asks for:

- a short summary of purpose
- key requirements or obligations
- critical compliance points

If a section is effectively only a title or non-substantive content, it can return null.

The output is written to `master_list.json`.

This artifact gives later phases a compact section inventory and is also useful for debugging and review.

## 8. Phase 2: Gap Analysis Architecture

Phase 2 is implemented primarily in:

- [`src/gap_analyzer.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/gap_analyzer.py)
- [`src/agents/nist_gap_agents.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/nist_gap_agents.py)
- [`src/agents/gap_analysis_tools.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/gap_analysis_tools.py)
- [`src/agents/function_summarizer_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/function_summarizer_agent.py)

### 8.1 Framework Basis

The analysis is anchored on:

- NIST CSF functions
- subcategory metadata stored in `src/nist/nist_config.yaml`
- supporting reference policy templates under `src/nist/framework-documents/`

This allows the system to reason not only from a general framework label but from:

- concrete subcategory descriptions
- implementation guidance
- key questions
- associated policy templates

### 8.2 NIST Function Set

The system works across the six NIST CSF functions:

- Govern
- Identify
- Protect
- Detect
- Respond
- Recover

These are defined in [`src/gap_analyzer.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/gap_analyzer.py).

### 8.3 Building Policy Content

`create_combined_policy_content()` builds a rich policy representation for analysis.

It prefers full section text from `sections_output.json`. If full content is unavailable, it falls back to section summaries from `master_list.json`.

This is important because:

- full policy language gives better evidence grounding
- fallback to summaries makes the pipeline more fault-tolerant

Very large sections are truncated using a content character limit to avoid context overload.

### 8.4 Policy-Level Function Classification

Before running detailed analysis, `classify_policy_functions()` determines which NIST functions are relevant to the policy.

This is a very important noise-reduction step.

Example:

- a risk management policy should not be deeply analyzed for every Protect, Detect, or Recover requirement
- an incident response policy should not be treated like a full enterprise information security policy

If a function is irrelevant, the system marks its subcategories as `Out of Scope` and avoids unnecessary LLM calls.

### 8.5 Function-Level Subcategory Scope Classification

Within a function, `_classify_scope()` decides which subcategories are in scope for the current policy.

This is another important precision layer. Without it, every missing subcategory could look like a deficiency even when it belongs in a different dedicated policy document.

### 8.6 Current Assessment Strategy

The current active `run_nist_gap_agent()` in [`src/agents/nist_gap_agents.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/nist_gap_agents.py) uses a **single-call-per-subcategory** strategy:

1. classify in-scope subcategories (one LLM call per function)
2. for each in-scope subcategory, send the **full policy content** plus subcategory-specific context in one call
3. generate one structured `SubcategoryAssessment`
4. mark out-of-scope subcategories deterministically in code (no LLM call)

The codebase does contain residual helper code for an older map-reduce evidence architecture (`_map_one_section`, `_map_sections_for_subcategory`, `_reduce_to_assessment`), but these are no longer called from the main path. The map-reduce approach was empirically tested and found to produce three times more hallucinations and 2.3 times more latency compared to full-policy single-call assessment. With a 65 536-token context window, the full policy fits comfortably in each call.

That is a useful technical talking point: the team actively changed architecture based on measured empirical behavior, not just on abstract preference.

### 8.7 Subcategory Prompt Composition

For each in-scope subcategory, the assessment prompt includes:

- full customer policy content
- subcategory ID
- category
- description
- implementation guidance
- key questions
- required policy templates
- a short framework excerpt from the associated template documents

This gives the model:

- the source material to judge
- the target requirement to compare against
- a reference for what compliant policy language should resemble

### 8.8 Assessment Status Semantics

Each subcategory receives one of:

- `Addressed`
- `Partially Addressed`
- `Not Addressed`
- `Out of Scope`

This distinction is very important. Real policy documents often have weak or partial coverage, and collapsing that into a simple yes/no would lose too much information.

### 8.9 Out-Of-Scope Handling

Out-of-scope subcategories are generated in code, not by the model.

For these, the system writes:

- a scope explanation
- a gap that points toward a dedicated policy template
- a recommendation listing the required policy templates

This is a strong design decision because it avoids generating false remediation work for the wrong document.

## 9. Function Reports And Consolidation

### 9.1 Per-Function Reports

`_assemble_function_report()` creates markdown reports for each NIST function.

Each report includes:

- total subcategories
- in-scope and out-of-scope counts
- counts by status
- overall maturity
- detailed assessment entries
- out-of-scope summary table
- top-priority gaps

These reports are persisted as:

- `govern_gap_analysis.md`
- `identify_gap_analysis.md`
- `protect_gap_analysis.md`
- `detect_gap_analysis.md`
- `respond_gap_analysis.md`
- `recover_gap_analysis.md`

### 9.2 Function Summaries

The current active path uses the deterministic `build_code_summary()` function exclusively. It computes directly from structured assessment data:

- counts (total, in-scope, addressed, partial, not-addressed, out-of-scope)
- maturity rating
- critical gaps (from Not Addressed items)
- key recommendations
- required policy documents

This replaced an older LLM-based function summarizer that was found to hallucinate maturity ratings even when given the exact numbers in the prompt. The code-based path is faster, deterministic, and provably accurate since it reads from the structured `SubcategoryAssessment` objects directly. The LLM-based summarizer code still exists in `src/agents/function_summarizer_agent.py` but is no longer called by the active pipeline.

### 9.3 Consolidated Report

`build_consolidated_report()` aggregates all assessments across all functions into one code-generated report.

It computes:

- overall maturity
- global counts
- per-function maturity table
- not-addressed gaps
- partially addressed gaps
- missing policy documents

The key point is that this report is assembled **without another LLM call**. Once structured assessments exist, the system prefers deterministic aggregation.

### 9.4 Summary JSON

`save_gap_analysis_summary()` writes a lightweight JSON summary containing:

- timestamp
- analyzed functions
- report previews
- consolidation flag

This is mainly an operational artifact, useful for quick inspection or orchestration.

## 10. Phase 3: Policy Revision Architecture

Phase 3 is implemented primarily in:

- [`src/policy_reviser.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/policy_reviser.py)
- [`src/agents/policy_revision_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/policy_revision_agent.py)
- [`src/agents/policy_revision_schema.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/policy_revision_schema.py)
- [`src/agents/text_summarizer.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/text_summarizer.py)
- [`src/agents/roadmap_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/roadmap_agent.py)

The revision architecture is described in code as **RAPTOR + CoVe**.

### 10.1 Why Revision Is Separate From Gap Analysis

Gap analysis and revision are different tasks.

Gap analysis asks:

- what is present
- what is missing
- what should change

Revision asks:

- where should each gap be fixed
- should it modify an existing section or create a new one
- how can the changes be integrated without rewriting the whole policy badly

Separating these phases makes the overall system more modular and explainable.

### 10.2 Inputs Into Revision

Revision uses:

- `sections_output.json` — original policy sections for structure and style reference
- `assessments.json` — structured gap findings from Phase 2

Per-function summaries are computed on the fly from `assessments.json` using `build_code_summary()` rather than loaded from disk. This means Phase 3 is self-contained: it only requires the two JSON artifacts above and does not depend on any intermediate markdown files from Phase 2.

### 10.3 Gap Targeting

The revision phase first determines where each actionable gap belongs.

This happens in `parse_gap_targets()` and `classify_gap_target()`.

For each actionable subcategory:

- determine whether it belongs in an existing section or a new section
- if modifying, identify the target section number
- load relevant framework excerpt and NIST guidance

This decision is done by an LLM with structured output rather than regex heuristics.

### 10.4 Domain Filtering Before Revision

One of the more sophisticated parts of the revision flow is domain filtering.

The system tries to detect what kind of policy the uploaded document actually is by matching:

- section titles
- early section content
- keyword-to-template mappings

Using this, it builds a revision allowlist so the policy is not polluted with unrelated subcategories from other policy domains.

There are also explicit exclusions for known false-positive mappings, especially around access control and indirectly related inventory or supply chain items.

This is a very important design choice. It prevents the revision engine from turning one policy into an unrealistic mega-policy.

### 10.5 RAPTOR Concept In This Codebase

In this project, RAPTOR is used as a compact context-passing strategy.

The idea is:

- generate additions per gap
- summarize groups of additions per NIST function
- pass those compact summaries to later writers

This helps later generation steps know what content was already introduced without feeding the full accumulated text back every time.

### 10.6 CoVe Concept In This Codebase

CoVe is used as a verification loop.

For each generated addition block:

1. generate verification questions from the gap
2. independently test whether the block answers those questions
3. if some fail, regenerate with feedback

This reduces the chance that the model produces persuasive but incomplete additions.

### 10.7 Addition Blocks

The first active content generation step is `run_write_addition()`.

It generates an `AdditionBlock` for exactly one gap. The model receives:

- original section content as a style reference
- prior additions summary
- subcategory ID
- missing requirement description
- recommendation
- NIST guidance
- framework excerpt

The output is only the **new content block**, not a rewritten full section.

This is a very good architectural choice because it localizes generation and makes validation easier.

### 10.8 Style Preservation

The original section is not passed as raw full text indefinitely. It is compressed into a style sample using `summarize_lossless()` where needed.

This keeps the prompt manageable while still giving the model:

- tone reference
- formatting cues
- scope context

### 10.9 Cluster Summaries And Prior Context

After a function’s blocks are generated, they are summarized into a `ClusterSummary`.

This summary captures:

- function name
- covered subcategory IDs
- key topics already introduced

Later addition writers use this compact summary to avoid repetition.

### 10.10 Integration Phase

Once all addition blocks for a section are ready, the system performs integration.

The integration step merges:

- original section content
- all validated addition blocks

into a single coherent section.

The corresponding schema is `IntegrationResult`, which includes:

- integrated content
- covered subcategory IDs
- a section-level changes summary

### 10.11 New Section Creation

If no existing section is an appropriate target, the system can create a brand-new section using `SectionRevision`.

This keeps the revision engine flexible enough to handle real missing structural areas rather than forcing everything into the wrong section.

### 10.12 Final Revision Outputs

The revision phase writes:

- `revised_policy.md`
- `revision_report.md`
- `improvement_roadmap.md`

The revised policy is the main transformed document.
The revision report explains what changed.
The roadmap translates gaps into prioritized remediation work.

## 11. Shared Text Summarization Utility

One of the most important support components is [`src/agents/text_summarizer.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/text_summarizer.py).

This utility is used whenever raw text may be too large or too noisy for downstream prompts.

### 11.1 Why This Utility Exists

Naive summarization is dangerous in this kind of system because if a key requirement disappears in a summary, every later reasoning step built on that summary may be wrong.

To address that, the code uses a **lossless summarization loop**:

1. summarize into `TextSummary`
2. generate a checklist of key points
3. validate whether every key point is represented
4. if not, retry with missing-point feedback
5. if still lossy after retries, fall back to the original text

This is a very strong design choice because it treats summarization as an integrity-sensitive step rather than a convenience feature.

### 11.2 Where It Is Used

This summarizer is used in several places, including:

- policy scope classification when text is very large
- function summary generation
- recommendation compression for revision prompts
- roadmap planning and detailing

## 12. Roadmap Generation

The roadmap system is implemented in [`src/agents/roadmap_agent.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/roadmap_agent.py).

Its workflow is a smaller multi-agent pipeline:

1. **Planner**
   Organize gaps into tiers.
2. **Detailer**
   Enrich action items.
3. **Validator**
   Check that coverage and specificity are acceptable.

### 12.1 Inputs

The roadmap logic uses:

- all actionable subcategory assessments
- function summaries
- missing policy documents

### 12.2 Roadmap Goals

It aims to produce action items with:

- priority tier
- title
- NIST IDs
- responsible party
- effort estimate
- dependencies
- success criteria

This is useful because the system’s purpose is not only to say “the policy is weak,” but also to help operationalize remediation.

## 13. Framework Data Access Layer

Framework lookup is centralized in [`src/agents/gap_analysis_tools.py`](/Users/shubhang/dev/hackathon/gap-hunter-2/src/agents/gap_analysis_tools.py).

This layer provides:

- framework document reading
- function info extraction
- subcategory extraction
- function context generation
- policy template allowlist building
- reference excerpt loading

This is important because it separates:

- source-of-truth framework data
- LLM orchestration logic

The biggest benefit is maintainability. If framework metadata changes, the system can update configuration and templates without rewriting the entire reasoning flow.

## 14. Output Artifacts And Their Purpose

The system persists many outputs. Each one serves a different operational need.

### 14.1 Extraction Outputs

- `sections_output.json`
  Canonical structured extraction of policy sections.
- `master_list.json`
  Compact summarized section inventory.

### 14.2 Analysis Outputs

- `<function>_gap_analysis.md`
  Detailed function-level findings for each of the six NIST CSF functions.
- `combined_gap_analysis.md`
  All six function reports concatenated into one markdown file.
- `consolidated_gap_analysis.md`
  Code-built aggregate report: overall maturity, per-function maturity table, gap tables, missing policy documents.
- `assessments.json`
  Structured subcategory findings (the primary machine-readable artifact consumed by Phase 3).
- `summary.json`
  Lightweight report metadata: timestamp, analyzed functions, report previews.

Note: individual `<function>_gap_summary.md` files were removed from the pipeline. Function-level summaries are now computed in code from `assessments.json` when needed rather than written as separate files.

### 14.3 Revision Outputs

- `revised_policy.md`
  Final revised policy draft.
- `revision_report.md`
  Summary of revisions made.
- `improvement_roadmap.md`
  Prioritized remediation roadmap.
- `debug.log`
  Full diagnostic trace.

## 15. Reliability And Guardrails

This repository uses several reliability patterns repeatedly.

### 15.1 Structured Output Everywhere Possible

The agents generally return Pydantic-based structured output rather than unconstrained text.

Benefits:

- easier validation
- more deterministic downstream processing
- less brittle parsing

### 15.2 Retry Logic For Structured Parsing Failures

Several modules implement `_invoke_with_retries()` wrappers.

This is a practical concession to real-world structured LLM behavior: valid logic can still fail because of transient formatting issues.

### 15.3 Deterministic Fallbacks

The code often falls back to deterministic behavior when model steps fail:

- scope classification can fall back to “all in scope”
- summary generation can fall back to code-built summaries
- revision targeting can fall back to `new_section`
- lossy summarization can fall back to original text

This is good engineering. The pipeline degrades in a conservative direction rather than silently failing.

### 15.4 Explicit Out-Of-Scope Modeling

The system distinguishes between:

- a real policy gap in the current document
- a requirement that belongs in a different dedicated policy

That distinction is one of the project’s strongest technical choices.

### 15.5 Human Review Assumption

The system is built as an AI-assisted drafting and analysis engine, not as an autonomous compliance authority.

The outputs are designed to be:

- inspectable
- traceable
- editable
- reviewable

This is an architectural assumption, not just a business statement.

## 16. Important Current Limitations

A realistic technical explanation should also cover limitations.

### 16.1 Evaluation Maturity

The code contains strong orchestration and guardrails, but broad benchmark-driven evaluation across many real-world policy types is still the next major hardening step.

### 16.2 PDF Quality Dependency

Badly scanned or heavily malformed PDFs remain a challenge despite the extraction safeguards.

### 16.3 Framework Breadth

The current implementation is most concretely grounded in the CIS MS-ISAC NIST-oriented template structure and NIST CSF organization. Broader direct framework-to-framework transformation is still a growth path.

### 16.4 CLI-Centric Product State

The current repo is a working technical prototype and workflow engine, not yet a polished review application with full enterprise UX, auth, tenancy, and governance controls.

## 17. Why This Architecture Makes Sense

The architecture is strong for this problem because:

- policy documents are long and messy, so line-based extraction matters
- semantic interpretation is required, so LLMs are useful
- compliance work needs traceability, so structured assessments matter
- revision must preserve context, so delta-style additions matter
- large prompts are risky, so summarization and validation utilities matter
- not all gaps belong in the same document, so out-of-scope handling matters

In short, the code does not treat this as just a text generation problem. It treats it as a **document intelligence and transformation pipeline**.

## 18. Technical Q&A

### Q: Why not just send the full PDF to one model and ask for gaps plus a revised policy?

Because that approach is easy to demo but weak to trust. You lose structural traceability, you cannot validate intermediate steps cleanly, and you have no reusable machine-readable outputs between stages. This repository deliberately separates extraction, assessment, and revision so that every stage can be inspected and improved independently.

### Q: Why does the extractor use both rules and LLMs?

Because rules are faster and more reliable when the document is structurally clean, while LLMs are better for ambiguous or badly formatted cases. The hybrid strategy gives better speed and robustness than either approach alone.

### Q: Why extract content directly from source lines after boundary detection?

Because once the boundaries are known, the source document is the most trustworthy representation of content. Letting the model rewrite section content at this stage would create unnecessary hallucination risk.

### Q: Why are there validation loops in extraction, summarization, and revision?

Because generation alone is not enough for reliability-sensitive workflows. The code repeatedly follows a pattern of generate, validate, and regenerate with feedback. That pattern is visible in extraction correction, lossless summarization, function summary validation, and revision verification.

### Q: Why classify scope before analyzing all subcategories?

Because otherwise the system would create many false gaps for requirements that belong in a different policy domain. Scope classification is a cost-saving step, but more importantly it is a correctness step.

### Q: Why does the current gap agent use full-policy subcategory assessment instead of only map-reduce evidence scanning?

The current code comments explain this directly: with a larger context window, full-policy per-subcategory assessment became practical and empirically more reliable than the older map-reduce approach, which introduced extra hallucinations and latency in this specific implementation.

### Q: Why is deterministic report assembly preferred after assessments are generated?

Because once structured assessments exist, counts, tables, maturity aggregation, and report assembly are better computed in code. This avoids wasting LLM calls on work that is already deterministic.

### Q: Why generate delta blocks in revision instead of rewriting the full document each time?

Delta blocks make the generation task narrower, easier to validate, and less likely to overwrite useful original content. They also make it easier to merge multiple changes coherently at the section level later.

### Q: Why does the revision engine try to detect policy domain and build an allowlist?

Because a good revision engine should improve the current policy, not convert it into a giant unrelated control document. Domain filtering keeps the revised document realistic and prevents the system from adding controls that belong in separate dedicated policies.

### Q: Why is local model execution useful here?

Policy documents are sensitive. Running the pipeline locally improves privacy, reduces external dependency, and makes debugging and repeatability easier during development.

### Q: What is the most important engineering strength of this repo?

The strongest engineering quality is that it combines LLM reasoning with deterministic structure and validation. The code repeatedly narrows the model’s job to the semantic parts where it is genuinely useful, while preserving control of state, artifacts, and aggregation in code.
