import React, { useEffect, useMemo, useRef, useState } from "react";
import type {
  AppInfo,
  BackendEvent,
  ExitEvent,
  LogEntry,
  ProcessStats,
  RunEvent,
  RunRecord,
  StatusEvent
} from "./types";
import type {
  AppConfig,
  AssessmentStatus,
  LogView,
  MasterListEntry,
  MatrixView,
  PolicySection,
  RevisionView,
  RoadmapView,
  RunData,
  RunStep,
  StatusCounts,
  SubcategoryAssessment,
  SummaryPayload,
  View
} from "./types/ui";
import { DEFAULT_CONFIG, DEFAULT_PHASES, NIST_FUNCTIONS, VIEW_META } from "./constants";
import {
  buildEvidenceMap,
  parseRevisionReport,
  parseRoadmap,
  summarizeAssessments
} from "./utils/analysis";
import { extractFileName } from "./utils/paths";
import Sidebar from "./components/Sidebar";
import CommandBar from "./components/CommandBar";
import MissionControlView from "./views/MissionControlView";
import DashboardView from "./views/DashboardView";
import RunBuilderView from "./views/RunBuilderView";
import LogsView from "./views/LogsView";
import ArtifactsView from "./views/ArtifactsView";
import SettingsView from "./views/SettingsView";
import EvidenceView from "./views/EvidenceView";
import MatrixViewComponent from "./views/MatrixView";
import RevisionViewComponent from "./views/RevisionView";
import RoadmapViewComponent from "./views/RoadmapView";
import LibraryView from "./views/LibraryView";
import DiagnosticsView from "./views/DiagnosticsView";
import DemoView from "./views/DemoView";
import HelpView from "./views/HelpView";

type Notice = {
  id: string;
  kind: "info" | "success" | "warning" | "error";
  message: string;
};

type DataState = {
  state: "idle" | "refreshing" | "fresh" | "stale" | "error";
  runId?: string | null;
  updatedAt?: string;
  error?: string;
};

function sortRunsByUpdatedAt(runs: RunRecord[]) {
  return [...runs].sort((a, b) =>
    (b.updatedAt || b.createdAt || "").localeCompare(a.updatedAt || a.createdAt || "")
  );
}

const RUN_STATUS_LABELS: Record<string, string> = {
  queued: "Queued",
  starting: "Starting",
  running: "Running",
  stopping: "Stopping",
  "force-stopping": "Force stopping",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
  orphaned: "Orphaned",
  unknown: "Unknown",
  recovering: "Recovering"
};

const RUN_STATUS_TONES: Record<string, "idle" | "live" | "warning" | "error"> = {
  queued: "idle",
  starting: "live",
  running: "live",
  stopping: "warning",
  "force-stopping": "warning",
  completed: "idle",
  failed: "error",
  cancelled: "warning",
  orphaned: "warning",
  unknown: "idle",
  recovering: "warning"
};

const LOG_TAIL_BYTES = 1_500_000;
const RUN_LOG_PATTERN = /^\[(.+?)\]\s+(\S+)\s+(\S+)\s+(.*)$/;

function getRunStatusLabel(status?: string | null) {
  if (!status) {
    return "Idle";
  }
  return RUN_STATUS_LABELS[status] || status;
}

function getRunStatusTone(status?: string | null) {
  if (!status) {
    return "idle";
  }
  return RUN_STATUS_TONES[status] || "idle";
}

function parseRunLog(raw: string): LogEntry[] {
  return raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const match = line.match(RUN_LOG_PATTERN);
      if (match) {
        return {
          time: match[1],
          level: match[2],
          logger: match[3],
          message: match[4],
          source: "logfile"
        };
      }
      return {
        time: new Date().toISOString(),
        level: "INFO",
        logger: "logfile",
        message: line,
        source: "logfile"
      };
    });
}

function App() {
  const [activeView, setActiveView] = useState<View>("dashboard");
  const [config, setConfig] = useState<AppConfig>(DEFAULT_CONFIG);
  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [logsByRunId, setLogsByRunId] = useState<Record<string, LogEntry[]>>({});
  const [eventsByRunId, setEventsByRunId] = useState<Record<string, BackendEvent[]>>({});
  const [runData, setRunData] = useState<RunData | null>(null);
  const [runDataState, setRunDataState] = useState<DataState>({ state: "idle" });
  const [artifactState, setArtifactState] = useState<DataState>({ state: "idle" });
  const [ollamaStatus, setOllamaStatus] = useState<"unknown" | "ok" | "error">(
    "unknown"
  );
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [ollamaLatency, setOllamaLatency] = useState<number | null>(null);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [search, setSearch] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);
  const [showRawBackend, setShowRawBackend] = useState(false);
  const [levelFilter, setLevelFilter] = useState({
    INFO: true,
    WARNING: true,
    ERROR: true,
    DEBUG: false
  });
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [selectedAssessment, setSelectedAssessment] =
    useState<SubcategoryAssessment | null>(null);
  const [matrixFunction, setMatrixFunction] = useState<string>(NIST_FUNCTIONS[0]);
  const [evidenceStatus, setEvidenceStatus] = useState<AssessmentStatus | "All">("All");
  const [librarySearch, setLibrarySearch] = useState("");
  const [libraryStatus, setLibraryStatus] = useState("all");
  const [libraryType, setLibraryType] = useState("all");
  const [libraryProvider, setLibraryProvider] = useState("all");
  const [librarySort, setLibrarySort] = useState("newest");
  const [libraryPinnedOnly, setLibraryPinnedOnly] = useState(false);
  const [libraryDateFrom, setLibraryDateFrom] = useState("");
  const [libraryDateTo, setLibraryDateTo] = useState("");
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [processStats, setProcessStats] = useState<ProcessStats | null>(null);
  const [debugLog, setDebugLog] = useState<string>("");
  const [runStep, setRunStep] = useState<RunStep>("setup");
  const [logView, setLogView] = useState<LogView>("stream");
  const [matrixView, setMatrixView] = useState<MatrixView>("overview");
  const [revisionView, setRevisionView] = useState<RevisionView>("summary");
  const [roadmapView, setRoadmapView] = useState<RoadmapView>("overview");
  const [sectionSearch, setSectionSearch] = useState("");

  const logEndRef = useRef<HTMLDivElement | null>(null);
  const selectedRunRef = useRef<string | null>(null);
  const refreshTimerRef = useRef<number | null>(null);

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
    selectedRunRef.current = selectedRunId;
  }, [selectedRunId]);

  useEffect(() => {
    const unsub = window.api.onRunEvent((event: RunEvent) => {
      if (!event) {
        return;
      }

      if (event.type === "run-created" || event.type === "run-updated") {
        setRuns((prev) => {
          const index = prev.findIndex((run) => run.id === event.run.id);
          if (index >= 0) {
            const next = [...prev];
            next[index] = event.run;
            return sortRunsByUpdatedAt(next);
          }
          return sortRunsByUpdatedAt([event.run, ...prev]);
        });
      }

      if (event.type === "run-selected") {
        setSelectedRunId(event.runId || null);
      }

      if (event.type === "run-removed") {
        setRuns((prev) => prev.filter((run) => run.id !== event.runId));
        if (selectedRunRef.current === event.runId) {
          setSelectedRunId(null);
          setRunData(null);
          setSelectedSection(null);
          setSelectedAssessment(null);
          setRunDataState({ state: "idle" });
          setArtifactState({ state: "idle" });
        }
      }

      if (event.type === "run-log") {
        setLogsByRunId((prev) => {
          const limit = config.logRetention || 2000;
          const existing = prev[event.runId] || [];
          const next = [...existing, event.entry];
          return {
            ...prev,
            [event.runId]: next.length > limit ? next.slice(-limit) : next
          };
        });
      }

      if (event.type === "backend-event") {
        setEventsByRunId((prev) => {
          const existing = prev[event.runId] || [];
          const next = [...existing.slice(-199), event.event];
          return { ...prev, [event.runId]: next };
        });
        if (event.runId === selectedRunRef.current) {
          setRunDataState((prev) =>
            prev.state === "fresh" ? { ...prev, state: "stale" } : prev
          );
        }
      }

      if (event.type === "run-exit") {
        if (event.exitCode && event.exitCode !== 0) {
          addNotice("error", `Run exited with code ${event.exitCode}`);
        } else if (event.signal && event.signal !== "SIGTERM") {
          addNotice("warning", `Run stopped: ${event.signal}`);
        } else {
          addNotice("success", "Run complete");
        }
        if (event.runId === selectedRunRef.current) {
          scheduleRefresh(event.runId);
        }
      }

      if (event.type === "run-artifacts") {
        if (event.runId === selectedRunRef.current) {
          setArtifactState({
            state: "fresh",
            runId: event.runId,
            updatedAt: new Date().toISOString()
          });
        }
      }
    });

    return () => {
      unsub();
    };
  }, [config.logRetention]);

  useEffect(() => {
    if (!autoScroll) {
      return;
    }
    const currentLogs = selectedRunId ? logsByRunId[selectedRunId] || [] : [];
    if (currentLogs.length === 0) {
      return;
    }
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [autoScroll, logsByRunId, selectedRunId]);

  useEffect(() => {
    window.api
      .getRunsSnapshot()
      .then((snapshot) => {
        setRuns(snapshot.runs || []);
        setSelectedRunId(snapshot.selectedRunId || null);
      })
      .catch(() => {
        setRuns([]);
        setSelectedRunId(null);
      });
    window.api.getAppInfo().then(setAppInfo).catch(() => setAppInfo(null));
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setRunData(null);
      setSelectedSection(null);
      setSelectedAssessment(null);
      setRunDataState({ state: "idle" });
      setArtifactState({ state: "idle" });
      setDebugLog("");
      return;
    }
    setRunDataState({ state: "stale", runId: selectedRunId });
    setArtifactState({ state: "stale", runId: selectedRunId });
    setSelectedAssessment(null);
    setDebugLog("");
    void hydrateRunLogs(selectedRunId);
    void refreshRunData(selectedRunId);
    void refreshArtifacts(selectedRunId);
  }, [selectedRunId]);

  useEffect(() => {
    if (!config.autoRefresh || !selectedRunId) {
      return undefined;
    }

    const interval = setInterval(() => {
      if (selectedRunId) {
        void refreshRunData(selectedRunId);
        void refreshArtifacts(selectedRunId);
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [config.autoRefresh, selectedRunId]);

  useEffect(() => {
    const interval = setInterval(() => {
      window.api
        .getProcessStats(selectedRunId || undefined)
        .then(setProcessStats)
        .catch(() => setProcessStats(null));
    }, 6000);

    return () => clearInterval(interval);
  }, [selectedRunId]);

  const selectedRun = useMemo(() => {
    if (!selectedRunId) {
      return null;
    }
    return runs.find((run) => run.id === selectedRunId) || null;
  }, [runs, selectedRunId]);

  useEffect(() => {
    if (selectedRun?.runDir && selectedRun.runDir !== config.runDir) {
      updateConfig("runDir", selectedRun.runDir);
    }
  }, [selectedRun?.runDir]);

  useEffect(() => {
    if (!selectedRunId || selectedRun?.status !== "recovering") {
      return undefined;
    }
    const interval = window.setInterval(() => {
      void hydrateRunLogs(selectedRunId);
    }, 4000);
    return () => window.clearInterval(interval);
  }, [selectedRunId, selectedRun?.status, config.logRetention]);

  const logs = useMemo(() => {
    if (!selectedRunId) {
      return [];
    }
    return logsByRunId[selectedRunId] || [];
  }, [logsByRunId, selectedRunId]);

  const events = useMemo(() => {
    if (!selectedRunId) {
      return [];
    }
    return eventsByRunId[selectedRunId] || [];
  }, [eventsByRunId, selectedRunId]);

  const phases = useMemo(() => {
    return selectedRun?.phases || DEFAULT_PHASES;
  }, [selectedRun]);

  const artifacts = selectedRun?.artifacts || [];
  const summarySource =
    (runData?.summary as SummaryPayload | null) ||
    (selectedRun?.summary as SummaryPayload | null) ||
    null;
  const statusEvent: StatusEvent | null = selectedRun
    ? {
        state: selectedRun.status,
        pid: selectedRun.pid || undefined
      }
    : null;
  const exitInfo: ExitEvent | null = selectedRun
    ? {
        code: selectedRun.exitCode ?? null,
        signal: selectedRun.signal ?? null
      }
    : null;
  const isRunning = selectedRun
    ? [
        "queued",
        "starting",
        "running",
        "stopping",
        "force-stopping",
        "recovering"
      ].includes(selectedRun.status)
    : false;
  const activeRun = useMemo(() => {
    return (
      runs.find((run) =>
        [
          "queued",
          "starting",
          "running",
          "stopping",
          "force-stopping",
          "recovering"
        ].includes(run.status)
      ) || null
    );
  }, [runs]);
  const hasActiveRun = Boolean(activeRun);
  const selectedRunDir = selectedRun?.runDir || "";
  const selectedProvider = selectedRun?.provider || config.provider;
  const selectedModel = selectedRun?.model || config.model;

  useEffect(() => {
    if (activeRun && activeRun.id !== selectedRunId) {
      void window.api.selectRun(activeRun.id);
      setSelectedRunId(activeRun.id);
    }
  }, [activeRun?.id, selectedRunId]);

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
      if (!showRawBackend && entry.source === "stderr" && entry.logger === "backend") {
        return false;
      }
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
  }, [logs, levelFilter, search, showRawBackend]);

  const recentLogs = useMemo(() => logs.slice(-6), [logs]);
  const artifactsPreview = useMemo(() => artifacts.slice(0, 5), [artifacts]);

  const summaryCounts = useMemo(() => {
    return {
      functions: summarySource?.functions_analyzed?.length ?? 0,
      reports: summarySource?.reports ? Object.keys(summarySource.reports).length : 0
    };
  }, [summarySource]);

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

  const runHistory = useMemo<RunRecord[]>(() => {
    return runs.map((run) => ({
      ...run,
      runDir: run.runDir || "",
      policyName: run.policyName || extractFileName(run.pdfPath || "")
    }));
  }, [runs]);

  const demoRun = useMemo(() => {
    return runs.find((run) => run.runType === "demo") || null;
  }, [runs]);

  const statusOptions = useMemo(() => {
    const set = new Set<string>();
    runHistory.forEach((run) => set.add(run.status || "unknown"));
    return Array.from(set).sort();
  }, [runHistory]);

  const providerOptions = useMemo(() => {
    const set = new Set<string>();
    runHistory.forEach((run) => {
      if (run.provider) {
        set.add(run.provider);
      }
    });
    return Array.from(set).sort();
  }, [runHistory]);

  const runLibraryFiltered = useMemo(() => {
    const needle = librarySearch.trim().toLowerCase();
    const fromDate = libraryDateFrom ? new Date(libraryDateFrom) : null;
    const toDate = libraryDateTo ? new Date(libraryDateTo) : null;
    if (toDate && Number.isFinite(toDate.getTime())) {
      toDate.setHours(23, 59, 59, 999);
    }

    const filtered = runHistory.filter((entry) => {
      if (needle) {
        const haystack = [
          entry.runName,
          entry.policyName,
          entry.runDir,
          entry.id,
          entry.provider,
          (entry.tags || []).join(" "),
          entry.notes
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(needle)) {
          return false;
        }
      }

      if (libraryStatus !== "all") {
        const statusValue = entry.status || "unknown";
        if (statusValue !== libraryStatus) {
          return false;
        }
      }

      if (libraryType !== "all") {
        if ((entry.runType || "real") !== libraryType) {
          return false;
        }
      }

      if (libraryProvider !== "all") {
        if ((entry.provider || "") !== libraryProvider) {
          return false;
        }
      }

      if (libraryPinnedOnly && !entry.pinned) {
        return false;
      }

      if (fromDate && Number.isFinite(fromDate.getTime())) {
        const createdAt = new Date(entry.createdAt);
        if (createdAt < fromDate) {
          return false;
        }
      }

      if (toDate && Number.isFinite(toDate.getTime())) {
        const createdAt = new Date(entry.createdAt);
        if (createdAt > toDate) {
          return false;
        }
      }

      return true;
    });

    const sorted = [...filtered].sort((a, b) => {
      const aPinned = Boolean(a.pinned);
      const bPinned = Boolean(b.pinned);
      if (aPinned !== bPinned) {
        return aPinned ? -1 : 1;
      }

      if (librarySort === "oldest") {
        const aDate = a.updatedAt || a.createdAt || "";
        const bDate = b.updatedAt || b.createdAt || "";
        return aDate.localeCompare(bDate);
      }
      if (librarySort === "status") {
        return (a.status || "").localeCompare(b.status || "");
      }
      if (librarySort === "name") {
        return (a.runName || a.policyName || "").localeCompare(
          b.runName || b.policyName || ""
        );
      }
      if (librarySort === "duration") {
        return (b.durationMs || 0) - (a.durationMs || 0);
      }
      const aDate = a.updatedAt || a.createdAt || "";
      const bDate = b.updatedAt || b.createdAt || "";
      return bDate.localeCompare(aDate);
    });

    return sorted;
  }, [
    librarySearch,
    libraryStatus,
    libraryType,
    libraryProvider,
    libraryPinnedOnly,
    libraryDateFrom,
    libraryDateTo,
    librarySort,
    runHistory
  ]);

  const filteredSections = useMemo(() => {
    const sections = runData?.sections || [];
    const needle = sectionSearch.trim().toLowerCase();
    if (!needle) {
      return sections;
    }
    return sections.filter((section) => {
      const haystack = `${section.number} ${section.title}`.toLowerCase();
      return haystack.includes(needle);
    });
  }, [runData, sectionSearch]);

  const evidenceCounts = useMemo(() => {
    return summarizeAssessments(evidenceForSection);
  }, [evidenceForSection]);

  const matrixSummary = useMemo(() => {
    const summaryData: Record<string, StatusCounts> = {};
    NIST_FUNCTIONS.forEach((name) => {
      summaryData[name] = summarizeAssessments(runData?.assessments?.[name] || []);
    });
    return summaryData;
  }, [runData]);

  const roadmapCounts = useMemo(() => {
    const tiers = runData?.roadmap?.tiers || [];
    const items = tiers.reduce((total, tier) => total + tier.items.length, 0);
    return {
      tiers: tiers.length,
      items,
      missing: runData?.roadmap?.missingDocs.length || 0
    };
  }, [runData]);

  const allAssessments = useMemo(() => {
    return Object.values(runData?.assessments || {}).flat();
  }, [runData]);

  const coverageCounts = useMemo(() => {
    return summarizeAssessments(allAssessments);
  }, [allAssessments]);

  const sectionsCount = runData?.sections?.length ?? 0;
  const masterListCount = runData?.masterList?.length ?? 0;
  const assessmentsCount = allAssessments.length;

  const runStateLabel = getRunStatusLabel(selectedRun?.status);
  const runOutcomeLabel = getRunStatusLabel(selectedRun?.status);
  const runOutcomeTone = getRunStatusTone(selectedRun?.status);
  const hasStatus = Boolean(selectedRun);
  const canClearStatus = !isRunning && hasStatus;
  const progressPct = Math.round(progress * 100);
  const viewMeta = VIEW_META[activeView];
  const policyFileName =
    extractFileName(selectedRun?.pdfPath || config.pdfPath) || "Not selected";

  function updateConfig<K extends keyof AppConfig>(key: K, value: AppConfig[K]) {
    setConfig((prev) => {
      const next = { ...prev, [key]: value };
      void window.api.saveConfig(next);
      return next;
    });
  }

  function scheduleRefresh(runId: string) {
    if (!runId) {
      return;
    }
    if (refreshTimerRef.current) {
      window.clearTimeout(refreshTimerRef.current);
    }
    refreshTimerRef.current = window.setTimeout(() => {
      void refreshRunData(runId);
      void refreshArtifacts(runId);
    }, 500);
  }

  function addNotice(kind: Notice["kind"], message: string) {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setNotices((prev) => [...prev, { id, kind, message }]);
    setTimeout(() => {
      setNotices((prev) => prev.filter((n) => n.id !== id));
    }, 6000);
  }

  async function hydrateRunLogs(runId: string) {
    const content = await window.api.readRunText(runId, "run.log", LOG_TAIL_BYTES);
    if (content == null) {
      return;
    }
    const parsed = parseRunLog(content);
    const limit = config.logRetention || 2000;
    const trimmed = parsed.length > limit ? parsed.slice(-limit) : parsed;
    setLogsByRunId((prev) => ({ ...prev, [runId]: trimmed }));
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
    const result = await window.api.startRun(payload);
    if (!result.ok) {
      addNotice("error", result.error || "Failed to start run");
      return;
    }
    if (result.runId) {
      setLogsByRunId((prev) => ({ ...prev, [result.runId]: [] }));
      setEventsByRunId((prev) => ({ ...prev, [result.runId]: [] }));
      setRunData(null);
      setSelectedSection(null);
      setRunDataState({ state: "stale", runId: result.runId });
      setArtifactState({ state: "stale", runId: result.runId });
      setSelectedRunId(result.runId);
    }
    addNotice("info", "Run started");
  }

  async function stopRun(force = false) {
    if (!selectedRunId) {
      addNotice("warning", "No run selected");
      return;
    }
    const result = await window.api.stopRun({ runId: selectedRunId, force });
    if (!result.ok) {
      addNotice("error", result.error || "Failed to stop run");
      return;
    }
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
    if (selectedRunId) {
      setLogsByRunId((prev) => ({ ...prev, [selectedRunId]: [] }));
      setEventsByRunId((prev) => ({ ...prev, [selectedRunId]: [] }));
      setRunData(null);
      setSelectedSection(null);
      setRunDataState({ state: "stale", runId: selectedRunId });
    }
    addNotice("info", "Run telemetry cleared");
  }

  async function clearLogs() {
    if (!selectedRunId) {
      addNotice("warning", "No run selected");
      return;
    }
    const result = await window.api.clearRunLog(selectedRunId);
    if (!result.ok) {
      addNotice("warning", result.error || "Unable to clear persisted log");
    }
    setLogsByRunId((prev) => ({ ...prev, [selectedRunId]: [] }));
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
    const targetDir = selectedRun?.runDir || config.runDir;
    if (!targetDir) {
      addNotice("warning", "No run directory available");
      return;
    }
    await window.api.openPath(targetDir);
  }

  async function refreshArtifacts(runId: string) {
    if (!runId) {
      return;
    }
    setArtifactState({ state: "refreshing", runId });
    const updated = await window.api.refreshRun(runId);
    if (selectedRunRef.current !== runId) {
      return;
    }
    if (updated) {
      setArtifactState({
        state: "fresh",
        runId,
        updatedAt: new Date().toISOString()
      });
    }
  }

  async function refreshRunData(runId: string) {
    if (!runId) {
      return;
    }
    setRunDataState({ state: "refreshing", runId });
    try {
      const data = await loadRunData(runId);
      if (selectedRunRef.current !== runId) {
        return;
      }
      setRunData(data);
      setRunDataState({
        state: "fresh",
        runId,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      if (selectedRunRef.current === runId) {
        setRunDataState({
          state: "error",
          runId,
          error: "Failed to load run data"
        });
      }
    }
  }

  async function loadRunData(runId: string) {
    if (!runId) {
      return null;
    }

    const [
      sectionsRaw,
      masterListRaw,
      assessmentsRaw,
      summaryRaw,
      revisionReportRaw,
      revisedPolicyRaw,
      roadmapRaw
    ] = await Promise.all([
      window.api.readRunJson(runId, "sections_output.json"),
      window.api.readRunJson(runId, "master_list.json"),
      window.api.readRunJson(runId, "assessments.json"),
      window.api.readRunJson(runId, "summary.json"),
      window.api.readRunText(runId, "revision_report.md", 1_500_000),
      window.api.readRunText(runId, "revised_policy.md", 1_500_000),
      window.api.readRunText(runId, "improvement_roadmap.md", 1_500_000)
    ]);

    const sections = Array.isArray(sectionsRaw)
      ? (sectionsRaw as PolicySection[])
      : [];
    const masterList = Array.isArray(masterListRaw)
      ? (masterListRaw as MasterListEntry[])
      : [];
    const assessments = (assessmentsRaw || {}) as Record<string, SubcategoryAssessment[]>;
    const summaryPayload = (summaryRaw || null) as SummaryPayload | null;

    const revisionReport = revisionReportRaw ? parseRevisionReport(revisionReportRaw) : null;
    const roadmap = roadmapRaw ? parseRoadmap(roadmapRaw) : null;

    const nextRunData: RunData = {
      sections,
      masterList,
      assessments,
      summary: summaryPayload,
      revisionReport,
      revisedPolicy: revisedPolicyRaw || null,
      roadmap
    };

    if (selectedRunRef.current === runId && !selectedSection && sections.length > 0) {
      setSelectedSection(sections[0].number);
    }

    return nextRunData;
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
    if (!selectedRunId) {
      addNotice("warning", "No run directory selected");
      return;
    }
    const content = await window.api.readRunText(selectedRunId, "debug.log", 1_500_000);
    setDebugLog(content || "No debug log found.");
  }

  async function scanRuns() {
    const baseDir = config.outputDir || "gap_analysis_reports";
    const results = await window.api.scanRuns(baseDir);
    if (!results || results.length === 0) {
      addNotice("warning", "No runs found in output directory");
      return;
    }
    setRuns((prev) => {
      const map = new Map(prev.map((run) => [run.id, run]));
      results.forEach((run) => map.set(run.id, run));
      return sortRunsByUpdatedAt(Array.from(map.values()));
    });
  }

  function selectRun(entry: RunRecord) {
    updateConfig("runDir", entry.runDir);
    void window.api.selectRun(entry.id);
    setSelectedRunId(entry.id);
  }

  function openRun(entry: RunRecord) {
    activateRun(entry.id, "dashboard");
  }

  function activateRun(runId: string, view: View) {
    if (!runId) {
      return;
    }
    void window.api.selectRun(runId);
    setSelectedRunId(runId);
    setActiveView(view);
  }

  function updateHistoryEntry(entry: RunRecord, updates: Partial<RunRecord>) {
    window.api.updateRun(entry.id, updates).then((updated) => {
      if (!updated) {
        return;
      }
      setRuns((prev) => {
        const index = prev.findIndex((run) => run.id === updated.id);
        if (index < 0) {
          return sortRunsByUpdatedAt([updated, ...prev]);
        }
        const next = [...prev];
        next[index] = updated;
        return sortRunsByUpdatedAt(next);
      });
    });
  }

  async function removeRun(entry: RunRecord, options: { deleteFiles: boolean }) {
    const result = await window.api.removeRun(entry.id, options);
    if (!result.ok) {
      addNotice("error", result.error || "Failed to remove run");
      return;
    }
    setRuns((prev) => prev.filter((run) => run.id !== entry.id));
    if (selectedRunRef.current === entry.id) {
      setSelectedRunId(null);
      setRunData(null);
      setSelectedSection(null);
      setSelectedAssessment(null);
      setRunDataState({ state: "idle" });
      setArtifactState({ state: "idle" });
    }
    addNotice("success", options.deleteFiles ? "Run deleted" : "Run removed from library");
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
      <Sidebar
        activeView={activeView}
        onSelectView={setActiveView}
        runStateLabel={runStateLabel}
        config={config}
      />

      <div className="content">
        <header className="topbar">
          <div className="page-title">
            <span className="kicker">{viewMeta.subtitle}</span>
            <h1>{viewMeta.title}</h1>
          </div>
          <div className="page-meta">
            <span className="meta-label">Policy</span>
            <strong>{policyFileName}</strong>
          </div>
        </header>

        <CommandBar
          runOutcomeTone={runOutcomeTone}
          runOutcomeLabel={runOutcomeLabel}
          statusEvent={statusEvent}
          exitInfo={exitInfo}
          progressPct={progressPct}
          runDir={selectedRunDir || config.runDir}
          provider={selectedProvider}
          startDisabled={hasActiveRun || validation.length > 0}
          isRunning={isRunning}
          canClearStatus={canClearStatus}
          onStart={startRun}
          onStop={() => stopRun(false)}
          onForceStop={() => stopRun(true)}
          onClearStatus={clearRunStatus}
          onOpenRunDir={openRunDir}
        />

        {activeView === "run" && validation.length > 0 && (
          <div className="command-alert">
            <div>
              <strong>Ready check</strong>
              <span className="subtle">Resolve these before launching a run.</span>
            </div>
            <ul>
              {validation.map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
            <div className="inline-actions">
              <button className="ghost" onClick={() => setRunStep("setup")}>
                Review setup
              </button>
            </div>
          </div>
        )}

        <main className="page">
          {activeView === "mission" && (
            <MissionControlView
              runStateLabel={runStateLabel}
              runOutcomeLabel={runOutcomeLabel}
              runOutcomeTone={runOutcomeTone}
              progressPct={progressPct}
              phases={phases}
              policyFileName={policyFileName}
              runDir={selectedRunDir}
              provider={selectedProvider}
              model={selectedModel}
              summaryCounts={summaryCounts}
              sectionsCount={sectionsCount}
              masterListCount={masterListCount}
              assessmentsCount={assessmentsCount}
              coverageCounts={coverageCounts}
              matrixSummary={matrixSummary}
              revisionReport={runData?.revisionReport || null}
              roadmapCounts={roadmapCounts}
              artifactsPreview={artifactsPreview}
              recentLogs={recentLogs}
              events={events}
              processStats={processStats}
              onOpenRunDir={openRunDir}
              onViewArtifacts={() => setActiveView("artifacts")}
              onViewLogs={() => setActiveView("logs")}
            />
          )}

          {activeView === "dashboard" && (
            <DashboardView
              runStateLabel={runStateLabel}
              statusEvent={statusEvent}
              exitInfo={exitInfo}
              progressPct={progressPct}
              phases={phases}
              config={config}
              summaryCounts={summaryCounts}
              artifacts={artifacts}
              artifactsPreview={artifactsPreview}
              logs={logs}
              recentLogs={recentLogs}
              ollamaStatus={ollamaStatus}
              ollamaLatency={ollamaLatency}
              ollamaModels={ollamaModels}
              onOpenRunDir={openRunDir}
              onViewRun={() => setActiveView("run")}
              onViewArtifacts={() => setActiveView("artifacts")}
              onRefreshArtifacts={() => selectedRunId && refreshArtifacts(selectedRunId)}
              onViewLogs={() => setActiveView("logs")}
              onTestOllama={testOllama}
            />
          )}

          {activeView === "run" && (
            <RunBuilderView
              config={config}
              runStep={runStep}
              onSetRunStep={setRunStep}
              policyFileName={policyFileName}
              validation={validation}
              runStateLabel={runStateLabel}
              statusEvent={statusEvent}
              exitInfo={exitInfo}
              progressPct={progressPct}
              phases={phases}
              logsCount={logs.length}
              onUpdateConfig={updateConfig}
              onSelectPdf={handleSelectPdf}
              onSelectOutputDir={handleSelectOutputDir}
              onSelectRunDir={handleSelectRunDir}
              onViewLogs={() => setActiveView("logs")}
              onViewArtifacts={() => setActiveView("artifacts")}
            />
          )}

          {activeView === "logs" && (
            <LogsView
              logView={logView}
              onSetLogView={setLogView}
              filteredLogs={filteredLogs}
              events={events}
              levelFilter={levelFilter}
              onSetLevelFilter={setLevelFilter}
              search={search}
              onSearchChange={setSearch}
              autoScroll={autoScroll}
              onAutoScrollChange={setAutoScroll}
              showRawBackend={showRawBackend}
              onShowRawBackendChange={setShowRawBackend}
              logEndRef={logEndRef}
              onClearLogs={clearLogs}
              onClearEvents={() =>
                selectedRunId &&
                setEventsByRunId((prev) => ({ ...prev, [selectedRunId]: [] }))
              }
            />
          )}

          {activeView === "artifacts" && (
            <ArtifactsView
              artifacts={artifacts}
              summaryCounts={summaryCounts}
              exitInfo={exitInfo}
              logsCount={logs.length}
              runDir={selectedRunDir}
              onRefreshArtifacts={() => selectedRunId && refreshArtifacts(selectedRunId)}
              onRefreshSummary={() => selectedRunId && refreshRunData(selectedRunId)}
              onOpenRunDir={openRunDir}
            />
          )}

          {activeView === "settings" && (
            <SettingsView
              config={config}
              ollamaStatus={ollamaStatus}
              ollamaModels={ollamaModels}
              ollamaLatency={ollamaLatency}
              statusEvent={statusEvent}
              logsCount={logs.length}
              onUpdateConfig={updateConfig}
              onTestOllama={testOllama}
            />
          )}

          {activeView === "evidence" && (
            <EvidenceView
              sections={runData?.sections || []}
              filteredSections={filteredSections}
              selectedSection={selectedSection}
              onSelectSection={setSelectedSection}
              sectionSearch={sectionSearch}
              onSectionSearchChange={setSectionSearch}
              evidenceCounts={evidenceCounts}
              evidenceStatus={evidenceStatus}
              onEvidenceStatusChange={setEvidenceStatus}
              evidenceForSection={evidenceForSection}
            />
          )}

          {activeView === "matrix" && (
            <MatrixViewComponent
              matrixView={matrixView}
              onSetMatrixView={setMatrixView}
              matrixSummary={matrixSummary}
              matrixFunction={matrixFunction}
              onSetMatrixFunction={setMatrixFunction}
              matrixAssessments={matrixAssessments}
              selectedAssessment={selectedAssessment}
              onSelectAssessment={setSelectedAssessment}
              assessments={runData?.assessments || null}
            />
          )}

          {activeView === "revision" && (
            <RevisionViewComponent
              revisionView={revisionView}
              onSetRevisionView={setRevisionView}
              runData={runData}
            />
          )}

          {activeView === "roadmap" && (
            <RoadmapViewComponent
              roadmapView={roadmapView}
              onSetRoadmapView={setRoadmapView}
              runData={runData}
              roadmapCounts={roadmapCounts}
              runDir={selectedRunDir}
            />
          )}

          {activeView === "demo" && (
            <DemoView
              demoRun={demoRun}
              onNavigate={setActiveView}
              onActivateRun={activateRun}
            />
          )}

          {activeView === "help" && <HelpView />}

          {activeView === "library" && (
            <LibraryView
              runLibraryFiltered={runLibraryFiltered}
              librarySearch={librarySearch}
              libraryStatus={libraryStatus}
              libraryType={libraryType}
              libraryProvider={libraryProvider}
              librarySort={librarySort}
              libraryPinnedOnly={libraryPinnedOnly}
              libraryDateFrom={libraryDateFrom}
              libraryDateTo={libraryDateTo}
              statusOptions={statusOptions}
              providerOptions={providerOptions}
              onLibrarySearchChange={setLibrarySearch}
              onLibraryStatusChange={setLibraryStatus}
              onLibraryTypeChange={setLibraryType}
              onLibraryProviderChange={setLibraryProvider}
              onLibrarySortChange={setLibrarySort}
              onLibraryPinnedOnlyChange={setLibraryPinnedOnly}
              onLibraryDateFromChange={setLibraryDateFrom}
              onLibraryDateToChange={setLibraryDateTo}
              selectedRunId={selectedRunId}
              runHistory={runHistory}
              onSelectRun={selectRun}
              onScanRuns={scanRuns}
              onUpdateHistoryEntry={updateHistoryEntry}
              onOpenRunDir={openRunDir}
              onRemoveRun={removeRun}
              onOpenRun={openRun}
            />
          )}

          {activeView === "diagnostics" && (
            <DiagnosticsView
              appInfo={appInfo}
              processStats={processStats}
              runDir={selectedRunDir}
              debugLog={debugLog}
              onLoadDebugLog={loadDebugLog}
              runDataState={runDataState}
              artifactState={artifactState}
              runStatus={selectedRun?.status || null}
              lastHeartbeat={selectedRun?.lastHeartbeat || null}
            />
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

export default App;
