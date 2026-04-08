export {};

declare global {
  interface Window {
    api: {
      loadConfig: () => Promise<Record<string, unknown>>;
      saveConfig: (config: Record<string, unknown>) => Promise<Record<string, unknown>>;
      selectPdf: () => Promise<string | null>;
      selectDirectory: () => Promise<string | null>;
      startRun: (params: Record<string, unknown>) => Promise<{ ok: boolean; error?: string }>;
      stopRun: (options?: { force?: boolean }) => Promise<{ ok: boolean }>;
      listArtifacts: (runDir: string) => Promise<Array<{ name: string; path: string; size: number }>>;
      readSummary: (runDir: string) => Promise<Record<string, unknown> | null>;
      readJson: (filePath: string) => Promise<Record<string, unknown> | unknown[] | null>;
      readText: (filePath: string, maxBytes?: number) => Promise<string | null>;
      historyList: () => Promise<RunHistoryEntry[]>;
      historyAdd: (entry: RunHistoryEntry) => Promise<RunHistoryEntry[]>;
      historyUpdate: (entry: RunHistoryEntry) => Promise<RunHistoryEntry[]>;
      historyRemove: (runDir: string) => Promise<RunHistoryEntry[]>;
      historyScan: (baseDir: string) => Promise<Array<RunHistoryEntry | null>>;
      getAppInfo: () => Promise<AppInfo>;
      getProcessStats: () => Promise<ProcessStats>;
      openPath: (targetPath: string) => Promise<void>;
      testOllama: (url: string) => Promise<{ ok: boolean; status?: number; models?: string[]; error?: string; durationMs?: number }>;
      onEvent: (callback: (data: BackendEvent) => void) => () => void;
      onLog: (callback: (entry: LogEntry) => void) => () => void;
      onStatus: (callback: (status: StatusEvent) => void) => () => void;
      onExit: (callback: (data: ExitEvent) => void) => () => void;
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
  state: "running" | "stopped" | "error";
  pid?: number;
};

export type ExitEvent = {
  code: number | null;
  signal: string | null;
};

export type RunHistoryEntry = {
  id?: string;
  runDir: string;
  createdAt?: string;
  policyName?: string | null;
  model?: string | null;
  provider?: string | null;
  status?: string | null;
  tags?: string[];
  notes?: string;
};

export type BackendEvent = {
  name: string;
  timestamp?: string;
  [key: string]: unknown;
};

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
