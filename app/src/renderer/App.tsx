import React, { useEffect, useMemo, useRef, useState } from "react";
import type { ExitEvent, LogEntry, StatusEvent } from "./types";

type Provider = "ollama" | "llamacpp";
type View = "dashboard" | "run" | "logs" | "artifacts" | "settings";

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

type SummaryPayload = {
  functions_analyzed?: string[];
  reports?: Record<string, unknown>;
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
  revisionOnly: false
};

const DEFAULT_PHASES: Phase[] = [
  { id: "extraction", label: "Extraction", status: "pending" },
  { id: "analysis", label: "Gap Analysis", status: "pending" },
  { id: "revision", label: "Policy Revision", status: "pending" },
  { id: "roadmap", label: "Roadmap", status: "pending" }
];

const VIEW_META: Record<View, { title: string; subtitle: string }> = {
  dashboard: {
    title: "Operations Dashboard",
    subtitle: "Overview"
  },
  run: {
    title: "Run Builder",
    subtitle: "Configure"
  },
  logs: {
    title: "Live Telemetry",
    subtitle: "Logs"
  },
  artifacts: {
    title: "Artifacts",
    subtitle: "Outputs"
  },
  settings: {
    title: "LLM Settings",
    subtitle: "Providers"
  }
};

const LOG_LIMIT = 2000;

function App() {
  const [activeView, setActiveView] = useState<View>("dashboard");
  const [config, setConfig] = useState<AppConfig>(DEFAULT_CONFIG);
  const [logs, setLogs] = useState<LogEntry[]>([]);
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
  const [notices, setNotices] = useState<Notice[]>([]);
  const [search, setSearch] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);
  const [levelFilter, setLevelFilter] = useState({
    INFO: true,
    WARNING: true,
    ERROR: true,
    DEBUG: false
  });

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
    const unsubLog = window.api.onLog((entry) => {
      setLogs((prev) => {
        const next = [...prev, entry];
        return next.length > LOG_LIMIT ? next.slice(-LOG_LIMIT) : next;
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
      }
    });

    return () => {
      unsubLog();
      unsubStatus();
      unsubExit();
    };
  }, []);

  useEffect(() => {
    if (!autoScroll) {
      return;
    }
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length, autoScroll]);

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

  async function startRun() {
    const payload = {
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

    setLogs([]);
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
    addNotice(force ? "warning" : "info", force ? "Force stop sent" : "Stop requested");
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

  async function testOllama() {
    const result = await window.api.testOllama(config.ollamaUrl);
    if (result.ok) {
      setOllamaStatus("ok");
      setOllamaModels(result.models || []);
      addNotice("success", "Ollama is reachable");
      return;
    }
    setOllamaStatus("error");
    setOllamaModels([]);
    addNotice("error", result.error || "Ollama check failed");
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

  const runStateLabel = isRunning ? "Running" : "Idle";
  const progressPct = Math.round(progress * 100);
  const viewMeta = VIEW_META[activeView];

  const navItems: Array<{ id: View; label: string }> = [
    { id: "dashboard", label: "Dashboard" },
    { id: "run", label: "Run" },
    { id: "logs", label: "Logs" },
    { id: "artifacts", label: "Artifacts" },
    { id: "settings", label: "Settings" }
  ];

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
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-button ${activeView === item.id ? "active" : ""}`}
              onClick={() => setActiveView(item.id)}
            >
              <span className="nav-dot" />
              <span>{item.label}</span>
            </button>
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
                <div className="note">
                  Run directory: {config.runDir || "-"}
                </div>
              </section>

              <section className="card span-6">
                <div className="card-header">
                  <div>
                    <h2>LLM health</h2>
                    <span className="subtle">Provider and model readiness</span>
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
                    <span>Reports</span>
                    <strong>{summaryCounts.reports}</strong>
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
                <button className="ghost" onClick={() => setActiveView("artifacts")}>View artifacts</button>
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
                  <button className="ghost" onClick={() => setActiveView("logs")}>View logs</button>
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
                    <button className="ghost" onClick={handleSelectPdf} disabled={config.revisionOnly}>
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
                    className={
                      config.provider === "ollama" ? "pill-btn active" : "pill-btn"
                    }
                    onClick={() => updateConfig("provider", "ollama")}
                  >
                    Ollama
                  </button>
                  <button
                    className={
                      config.provider === "llamacpp" ? "pill-btn active" : "pill-btn"
                    }
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
                    <h2>Runtime status</h2>
                    <span className="subtle">Process telemetry</span>
                  </div>
                </div>
                <div className="stat-grid">
                  <div className="stat">
                    <span>Process</span>
                    <strong>{statusEvent?.state || "idle"}</strong>
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
                    <span>Logs</span>
                    <strong>{logs.length}</strong>
                  </div>
                </div>
                <div className="note">Run directory: {config.runDir || "-"}</div>
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

export default App;