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
      openPath: (targetPath: string) => Promise<void>;
      testOllama: (url: string) => Promise<{ ok: boolean; status?: number; models?: string[]; error?: string }>;
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
