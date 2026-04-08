import React, { useEffect, useMemo, useRef, useState } from "react";
import type {
  AppInfo,
  BackendEvent,
  ExitEvent,
  LogEntry,
  ProcessStats,
  RunHistoryEntry,
  StatusEvent
} from "./types";

type Provider = "ollama" | "llamacpp";

type View =
  | "dashboard"
  | "run"
  | "logs"
  | "artifacts"
  | "settings"
  | "evidence"
  | "matrix"
  | "revision"
  | "roadmap"
  | "library"
  | "diagnostics";

type AssessmentStatus =
  | "Addressed"
  | "Partially Addressed"
  | "Not Addressed"
  | "Out of Scope";

type SubcategoryAssessment = {
  subcategory_id: string;
  title: string;
  status: AssessmentStatus;
  evidence: string;
  gap: string;
  recommendation: string;
};

type PolicySection = {
  number: string;
  title: string;
  content: string;
  start_line: number;
  end_line: number | null;
  is_complete: boolean;
};

type MasterListEntry = {
  number: string;
  title: string;
  summary: string;
  start_line: number;
  end_line: number | null;
};

type SummaryPayload = {
  functions_analyzed?: string[];
  reports?: Record<string, unknown>;
  timestamp?: string;
};

type RevisionChange = {
  id: string;
  action: string;
  section: string;
  description: string;
};

type RevisionReport = {
  totalGaps: number;
  modifiedSections: number;
  newSections: number;
  changes: RevisionChange[];
};

type RoadmapItem = {
  title: string;
  nistReference: string;
  description: string;
  responsible: string;
  effort: string;
  successCriteria: string;
  dependencies: string;
};

type RoadmapTier = {
  tierName: string;
  rationale: string;
  items: RoadmapItem[];
};

type RoadmapData = {
  executiveSummary: string;
  tiers: RoadmapTier[];
  missingDocs: string[];
};

type RunData = {
  sections: PolicySection[];
  masterList: MasterListEntry[];
  assessments: Record<string, SubcategoryAssessment[]>;
  summary: SummaryPayload | null;
  revisionReport: RevisionReport | null;
  revisedPolicy: string | null;
  roadmap: RoadmapData | null;
};

type AppConfig = {
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

type PhaseStatus = "pending" | "running" | "done" | "error";

type Phase = {
  id: "extraction" | "analysis" | "revision" | "roadmap";
  label: string;
  status: PhaseStatus;
  startedAt?: number;
  finishedAt?: number;
};

type Notice = {
  id: string;
  kind: "info" | "success" | "warning" | "error";
  message: string;
};

type Artifact = {
  name: string;
  path: string;
  size: number;
};

const DEFAULT_CONFIG: AppConfig = {
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

const DEFAULT_PHASES: Phase[] = [
  { id: "extraction", label: "Extraction", status: "pending" },
  { id: "analysis", label: "Gap Analysis", status: "pending" },
  { id: "revision", label: "Policy Revision", status: "pending" },
  { id: "roadmap", label: "Roadmap", status: "pending" }
];

const NIST_FUNCTIONS = [
  "Govern",
  "Identify",
  "Protect",
  "Detect",
  "Respond",
  "Recover"
];

const VIEW_META: Record<View, { title: string; subtitle: string }> = {
  dashboard: { title: "Operations Dashboard", subtitle: "Overview" },
  run: { title: "Run Builder", subtitle: "Configure" },
  logs: { title: "Live Telemetry", subtitle: "Logs" },
  artifacts: { title: "Artifacts", subtitle: "Outputs" },
  settings: { title: "LLM Settings", subtitle: "Providers" },
  evidence: { title: "Evidence Explorer", subtitle: "Policy Sections" },
  matrix: { title: "Gap Matrix", subtitle: "Coverage" },
  revision: { title: "Revision Diff Studio", subtitle: "Changes" },
  roadmap: { title: "Roadmap Planner", subtitle: "Execution" },
  library: { title: "Run Library", subtitle: "History" },
  diagnostics: { title: "Diagnostics", subtitle: "System" }
};

const NAV_GROUPS: Array<{ label: string; items: View[] }> = [
  { label: "Core", items: ["dashboard", "run", "logs", "artifacts"] },
  { label: "Deep Dives", items: ["evidence", "matrix", "revision", "roadmap"] },
  { label: "Library", items: ["library"] },
  { label: "Admin", items: ["settings", "diagnostics"] }
];

function App() {
  const [activeView, setActiveView] = useState<View>("dashboard");
  const [config, setConfig] = useState<AppConfig>(DEFAULT_CONFIG);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [events, setEvents] = useState<BackendEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [exitInfo, setExitInfo] = useState<ExitEvent | null>(null);
  const [statusEvent, setStatusEvent] = useState<StatusEvent | null>(null);
  const [phases, setPhases] = useState<Phase[]>(DEFAULT_PHASES);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [summary, setSummary] = useState<SummaryPayload | null>(null);
  const [ollamaStatus, setOllamaStatus] = useState<"unknown" | "ok" | "error">(
    "unknown"
  );
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [ollamaLatency, setOllamaLatency] = useState<number | null>(null);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [search, setSearch] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);
  const [levelFilter, setLevelFilter] = useState({
    INFO: true,
    WARNING: true,
    ERROR: true,
    DEBUG: false
  });
  const [runHistory, setRunHistory] = useState<RunHistoryEntry[]>([]);
  const [runData, setRunData] = useState<RunData | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [selectedAssessment, setSelectedAssessment] = useState<SubcategoryAssessment | null>(null);
  const [matrixFunction, setMatrixFunction] = useState<string>(NIST_FUNCTIONS[0]);
  const [evidenceStatus, setEvidenceStatus] = useState<AssessmentStatus | "All">("All");
  const [librarySearch, setLibrarySearch] = useState("");
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [processStats, setProcessStats] = useState<ProcessStats | null>(null);
  const [debugLog, setDebugLog] = useState<string>("");

  const logEndRef = useRef<HTMLDivElement | null>(null);
  const runDirRef = useRef<string>("");

  useEffect(() => {
    window.api
      .loadConfig()
      .then((loaded) => {
        const next = { ...DEFAULT_CONFIG, ...loaded } as AppConfig;
        setConfig(next);
      })
      .catch(() => {
        setConfig(DEFAULT_CONFIG);
      });
  }, []);

  useEffect(() => {
    runDirRef.current = config.runDir;
  }, [config.runDir]);

  useEffect(() => {
    const unsubEvent = window.api.onEvent((event) => {
      setEvents((prev) => [...prev.slice(-200), event]);
    });

    const unsubLog = window.api.onLog((entry) => {
      setLogs((prev) => {
        const limit = config.logRetention || 2000;
        const next = [...prev, entry];
        return next.length > limit ? next.slice(-limit) : next;
      });

      updatePhasesFromLog(entry);
      captureRunDir(entry.message);
    });

    const unsubStatus = window.api.onStatus((status) => {
      setStatusEvent(status);
      setIsRunning(status.state === "running");
    });

    const unsubExit = window.api.onExit((info) => {
      setExitInfo(info);
      setIsRunning(false);
      if (info.code && info.code !== 0) {
        addNotice("error", `Run exited with code ${info.code}`);
      } else if (info.signal && info.signal !== "SIGTERM") {
        addNotice("warning", `Run stopped: ${info.signal}`);
      } else {
        addNotice("success", "Run complete");
      }

      const currentRunDir = runDirRef.current;
      if (currentRunDir) {
        refreshArtifacts(currentRunDir);
        refreshSummary(currentRunDir);
        void loadRunData(currentRunDir);
        void saveRunHistory(
          info.code && info.code !== 0 ? "error" : "success"
        );
      }
    });

    return () => {
      unsubEvent();
      unsubLog();
      unsubStatus();
      unsubExit();
    };
  }, [config.logRetention]);

  useEffect(() => {
    if (!autoScroll) {
      return;
    }
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length, autoScroll]);

  useEffect(() => {
    window.api.historyList().then(setRunHistory).catch(() => setRunHistory([]));
    window.api.getAppInfo().then(setAppInfo).catch(() => setAppInfo(null));
  }, []);

  useEffect(() => {
    if (!config.runDir) {
      setRunData(null);
      setSelectedSection(null);
      return;
    }
    void loadRunData(config.runDir);
  }, [config.runDir]);

  useEffect(() => {
    if (!config.autoRefresh || !config.runDir) {
      return undefined;
    }

    const interval = setInterval(() => {
      if (config.runDir) {
        void loadRunData(config.runDir);
        void refreshArtifacts(config.runDir);
        void refreshSummary(config.runDir);
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [config.autoRefresh, config.runDir]);

  useEffect(() => {
    const interval = setInterval(() => {
      window.api
        .getProcessStats()
        .then(setProcessStats)
        .catch(() => setProcessStats(null));
    }, 6000);

    return () => clearInterval(interval);
  }, []);

  const progress = useMemo(() => {
    const weights: Record<string, number> = {
      extraction: 0.25,
      analysis: 0.35,
      revision: 0.25,
      roadmap: 0.15
    };
    let total = 0;
    phases.forEach((phase) => {
      if (phase.status === "done") {
        total += weights[phase.id];
      } else if (phase.status === "running") {
        total += weights[phase.id] * 0.5;
      }
    });
    return Math.min(total, 1);
  }, [phases]);

  const filteredLogs = useMemo(() => {
    const needle = search.trim().toLowerCase();
    return logs.filter((entry) => {
      const level = entry.level.toUpperCase();
      if (levelFilter[level as keyof typeof levelFilter] === false) {
        return false;
      }
      if (!needle) {
        return true;
      }
      return (
        entry.message.toLowerCase().includes(needle) ||
        entry.logger.toLowerCase().includes(needle)
      );
    });
  }, [logs, levelFilter, search]);

  const recentLogs = useMemo(() => logs.slice(-6), [logs]);
  const artifactsPreview = useMemo(() => artifacts.slice(0, 5), [artifacts]);

  const summaryCounts = useMemo(() => {
    return {
      functions: summary?.functions_analyzed?.length ?? 0,
      reports: summary?.reports ? Object.keys(summary.reports).length : 0
    };
  }, [summary]);

  const evidenceMap = useMemo(() => {
    return buildEvidenceMap(runData?.sections || [], runData?.assessments || {});
  }, [runData]);

  const evidenceForSection = useMemo(() => {
    if (!selectedSection) {
      return [];
    }
    const matches = evidenceMap[selectedSection] || [];
    return matches.filter((item) =>
      evidenceStatus === "All" ? true : item.status === evidenceStatus
    );
  }, [evidenceMap, selectedSection, evidenceStatus]);

  const matrixAssessments = useMemo(() => {
    if (!runData?.assessments) {
      return [];
    }
    return runData.assessments[matrixFunction] || [];
  }, [runData, matrixFunction]);

  const runLibraryFiltered = useMemo(() => {
    const needle = librarySearch.trim().toLowerCase();
    if (!needle) {
      return runHistory;
    }
    return runHistory.filter((entry) => {
      return (
        (entry.runDir || "").toLowerCase().includes(needle) ||
        (entry.policyName || "").toLowerCase().includes(needle) ||
        (entry.tags || []).join(" ").toLowerCase().includes(needle)
      );
    });
  }, [runHistory, librarySearch]);

  const runStateLabel = isRunning ? "Running" : "Idle";
  const hasStatus = Boolean(
    exitInfo || statusEvent || phases.some((phase) => phase.status !== "pending")
  );
  const canClearStatus = !isRunning && hasStatus;
  const progressPct = Math.round(progress * 100);
  const viewMeta = VIEW_META[activeView];

  function updateConfig<K extends keyof AppConfig>(
    key: K,
    value: AppConfig[K]
  ) {
    setConfig((prev) => {
      const next = { ...prev, [key]: value };
      void window.api.saveConfig(next);
      return next;
    });
  }

  function captureRunDir(message: string) {
    if (!message) {
      return;
    }

    const outputMatch = message.match(/Output directory:\s*(.*)$/i);
    const runMatch = message.match(/Run directory:\s*(.*)$/i);
    const allMatch = message.match(/All outputs in:\s*(.*)$/i);

    const candidate =
      (outputMatch && outputMatch[1]) ||
      (runMatch && runMatch[1]) ||
      (allMatch && allMatch[1]);

    if (candidate) {
      const trimmed = candidate.replace(/\s+$/, "").replace(/\/$/, "");
      updateConfig("runDir", trimmed);
    }
  }

  function updatePhasesFromLog(entry: LogEntry) {
    const message = entry.message.toLowerCase();
    setPhases((prev) => {
      const next = prev.map((phase) => ({ ...phase }));
      const now = Date.now();

      const setPhase = (id: Phase["id"], status: PhaseStatus) => {
        const target = next.find((p) => p.id === id);
        if (!target) {
          return;
        }
        if (status === "running" && target.status === "pending") {
          target.status = "running";
          target.startedAt = now;
        } else if (status === "done" && target.status !== "done") {
          target.status = "done";
          target.finishedAt = now;
        } else if (status === "error") {
          target.status = "error";
        }
      };

      if (message.includes("phase 1")) {
        setPhase("extraction", "running");
      }
      if (message.includes("phase 2")) {
        setPhase("extraction", "done");
        setPhase("analysis", "running");
      }
      if (message.includes("phase 3")) {
        setPhase("analysis", "done");
        setPhase("revision", "running");
      }
      if (message.includes("phase d") || message.includes("roadmap")) {
        setPhase("revision", "done");
        setPhase("roadmap", "running");
      }
      if (message.includes("gap analysis complete")) {
        setPhase("analysis", "done");
      }
      if (message.includes("policy revision complete")) {
        setPhase("revision", "done");
      }
      if (message.includes("saved improvement roadmap")) {
        setPhase("roadmap", "done");
      }
      if (entry.level.toUpperCase() === "ERROR") {
        const active = next.find((p) => p.status === "running");
        if (active) {
          active.status = "error";
        }
      }

      return next;
    });
  }

  function addNotice(kind: Notice["kind"], message: string) {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setNotices((prev) => [...prev, { id, kind, message }]);
    setTimeout(() => {
      setNotices((prev) => prev.filter((n) => n.id !== id));
    }, 6000);
  }

  function buildRunPayload() {
    return {
      pdfPath: config.pdfPath,
      outputDir: config.outputDir,
      runDir: config.runDir,
      provider: config.provider,
      ollamaUrl: config.ollamaUrl,
      model: config.model,
      ggufModelPath: config.ggufModelPath,
      windowSize: config.windowSize,
      overlap: config.overlap,
      extractOnly: config.extractOnly,
      skipRevision: config.skipRevision,
      skipExtraction: config.skipExtraction,
      revisionOnly: config.revisionOnly
    };
  }

  async function startRun() {
    const payload = buildRunPayload();

    setLogs([]);
    setEvents([]);
    setExitInfo(null);
    setStatusEvent(null);
    setPhases(DEFAULT_PHASES);
    setArtifacts([]);
    setSummary(null);

    const result = await window.api.startRun(payload);
    if (!result.ok) {
      addNotice("error", result.error || "Failed to start run");
      setIsRunning(false);
      return;
    }

    addNotice("info", "Run started");
    setIsRunning(true);
  }

  async function stopRun(force = false) {
    await window.api.stopRun({ force });
    addNotice(
      force ? "warning" : "info",
      force ? "Force stop sent" : "Stop requested"
    );
  }

  function clearRunStatus() {
    if (isRunning) {
      addNotice("warning", "Stop the run before clearing status");
      return;
    }
    setExitInfo(null);
    setStatusEvent(null);
    setPhases(DEFAULT_PHASES);
    setEvents([]);
    addNotice("info", "Run status cleared");
  }

  async function handleSelectPdf() {
    const path = await window.api.selectPdf();
    if (path) {
      updateConfig("pdfPath", path);
    }
  }

  async function handleSelectOutputDir() {
    const path = await window.api.selectDirectory();
    if (path) {
      updateConfig("outputDir", path);
    }
  }

  async function handleSelectRunDir() {
    const path = await window.api.selectDirectory();
    if (path) {
      updateConfig("runDir", path);
    }
  }

  async function openRunDir() {
    if (!config.runDir) {
      addNotice("warning", "No run directory available");
      return;
    }
    await window.api.openPath(config.runDir);
  }

  async function refreshArtifacts(targetDir: string) {
    const items = await window.api.listArtifacts(targetDir);
    setArtifacts(items);
  }

  async function refreshSummary(targetDir: string) {
    const data = await window.api.readSummary(targetDir);
    setSummary(data as SummaryPayload | null);
  }

  async function saveRunHistory(status: string) {
    if (!config.runDir) {
      return;
    }
    const policyName = extractFileName(config.pdfPath);
    const entry: RunHistoryEntry = {
      runDir: config.runDir,
      policyName,
      model: config.model,
      provider: config.provider,
      status,
      tags: [],
      notes: ""
    };
    const updated = await window.api.historyAdd(entry);
    setRunHistory(updated || []);
  }

  async function loadRunData(runDir: string) {
    if (!runDir) {
      setRunData(null);
      return;
    }

    const sectionsPath = joinPath(runDir, "sections_output.json");
    const masterListPath = joinPath(runDir, "master_list.json");
    const assessmentsPath = joinPath(runDir, "assessments.json");
    const summaryPath = joinPath(runDir, "summary.json");
    const revisionReportPath = joinPath(runDir, "revision_report.md");
    const revisedPolicyPath = joinPath(runDir, "revised_policy.md");
    const roadmapPath = joinPath(runDir, "improvement_roadmap.md");

    const [sectionsRaw, masterListRaw, assessmentsRaw, summaryRaw, revisionReportRaw, revisedPolicyRaw, roadmapRaw] =
      await Promise.all([
        window.api.readJson(sectionsPath),
        window.api.readJson(masterListPath),
        window.api.readJson(assessmentsPath),
        window.api.readJson(summaryPath),
        window.api.readText(revisionReportPath, 1_500_000),
        window.api.readText(revisedPolicyPath, 1_500_000),
        window.api.readText(roadmapPath, 1_500_000)
      ]);

    const sections = Array.isArray(sectionsRaw) ? (sectionsRaw as PolicySection[]) : [];
    const masterList = Array.isArray(masterListRaw) ? (masterListRaw as MasterListEntry[]) : [];
    const assessments = (assessmentsRaw || {}) as Record<string, SubcategoryAssessment[]>;
    const summaryPayload = (summaryRaw || null) as SummaryPayload | null;

    const revisionReport = revisionReportRaw ? parseRevisionReport(revisionReportRaw) : null;
    const roadmap = roadmapRaw ? parseRoadmap(roadmapRaw) : null;

    setRunData({
      sections,
      masterList,
      assessments,
      summary: summaryPayload,
      revisionReport,
      revisedPolicy: revisedPolicyRaw || null,
      roadmap
    });

    if (!selectedSection && sections.length > 0) {
      setSelectedSection(sections[0].number);
    }
  }

  async function testOllama() {
    const result = await window.api.testOllama(config.ollamaUrl);
    if (result.ok) {
      setOllamaStatus("ok");
      setOllamaModels(result.models || []);
      setOllamaLatency(result.durationMs || null);
      addNotice("success", "Ollama is reachable");
      return;
    }
    setOllamaStatus("error");
    setOllamaModels([]);
    setOllamaLatency(result.durationMs || null);
    addNotice("error", result.error || "Ollama check failed");
  }

  async function loadDebugLog() {
    if (!config.runDir) {
      addNotice("warning", "No run directory selected");
      return;
    }
    const logPath = joinPath(config.runDir, "debug.log");
    const content = await window.api.readText(logPath, 1_500_000);
    setDebugLog(content || "No debug log found.");
  }

  async function scanRuns() {
    const baseDir = config.outputDir || "gap_analysis_reports";
    const results = await window.api.historyScan(baseDir);
    if (!results) {
      return;
    }
    const normalized = results.filter(Boolean) as RunHistoryEntry[];
    if (normalized.length === 0) {
      addNotice("warning", "No runs found in output directory");
      return;
    }
    setRunHistory((prev) => mergeHistory(prev, normalized));
  }

  function selectRun(entry: RunHistoryEntry) {
    updateConfig("runDir", entry.runDir);
    setActiveView("dashboard");
  }

  function updateHistoryEntry(entry: RunHistoryEntry, updates: Partial<RunHistoryEntry>) {
    const next = { ...entry, ...updates } as RunHistoryEntry;
    window.api.historyUpdate(next).then((updated) => {
      if (updated) {
        setRunHistory(updated);
      }
    });
  }

  const validation = useMemo(() => {
    const issues = [] as string[];

    if (config.revisionOnly) {
      if (!config.runDir) {
        issues.push("Run directory is required for revision-only mode");
      }
    } else {
      if (!config.pdfPath) {
        issues.push("PDF policy file is required");
      }
      if (config.skipExtraction && !config.runDir) {
        issues.push("Run directory is required when skipping extraction");
      }
    }

    if (config.provider === "ollama") {
      if (!config.ollamaUrl) {
        issues.push("Ollama URL is required");
      }
    } else if (!config.ggufModelPath) {
      issues.push("GGUF model path is required for local mode");
    }

    return issues;
  }, [config]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">GH</div>
          <div>
            <div className="brand-title">Gap Hunter Studio</div>
            <div className="brand-subtitle">Policy gap analysis</div>
          </div>
        </div>

        <nav className="nav">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="nav-group">
              <div className="nav-group-title">{group.label}</div>
              {group.items.map((item) => (
                <button
                  key={item}
                  className={`nav-button ${activeView === item ? "active" : ""}`}
                  onClick={() => setActiveView(item)}
                >
                  <span className="nav-dot" />
                  <span>{VIEW_META[item].title}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className={`status-pill ${isRunning ? "live" : "idle"}`}>
            <span className="status-dot" />
            <span>{runStateLabel}</span>
          </div>
          <div className="sidebar-meta">
            <span>Provider: {config.provider}</span>
            <span>Model: {config.model}</span>
          </div>
        </div>
      </aside>

      <div className="content">
        <header className="topbar">
          <div>
            <span className="kicker">{viewMeta.subtitle}</span>
            <h1>{viewMeta.title}</h1>
          </div>
          <div className="top-actions">
            <button
              className="primary"
              onClick={startRun}
              disabled={isRunning || validation.length > 0}
            >
              Start run
            </button>
            <button className="ghost" onClick={() => stopRun(false)} disabled={!isRunning}>
              Stop
            </button>
            <button className="danger" onClick={() => stopRun(true)} disabled={!isRunning}>
              Force stop
            </button>
          </div>
        </header>

        <main className="page">
          {activeView === "dashboard" && (
            <div className="grid">
              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Run status</h2>
                    <span className="subtle">Pipeline state and progress</span>
                  </div>
                </div>
                <div className="stat-grid">
                  <div className="stat">
                    <span>State</span>
                    <strong>{runStateLabel}</strong>
                  </div>
                  <div className="stat">
                    <span>PID</span>
                    <strong>{statusEvent?.pid ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Exit</span>
                    <strong>{exitInfo?.code ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Progress</span>
                    <strong>{progressPct}%</strong>
                  </div>
                </div>
                <div className="progress">
                  <div className="progress-bar" style={{ width: `${progressPct}%` }} />
                </div>
                <div className="inline-actions">
                  <button className="ghost" onClick={openRunDir}>
                    Open run folder
                  </button>
                  <button className="ghost" onClick={() => setActiveView("run")}>Edit run</button>
                </div>
                <div className="note">Run directory: {config.runDir || "-"}</div>
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>LLM health</h2>
                    <span className="subtle">Provider readiness</span>
                  </div>
                  {config.provider === "ollama" && (
                    <button className="ghost" onClick={testOllama}>
                      Test
                    </button>
                  )}
                </div>
                <div className="stat-grid">
                  <div className="stat">
                    <span>Provider</span>
                    <strong>{config.provider}</strong>
                  </div>
                  <div className="stat">
                    <span>Model</span>
                    <strong>{config.model}</strong>
                  </div>
                  <div className="stat">
                    <span>Status</span>
                    <strong>
                      {config.provider === "ollama" ? ollamaStatus : "local"}
                    </strong>
                  </div>
                  <div className="stat">
                    <span>Latency</span>
                    <strong>{ollamaLatency ? `${ollamaLatency} ms` : "-"}</strong>
                  </div>
                </div>
                {config.provider === "ollama" ? (
                  <div className={`status-chip ${ollamaStatus}`}>
                    <span>Ollama</span>
                    <strong>
                      {ollamaStatus === "ok"
                        ? "Connected"
                        : ollamaStatus === "error"
                        ? "Error"
                        : "Unknown"}
                    </strong>
                  </div>
                ) : (
                  <div className="note">GGUF path: {config.ggufModelPath || "-"}</div>
                )}
                {ollamaModels.length > 0 && (
                  <div className="chips">
                    {ollamaModels.slice(0, 5).map((model) => (
                      <span key={model} className="chip">
                        {model}
                      </span>
                    ))}
                  </div>
                )}
              </section>

              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Phases</h2>
                    <span className="subtle">Stage progression</span>
                  </div>
                </div>
                <div className="phase-list">
                  {phases.map((phase) => (
                    <div key={phase.id} className={`phase ${phase.status}`}>
                      <span>{phase.label}</span>
                      <small>{phase.status}</small>
                    </div>
                  ))}
                </div>
              </section>

              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Quick stats</h2>
                    <span className="subtle">Run summary</span>
                  </div>
                </div>
                <div className="stat-grid compact">
                  <div className="stat">
                    <span>Functions</span>
                    <strong>{summaryCounts.functions}</strong>
                  </div>
                  <div className="stat">
                    <span>Artifacts</span>
                    <strong>{artifacts.length}</strong>
                  </div>
                  <div className="stat">
                    <span>Logs</span>
                    <strong>{logs.length}</strong>
                  </div>
                  <div className="stat">
                    <span>Output dir</span>
                    <strong>{config.outputDir || "default"}</strong>
                  </div>
                </div>
                <button className="ghost" onClick={() => setActiveView("artifacts")}>
                  View artifacts
                </button>
              </section>

              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Artifacts preview</h2>
                    <span className="subtle">Recent outputs</span>
                  </div>
                  <button
                    className="ghost"
                    onClick={() => config.runDir && refreshArtifacts(config.runDir)}
                  >
                    Refresh
                  </button>
                </div>
                {artifactsPreview.length === 0 ? (
                  <div className="empty">No artifacts yet.</div>
                ) : (
                  <div className="artifact-list">
                    {artifactsPreview.map((artifact) => (
                      <div key={artifact.path} className="artifact">
                        <div>
                          <strong>{artifact.name}</strong>
                          <span>{formatBytes(artifact.size)}</span>
                        </div>
                        <button
                          className="ghost"
                          onClick={() => window.api.openPath(artifact.path)}
                        >
                          Open
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Recent logs</h2>
                    <span className="subtle">Latest telemetry lines</span>
                  </div>
                  <button className="ghost" onClick={() => setActiveView("logs")}>
                    View logs
                  </button>
                </div>
                <div className="log-panel compact">
                  {recentLogs.length === 0 ? (
                    <div className="empty">No log activity yet.</div>
                  ) : (
                    recentLogs.map((entry, index) => (
                      <div
                        key={`${entry.time}-${index}`}
                        className={`log-line ${entry.level.toLowerCase()}`}
                      >
                        <span className="log-time">{entry.time}</span>
                        <span className="log-level">{entry.level}</span>
                        <span className="log-message">
                          <strong>{entry.logger}</strong> {entry.message}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          )}

          {activeView === "run" && (
            <div className="grid">
              <section className="card span-7">
                <div className="card-header">
                  <div>
                    <h2>Inputs</h2>
                    <span className="subtle">Policy and run settings</span>
                  </div>
                </div>

                <div className="field-group">
                  <label>Policy PDF</label>
                  <div className="field-row">
                    <input
                      type="text"
                      value={config.pdfPath}
                      placeholder="Select a policy PDF"
                      onChange={(event) => updateConfig("pdfPath", event.target.value)}
                      disabled={config.revisionOnly}
                    />
                    <button
                      className="ghost"
                      onClick={handleSelectPdf}
                      disabled={config.revisionOnly}
                    >
                      Browse
                    </button>
                  </div>
                </div>

                <div className="field-group">
                  <label>Output directory</label>
                  <div className="field-row">
                    <input
                      type="text"
                      value={config.outputDir}
                      placeholder="Default: gap_analysis_reports"
                      onChange={(event) => updateConfig("outputDir", event.target.value)}
                    />
                    <button className="ghost" onClick={handleSelectOutputDir}>
                      Choose
                    </button>
                  </div>
                </div>

                <div className="field-group">
                  <label>Run directory (reuse)</label>
                  <div className="field-row">
                    <input
                      type="text"
                      value={config.runDir}
                      placeholder="Required for revision-only or skip-extraction"
                      onChange={(event) => updateConfig("runDir", event.target.value)}
                    />
                    <button className="ghost" onClick={handleSelectRunDir}>
                      Select
                    </button>
                  </div>
                </div>

                <div className="split">
                  <div className="field-group">
                    <label>Window size</label>
                    <input
                      type="number"
                      value={config.windowSize}
                      onChange={(event) => updateConfig("windowSize", Number(event.target.value))}
                      min={20}
                      max={200}
                    />
                  </div>
                  <div className="field-group">
                    <label>Overlap</label>
                    <input
                      type="number"
                      value={config.overlap}
                      onChange={(event) => updateConfig("overlap", Number(event.target.value))}
                      min={0}
                      max={100}
                    />
                  </div>
                </div>

                <div className="toggle-grid">
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={config.extractOnly}
                      onChange={(event) => updateConfig("extractOnly", event.target.checked)}
                    />
                    <span>Extract only</span>
                  </label>
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={config.skipExtraction}
                      onChange={(event) => updateConfig("skipExtraction", event.target.checked)}
                    />
                    <span>Skip extraction</span>
                  </label>
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={config.skipRevision}
                      onChange={(event) => updateConfig("skipRevision", event.target.checked)}
                    />
                    <span>Skip revision</span>
                  </label>
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={config.revisionOnly}
                      onChange={(event) => updateConfig("revisionOnly", event.target.checked)}
                    />
                    <span>Revision only</span>
                  </label>
                </div>
              </section>

              <section className="card span-5">
                <div className="card-header">
                  <div>
                    <h2>Execution</h2>
                    <span className="subtle">Run controls and validation</span>
                  </div>
                </div>

                <div className="stat-grid compact">
                  <div className="stat">
                    <span>Status</span>
                    <strong>{runStateLabel}</strong>
                  </div>
                  <div className="stat">
                    <span>PID</span>
                    <strong>{statusEvent?.pid ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Exit</span>
                    <strong>{exitInfo?.code ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Progress</span>
                    <strong>{progressPct}%</strong>
                  </div>
                </div>

                {validation.length > 0 && (
                  <div className="alert warning">
                    <strong>Ready check</strong>
                    <ul>
                      {validation.map((issue) => (
                        <li key={issue}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="actions">
                  <button
                    className="primary"
                    onClick={startRun}
                    disabled={isRunning || validation.length > 0}
                  >
                    Start run
                  </button>
                  <button className="ghost" onClick={() => stopRun(false)} disabled={!isRunning}>
                    Stop
                  </button>
                  <button className="danger" onClick={() => stopRun(true)} disabled={!isRunning}>
                    Force stop
                  </button>
                  <button className="ghost" onClick={clearRunStatus} disabled={!canClearStatus}>
                    Clear status
                  </button>
                  <button className="ghost" onClick={openRunDir}>
                    Open run folder
                  </button>
                </div>
                <div className="note">Run directory: {config.runDir || "-"}</div>
              </section>
            </div>
          )}

          {activeView === "logs" && (
            <div className="grid">
              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Live logs</h2>
                    <span className="subtle">Streaming telemetry</span>
                  </div>
                  <div className="inline-actions">
                    <button className="ghost" onClick={() => setLogs([])}>Clear</button>
                  </div>
                </div>

                <div className="log-toolbar">
                  <div className="log-filters">
                    {Object.keys(levelFilter).map((level) => (
                      <button
                        key={level}
                        className={
                          levelFilter[level as keyof typeof levelFilter]
                            ? "pill-btn active"
                            : "pill-btn"
                        }
                        onClick={() =>
                          setLevelFilter((prev) => ({
                            ...prev,
                            [level]: !prev[level as keyof typeof levelFilter]
                          }))
                        }
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                  <div className="log-tools">
                    <input
                      type="text"
                      placeholder="Search logs"
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                    />
                    <label className="toggle compact">
                      <input
                        type="checkbox"
                        checked={autoScroll}
                        onChange={(event) => setAutoScroll(event.target.checked)}
                      />
                      <span>Auto-scroll</span>
                    </label>
                  </div>
                </div>

                <div className="log-panel">
                  {filteredLogs.length === 0 ? (
                    <div className="empty">No log activity yet.</div>
                  ) : (
                    filteredLogs.map((entry, index) => (
                      <div
                        key={`${entry.time}-${index}`}
                        className={`log-line ${entry.level.toLowerCase()}`}
                      >
                        <span className="log-time">{entry.time}</span>
                        <span className="log-level">{entry.level}</span>
                        <span className="log-message">
                          <strong>{entry.logger}</strong> {entry.message}
                        </span>
                      </div>
                    ))
                  )}
                  <div ref={logEndRef} />
                </div>

                <div className="timeline">
                  {events.length === 0 ? (
                    <div className="empty">No structured events yet.</div>
                  ) : (
                    events.slice(-12).map((event, index) => (
                      <div key={`${event.name}-${index}`} className="timeline-item">
                        <div className="timeline-dot" />
                        <div>
                          <strong>{event.name}</strong>
                          <div className="subtle">{event.timestamp || ""}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          )}

          {activeView === "artifacts" && (
            <div className="grid">
              <section className="card span-8">
                <div className="card-header">
                  <div>
                    <h2>Artifacts</h2>
                    <span className="subtle">Run outputs and files</span>
                  </div>
                  <div className="inline-actions">
                    <button
                      className="ghost"
                      onClick={() => config.runDir && refreshArtifacts(config.runDir)}
                    >
                      Refresh
                    </button>
                    <button className="ghost" onClick={openRunDir}>
                      Open folder
                    </button>
                  </div>
                </div>
                <div className="artifact-list">
                  {artifacts.length === 0 ? (
                    <div className="empty">No artifacts yet.</div>
                  ) : (
                    artifacts.map((artifact) => (
                      <div key={artifact.path} className="artifact">
                        <div>
                          <strong>{artifact.name}</strong>
                          <span>{formatBytes(artifact.size)}</span>
                        </div>
                        <button
                          className="ghost"
                          onClick={() => window.api.openPath(artifact.path)}
                        >
                          Open
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </section>

              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Run insights</h2>
                    <span className="subtle">Summary stats</span>
                  </div>
                  <button
                    className="ghost"
                    onClick={() => config.runDir && refreshSummary(config.runDir)}
                  >
                    Refresh summary
                  </button>
                </div>
                <div className="stat-grid compact">
                  <div className="stat">
                    <span>Functions</span>
                    <strong>{summaryCounts.functions}</strong>
                  </div>
                  <div className="stat">
                    <span>Reports</span>
                    <strong>{summaryCounts.reports}</strong>
                  </div>
                  <div className="stat">
                    <span>Exit</span>
                    <strong>{exitInfo?.code ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Log entries</span>
                    <strong>{logs.length}</strong>
                  </div>
                </div>
                <div className="note">Run directory: {config.runDir || "-"}</div>
              </section>
            </div>
          )}

          {activeView === "settings" && (
            <div className="grid">
              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>LLM provider</h2>
                    <span className="subtle">Connectivity and model selection</span>
                  </div>
                </div>

                <div className="provider-switch">
                  <button
                    className={config.provider === "ollama" ? "pill-btn active" : "pill-btn"}
                    onClick={() => updateConfig("provider", "ollama")}
                  >
                    Ollama
                  </button>
                  <button
                    className={config.provider === "llamacpp" ? "pill-btn active" : "pill-btn"}
                    onClick={() => updateConfig("provider", "llamacpp")}
                  >
                    Local GGUF
                  </button>
                </div>

                <div className="field-group">
                  <label>Model name</label>
                  <input
                    type="text"
                    value={config.model}
                    onChange={(event) => updateConfig("model", event.target.value)}
                  />
                </div>

                {config.provider === "ollama" ? (
                  <>
                    <div className="field-group">
                      <label>Ollama URL</label>
                      <div className="field-row">
                        <input
                          type="text"
                          value={config.ollamaUrl}
                          onChange={(event) => updateConfig("ollamaUrl", event.target.value)}
                        />
                        <button className="ghost" onClick={testOllama}>
                          Test
                        </button>
                      </div>
                    </div>

                    <div className={`status-chip ${ollamaStatus}`}>
                      <span>Ollama status</span>
                      <strong>
                        {ollamaStatus === "ok"
                          ? "Connected"
                          : ollamaStatus === "error"
                          ? "Error"
                          : "Unknown"}
                      </strong>
                    </div>

                    {ollamaModels.length > 0 && (
                      <div className="chips">
                        {ollamaModels.slice(0, 8).map((model) => (
                          <span key={model} className="chip">
                            {model}
                          </span>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="field-group">
                    <label>GGUF model path</label>
                    <input
                      type="text"
                      value={config.ggufModelPath}
                      onChange={(event) => updateConfig("ggufModelPath", event.target.value)}
                      placeholder="/path/to/model.gguf"
                    />
                    <p className="hint">Local mode requires a GGUF model on disk.</p>
                  </div>
                )}
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Preferences</h2>
                    <span className="subtle">UI and telemetry</span>
                  </div>
                </div>

                <div className="field-group">
                  <label>Log retention (lines)</label>
                  <input
                    type="number"
                    min={500}
                    max={5000}
                    value={config.logRetention}
                    onChange={(event) => updateConfig("logRetention", Number(event.target.value))}
                  />
                </div>

                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.autoRefresh}
                    onChange={(event) => updateConfig("autoRefresh", event.target.checked)}
                  />
                  <span>Auto refresh run data</span>
                </label>

                <div className="stat-grid compact">
                  <div className="stat">
                    <span>Process</span>
                    <strong>{statusEvent?.state || "idle"}</strong>
                  </div>
                  <div className="stat">
                    <span>PID</span>
                    <strong>{statusEvent?.pid ?? "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Logs</span>
                    <strong>{logs.length}</strong>
                  </div>
                  <div className="stat">
                    <span>Latency</span>
                    <strong>{ollamaLatency ? `${ollamaLatency} ms` : "-"}</strong>
                  </div>
                </div>
              </section>
            </div>
          )}

          {activeView === "evidence" && (
            <div className="grid">
              <section className="card span-3">
                <div className="card-header">
                  <div>
                    <h2>Sections</h2>
                    <span className="subtle">Policy content</span>
                  </div>
                </div>
                <div className="list">
                  {(runData?.sections || []).map((section) => (
                    <button
                      key={section.number}
                      className={`list-item ${selectedSection === section.number ? "active" : ""}`}
                      onClick={() => setSelectedSection(section.number)}
                    >
                      <span>{section.number}</span>
                      <strong>{section.title}</strong>
                    </button>
                  ))}
                </div>
              </section>

              <section className="card span-5">
                <div className="card-header">
                  <div>
                    <h2>Section detail</h2>
                    <span className="subtle">Original policy text</span>
                  </div>
                </div>
                <div className="scroll-pane">
                  {selectedSection ? (
                    <div className="text-block">
                      <h3>
                        Section {selectedSection}: {getSectionTitle(runData?.sections, selectedSection)}
                      </h3>
                      <p>
                        {getSectionContent(runData?.sections, selectedSection) ||
                          "No content available."}
                      </p>
                    </div>
                  ) : (
                    <div className="empty">Select a section to view details.</div>
                  )}
                </div>
              </section>

              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Evidence matches</h2>
                    <span className="subtle">Mapped subcategories</span>
                  </div>
                </div>
                <div className="field-group">
                  <label>Status filter</label>
                  <select
                    value={evidenceStatus}
                    onChange={(event) => setEvidenceStatus(event.target.value as AssessmentStatus | "All")}
                  >
                    <option value="All">All</option>
                    <option value="Addressed">Addressed</option>
                    <option value="Partially Addressed">Partially Addressed</option>
                    <option value="Not Addressed">Not Addressed</option>
                    <option value="Out of Scope">Out of Scope</option>
                  </select>
                </div>
                <div className="list">
                  {evidenceForSection.length === 0 ? (
                    <div className="empty">No evidence mapped to this section.</div>
                  ) : (
                    evidenceForSection.map((item) => (
                      <div key={item.subcategory_id} className={`evidence-card ${statusClass(item.status)}`}>
                        <div className="pill">{item.subcategory_id}</div>
                        <strong>{item.title}</strong>
                        <span>{item.status}</span>
                        <p>{truncate(item.evidence, 160)}</p>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          )}

          {activeView === "matrix" && (
            <div className="grid">
              <section className="card span-4">
                <div className="card-header">
                  <div>
                    <h2>Functions</h2>
                    <span className="subtle">Coverage by function</span>
                  </div>
                </div>
                <div className="list">
                  {NIST_FUNCTIONS.map((name) => (
                    <button
                      key={name}
                      className={`list-item ${matrixFunction === name ? "active" : ""}`}
                      onClick={() => setMatrixFunction(name)}
                    >
                      <span>{name}</span>
                      <strong>{getFunctionSummary(runData?.assessments, name)}</strong>
                    </button>
                  ))}
                </div>
              </section>

              <section className="card span-8">
                <div className="card-header">
                  <div>
                    <h2>{matrixFunction} Coverage</h2>
                    <span className="subtle">Subcategory matrix</span>
                  </div>
                </div>
                {matrixAssessments.length === 0 ? (
                  <div className="empty">No assessments loaded yet.</div>
                ) : (
                  <div className="matrix-grid">
                    {matrixAssessments.map((assessment) => (
                      <button
                        key={assessment.subcategory_id}
                        className={`matrix-chip ${statusClass(assessment.status)}`}
                        onClick={() => setSelectedAssessment(assessment)}
                      >
                        <span>{assessment.subcategory_id}</span>
                        <small>{assessment.status}</small>
                      </button>
                    ))}
                  </div>
                )}
                {selectedAssessment && (
                  <div className="detail-card">
                    <div className="pill">{selectedAssessment.subcategory_id}</div>
                    <h3>{selectedAssessment.title}</h3>
                    <p><strong>Status:</strong> {selectedAssessment.status}</p>
                    <p><strong>Evidence:</strong> {selectedAssessment.evidence}</p>
                    <p><strong>Gap:</strong> {selectedAssessment.gap}</p>
                    <p><strong>Recommendation:</strong> {selectedAssessment.recommendation}</p>
                  </div>
                )}
              </section>
            </div>
          )}

          {activeView === "revision" && (
            <div className="grid">
              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Revision report</h2>
                    <span className="subtle">Change rationale and diff preview</span>
                  </div>
                </div>
                {runData?.revisionReport ? (
                  <div className="stat-grid">
                    <div className="stat">
                      <span>Gaps addressed</span>
                      <strong>{runData.revisionReport.totalGaps}</strong>
                    </div>
                    <div className="stat">
                      <span>Sections modified</span>
                      <strong>{runData.revisionReport.modifiedSections}</strong>
                    </div>
                    <div className="stat">
                      <span>New sections</span>
                      <strong>{runData.revisionReport.newSections}</strong>
                    </div>
                    <div className="stat">
                      <span>Changes</span>
                      <strong>{runData.revisionReport.changes.length}</strong>
                    </div>
                  </div>
                ) : (
                  <div className="empty">No revision report found.</div>
                )}
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Original policy</h2>
                    <span className="subtle">Extracted content</span>
                  </div>
                </div>
                <div className="policy-panel">
                  <pre>{buildOriginalPolicy(runData?.sections || [])}</pre>
                </div>
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Revised policy</h2>
                    <span className="subtle">Generated output</span>
                  </div>
                </div>
                <div className="policy-panel">
                  <pre>{runData?.revisedPolicy || "No revised policy found."}</pre>
                </div>
              </section>

              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Change rationale</h2>
                    <span className="subtle">Revision report details</span>
                  </div>
                </div>
                {runData?.revisionReport?.changes.length ? (
                  <div className="change-grid">
                    {runData.revisionReport.changes.map((change) => (
                      <div key={change.id} className="change-card">
                        <div className="pill">{change.id}</div>
                        <strong>{change.action}</strong>
                        <span>{change.section}</span>
                        <p>{change.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty">No change entries available.</div>
                )}
              </section>
            </div>
          )}

          {activeView === "roadmap" && (
            <div className="grid">
              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Roadmap overview</h2>
                    <span className="subtle">Priority execution plan</span>
                  </div>
                </div>
                {runData?.roadmap ? (
                  <p>{runData.roadmap.executiveSummary}</p>
                ) : (
                  <div className="empty">No roadmap available for this run.</div>
                )}
              </section>

              {runData?.roadmap?.tiers.map((tier) => (
                <section key={tier.tierName} className="card span-6">
                  <div className="card-header">
                    <div>
                      <h2>{tier.tierName}</h2>
                      <span className="subtle">{tier.rationale}</span>
                    </div>
                  </div>
                  <div className="roadmap-list">
                    {tier.items.map((item) => (
                      <div key={item.title} className="roadmap-item">
                        <strong>{item.title}</strong>
                        <span>NIST: {item.nistReference || "-"}</span>
                        <p>{item.description}</p>
                        <div className="roadmap-meta">
                          <span>Owner: {item.responsible}</span>
                          <span>Effort: {item.effort}</span>
                        </div>
                        <div className="note">Success: {item.successCriteria}</div>
                        <div className="note">Dependencies: {item.dependencies}</div>
                      </div>
                    ))}
                  </div>
                </section>
              ))}

              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Missing policy documents</h2>
                    <span className="subtle">Templates to produce</span>
                  </div>
                </div>
                {runData?.roadmap?.missingDocs.length ? (
                  <ul className="doc-list">
                    {runData.roadmap.missingDocs.map((doc) => (
                      <li key={doc}>{doc}</li>
                    ))}
                  </ul>
                ) : (
                  <div className="empty">No missing document list found.</div>
                )}
              </section>
            </div>
          )}

          {activeView === "library" && (
            <div className="grid">
              <section className="card span-5">
                <div className="card-header">
                  <div>
                    <h2>Run library</h2>
                    <span className="subtle">Saved runs and tags</span>
                  </div>
                  <button className="ghost" onClick={scanRuns}>
                    Scan output dir
                  </button>
                </div>
                <input
                  type="text"
                  placeholder="Search runs"
                  value={librarySearch}
                  onChange={(event) => setLibrarySearch(event.target.value)}
                />
                <div className="list">
                  {runLibraryFiltered.length === 0 ? (
                    <div className="empty">No saved runs yet.</div>
                  ) : (
                    runLibraryFiltered.map((entry) => (
                      <button
                        key={entry.runDir}
                        className={`list-item ${entry.runDir === config.runDir ? "active" : ""}`}
                        onClick={() => selectRun(entry)}
                      >
                        <span>{entry.policyName || "Policy"}</span>
                        <strong>{entry.runDir}</strong>
                        <small>{entry.status || "-"}</small>
                      </button>
                    ))
                  )}
                </div>
              </section>

              <section className="card span-7">
                <div className="card-header">
                  <div>
                    <h2>Run details</h2>
                    <span className="subtle">Tags and notes</span>
                  </div>
                </div>
                {config.runDir ? (
                  <RunDetails
                    entry={runHistory.find((item) => item.runDir === config.runDir) || null}
                    onUpdate={updateHistoryEntry}
                    onOpen={openRunDir}
                  />
                ) : (
                  <div className="empty">Select a run to view details.</div>
                )}
              </section>
            </div>
          )}

          {activeView === "diagnostics" && (
            <div className="grid">
              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Environment snapshot</h2>
                    <span className="subtle">System and runtime info</span>
                  </div>
                </div>
                <div className="stat-grid compact">
                  <div className="stat">
                    <span>App</span>
                    <strong>{appInfo?.appVersion || "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Electron</span>
                    <strong>{appInfo?.electron || "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Node</span>
                    <strong>{appInfo?.node || "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Platform</span>
                    <strong>{appInfo?.platform || "-"}</strong>
                  </div>
                </div>
                <div className="note">Active run: {config.runDir || "-"}</div>
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>Resource monitor</h2>
                    <span className="subtle">App and backend usage</span>
                  </div>
                </div>
                <div className="stat-grid compact">
                  <div className="stat">
                    <span>App RSS</span>
                    <strong>{processStats?.app?.rssMb ? `${processStats.app.rssMb.toFixed(1)} MB` : "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Heap used</span>
                    <strong>{processStats?.app?.heapUsedMb ? `${processStats.app.heapUsedMb.toFixed(1)} MB` : "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Backend CPU</span>
                    <strong>{processStats?.backend?.cpuPercent != null ? `${processStats.backend.cpuPercent.toFixed(1)}%` : "-"}</strong>
                  </div>
                  <div className="stat">
                    <span>Backend memory</span>
                    <strong>{processStats?.backend?.memoryMb != null ? `${processStats.backend.memoryMb.toFixed(1)} MB` : "-"}</strong>
                  </div>
                </div>
                <div className="note">Last updated: {processStats?.timestamp || "-"}</div>
              </section>

              <section className="card span-12">
                <div className="card-header">
                  <div>
                    <h2>Debug log</h2>
                    <span className="subtle">Backend debug trace</span>
                  </div>
                  <button className="ghost" onClick={loadDebugLog}>
                    Load debug log
                  </button>
                </div>
                <div className="policy-panel">
                  <pre>{debugLog || "No debug log loaded."}</pre>
                </div>
              </section>
            </div>
          )}
        </main>
      </div>

      <div className="notice-stack">
        {notices.map((notice) => (
          <div key={notice.id} className={`notice ${notice.kind}`}>
            {notice.message}
          </div>
        ))}
      </div>
    </div>
  );
}

function RunDetails({
  entry,
  onUpdate,
  onOpen
}: {
  entry: RunHistoryEntry | null;
  onUpdate: (entry: RunHistoryEntry, updates: Partial<RunHistoryEntry>) => void;
  onOpen: () => void;
}) {
  const [tags, setTags] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!entry) {
      setTags("");
      setNotes("");
      return;
    }
    setTags((entry.tags || []).join(", "));
    setNotes(entry.notes || "");
  }, [entry]);

  if (!entry) {
    return <div className="empty">Select a run to view details.</div>;
  }

  const handleSave = () => {
    const tagList = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
    onUpdate(entry, { tags: tagList, notes });
  };

  return (
    <div className="detail-block">
      <div className="note">Run directory: {entry.runDir}</div>
      <div className="stat-grid compact">
        <div className="stat">
          <span>Policy</span>
          <strong>{entry.policyName || "-"}</strong>
        </div>
        <div className="stat">
          <span>Model</span>
          <strong>{entry.model || "-"}</strong>
        </div>
        <div className="stat">
          <span>Status</span>
          <strong>{entry.status || "-"}</strong>
        </div>
        <div className="stat">
          <span>Provider</span>
          <strong>{entry.provider || "-"}</strong>
        </div>
      </div>

      <div className="field-group">
        <label>Tags</label>
        <input
          type="text"
          value={tags}
          onChange={(event) => setTags(event.target.value)}
          placeholder="e.g. priority, audit"
        />
      </div>

      <div className="field-group">
        <label>Notes</label>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={6}
        />
      </div>

      <div className="actions">
        <button className="primary" onClick={handleSave}>
          Save notes
        </button>
        <button className="ghost" onClick={onOpen}>
          Open folder
        </button>
      </div>
    </div>
  );
}

function joinPath(base: string, name: string) {
  if (!base) {
    return name;
  }
  const separator = base.includes("\\") ? "\\" : "/";
  return `${base.replace(/[\\/]+$/, "")}${separator}${name}`;
}

function extractFileName(pathValue: string) {
  if (!pathValue) {
    return "";
  }
  const parts = pathValue.split(/[\\/]/);
  return parts[parts.length - 1] || "";
}

function buildEvidenceMap(
  sections: PolicySection[],
  assessments: Record<string, SubcategoryAssessment[]>
) {
  const map: Record<string, SubcategoryAssessment[]> = {};
  sections.forEach((section) => {
    map[section.number] = [];
  });
  map.unmapped = [];

  Object.values(assessments)
    .flat()
    .forEach((assessment) => {
      const snippet = normalizeEvidence(assessment.evidence);
      if (!snippet) {
        return;
      }

      const snippetLower = snippet.toLowerCase();
      let matched = false;
      for (const section of sections) {
        const content = (section.content || "").toLowerCase();
        if (content.includes(snippetLower)) {
          map[section.number].push(assessment);
          matched = true;
        }
      }
      if (!matched) {
        map.unmapped.push(assessment);
      }
    });

  return map;
}

function normalizeEvidence(evidence: string) {
  if (!evidence) {
    return "";
  }
  const lowered = evidence.toLowerCase();
  if (
    lowered.includes("no relevant") ||
    lowered.includes("none found") ||
    lowered.includes("n/a")
  ) {
    return "";
  }
  return evidence.trim().slice(0, 120);
}

function getSectionTitle(sections: PolicySection[] | undefined, number: string | null) {
  if (!sections || !number) {
    return "";
  }
  return sections.find((s) => s.number === number)?.title || "";
}

function getSectionContent(sections: PolicySection[] | undefined, number: string | null) {
  if (!sections || !number) {
    return "";
  }
  return sections.find((s) => s.number === number)?.content || "";
}

function getFunctionSummary(
  assessments: Record<string, SubcategoryAssessment[]> | undefined,
  functionName: string
) {
  if (!assessments) {
    return "No data";
  }
  const items = assessments[functionName] || [];
  if (items.length === 0) {
    return "No data";
  }
  const inScope = items.filter((item) => item.status !== "Out of Scope");
  const notAddressed = inScope.filter((item) => item.status === "Not Addressed").length;
  const partial = inScope.filter((item) => item.status === "Partially Addressed").length;
  const addressed = inScope.filter((item) => item.status === "Addressed").length;
  return `${addressed} addressed, ${partial} partial, ${notAddressed} gaps`;
}

function buildOriginalPolicy(sections: PolicySection[]) {
  if (!sections.length) {
    return "No sections available.";
  }
  const lines: string[] = ["# Original Policy\n"];
  sections.forEach((section) => {
    lines.push(`## ${section.number}. ${section.title}`);
    lines.push(section.content || "");
    lines.push("\n---\n");
  });
  return lines.join("\n");
}

function parseRevisionReport(markdown: string): RevisionReport {
  const lines = markdown.split(/\r?\n/);
  let totalGaps = 0;
  let modifiedSections = 0;
  let newSections = 0;
  const changes: RevisionChange[] = [];
  let inChangesTable = false;

  for (const line of lines) {
    if (line.startsWith("- **Total gaps addressed**:")) {
      totalGaps = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }
    if (line.startsWith("- **Sections modified**:")) {
      modifiedSections = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }
    if (line.startsWith("- **New sections added**:")) {
      newSections = Number.parseInt(line.replace(/[^0-9]/g, ""), 10) || 0;
    }

    if (line.startsWith("## Changes")) {
      inChangesTable = true;
      continue;
    }
    if (inChangesTable && line.startsWith("## ")) {
      inChangesTable = false;
    }
    if (inChangesTable && line.startsWith("|") && !line.includes("---")) {
      const cells = line
        .split("|")
        .map((cell) => cell.trim())
        .filter(Boolean);
      if (cells.length >= 5) {
        changes.push({
          id: cells[1],
          action: cells[2],
          section: cells[3],
          description: cells[4]
        });
      }
    }
  }

  return { totalGaps, modifiedSections, newSections, changes };
}

function parseRoadmap(markdown: string): RoadmapData {
  const lines = markdown.split(/\r?\n/);
  let executiveSummary = "";
  const tiers: RoadmapTier[] = [];
  const missingDocs: string[] = [];

  let currentTier: RoadmapTier | null = null;
  let currentItem: RoadmapItem | null = null;
  let mode: "summary" | "tier" | "docs" | null = null;

  for (const line of lines) {
    if (line.startsWith("## Executive Summary")) {
      mode = "summary";
      continue;
    }
    if (line.startsWith("## Missing Policy Documents")) {
      mode = "docs";
      currentTier = null;
      currentItem = null;
      continue;
    }
    if (line.startsWith("## ") && !line.includes("Executive Summary")) {
      mode = "tier";
      const tierName = line.replace("## ", "").trim();
      currentTier = { tierName, rationale: "", items: [] };
      tiers.push(currentTier);
      continue;
    }
    if (mode === "tier" && line.startsWith("*")) {
      if (currentTier) {
        currentTier.rationale = line.replace(/\*/g, "").trim();
      }
      continue;
    }
    if (mode === "tier" && line.startsWith("### ")) {
      const title = line.replace("### ", "").trim();
      currentItem = {
        title,
        nistReference: "",
        description: "",
        responsible: "",
        effort: "",
        successCriteria: "",
        dependencies: ""
      };
      currentTier?.items.push(currentItem);
      continue;
    }
    if (mode === "tier" && line.startsWith("- **") && currentItem) {
      const [label, value] = line.split("**:");
      const cleanValue = (value || "").trim();
      if (label.includes("NIST Reference")) {
        currentItem.nistReference = cleanValue;
      } else if (label.includes("Description")) {
        currentItem.description = cleanValue;
      } else if (label.includes("Responsible")) {
        currentItem.responsible = cleanValue;
      } else if (label.includes("Effort")) {
        currentItem.effort = cleanValue;
      } else if (label.includes("Success Criteria")) {
        currentItem.successCriteria = cleanValue;
      } else if (label.includes("Dependencies")) {
        currentItem.dependencies = cleanValue;
      }
    }

    if (mode === "summary" && line.trim()) {
      executiveSummary += `${line.trim()} `;
    }

    if (mode === "docs" && /^\d+\./.test(line.trim())) {
      missingDocs.push(line.replace(/^\d+\./, "").trim());
    }
  }

  return {
    executiveSummary: executiveSummary.trim(),
    tiers,
    missingDocs
  };
}

function statusClass(status: AssessmentStatus) {
  switch (status) {
    case "Addressed":
      return "status-success";
    case "Partially Addressed":
      return "status-warning";
    case "Not Addressed":
      return "status-danger";
    default:
      return "status-muted";
  }
}

function formatBytes(bytes: number) {
  if (Number.isNaN(bytes)) {
    return "-";
  }
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kb = bytes / 1024;
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

function truncate(text: string, maxLength: number) {
  if (!text) {
    return "";
  }
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}

function mergeHistory(current: RunHistoryEntry[], incoming: RunHistoryEntry[]) {
  const map = new Map<string, RunHistoryEntry>();
  current.forEach((entry) => map.set(entry.runDir, entry));
  incoming.forEach((entry) => {
    const existing = map.get(entry.runDir);
    map.set(entry.runDir, { ...existing, ...entry });
  });
  return Array.from(map.values()).sort((a, b) =>
    (b.createdAt || "").localeCompare(a.createdAt || "")
  );
}

export default App;
