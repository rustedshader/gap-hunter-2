import type { AppConfig, Phase, RunStep, View } from "./types/ui";

export const DEFAULT_CONFIG: AppConfig = {
  pdfPath: "",
  outputDir: "",
  runDir: "",
  provider: "ollama",
  ollamaUrl: "http://localhost:11434",
  model: "gemma4:e2b",
  ggufModelPath: "",
  windowSize: 80,
  overlap: 20,
  extractOnly: false,
  skipRevision: false,
  skipExtraction: false,
  revisionOnly: false,
  logRetention: 2000,
  autoRefresh: true
};

export const DEFAULT_PHASES: Phase[] = [
  { id: "extraction", label: "Extraction", status: "pending" },
  { id: "analysis", label: "Gap Analysis", status: "pending" },
  { id: "revision", label: "Policy Revision", status: "pending" },
  { id: "roadmap", label: "Roadmap", status: "pending" }
];

export const NIST_FUNCTIONS = [
  "Govern",
  "Identify",
  "Protect",
  "Detect",
  "Respond",
  "Recover"
];

export const VIEW_META: Record<View, { title: string; subtitle: string }> = {
  mission: { title: "Mission Control", subtitle: "Showcase" },
  dashboard: { title: "Operations Dashboard", subtitle: "Overview" },
  run: { title: "Run Builder", subtitle: "Configure" },
  logs: { title: "Live Telemetry", subtitle: "Logs" },
  artifacts: { title: "Artifacts", subtitle: "Outputs" },
  demo: { title: "Guided Demo", subtitle: "Walkthrough" },
  settings: { title: "LLM Settings", subtitle: "Providers" },
  evidence: { title: "Evidence Explorer", subtitle: "Policy Sections" },
  matrix: { title: "Gap Matrix", subtitle: "Coverage" },
  revision: { title: "Revision Diff Studio", subtitle: "Changes" },
  roadmap: { title: "Roadmap Planner", subtitle: "Execution" },
  library: { title: "Run Library", subtitle: "History" },
  help: { title: "Help Center", subtitle: "FAQ" },
  diagnostics: { title: "Diagnostics", subtitle: "System" }
};

export const NAV_GROUPS: Array<{ label: string; items: View[] }> = [
  { label: "Core", items: ["run", "mission", "dashboard", "logs", "artifacts"] },
  { label: "Deep Dives", items: ["evidence", "matrix", "revision", "roadmap"] },
  { label: "Library", items: ["library"] },
  { label: "Guides", items: ["demo", "help"] },
  { label: "Admin", items: ["settings", "diagnostics"] }
];

export const RUN_STEPS: Array<{ id: RunStep; label: string; helper: string }> = [
  { id: "setup", label: "Setup", helper: "Source + output" },
  { id: "analysis", label: "Analysis", helper: "Parameters" },
  { id: "review", label: "Review", helper: "Validate + launch" }
];

export const RUN_STEP_ORDER: RunStep[] = ["setup", "analysis", "review"];
