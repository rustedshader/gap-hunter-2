# Gap Hunter Jury Questions And Suggested Answers

This document is a hackathon-facing Q&A sheet for jury preparation. The answers are written to be spoken, not just read, so they are intentionally fuller than a normal FAQ.

The strongest way to use this document is:

1. Start with the short answer in the first 1 to 3 sentences.
2. Expand only if the jury asks a follow-up.
3. Be precise about what is live today versus what is part of the roadmap.

## One-Line Pitch

**Q: What is Gap Hunter in one sentence?**

Gap Hunter is an AI-assisted policy gap analysis engine that takes an existing security policy, maps it against the **CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)**, identifies what is missing or weak, and produces a revised policy in a NIST-style template structure with a prioritized improvement roadmap.

## Problem And Market

**Q: What exact problem are you solving?**

Most organizations do not start from a blank page. They already have policies, but those policies are inconsistent in structure, written against different frameworks, and often incomplete when compared to modern cybersecurity guidance. The hard part is not just writing a new policy; it is understanding where the existing policy falls short, what evidence already exists, what is missing, and how to revise it into a cleaner and more auditable format.

Gap Hunter solves that specific problem. Instead of asking a team to manually read a long policy, compare it with a framework template, identify gaps, and rewrite the document section by section, we automate that workflow in three stages: extraction, gap analysis, and revision.

**Q: Who is the primary user?**

The primary user is a compliance or security governance team that already owns policy documentation but needs to align it to a standard quickly. In practice, that could be a CISO office, GRC analyst, internal audit team, consultant, MSSP, or a mid-sized company preparing for customer due diligence or a formal compliance exercise.

For hackathon framing, the best answer is that we are starting with teams that already have policy documents but lack the time or specialized expertise to convert them into a framework-aligned, review-ready format.

**Q: Why is this problem urgent today?**

Security questionnaires, procurement reviews, cyber insurance reviews, and regulatory expectations increasingly require organizations to show evidence that their policies are structured, current, and aligned to recognized frameworks. Many companies do have policies, but they are old, generic, or scattered across formats.

That creates a practical pain point: the organization is not starting from zero, but it still cannot confidently demonstrate coverage. Gap Hunter reduces the time between “we have a policy” and “we have a framework-aligned, explainable, remediated policy.”

**Q: Why not just hire a consultant or use a generic GRC platform?**

Consultants are valuable, but they are expensive and not always scalable for repeated internal policy refreshes. Generic GRC platforms often focus on control management, evidence collection, or questionnaires rather than deep policy-to-template restructuring. Our focus is narrower and more execution-oriented: take an existing policy document, analyze its language against framework requirements, show specific gaps with evidence, and generate a revised policy draft that a human reviewer can approve.

The wedge is speed and document-level actionability. We are not trying to replace governance programs; we are trying to make one painful workflow dramatically faster.

## Product Workflow

**Q: Walk us through the product end to end.**

The current pipeline has three phases.

Phase 1 is document extraction. We take a PDF policy, convert it into markdown, detect section boundaries, validate the extraction, and build a structured section list.

Phase 2 is gap analysis. We assemble the policy content, classify which NIST CSF functions are relevant, analyze the policy against those functions and subcategories, and generate function-wise and consolidated gap reports. We also persist structured assessments in JSON so they can be reused later.

Phase 3 is policy revision. We use the structured gap findings to determine where existing sections should be modified, where new sections should be created, and then generate a revised policy along with an improvement roadmap.

That is important for a demo because it shows this is not just a chat prompt. It is a pipeline with intermediate artifacts, traceability, and reusable outputs.

**Q: What exactly does the user input and what do they get back?**

Today the input is a policy PDF. The system extracts sections, summarizes and organizes them, and then produces several outputs in a run directory.

The key outputs are:

- extracted sections
- a master section list
- function-level gap analysis reports
- a consolidated gap analysis
- structured machine-readable assessments
- a revised policy draft
- an improvement roadmap

That matters because different stakeholders care about different outputs. An analyst may want the structured assessment and evidence trail, while leadership may prefer the consolidated report and revised policy draft.

**Q: What is working live right now?**

The CLI pipeline is live. The repository already contains:

- PDF extraction into structured sections
- multi-step validation and correction during extraction
- NIST CSF function-based gap analysis
- scope classification to avoid irrelevant analysis
- consolidated reporting
- policy revision generation
- roadmap generation

So the strongest live demo is: upload a policy PDF, run the analysis, show the gap reports, then open the revised policy and roadmap.

**Q: What is mocked or still evolving?**

The core analysis pipeline is real, but some productization layers are still roadmap items. For example, the current repo is a CLI, not a polished multi-user SaaS app. We should present that honestly.

If asked, the right framing is: the intelligence workflow is implemented, while packaging, workflow UI, enterprise auth, tenancy, deployment flexibility, and broader framework coverage are natural next steps after the hackathon.

## Why This Framework

**Q: Why did you choose the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)?**

We chose it because it gives us a strong target structure for policy improvement. Many security frameworks define what outcomes matter, but not all of them are equally practical when the task is “help me rewrite my policy document.” The CIS MS-ISAC guide is useful because it bridges framework intent and policy language, which makes it a good basis for gap analysis plus revision.

In other words, it is not just a scoring reference. It is a drafting reference. That is exactly what we need because our system does not stop at identifying gaps; it also produces a revised policy in a template-oriented format.

**Q: Are you mapping only to NIST, or also to ISO and others?**

The current revision target is NIST-style policy output anchored on the CIS MS-ISAC 2024 guide. However, the input policy does not need to already be written in NIST language. The system is designed to evaluate an existing policy regardless of whether its original language feels more ISO-like, NIST-like, or organization-specific.

Our current implementation is strongest when the goal is to normalize policy quality into a NIST CSF oriented destination format. Broader framework-to-framework mapping is a roadmap extension, not something we should overclaim.

**Q: How do you handle policies that are not explicitly labeled to any framework?**

We analyze the content and subject matter of the policy itself rather than depending on a label. The system first extracts section content and then classifies which NIST functions are relevant to that document. For example, a risk policy is expected to overlap more with Govern and Identify, while an incident response policy overlaps more with Detect, Respond, and Recover.

This is useful because many real-world policies are not cleanly tagged. What matters is the content and intended scope, not whether the document explicitly says “this aligns with framework X.”

## Technical Architecture

**Q: What is the architecture at a high level?**

The architecture is a staged policy-processing pipeline.

First, the document is converted from PDF into markdown and broken into line-numbered content. Then a section extractor identifies section boundaries, a validator checks whether the boundaries are accurate, and a corrector repairs issues if needed. That gives us a structured representation of the original policy.

Next, the gap analysis layer builds a rich policy content view, classifies which NIST CSF functions are relevant, and runs function-specific analysis. For each in-scope subcategory, the full policy content is sent in one focused LLM call alongside the subcategory's specific requirement, implementation guidance, and reference template excerpt. This single-call-per-subcategory approach was chosen after empirically testing a map-reduce alternative, which introduced more hallucinations and latency.

Finally, the revision layer consumes the structured assessments, targets the right sections for modification or new section creation, integrates additions coherently, and generates a revised policy plus roadmap.

**Q: Why is this more than just a single LLM prompt?**

Because the repo is not doing “upload document and ask the model for a summary.” It uses staged processing, validation, structured outputs, and intermediate artifacts.

Examples of that are:

- rule-based and validated section extraction rather than free-form summarization
- scope classification so irrelevant NIST functions can be skipped entirely
- full-policy single-call assessment with structured schema output per subcategory
- structured JSON assessment outputs that feed the revision phase
- domain-aware revision filtering so the revised policy stays within its policy type
- revision logic that separates modifications to existing sections from creation of new sections

That structure matters because policy analysis is a reliability problem, not just a text generation problem.

**Q: What technologies are you using?**

The project is written in Python and managed with `uv`. It uses `docling` for PDF-to-markdown conversion, `pydantic` for structured data schemas, and local LLM integration through `langchain-community`, `langchain-ollama`, and `llama-cpp-python`.

A notable design choice in this repo is the move toward `ChatLlamaCpp` for structured output reliability and large context handling. The code is also configured to run in offline mode for model loading where the required assets are already cached.

**Q: Why did you choose local model execution?**

There are two main reasons. First, privacy: policy documents are often sensitive, and local processing is easier to defend than sending everything to a remote API. Second, determinism and control: for a hackathon prototype we wanted a setup where we could inspect the pipeline closely and avoid dependency on internet availability or hosted inference behavior.

That said, the architecture can support deployment-specific choices later. Local execution is our current implementation choice, not a permanent product constraint.

## AI Design And Reliability

**Q: Where exactly is AI used in the pipeline?**

AI is used in several bounded places:

- extraction assistance when identifying section boundaries in difficult PDFs
- validation and correction of extraction results
- classification of which policy functions and subcategories are relevant
- assessment of whether evidence in the policy addresses a framework requirement
- generation of revised policy language
- roadmap generation

Importantly, not every step is purely generative. Some parts are closer to classification, verification, or transformation tasks, which are easier to constrain and evaluate.

**Q: What is deterministic versus model-driven?**

The line numbering, content slicing, file outputs, orchestration, and report assembly are deterministic. The extraction flow also includes direct content extraction from source lines rather than asking the model to rewrite section text.

The model-driven parts are the judgment tasks: identifying section boundaries when structure is ambiguous, deciding policy scope, assessing whether a subcategory is addressed, and drafting revisions.

That distinction is important because it shows we are not using the model where deterministic logic is stronger. We use the model where semantic interpretation is required.

**Q: How do you reduce hallucinations?**

We reduce hallucinations with architecture, not with a vague prompt.

First, extraction is validated in a loop: extractor, validator, then corrector. Second, section content is taken directly from source lines once boundaries are established, which avoids the model inventing policy text during extraction. Third, the gap analysis uses a scope-first design so the system does not force every policy through all six functions unnecessarily. Fourth, each subcategory is assessed with the full policy in context so the model quotes from what it can actually read — this was found empirically to produce far fewer hallucinations than alternative approaches that fragmented the policy into smaller chunks. Fifth, outputs are structured with Pydantic schemas where possible, which reduces free-form drift. Sixth, the revision phase uses domain detection to prevent adding content from the wrong policy domain into the current document.

No LLM system eliminates hallucinations completely, but this design reduces the surface area significantly.

**Q: How do you keep answers explainable and auditable?**

Each assessment is tied to a specific NIST subcategory and includes evidence, a gap statement, and a recommendation. That means the model is not just outputting “this is weak”; it is required to say what requirement it is evaluating, what evidence it found in the customer policy, and what is missing.

That creates a human-reviewable chain. For an auditor or compliance lead, this is much more usable than a generic score because they can inspect both the supporting evidence and the resulting recommendation.

**Q: How do you ensure the revised policy is not generic AI fluff?**

The revision stage is grounded in the original policy sections and in the structured assessment outputs from Phase 2. Instead of generating a whole new policy from scratch without context, the system targets specific sections for modification, integrates additions, and creates new sections only when necessary.

That is a much better approach than one-shot generation because it preserves the original policy where it is already good and only changes what needs to change.

**Q: Why is an LLM needed at all? Why not just a rules engine?**

A rules engine is good for static checks, but policies are written in messy, variable language. Two organizations can express the same control intent in very different wording, structure, or sectioning. The challenge is semantic interpretation: understanding whether a policy meaningfully covers a requirement even if the wording is indirect or spread across sections.

We still use rules and deterministic logic where it makes sense. But pure rules are not enough for cross-document semantic alignment and revision drafting. The value of the LLM is in understanding meaning, while the value of the system design is in constraining where and how that meaning is used.

**Q: What are the main failure modes?**

The main failure modes are:

- poor PDF extraction when the source document is highly unstructured
- borderline misclassification of policy scope
- over-crediting vague language as sufficient coverage
- under-crediting organization-specific language that is valid but unconventional
- generating revised language that is technically correct but too generic for a specific organization

The right answer to the jury is not that failure is impossible. It is that we know the failure modes, we have designed guardrails around them, and we keep a human reviewer in the loop for approval.

## Gap Analysis Logic

**Q: How do you determine which NIST functions apply to a policy?**

The system runs a policy-level classifier across the full policy content to determine which of the six NIST CSF functions are relevant to the policy’s subject matter. For example, a Risk Management Policy should not be deeply evaluated against every Detect or Recover subcategory if the document was never meant to serve that purpose.

This is important because it reduces noise. Otherwise, the system would produce a large number of misleading “gaps” that are not actual deficiencies in the document, but simply belong to a different policy domain.

**Q: How do you analyze coverage inside a function?**

Within each relevant function, the system performs subcategory-level analysis using a scope-first, single-call-per-subcategory approach.

First, it determines which subcategories are in scope for that policy type. Then for each in-scope subcategory it sends the full policy content alongside the subcategory's requirement, implementation guidance, key questions, and a reference excerpt from the relevant CIS MS-ISAC template document. The model returns a structured assessment: status, evidence quote from the policy, gap description, and recommendation.

This full-policy approach was chosen after empirically testing a map-reduce alternative (which scanned sections individually before a reduce step). The map-reduce path produced three times more hallucinations because the model would sometimes quote text from the NIST requirement description rather than from the policy itself. With a 65 536-token context window the full policy fits in a single call, making map-reduce unnecessary.

**Q: How do you distinguish between fully addressed, partially addressed, and not addressed?**

Each subcategory assessment uses a structured schema with a status field and supporting rationale. A requirement is fully addressed only when the policy language demonstrates the expected intent clearly enough. It is partially addressed when the policy mentions the area but lacks specificity, ownership, enforcement detail, cadence, or required structure. It is not addressed when the requirement is materially absent.

The important point is that “partial” is treated seriously. In real policy work, many documents are not empty; they are incomplete. Capturing that nuance is more useful than a binary pass/fail.

**Q: How do you prevent irrelevant recommendations?**

We use scope filtering at two levels: function-level and subcategory-level. If a function is out of scope for the policy, we mark it as such rather than generating remediation work for an unrelated domain. Likewise, if a subcategory belongs to a different policy type, it should not become a false gap.

This is a major product distinction because many naive systems confuse “not present in this document” with “organizational weakness.” Sometimes a requirement belongs in a different policy entirely.

## Revision And Output

**Q: How do you generate the revised policy?**

The revision phase starts from structured gap findings, not just from the original PDF. It parses targets for where each gap should be handled, separates modifications to existing sections from genuinely new sections, and then integrates those additions into a coherent revised document.

The code explicitly treats these as different actions because revising an existing section is different from inventing a new section. That makes the output more faithful to the original policy and easier for a reviewer to approve.

**Q: How do you preserve the organization’s original voice and context?**

The best answer is that we do not treat the original policy as disposable input. We preserve section structure, use the original content as context during modifications, and only add or revise language where the assessments identify a concrete gap.

This means the revised policy should look like an improved version of the customer’s document, not like a totally generic policy pasted on top of it.

**Q: What outputs are most useful to show in the demo?**

The strongest sequence is:

1. show the original policy input
2. show extracted sections or master list
3. show one function-level gap analysis with evidence and recommendations
4. show the consolidated report
5. show the revised policy
6. show the roadmap

That progression makes the intelligence traceable. It demonstrates not just that a final draft exists, but how the system got there.

## Security, Privacy, And Trust

**Q: These are sensitive policy documents. How do you handle privacy?**

The current implementation is well positioned for privacy because it is designed around local processing. The repo uses local model execution and explicitly enables offline behavior for model loading where cached artifacts exist. That reduces dependence on external APIs and makes it easier to defend data handling for sensitive internal policy documents.

For a production product, we would still need enterprise-grade controls such as encryption, access control, retention policies, audit logging, and deployment choices like single-tenant or on-prem. But the prototype already reflects the right architectural instinct: do not casually move sensitive policy text across third-party services if you do not have to.

**Q: Why should a customer trust an AI to rewrite security policy?**

They should not trust it blindly, and we should say that directly. The value is not blind automation; it is accelerated expert review. Gap Hunter gives the team a structured first draft of the analysis and a proposed revision grounded in evidence. A human owner still reviews, approves, edits, and signs off.

The trust model is therefore “AI-assisted governance workflow” rather than “autonomous compliance authority.” That is a much more defensible position.

**Q: How would you defend this in front of an auditor?**

We would position the system as a policy analysis and drafting assistant, not as the final compliance attestation layer. The auditor should be able to inspect:

- the original source policy
- the extracted structured sections
- the identified subcategory assessments
- the evidence used for those assessments
- the revised policy draft

That traceability is the key. We are not saying, “trust the score.” We are saying, “here is the evidence-backed reasoning chain that the organization reviewed and approved.”

## Business And Differentiation

**Q: What makes this different from ChatGPT plus a prompt?**

Three things.

First, pipeline design. We have extraction, validation, scope classification, structured assessments, revision, and roadmap generation as separate stages with reusable artifacts.

Second, domain anchoring. The analysis is explicitly framed against the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024), not just “best practice” in the abstract.

Third, output usefulness. A generic chat session may give a broad narrative. Gap Hunter gives section-level structure, function-level analyses, machine-readable assessment data, and a revised policy draft that flows from the evidence.

**Q: What is your moat or defensibility?**

At an early stage, the moat is not just model choice. It is workflow quality, domain-specific prompt and schema design, policy-to-framework mapping logic, and the accumulation of evaluation data over time.

If we continue building this, the strongest defensibility would come from:

- high-quality framework mapping assets
- evaluation datasets across real policy types
- reviewer feedback loops
- strong policy revision workflows
- integration into recurring governance processes

So the honest answer is: today the moat is the architecture and product direction; over time the moat becomes proprietary evaluation and workflow integration.

**Q: Who pays for this and what is the ROI?**

The buyer would likely be the team responsible for policy readiness and compliance velocity: security leadership, GRC, internal audit, consulting practices, or managed security/compliance providers.

The ROI comes from reducing manual analysis and rewrite cycles. If a team currently spends days comparing policies to framework templates and writing remediation drafts, a system that compresses that into a much shorter review workflow has immediate operational value. The product does not need to replace an entire GRC program to be valuable; it only needs to make one expensive workflow much faster and more consistent.

## Evaluation And Metrics

**Q: How do you know the system is correct?**

For a hackathon, the best honest answer is that correctness is evaluated through expert review of the outputs and by checking whether the identified gaps, evidence, and revised language are plausible, traceable, and consistent with the target framework template.

For the next stage, we would formalize this with benchmark documents and reviewer scoring across dimensions like:

- extraction accuracy
- section boundary accuracy
- precision of identified gaps
- recall of critical missing controls
- quality of evidence mapping
- usefulness of revised policy language

The key is to show that we already know what rigorous evaluation should look like, even if the dataset is still being built.

**Q: What is the single most important metric?**

The best primary metric is “expert-accepted gap identification quality,” meaning how often a human reviewer agrees that a flagged gap is real and material. If the gap analysis is not trusted, everything after that becomes less valuable.

A close second is “time-to-reviewable revised policy draft,” because that reflects business value very directly.

**Q: Can you show an example where the system was wrong?**

If asked this, answer transparently. A good example would be a case where the policy used unusual internal terminology, and the system initially under-recognized that it was actually covering a requirement. That shows maturity because it demonstrates we are aware that semantic variance is hard and that human review remains important.

Juries usually trust teams more when they can explain their system’s errors clearly rather than pretending there are none.

## Edge Cases

**Q: What happens if the PDF is poorly formatted or scanned?**

The extraction quality depends on document quality, so poor scans are a real challenge. Our extraction layer already uses validation and correction to improve robustness, but garbage-in still matters. For production, we would strengthen preprocessing, OCR quality checks, and document-quality warnings so the user knows when an analysis may be less reliable.

That is the right answer because it is accurate and still shows a clear path to hardening.

**Q: What if the policy mixes policy, standards, and procedures in one file?**

That is common in real organizations, and our section-based architecture is actually helpful there. Because we extract and analyze the document in sections, the system can still identify evidence and gaps even when the document is messy. The challenge is not impossibility; it is classification granularity.

In a more mature version, we would label sections by document type or control intent so mixed documents can be treated even more precisely.

**Q: What if the organization intentionally deviates from a framework?**

That is not inherently a bug. A strong governance workflow should allow exceptions if they are deliberate, approved, and documented. Our system should therefore be seen as identifying divergence and missing rationale, not just enforcing blind conformity.

A good future enhancement would be explicit exception handling, where the reviewer can mark a gap as intentionally accepted with justification instead of treating every deviation as remediation work.

## Demo And Hackathon Questions

**Q: What did you build during the hackathon?**

The best way to answer is by naming the live workflow pieces: document extraction, section validation, NIST-function gap analysis, consolidated reporting, revised policy generation, and roadmap generation. Focus on the end-to-end flow rather than low-level implementation details.

If the jury presses further, emphasize that the value is not one isolated model call; it is the orchestration across phases with intermediate artifacts and explainable outputs.

**Q: If you had one more week, what would you improve first?**

The strongest next improvements would be:

- a simple review UI on top of the current CLI outputs
- better evaluation datasets and scoring
- clearer evidence-to-section traceability in the final report
- support for more input formats and document quality checks
- configurable organization context such as industry, size, and risk tolerance

That answer is good because it prioritizes product trust and usability, not just adding more AI.

**Q: Why is this a startup opportunity and not just a demo?**

Because policy review and remediation is a repeated operational workflow, not a one-time curiosity. Security teams repeatedly update policies, prepare for customer diligence, respond to audit observations, adapt to framework changes, and onboard new business units or vendors.

If we can make policy gap analysis and revision faster, more consistent, and more explainable, that is a recurring business process with real budget behind it.

## Tough Questions You Should Practice Exactly

**Q: What happens when your AI gives a wrong recommendation?**

The recommendation is treated as a proposed remediation, not as an authoritative final decision. The workflow is designed so that the reviewer can inspect the evidence, inspect the gap statement, and then accept, modify, or reject the recommendation.

The right way to position the product is that it reduces first-draft effort and improves consistency, while final accountability remains with the organization’s policy owner.

**Q: Why should we believe your revised policy is actually compliant?**

We should not overstate this. The correct answer is that the revised policy is framework-aligned and review-ready, not self-certifying. Compliance always depends on human approval, operational implementation, and sometimes legal or regulatory interpretation.

What our system does is dramatically improve the quality and speed of the policy drafting and review process by grounding revisions in framework requirements and evidence from the original document.

**Q: What is the weakest part of your current system?**

The weakest part today is not the orchestration logic; it is evaluation maturity. Like many hackathon projects, the next big step is proving performance systematically across a broad set of real-world policies and edge cases.

That is a good answer because it shows self-awareness. It is better than pretending the model is already universally reliable.

## Closing Positioning

**Q: If the jury remembers only one thing, what should it be?**

They should remember that Gap Hunter is not trying to replace governance expertise. It is building an AI-assisted workflow that turns an existing policy into an explainable gap analysis, a revised NIST-style policy draft, and a practical remediation roadmap. The value is speed, structure, and reviewability for a workflow that is currently slow, manual, and inconsistent.
