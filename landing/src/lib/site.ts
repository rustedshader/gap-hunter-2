import type { LucideIcon } from "lucide-react";
import {
  BookOpenText,
  FolderKanban,
  Radar,
  ScanText,
  ShieldCheck,
  Sparkles,
  Waypoints
} from "lucide-react";

export type Benefit = {
  title: string;
  description: string;
  icon: LucideIcon;
  highlight: string;
};

export type Testimonial = {
  quote: string;
  role: string;
  initials: string;
};

export type FAQItem = {
  question: string;
  answer: string;
};

export const navItems = [
  { label: "Platform", href: "#platform" },
  { label: "Benefits", href: "#benefits" },
  { label: "Proof", href: "#proof" },
  { label: "FAQ", href: "#faq" }
];

export const heroStats = [
  { value: "6", label: "NIST functions mapped across every run" },
  { value: "4", label: "Pipeline phases from extraction to roadmap" },
  { value: "1", label: "Desktop workspace for policy owners and reviewers" }
];

export const trustBar = [
  "CIS MS-ISAC NIST CSF guide aligned",
  "Desktop app + CLI workflow",
  "Live logs, revisions, and roadmap outputs"
];

export const benefits: Benefit[] = [
  {
    title: "See the gap matrix before the audit thread starts",
    description:
      "Map sections to the NIST function landscape and surface what is addressed, partial, missing, or out of scope without waiting for a manual spreadsheet pass.",
    icon: Radar,
    highlight: "Gap Matrix"
  },
  {
    title: "Rewrite policy language into something reviewers can approve",
    description:
      "Move from extracted source text into revision-ready output that respects the target template instead of leaving teams to redraft from scratch.",
    icon: Sparkles,
    highlight: "Revision Diff Studio"
  },
  {
    title: "Keep evidence, telemetry, and artifacts in one command center",
    description:
      "Track every run through live logs, output folders, evidence views, and artifacts without losing the thread across tools or folders.",
    icon: FolderKanban,
    highlight: "Mission Control"
  },
  {
    title: "Turn findings into a roadmap operations teams can execute",
    description:
      "Translate policy gaps into an ordered plan so compliance cleanup becomes a scheduled program instead of a one-off emergency.",
    icon: Waypoints,
    highlight: "Roadmap Planner"
  },
  {
    title: "Start from real policy PDFs, not toy inputs",
    description:
      "Gap Hunter is built around existing policy documents, extraction, and review loops rather than abstract form builders or checklist UIs.",
    icon: ScanText,
    highlight: "Source-first analysis"
  },
  {
    title: "Keep the workflow private and operator-friendly",
    description:
      "Run with Ollama or local GGUF support, keep artifacts on disk, and give policy owners a desktop-first environment built for controlled review.",
    icon: ShieldCheck,
    highlight: "Desktop-first privacy"
  }
];

export const workflowSteps = [
  {
    title: "Ingest",
    body: "Bring in a live policy PDF, choose the output path, and reuse prior run directories when needed."
  },
  {
    title: "Analyze",
    body: "Run extraction, gap analysis, and framework coverage against the CIS MS-ISAC NIST CSF guide."
  },
  {
    title: "Revise",
    body: "Generate revision-ready policy output, evidence trails, and roadmap artifacts from a single workspace."
  }
];

export const testimonials: Testimonial[] = [
  {
    quote:
      "We stopped treating policy review like a dead document exercise. The matrix made the missing coverage obvious in minutes.",
    role: "Security program manager, regional fintech pilot",
    initials: "SP"
  },
  {
    quote:
      "The revision output finally gave our compliance lead and policy owner a shared starting point instead of two conflicting edits.",
    role: "GRC lead, healthcare operations team",
    initials: "GL"
  },
  {
    quote:
      "Mission Control feels like a real operating surface, not a demo toy. We can follow the run and inspect the artifacts without context switching.",
    role: "Platform engineer, manufacturing group",
    initials: "PE"
  },
  {
    quote:
      "The roadmap is what changed adoption. Findings are useful, but turning them into a sequence of actions made the product operationally credible.",
    role: "Compliance director, infrastructure provider",
    initials: "CD"
  }
];

export const faqs: FAQItem[] = [
  {
    question: "What kind of policy documents can Gap Hunter analyze?",
    answer:
      "The product is designed around real policy PDFs and turns them into extracted sections, framework coverage views, revisions, and roadmap outputs."
  },
  {
    question: "Does Gap Hunter replace legal or compliance review?",
    answer:
      "No. It compresses the first-pass analysis and drafting workload so legal, compliance, and policy owners start from a stronger artifact."
  },
  {
    question: "Can teams use local or self-hosted models?",
    answer:
      "Yes. The existing product supports Ollama and local GGUF-backed flows, which makes it practical for controlled environments."
  },
  {
    question: "What makes this different from a generic AI document tool?",
    answer:
      "The workflow is purpose-built for policy gap analysis, NIST-aligned coverage, revision output, evidence inspection, and roadmap planning."
  },
  {
    question: "Is there a way to inspect how a run produced its outputs?",
    answer:
      "Yes. Gap Hunter surfaces run directories, live logs, intermediate events, evidence views, and artifacts so teams can review provenance instead of trusting a black box."
  },
  {
    question: "Who is the landing page aimed at?",
    answer:
      "Security leaders, GRC operators, policy owners, and platform teams who need clearer policy review cycles and audit-ready output."
  }
];

export const footerLinks = [
  { label: "Privacy", href: "/privacy" },
  { label: "Terms", href: "/terms" },
  { label: "Contact", href: "mailto:hello@gaphunter.app" }
];

export const capabilityChips = [
  "Mission Control",
  "Gap Matrix",
  "Evidence Explorer",
  "Revision Diff Studio",
  "Roadmap Planner",
  "Run Library"
];

export const seoKeywords = [
  "policy gap analysis",
  "NIST policy review",
  "CIS MS-ISAC NIST CSF",
  "policy revision software",
  "compliance desktop app",
  "audit-ready policy workflow"
];

export const softwareApplicationSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Gap Hunter Studio",
  applicationCategory: "BusinessApplication",
  operatingSystem: "macOS, Windows, Linux",
  description:
    "Policy gap analysis workspace that aligns policy documents to the CIS MS-ISAC NIST CSF Policy Template Guide and produces revised, audit-ready outputs."
};

export const sectionEyebrows = {
  benefits: "What teams get",
  proof: "Workflow walkthrough",
  testimonials: "Design partner feedback",
  faq: "FAQ",
  finalCta: "Start your first review cycle"
};

export const editorialValues = [
  {
    label: "Framework alignment",
    detail: "CIS MS-ISAC NIST CSF guide"
  },
  {
    label: "Deployment shape",
    detail: "Desktop app plus Python backend"
  },
  {
    label: "Review outputs",
    detail: "Artifacts, revisions, roadmap"
  },
  {
    label: "Model strategy",
    detail: "Ollama or local GGUF"
  }
];

export const mediaBullets = [
  {
    title: "Command-center overview",
    description: "Track run state, pipeline phases, artifacts, and coverage from one screen."
  },
  {
    title: "Evidence-led review",
    description: "Move from raw sections to coverage, revisions, and roadmap without leaving the workspace."
  },
  {
    title: "Operational handoff",
    description: "Export outputs teams can review, share, and schedule against."
  }
];

export const legalCopy = {
  privacy:
    "Gap Hunter Studio stores analysis artifacts in your chosen output directory. Production privacy terms should be tailored before public launch.",
  terms:
    "This landing app is a product marketing surface for Gap Hunter Studio. Production commercial and legal terms should be finalized before deployment."
};

export const platformProof = [
  {
    label: "Run telemetry",
    detail: "Live status, logs, process stats, and progress signals"
  },
  {
    label: "Artifact review",
    detail: "Summaries, evidence, revisions, and roadmap outputs"
  },
  {
    label: "Operator controls",
    detail: "Output folders, model choice, run reuse, and advanced flags"
  }
];

export const narrativeCards = [
  {
    title: "From static PDF to live pipeline",
    body: "Run Builder, Mission Control, and Diagnostics frame policy work like an operational system instead of a scattered review ritual.",
    icon: BookOpenText
  },
  {
    title: "From vague findings to specific remediation",
    body: "Coverage summaries and roadmap planning shift the conversation from broad concern to prioritized action.",
    icon: Waypoints
  }
];
