"use client";

import { useState, useEffect } from "react";
import { FileText, Search, Shield, Sparkles, CheckCircle2, AlertCircle, ArrowRight, Layers, Zap, Brain, Code } from "lucide-react";

export function Architecture() {
  const [activePhase, setActivePhase] = useState<1 | 2 | 3>(1);
  const [animateFlow, setAnimateFlow] = useState(false);

  useEffect(() => {
    setAnimateFlow(true);
    const timer = setTimeout(() => setAnimateFlow(false), 2000);
    return () => clearTimeout(timer);
  }, [activePhase]);

  return (
    <section className="py-24 bg-gradient-to-b from-white to-slate-50" id="architecture">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold mb-4">
            <Layers className="w-4 h-4" />
            Multi-Agent Architecture
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Intelligent 3-Phase Pipeline
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Gap Hunter 2 uses a sophisticated multi-agent architecture with validation loops, 
            preventing hallucinations and ensuring compliance accuracy at every step.
          </p>
        </div>

        {/* Phase Selector */}
        <div className="flex justify-center gap-4 mb-12">
          <PhaseButton
            phase={1}
            active={activePhase === 1}
            onClick={() => setActivePhase(1)}
            icon={<FileText className="w-5 h-5" />}
            title="Extraction"
          />
          <PhaseButton
            phase={2}
            active={activePhase === 2}
            onClick={() => setActivePhase(2)}
            icon={<Search className="w-5 h-5" />}
            title="Gap Analysis"
          />
          <PhaseButton
            phase={3}
            active={activePhase === 3}
            onClick={() => setActivePhase(3)}
            icon={<Sparkles className="w-5 h-5" />}
            title="Remediation"
          />
        </div>

        {/* Phase Content */}
        <div className={`bg-white rounded-2xl shadow-2xl p-8 md:p-12 mb-16 transition-all duration-500 ${animateFlow ? 'ring-2 ring-blue-400' : ''}`}>
          {activePhase === 1 && <Phase1Content />}
          {activePhase === 2 && <Phase2Content />}
          {activePhase === 3 && <Phase3Content />}
        </div>

        {/* Visual Pipeline Flow */}
        <div className="mb-16 bg-gradient-to-r from-blue-50 via-purple-50 to-emerald-50 rounded-2xl p-8 border-2 border-slate-200">
          <h3 className="text-2xl font-bold text-slate-900 mb-6 text-center">Complete Pipeline Flow</h3>
          <div className="flex items-center justify-between gap-4 flex-wrap md:flex-nowrap">
            <PipelineStep number={1} label="PDF Input" icon={<FileText className="w-6 h-6" />} active={activePhase === 1} />
            <ArrowRight className="w-6 h-6 text-slate-400 hidden md:block" />
            <PipelineStep number={2} label="Extraction" icon={<Code className="w-6 h-6" />} active={activePhase === 1} />
            <ArrowRight className="w-6 h-6 text-slate-400 hidden md:block" />
            <PipelineStep number={3} label="Gap Analysis" icon={<Search className="w-6 h-6" />} active={activePhase === 2} />
            <ArrowRight className="w-6 h-6 text-slate-400 hidden md:block" />
            <PipelineStep number={4} label="Validation" icon={<Shield className="w-6 h-6" />} active={activePhase === 2} />
            <ArrowRight className="w-6 h-6 text-slate-400 hidden md:block" />
            <PipelineStep number={5} label="Remediation" icon={<Sparkles className="w-6 h-6" />} active={activePhase === 3} />
            <ArrowRight className="w-6 h-6 text-slate-400 hidden md:block" />
            <PipelineStep number={6} label="Output" icon={<CheckCircle2 className="w-6 h-6" />} active={activePhase === 3} />
          </div>
        </div>

        {/* Key Innovations */}
        <div className="grid md:grid-cols-3 gap-8">
          <InnovationCard
            icon={<Shield className="w-8 h-8 text-emerald-600" />}
            title="Privacy-First Design"
            description="Runs on local, self-hosted LLMs via Ollama. Your sensitive policy documents never leave your infrastructure."
          />
          <InnovationCard
            icon={<Brain className="w-8 h-8 text-purple-600" />}
            title="Validation Loops"
            description="Multi-agent verification prevents AI hallucinations. Every gap finding is cross-checked against source text."
          />
          <InnovationCard
            icon={<Zap className="w-8 h-8 text-orange-600" />}
            title="Dynamic Scoping"
            description="Intelligently identifies relevant NIST functions, skipping irrelevant analysis to save 60%+ compute time."
          />
        </div>
      </div>
    </section>
  );
}

function PhaseButton({ phase, active, onClick, icon, title }: {
  phase: number;
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 px-6 py-4 rounded-xl font-semibold transition-all ${
        active
          ? "bg-blue-600 text-white shadow-lg scale-105"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      <div className={`flex items-center justify-center w-8 h-8 rounded-lg ${
        active ? "bg-blue-500" : "bg-slate-200"
      }`}>
        {icon}
      </div>
      <div className="text-left">
        <div className="text-xs opacity-75">Phase {phase}</div>
        <div className="text-sm font-bold">{title}</div>
      </div>
    </button>
  );
}

function Phase1Content() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-3xl font-bold text-slate-900 mb-4">
          Phase 1: Intelligent Document Extraction
        </h3>
        <p className="text-lg text-slate-600 mb-6">
          Transforms unstructured PDF policies into machine-readable JSON without losing context 
          or allowing AI to rewrite original text.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <ProcessStep
          number={1}
          title="Document Ingestion"
          description="Docling library parses complex PDFs, decodes custom font codes (/MT), and assigns line numbers to every line."
          icon={<FileText className="w-6 h-6 text-blue-600" />}
        />
        <ProcessStep
          number={2}
          title="Rule-Based Fast Path"
          description="Attempts deterministic extraction using regex patterns (Markdown, numbered, ALL CAPS) to avoid expensive LLM calls."
          icon={<Zap className="w-6 h-6 text-yellow-600" />}
        />
        <ProcessStep
          number={3}
          title="Multi-Agent Extraction"
          description="If rules fail, uses sliding windows (80 lines, 20 overlap) with Extractor→Validator→Corrector agent loops."
          icon={<Brain className="w-6 h-6 text-purple-600" />}
        />
        <ProcessStep
          number={4}
          title="Stitching & Deduplication"
          description="Handles incomplete sections across chunks, removes duplicates, filters nested sections, and renumbers sequentially."
          icon={<Layers className="w-6 h-6 text-emerald-600" />}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" />
          Phase 1 Outputs
        </h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-semibold text-blue-900">sections_output.json</div>
            <div className="text-blue-700">Verbatim collection of every policy section with line numbers</div>
          </div>
          <div>
            <div className="font-semibold text-blue-900">master_list.json</div>
            <div className="text-blue-700">Lightweight index with titles, boundaries, and AI summaries</div>
          </div>
        </div>
      </div>

      <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-emerald-800">
          <strong>Key Innovation:</strong> Hybrid approach tries fast rule-based extraction first, 
          only falling back to expensive LLM processing when necessary. Saves 70%+ on compute costs.
        </div>
      </div>
    </div>
  );
}

function Phase2Content() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-3xl font-bold text-slate-900 mb-4">
          Phase 2: Multi-Agent Gap Analysis
        </h3>
        <p className="text-lg text-slate-600 mb-6">
          Scope-First + Map-Reduce architecture prevents context overflow and hallucinations 
          while analyzing hundreds of NIST subcategories.
        </p>
      </div>

      <div className="space-y-4">
        <ProcessStep
          number={1}
          title="Macro Scope Classifier"
          description="Determines which of 6 NIST functions (Govern, Identify, Protect, Detect, Respond, Recover) are relevant. Skips irrelevant functions entirely."
          icon={<Search className="w-6 h-6 text-blue-600" />}
          highlight="Saves 60%+ compute time"
        />
        <ArrowRight className="w-6 h-6 text-slate-400 mx-auto" />
        <ProcessStep
          number={2}
          title="Micro Scope Classifier"
          description="For relevant functions, determines which specific NIST subcategories apply to this policy type."
          icon={<Layers className="w-6 h-6 text-purple-600" />}
        />
        <ArrowRight className="w-6 h-6 text-slate-400 mx-auto" />
        <ProcessStep
          number={3}
          title="Map Phase (Evidence Gathering)"
          description="Scans every policy section individually for each subcategory. Extracts 200-char evidence snippets. Keeps prompts ~1K chars for small LLMs."
          icon={<FileText className="w-6 h-6 text-emerald-600" />}
          highlight="Prevents context overflow"
        />
        <ArrowRight className="w-6 h-6 text-slate-400 mx-auto" />
        <ProcessStep
          number={4}
          title="Reduce Phase (Assessment)"
          description="Feeds only relevant evidence snippets (not whole document) to generate structured SubcategoryAssessment with status, gap, and recommendation."
          icon={<Brain className="w-6 h-6 text-orange-600" />}
        />
        <ArrowRight className="w-6 h-6 text-slate-400 mx-auto" />
        <ProcessStep
          number={5}
          title="Validated Summarization"
          description="Chain of Verification loop: Python code verifies statistics, LLM checks for fabricated IDs, auto-corrects errors (up to 3 retries)."
          icon={<Shield className="w-6 h-6 text-red-600" />}
          highlight="Prevents hallucinations"
        />
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <h4 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" />
          Phase 2 Outputs
        </h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-semibold text-purple-900">Function Reports</div>
            <div className="text-purple-700">Detailed markdown for each NIST function (e.g., protect_gap_analysis.md)</div>
          </div>
          <div>
            <div className="font-semibold text-purple-900">assessments.json</div>
            <div className="text-purple-700">Structured dataset of every gap (input for Phase 3)</div>
          </div>
          <div>
            <div className="font-semibold text-purple-900">consolidated_gap_analysis.md</div>
            <div className="text-purple-700">Code-generated aggregation prioritizing remediation steps</div>
          </div>
          <div>
            <div className="font-semibold text-purple-900">master_gap_summary.md</div>
            <div className="text-purple-700">Executive summary of strongest/weakest security functions</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Phase3Content() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-3xl font-bold text-slate-900 mb-4">
          Phase 3: Automated Policy Remediation
        </h3>
        <p className="text-lg text-slate-600 mb-6">
          Uses RAPTOR (Recursive Abstractive Processing) + CoVe (Chain of Verification) to 
          rewrite policies without hallucinations or dropped requirements.
        </p>
      </div>

      <div className="space-y-6">
        <div className="border-l-4 border-blue-500 pl-6">
          <h4 className="font-bold text-slate-900 mb-2">Step 0: Gap Targeting (Intelligent Router)</h4>
          <p className="text-slate-600 text-sm mb-3">
            LLM-based SectionTargeter classifies each gap as "modify" (assign to existing section) 
            or "new_section" (create new section).
          </p>
        </div>

        <div className="border-l-4 border-purple-500 pl-6">
          <h4 className="font-bold text-slate-900 mb-2">Phase A: Addition Writer & CoVe Loop</h4>
          <p className="text-slate-600 text-sm mb-3">
            For "modify" gaps, executes strict Chain of Verification:
          </p>
          <ol className="space-y-2 text-sm text-slate-600">
            <li className="flex gap-2">
              <span className="font-semibold text-purple-600">1.</span>
              <span><strong>Addition Writer:</strong> Writes "Delta Block" (only new content needed)</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-purple-600">2.</span>
              <span><strong>CoVe Questioner:</strong> Generates 3-5 Yes/No verification questions</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-purple-600">3.</span>
              <span><strong>CoVe Verifier:</strong> Answers questions independently</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-purple-600">4.</span>
              <span><strong>Feedback & Retry:</strong> If any "No", reject and retry (up to 3x)</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-purple-600">5.</span>
              <span><strong>RAPTOR Cluster Summarizer:</strong> Compresses blocks to prevent redundancy</span>
            </li>
          </ol>
        </div>

        <div className="border-l-4 border-emerald-500 pl-6">
          <h4 className="font-bold text-slate-900 mb-2">Phase B: Integration Editor</h4>
          <p className="text-slate-600 text-sm mb-3">
            Merges Delta Blocks into original sections with dual validation:
          </p>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="flex gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <span><strong>Code-Based:</strong> Python verifies every NIST ID is accounted for</span>
            </li>
            <li className="flex gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <span><strong>LLM Coherence:</strong> Checks first 1500 chars for garbled text</span>
            </li>
          </ul>
        </div>

        <div className="border-l-4 border-orange-500 pl-6">
          <h4 className="font-bold text-slate-900 mb-2">Phase C: Section Creation</h4>
          <p className="text-slate-600 text-sm">
            For "new_section" gaps, Section Creator generates brand-new sections matching 
            document style with sequential numbering.
          </p>
        </div>

        <div className="border-l-4 border-red-500 pl-6">
          <h4 className="font-bold text-slate-900 mb-2">Phase D: Improvement Roadmap Pipeline</h4>
          <p className="text-slate-600 text-sm mb-3">
            Multi-agent sub-pipeline generates actionable IT roadmap:
          </p>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="flex gap-2">
              <span className="font-semibold text-red-600">→</span>
              <span><strong>Roadmap Planner:</strong> Categorizes gaps into execution tiers</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-red-600">→</span>
              <span><strong>Roadmap Detailer:</strong> Adds steps, success criteria, effort estimates</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold text-red-600">→</span>
              <span><strong>Roadmap Validator:</strong> Enforces 90%+ ID coverage, checks measurability</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6">
        <h4 className="font-semibold text-emerald-900 mb-3 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Phase 3 Outputs
        </h4>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <div className="font-semibold text-emerald-900">revised_policy.md</div>
            <div className="text-emerald-700">Fully updated, compliant policy document</div>
          </div>
          <div>
            <div className="font-semibold text-emerald-900">revision_report.md</div>
            <div className="text-emerald-700">Detailed changelog tied to NIST IDs</div>
          </div>
          <div>
            <div className="font-semibold text-emerald-900">improvement_roadmap.md</div>
            <div className="text-emerald-700">Strategic, tiered operational guide</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProcessStep({ number, title, description, icon, highlight }: {
  number: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  highlight?: string;
}) {
  return (
    <div className="flex gap-4 p-4 border border-slate-200 rounded-lg hover:shadow-md transition-shadow">
      <div className="flex-shrink-0">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-lg flex items-center justify-center font-bold text-lg">
          {number}
        </div>
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-2">
          {icon}
          <h4 className="font-bold text-slate-900">{title}</h4>
        </div>
        <p className="text-sm text-slate-600 mb-2">{description}</p>
        {highlight && (
          <div className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs font-semibold">
            <Zap className="w-3 h-3" />
            {highlight}
          </div>
        )}
      </div>
    </div>
  );
}

function InnovationCard({ icon, title, description }: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="mb-4">{icon}</div>
      <h4 className="text-lg font-bold text-slate-900 mb-2">{title}</h4>
      <p className="text-sm text-slate-600">{description}</p>
    </div>
  );
}

function PipelineStep({ number, label, icon, active }: {
  number: number;
  label: string;
  icon: React.ReactNode;
  active: boolean;
}) {
  return (
    <div className={`flex flex-col items-center gap-2 transition-all duration-300 ${active ? 'scale-110' : 'scale-100 opacity-60'}`}>
      <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
        active 
          ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg' 
          : 'bg-slate-200 text-slate-600'
      }`}>
        {icon}
      </div>
      <div className="text-xs font-semibold text-slate-700 text-center">{label}</div>
    </div>
  );
}
