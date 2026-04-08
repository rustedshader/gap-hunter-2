"use client";

import { useState } from "react";
import { Code, GitBranch, Database, Cpu, Network, Lock, ExternalLink } from "lucide-react";

export function TechnicalDeepDive() {
  const [activeSection, setActiveSection] = useState<"stack" | "algorithms" | "security">("stack");

  return (
    <section className="py-24 bg-gradient-to-b from-slate-900 to-slate-800 text-white" id="technical">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-full text-sm font-semibold mb-4">
            <Code className="w-4 h-4" />
            Technical Deep Dive
          </div>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Built for Engineers, By Engineers
          </h2>
          <p className="text-xl text-blue-200 max-w-3xl mx-auto">
            Open-source architecture with modern Python stack, rigorous testing, and production-ready deployment
          </p>
        </div>

        {/* Section Tabs */}
        <div className="flex justify-center gap-4 mb-12 flex-wrap">
          <TechTabButton
            active={activeSection === "stack"}
            onClick={() => setActiveSection("stack")}
            icon={<Cpu className="w-5 h-5" />}
            label="Tech Stack"
          />
          <TechTabButton
            active={activeSection === "algorithms"}
            onClick={() => setActiveSection("algorithms")}
            icon={<GitBranch className="w-5 h-5" />}
            label="Algorithms"
          />
          <TechTabButton
            active={activeSection === "security"}
            onClick={() => setActiveSection("security")}
            icon={<Lock className="w-5 h-5" />}
            label="Security"
          />
        </div>

        {/* Content */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 md:p-12">
          {activeSection === "stack" && <TechStackContent />}
          {activeSection === "algorithms" && <AlgorithmsContent />}
          {activeSection === "security" && <SecurityContent />}
        </div>

        {/* GitHub Link */}
        <div className="mt-12 text-center">
          <a
            href="https://github.com/yourusername/gap-hunter-2"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 rounded-lg font-semibold hover:bg-slate-100 transition-all"
          >
            <GitBranch className="w-5 h-5" />
            View on GitHub
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
}

function TechTabButton({ active, onClick, icon, label }: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 px-6 py-3 rounded-lg font-semibold transition-all ${
        active
          ? "bg-blue-500 text-white shadow-lg"
          : "bg-white/10 text-white hover:bg-white/20"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function TechStackContent() {
  const stack = [
    {
      category: "Core Framework",
      icon: <Code className="w-6 h-6 text-blue-400" />,
      items: [
        { name: "Python 3.11+", description: "Modern async/await, type hints, pattern matching" },
        { name: "Pydantic v2", description: "Data validation, serialization, JSON schema generation" },
        { name: "LangChain", description: "LLM orchestration, prompt templates, output parsers" },
      ]
    },
    {
      category: "LLM Integration",
      icon: <Cpu className="w-6 h-6 text-purple-400" />,
      items: [
        { name: "Ollama", description: "Local LLM hosting (Llama 3, Mistral, Qwen)" },
        { name: "OpenAI API", description: "Optional cloud LLM support (GPT-4, GPT-3.5)" },
        { name: "Custom Agents", description: "Multi-agent architecture with validation loops" },
      ]
    },
    {
      category: "Document Processing",
      icon: <Database className="w-6 h-6 text-emerald-400" />,
      items: [
        { name: "Docling", description: "PDF parsing, font decoding, line numbering" },
        { name: "RAPTOR", description: "Recursive abstractive processing for hierarchical docs" },
        { name: "Sliding Windows", description: "80-line chunks with 20-line overlap" },
      ]
    },
    {
      category: "Testing & Quality",
      icon: <GitBranch className="w-6 h-6 text-orange-400" />,
      items: [
        { name: "Pytest", description: "82 tests across 4 phases (unit, integration, E2E, adversarial)" },
        { name: "Hypothesis", description: "Property-based testing with 100+ iterations" },
        { name: "DeepEval", description: "LLM-as-a-judge evaluation framework" },
        { name: "Coverage.py", description: "85% code coverage with branch analysis" },
      ]
    },
    {
      category: "DevOps & CI/CD",
      icon: <Network className="w-6 h-6 text-yellow-400" />,
      items: [
        { name: "GitHub Actions", description: "3 CI pipelines (fast, nightly, full)" },
        { name: "uv", description: "Fast Python package manager" },
        { name: "Docker", description: "Containerized deployment with Ollama" },
      ]
    },
  ];

  return (
    <div className="space-y-8">
      <h3 className="text-2xl font-bold mb-6">Modern Python Stack</h3>
      {stack.map((section, i) => (
        <div key={i} className="border-l-4 border-blue-500 pl-6">
          <div className="flex items-center gap-3 mb-4">
            {section.icon}
            <h4 className="text-xl font-bold">{section.category}</h4>
          </div>
          <div className="space-y-3">
            {section.items.map((item, j) => (
              <div key={j} className="bg-white/5 rounded-lg p-4">
                <div className="font-semibold text-blue-300 mb-1">{item.name}</div>
                <div className="text-sm text-blue-200">{item.description}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AlgorithmsContent() {
  const algorithms = [
    {
      name: "RAPTOR (Recursive Abstractive Processing)",
      paper: "Sarthi et al., 2024",
      description: "Tree-organized retrieval for hierarchical document processing",
      implementation: [
        "Clusters related policy sections into semantic groups",
        "Generates abstractive summaries at each tree level",
        "Enables efficient retrieval across document hierarchy",
      ],
      link: "https://arxiv.org/abs/2401.18059"
    },
    {
      name: "Chain of Verification (CoVe)",
      paper: "Dhuliawala et al., 2023",
      description: "Multi-step validation preventing LLM hallucinations",
      implementation: [
        "Addition Writer generates delta blocks",
        "CoVe Questioner creates 3-5 verification questions",
        "CoVe Verifier answers independently",
        "Feedback loop with up to 3 retries",
      ],
      link: "https://arxiv.org/abs/2309.11495"
    },
    {
      name: "Map-Reduce for LLM Orchestration",
      paper: "Dean & Ghemawat, 2004 (adapted)",
      description: "Distributed evidence gathering preventing context overflow",
      implementation: [
        "Map phase: Scan each section for evidence (200-char snippets)",
        "Reduce phase: Aggregate evidence into assessments",
        "Keeps prompts ~1K chars for small LLMs",
        "Prevents context window overflow",
      ],
      link: "https://research.google/pubs/pub62/"
    },
    {
      name: "Property-Based Testing",
      paper: "Claessen & Hughes, 2000",
      description: "Formal verification using randomized test generation",
      implementation: [
        "12 universal correctness properties",
        "100+ randomized iterations per property",
        "Hypothesis framework for test generation",
        "Validates invariants across all inputs",
      ],
      link: "https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf"
    },
  ];

  return (
    <div className="space-y-8">
      <h3 className="text-2xl font-bold mb-6">Research-Backed Algorithms</h3>
      {algorithms.map((algo, i) => (
        <div key={i} className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h4 className="text-xl font-bold text-blue-300 mb-1">{algo.name}</h4>
              <div className="text-sm text-blue-400 italic">{algo.paper}</div>
            </div>
            <a
              href={algo.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
          </div>
          <p className="text-blue-200 mb-4">{algo.description}</p>
          <div className="space-y-2">
            <div className="text-sm font-semibold text-blue-300">Implementation:</div>
            <ul className="space-y-2">
              {algo.implementation.map((item, j) => (
                <li key={j} className="text-sm text-blue-200 flex items-start gap-2">
                  <span className="text-blue-400 mt-1">→</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}

function SecurityContent() {
  const securityFeatures = [
    {
      title: "Privacy-First Architecture",
      icon: <Lock className="w-6 h-6 text-emerald-400" />,
      features: [
        "100% local processing via Ollama",
        "Zero data sent to external APIs (unless explicitly configured)",
        "Sensitive policy documents never leave your infrastructure",
        "GDPR and HIPAA compliant by design",
      ]
    },
    {
      title: "Hallucination Defense",
      icon: <GitBranch className="w-6 h-6 text-blue-400" />,
      features: [
        "Multi-agent validation loops (Extractor→Validator→Corrector)",
        "Chain of Verification (CoVe) with 3-5 verification questions",
        "Python code verification for statistics and NIST IDs",
        "Evidence grounding: 92% faithfulness score",
      ]
    },
    {
      title: "Adversarial Robustness",
      icon: <Database className="w-6 h-6 text-orange-400" />,
      features: [
        "Corrupted PDF handling with graceful degradation",
        "Out-of-scope document detection",
        "Memory exhaustion prevention (12K char truncation)",
        "Section overflow safeguards (>20 sections triggers warning)",
      ]
    },
    {
      title: "Audit Trail",
      icon: <Network className="w-6 h-6 text-purple-400" />,
      features: [
        "Complete debug logs for every pipeline run",
        "Line-number references to original policy text",
        "Revision reports with NIST ID traceability",
        "Metrics tracking with 7-day rolling averages",
      ]
    },
  ];

  return (
    <div className="space-y-8">
      <h3 className="text-2xl font-bold mb-6">Enterprise-Grade Security</h3>
      {securityFeatures.map((section, i) => (
        <div key={i} className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center gap-3 mb-4">
            {section.icon}
            <h4 className="text-xl font-bold">{section.title}</h4>
          </div>
          <ul className="space-y-3">
            {section.features.map((feature, j) => (
              <li key={j} className="flex items-start gap-3 text-blue-200">
                <div className="w-2 h-2 bg-emerald-400 rounded-full mt-2 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}

      <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-6">
        <h4 className="font-semibold text-emerald-300 mb-3">Security Best Practices</h4>
        <p className="text-emerald-200 text-sm">
          Gap Hunter 2 follows OWASP Top 10 guidelines, implements input validation at every layer, 
          and uses Pydantic for strict type checking. All LLM outputs are validated before being 
          written to disk, and the system includes comprehensive error handling with graceful degradation.
        </p>
      </div>
    </div>
  );
}
