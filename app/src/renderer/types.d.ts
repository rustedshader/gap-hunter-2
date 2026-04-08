export {};

declare global {
  interface Window {
    api: {
      loadConfig: () => Promise<Record<string, unknown>>;
      saveConfig: (config: Record<string, unknown>) => Promise<Record<string, unknown>>;
      selectPdf: () => Promise<string | null>;
      selectDirectory: () => Promise<string | null>;
      startRun: (params: Record<string, unknown>) => Promise<{ ok: boolean; runId?: string; error?: string }>;
      stopRun: (payload?: { runId?: string; force?: boolean }) => Promise<{ ok: boolean; error?: string }>;
      getRunsSnapshot: () => Promise<RunSnapshot>;
      selectRun: (runId: string | null) => Promise<RunSnapshot>;
      updateRun: (runId: string, updates: Partial<RunRecord>) => Promise<RunRecord | null>;
      refreshRun: (runId: string) => Promise<RunRecord | null>;
      scanRuns: (baseDir: string) => Promise<RunRecord[]>;
      removeRun: (runId: string, options?: { deleteFiles?: boolean }) => Promise<{ ok: boolean; error?: string }>;
      readRunJson: (runId: string, fileName: string) => Promise<Record<string, unknown> | unknown[] | null>;
      readRunText: (runId: string, fileName: string, maxBytes?: number) => Promise<string | null>;
      clearRunLog: (runId: string) => Promise<{ ok: boolean; error?: string }>;
      getAppInfo: () => Promise<AppInfo>;
      getProcessStats: (runId?: string) => Promise<ProcessStats>;
      openPath: (targetPath: string) => Promise<void>;
      testOllama: (url: string) => Promise<{ ok: boolean; status?: number; models?: string[]; error?: string; durationMs?: number }>;
      onRunEvent: (callback: (data: RunEvent) => void) => () => void;
    };
  }
}

export type LogEntry = {
  time: string;
  level: string;
  logger: string;
  message: string;
  source: string;
};

export type StatusEvent = {
  state: RunStatus;
  pid?: number;
};

export type ExitEvent = {
  code: number | null;
  signal: string | null;
};

export type BackendEvent = {
  name: string;
  timestamp?: string;
  [key: string]: unknown;
};

export type RunStatus =
  | "queued"
  | "starting"
  | "running"
  | "stopping"
  | "force-stopping"
  | "completed"
  | "failed"
  | "cancelled"
  | "orphaned"
  | "unknown"
  | "recovering";

export type RunArtifact = {
  name: string;
  path: string;
  size: number;
  mtimeMs?: number;
};

export type RunRecord = {
  id: string;
  status: RunStatus;
  runType?: "real" | "demo";
  runName?: string;
  pinned?: boolean;
  createdAt: string;
  updatedAt: string;
  startedAt?: string | null;
  finishedAt?: string | null;
  stopRequestedAt?: string | null;
  durationMs?: number | null;
  runDir?: string;
  outputDir?: string;
  pdfPath?: string;
  provider?: string;
  model?: string;
  ggufModelPath?: string;
  ollamaUrl?: string;
  windowSize?: number | null;
  overlap?: number | null;
  extractOnly?: boolean;
  skipRevision?: boolean;
  skipExtraction?: boolean;
  revisionOnly?: boolean;
  executionMode?: string;
  pid?: number | null;
  exitCode?: number | null;
  signal?: string | null;
  error?: { message: string; details?: string } | null;
  phases?: Array<{
    id: string;
    label: string;
    status: string;
    startedAt?: number;
    finishedAt?: number;
  }> | null;
  progress?: number | null;
  lastHeartbeat?: string | null;
  artifacts?: RunArtifact[];
  artifactsUpdatedAt?: string | null;
  summary?: Record<string, unknown> | null;
  reportCount?: number | null;
  sectionCount?: number | null;
  masterListCount?: number | null;
  assessmentCount?: number | null;
  gapCount?: number | null;
  partialCount?: number | null;
  addressedCount?: number | null;
  outOfScopeCount?: number | null;
  artifactsCount?: number | null;
  artifactTotalBytes?: number | null;
  runDirExists?: boolean | null;
  missingArtifacts?: string[];
  hasRevision?: boolean;
  hasRevisedPolicy?: boolean;
  hasRoadmap?: boolean;
  metadataUpdatedAt?: string | null;
  tags?: string[];
  notes?: string;
  policyName?: string;
  command?: string;
  args?: string[];
  cwd?: string;
  version?: number;
};

export type RunSnapshot = {
  runs: RunRecord[];
  selectedRunId: string | null;
  generatedAt: string;
};

export type RunEvent =
  | { type: "run-created"; run: RunRecord }
  | { type: "run-updated"; run: RunRecord }
  | { type: "run-removed"; runId: string }
  | { type: "run-selected"; runId: string | null }
  | { type: "run-log"; runId: string; entry: LogEntry }
  | { type: "backend-event"; runId: string; event: BackendEvent }
  | { type: "run-exit"; runId: string; exitCode: number | null; signal: string | null; status: RunStatus }
  | { type: "run-artifacts"; runId: string; artifacts: RunArtifact[] };

export type AppInfo = {
  appVersion: string;
  electron: string;
  chrome: string;
  node: string;
  platform: string;
  arch: string;
};

export type ProcessStats = {
  timestamp: string;
  app: {
    rssMb: number;
    heapUsedMb: number;
    heapTotalMb: number;
  };
  backend: {
    pid: number;
    cpuPercent: number | null;
    memoryMb: number | null;
  } | null;
};
