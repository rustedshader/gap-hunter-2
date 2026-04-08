export type Provider = "ollama" | "llamacpp";

export type View =
  | "mission"
  | "dashboard"
  | "run"
  | "logs"
  | "artifacts"
  | "demo"
  | "settings"
  | "evidence"
  | "matrix"
  | "revision"
  | "roadmap"
  | "library"
  | "help"
  | "diagnostics";

export type RunStep = "setup" | "analysis" | "review";
export type LogView = "stream" | "events";
export type MatrixView = "overview" | "matrix";
export type RevisionView = "summary" | "compare" | "final";
export type RoadmapView = "overview" | "tiers" | "missing";

export type AssessmentStatus =
  | "Addressed"
  | "Partially Addressed"
  | "Not Addressed"
  | "Out of Scope";

export type SubcategoryAssessment = {
  subcategory_id: string;
  title: string;
  status: AssessmentStatus;
  evidence: string;
  gap: string;
  recommendation: string;
};

export type PolicySection = {
  number: string;
  title: string;
  content: string;
  start_line: number;
  end_line: number | null;
  is_complete: boolean;
};

export type MasterListEntry = {
  number: string;
  title: string;
  summary: string;
  start_line: number;
  end_line: number | null;
};

export type SummaryPayload = {
  functions_analyzed?: string[];
  reports?: Record<string, unknown>;
  timestamp?: string;
};

export type RevisionChange = {
  id: string;
  action: string;
  section: string;
  description: string;
};

export type RevisionReport = {
  totalGaps: number;
  modifiedSections: number;
  newSections: number;
  changes: RevisionChange[];
};

export type RoadmapItem = {
  title: string;
  nistReference: string;
  description: string;
  responsible: string;
  effort: string;
  successCriteria: string;
  dependencies: string;
};

export type RoadmapTier = {
  tierName: string;
  rationale: string;
  items: RoadmapItem[];
};

export type RoadmapData = {
  executiveSummary: string;
  tiers: RoadmapTier[];
  missingDocs: string[];
};

export type RunData = {
  sections: PolicySection[];
  masterList: MasterListEntry[];
  assessments: Record<string, SubcategoryAssessment[]>;
  summary: SummaryPayload | null;
  revisionReport: RevisionReport | null;
  revisedPolicy: string | null;
  roadmap: RoadmapData | null;
};

export type StatusCounts = {
  total: number;
  addressed: number;
  partiallyAddressed: number;
  notAddressed: number;
  outOfScope: number;
};

export type AppConfig = {
  pdfPath: string;
  outputDir: string;
  runDir: string;
  provider: Provider;
  ollamaUrl: string;
  model: string;
  ggufModelPath: string;
  windowSize: number;
  overlap: number;
  extractOnly: boolean;
  skipRevision: boolean;
  skipExtraction: boolean;
  revisionOnly: boolean;
  logRetention: number;
  autoRefresh: boolean;
};

export type PhaseStatus = "pending" | "running" | "done" | "error";

export type Phase = {
  id: "extraction" | "analysis" | "revision" | "roadmap";
  label: string;
  status: PhaseStatus;
  startedAt?: number;
  finishedAt?: number;
};

export type Artifact = {
  name: string;
  path: string;
  size: number;
};
