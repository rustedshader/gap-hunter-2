const fs = require("fs");
const path = require("path");
const { EventEmitter } = require("events");
const { spawn } = require("child_process");

const { RunStore } = require("./run_store");

const DEFAULT_PHASES = [
  { id: "extraction", label: "Extraction", status: "pending" },
  { id: "analysis", label: "Gap Analysis", status: "pending" },
  { id: "revision", label: "Policy Revision", status: "pending" },
  { id: "roadmap", label: "Roadmap", status: "pending" }
];

const ACTIVE_STATUSES = new Set([
  "queued",
  "starting",
  "running",
  "stopping",
  "force-stopping",
  "recovering"
]);

const RUN_FILE_LIMITS = {
  text: 1_500_000,
  json: 3_000_000
};

const ALLOWED_RUN_FILES = new Set([
  "sections_output.json",
  "master_list.json",
  "assessments.json",
  "summary.json",
  "revision_report.md",
  "revised_policy.md",
  "improvement_roadmap.md",
  "run.log",
  "debug.log"
]);

const REQUIRED_RUN_FILES = [
  "summary.json",
  "sections_output.json",
  "assessments.json",
  "master_list.json"
];

const DEMO_RUN_ID = "demo-run";

function nowIso() {
  return new Date().toISOString();
}

function clonePhases(phases) {
  return (phases || DEFAULT_PHASES).map((phase) => ({ ...phase }));
}

function updatePhase(phases, phaseId, status) {
  const next = clonePhases(phases);
  const target = next.find((phase) => phase.id === phaseId);
  if (!target) {
    return next;
  }
  if (status === "running" && target.status === "pending") {
    target.status = "running";
    target.startedAt = Date.now();
  } else if (status === "done" && target.status !== "done") {
    target.status = "done";
    target.finishedAt = Date.now();
  } else if (status === "error") {
    target.status = "error";
  }
  return next;
}

function inferRunOutcome(status, exitCode, signal, stopRequestedAt) {
  if (status === "completed" || status === "failed" || status === "cancelled") {
    return status;
  }
  if (exitCode === 0) {
    return "completed";
  }
  if (stopRequestedAt) {
    return "cancelled";
  }
  if (exitCode != null || signal) {
    return "failed";
  }
  return status;
}

function isProcessAlive(pid) {
  if (!pid) {
    return false;
  }
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return false;
  }
}

function sanitizeRunParams(params) {
  if (!params || typeof params !== "object") {
    return null;
  }
  return {
    pdfPath: typeof params.pdfPath === "string" ? params.pdfPath : "",
    outputDir: typeof params.outputDir === "string" ? params.outputDir : "",
    runDir: typeof params.runDir === "string" ? params.runDir : "",
    provider: typeof params.provider === "string" ? params.provider : "",
    ollamaUrl: typeof params.ollamaUrl === "string" ? params.ollamaUrl : "",
    model: typeof params.model === "string" ? params.model : "",
    ggufModelPath:
      typeof params.ggufModelPath === "string" ? params.ggufModelPath : "",
    windowSize: Number.isFinite(params.windowSize) ? params.windowSize : null,
    overlap: Number.isFinite(params.overlap) ? params.overlap : null,
    extractOnly: Boolean(params.extractOnly),
    skipRevision: Boolean(params.skipRevision),
    skipExtraction: Boolean(params.skipExtraction),
    revisionOnly: Boolean(params.revisionOnly)
  };
}

function computeExecutionMode(run) {
  if (!run) {
    return "";
  }
  if (run.revisionOnly) {
    return "Revision only";
  }
  if (run.extractOnly) {
    return "Extract only";
  }
  const flags = [];
  if (run.skipExtraction) {
    flags.push("Skip extraction");
  }
  if (run.skipRevision) {
    flags.push("Skip revision");
  }
  if (flags.length > 0) {
    return flags.join(" + ");
  }
  return "Full run";
}

function computeDurationMs(startedAt, finishedAt) {
  if (!startedAt || !finishedAt) {
    return null;
  }
  const startMs = Date.parse(startedAt);
  const endMs = Date.parse(finishedAt);
  if (!Number.isFinite(startMs) || !Number.isFinite(endMs)) {
    return null;
  }
  const delta = endMs - startMs;
  return delta >= 0 ? delta : null;
}

function summarizeAssessments(assessments) {
  const counts = {
    total: 0,
    addressed: 0,
    partiallyAddressed: 0,
    notAddressed: 0,
    outOfScope: 0
  };

  if (!assessments || typeof assessments !== "object") {
    return counts;
  }

  const groups = Object.values(assessments);
  for (const group of groups) {
    if (!Array.isArray(group)) {
      continue;
    }
    for (const item of group) {
      counts.total += 1;
      switch (item.status) {
        case "Addressed":
          counts.addressed += 1;
          break;
        case "Partially Addressed":
          counts.partiallyAddressed += 1;
          break;
        case "Not Addressed":
          counts.notAddressed += 1;
          break;
        case "Out of Scope":
          counts.outOfScope += 1;
          break;
        default:
          break;
      }
    }
  }

  return counts;
}

async function readJsonFile(filePath) {
  try {
    const raw = await fs.promises.readFile(filePath, "utf-8");
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
}

function buildTimestamp() {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(
    now.getHours()
  )}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

async function ensureDir(targetDir) {
  await fs.promises.mkdir(targetDir, { recursive: true });
}

async function createRunDir(baseDir) {
  await ensureDir(baseDir);
  let candidate = path.join(baseDir, buildTimestamp());
  let counter = 1;
  while (fs.existsSync(candidate)) {
    candidate = path.join(baseDir, `${buildTimestamp()}_${counter}`);
    counter += 1;
  }
  await ensureDir(candidate);
  return candidate;
}

function resolvePath(base, target) {
  if (!target) {
    return "";
  }
  if (path.isAbsolute(target)) {
    return target;
  }
  return path.resolve(base, target);
}

function parseLogLine(line, source) {
  const regex = /^(\d{2}:\d{2}:\d{2})\s+([A-Z]+)\s+(.+?)\s{2,}(.*)$/;
  const match = line.match(regex);
  if (match) {
    return {
      time: match[1],
      level: match[2],
      logger: match[3].trim(),
      message: match[4].trim(),
      source
    };
  }

  return {
    time: new Date().toISOString(),
    level: source === "stderr" ? "ERROR" : "INFO",
    logger: "backend",
    message: line.trim(),
    source
  };
}

function parseEventLine(line) {
  if (!line.startsWith("EVENT ")) {
    return null;
  }

  const payload = line.slice(6).trim();
  try {
    return JSON.parse(payload);
  } catch (error) {
    return null;
  }
}

function fingerprintArtifacts(artifacts) {
  return (artifacts || [])
    .map((item) => `${item.name}:${item.size}:${item.mtimeMs}`)
    .sort()
    .join("|");
}

class JobManager extends EventEmitter {
  constructor(options) {
    super();
    this.store = options.store;
    this.resolveBackendCommand = options.resolveBackendCommand;
    this.buildBackendArgs = options.buildBackendArgs;
    this.killProcessTree = options.killProcessTree;
    this.baseCwd = options.baseCwd || process.cwd();
    this.active = new Map();
    this.artifactIntervals = new Map();
    this.heartbeatWrites = new Map();
  }

  async initialize() {
    await this.store.load();
    await this.recoverRuns();
  }

  getSnapshot() {
    return {
      runs: this.store.listRuns(),
      selectedRunId: this.store.state.selectedRunId || null,
      generatedAt: nowIso()
    };
  }

  getRun(runId) {
    return this.store.getRun(runId);
  }

  getActiveRun() {
    return this.store.listRuns().find((run) => ACTIVE_STATUSES.has(run.status)) || null;
  }

  async selectRun(runId) {
    await this.store.setSelectedRunId(runId || null);
    this.emit("run-event", { type: "run-selected", runId: runId || null });
  }

  async updateRun(runId, patch) {
    const updated = await this.store.updateRun(runId, {
      ...patch,
      updatedAt: nowIso()
    });
    if (updated) {
      this.emit("run-event", { type: "run-updated", run: updated });
    }
    return updated;
  }

  async startRun(rawParams, runtimeContext) {
    const params = sanitizeRunParams(rawParams);
    if (!params) {
      return { ok: false, error: "Invalid run parameters." };
    }

    if (this.getActiveRun()) {
      return { ok: false, error: "A run is already in progress." };
    }

    const validation = this.validateParams(params);
    if (validation) {
      return { ok: false, error: validation };
    }

    let commandConfig;
    try {
      commandConfig = this.resolveBackendCommand();
    } catch (error) {
      return {
        ok: false,
        error: error && error.message ? error.message : "Failed to resolve backend"
      };
    }
    const { command, baseArgs, cwd } = commandConfig;
    const resolvedOutputDir = resolvePath(cwd, params.outputDir || "gap_analysis_reports");

    let resolvedRunDir = resolvePath(cwd, params.runDir);
    if (params.revisionOnly || params.skipExtraction) {
      if (!resolvedRunDir || !fs.existsSync(resolvedRunDir)) {
        return {
          ok: false,
          error: "Run directory was not found for the selected mode."
        };
      }
    }

    if (resolvedRunDir && fs.existsSync(resolvedRunDir)) {
      const stat = fs.statSync(resolvedRunDir);
      if (!stat.isDirectory()) {
        return { ok: false, error: "Run directory path is not a folder." };
      }
    }

    if (!resolvedRunDir) {
      resolvedRunDir = await createRunDir(resolvedOutputDir);
    } else if (!fs.existsSync(resolvedRunDir)) {
      await ensureDir(resolvedRunDir);
    }

    const runId = path.basename(resolvedRunDir);

    const existing = this.getRun(runId);
    const runRecord = await this.store.upsertRun({
      id: runId,
      status: "starting",
      runType: existing?.runType || "real",
      runName: existing?.runName || "",
      pinned: Boolean(existing?.pinned),
      createdAt: existing?.createdAt || nowIso(),
      updatedAt: nowIso(),
      runDir: resolvedRunDir,
      outputDir: resolvedOutputDir,
      pdfPath: params.pdfPath,
      provider: params.provider,
      model: params.model,
      ggufModelPath: params.ggufModelPath,
      ollamaUrl: params.ollamaUrl,
      windowSize: params.windowSize,
      overlap: params.overlap,
      extractOnly: params.extractOnly,
      skipRevision: params.skipRevision,
      skipExtraction: params.skipExtraction,
      revisionOnly: params.revisionOnly,
      executionMode: computeExecutionMode(params),
      phases: clonePhases(DEFAULT_PHASES),
      progress: 0,
      lastHeartbeat: nowIso(),
      tags: Array.isArray(existing?.tags) ? existing.tags : [],
      notes: existing?.notes || "",
      policyName: runtimeContext && runtimeContext.policyName ? runtimeContext.policyName : "",
      command,
      args: [],
      cwd
    });

    this.emit("run-event", { type: "run-created", run: runRecord });
    await this.selectRun(runId);

    const args = [...baseArgs, ...this.buildBackendArgs({
      ...params,
      outputDir: resolvedOutputDir,
      runDir: resolvedRunDir
    })];

    const fullCommand = [command, ...args].join(" ");

    await this.updateRun(runId, {
      status: "starting",
      command,
      args,
      cwd,
      lastHeartbeat: nowIso()
    });

    this.emit("run-log", {
      runId,
      entry: {
        time: new Date().toISOString(),
        level: "INFO",
        logger: "app",
        message: `Launching backend: ${fullCommand}`,
        source: "app"
      }
    });

    const env = {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      PYTHONUTF8: "1"
    };

    const child = spawn(command, args, {
      cwd,
      env,
      detached: false,
      windowsHide: true
    });

    const runStream = this.createRunLogStream(resolvedRunDir);
    const handle = {
      process: child,
      stdoutBuffer: "",
      stderrBuffer: "",
      logStream: runStream,
      stopTimer: null
    };

    this.active.set(runId, handle);

    this.attachProcessHandlers(runId, child, handle);

    await this.updateRun(runId, {
      status: "running",
      pid: child.pid,
      startedAt: nowIso(),
      lastHeartbeat: nowIso()
    });

    this.startArtifactPolling(runId);

    return { ok: true, runId };
  }

  validateParams(params) {
    if (params.revisionOnly) {
      if (!params.runDir) {
        return "Run directory is required for revision-only mode.";
      }
    } else {
      if (!params.pdfPath) {
        return "PDF policy file is required.";
      }
      if (params.skipExtraction && !params.runDir) {
        return "Run directory is required when skipping extraction.";
      }
    }

    if (params.provider === "ollama") {
      if (!params.ollamaUrl) {
        return "Ollama URL is required for provider=ollama.";
      }
    } else if (params.provider === "llamacpp" && !params.ggufModelPath) {
      return "GGUF model path is required for local mode.";
    }

    if (params.pdfPath && !fs.existsSync(params.pdfPath)) {
      return `PDF not found: ${params.pdfPath}`;
    }

    return "";
  }

  createRunLogStream(runDir) {
    if (!runDir) {
      return null;
    }
    try {
      const logPath = path.join(runDir, "run.log");
      return fs.createWriteStream(logPath, { flags: "a" });
    } catch (error) {
      return null;
    }
  }

  attachProcessHandlers(runId, child, handle) {
    const writeLog = (entry) => {
      if (handle.logStream) {
        handle.logStream.write(
          `[${entry.time}] ${entry.level} ${entry.logger} ${entry.message}\n`
        );
      }
    };

    const handleData = (data, source) => {
      const text = data.toString();
      if (source === "stdout") {
        handle.stdoutBuffer += text;
        const lines = handle.stdoutBuffer.split(/\r?\n/);
        handle.stdoutBuffer = lines.pop() || "";
        lines.filter(Boolean).forEach((line) => {
          const event = parseEventLine(line.trim());
          if (event) {
            this.handleBackendEvent(runId, event);
            return;
          }
          const entry = parseLogLine(line, "stdout");
          this.emit("run-log", { runId, entry });
          writeLog(entry);
          this.updateRunHeartbeat(runId);
        });
        return;
      }

      handle.stderrBuffer += text;
      const lines = handle.stderrBuffer.split(/\r?\n/);
      handle.stderrBuffer = lines.pop() || "";
      lines.filter(Boolean).forEach((line) => {
        const event = parseEventLine(line.trim());
        if (event) {
          this.handleBackendEvent(runId, event);
          return;
        }
        const entry = parseLogLine(line, "stderr");
        this.emit("run-log", { runId, entry });
        writeLog(entry);
        this.updateRunHeartbeat(runId);
      });
    };

    child.stdout.on("data", (data) => handleData(data, "stdout"));
    child.stderr.on("data", (data) => handleData(data, "stderr"));

    child.on("exit", async (code, signal) => {
      this.active.delete(runId);
      this.stopArtifactPolling(runId);
      if (handle.stopTimer) {
        clearTimeout(handle.stopTimer);
        handle.stopTimer = null;
      }
      if (handle.logStream) {
        handle.logStream.end();
      }
      const run = this.getRun(runId);
      const outcome = inferRunOutcome(run?.status, code, signal, run?.stopRequestedAt);
      const finishedAt = nowIso();
      const durationMs = computeDurationMs(run?.startedAt, finishedAt);
      const executionMode = run?.executionMode || computeExecutionMode(run);
      const updated = await this.updateRun(runId, {
        status: outcome,
        exitCode: code,
        signal: signal,
        finishedAt,
        durationMs,
        executionMode,
        lastHeartbeat: nowIso()
      });

      this.emit("run-event", {
        type: "run-exit",
        runId,
        exitCode: code,
        signal,
        status: updated ? updated.status : outcome
      });

      await this.refreshRun(runId);
    });

    child.on("error", async (error) => {
      this.active.delete(runId);
      this.stopArtifactPolling(runId);
      if (handle.stopTimer) {
        clearTimeout(handle.stopTimer);
        handle.stopTimer = null;
      }
      if (handle.logStream) {
        handle.logStream.end();
      }
      const finishedAt = nowIso();
      const durationMs = computeDurationMs(this.getRun(runId)?.startedAt, finishedAt);
      const message = error ? error.message : "Unknown process error";
      await this.updateRun(runId, {
        status: "failed",
        error: { message },
        finishedAt,
        durationMs,
        lastHeartbeat: nowIso()
      });
      this.emit("run-event", {
        type: "run-exit",
        runId,
        exitCode: 1,
        signal: "error",
        status: "failed"
      });
    });
  }

  updateRunHeartbeat(runId) {
    const now = Date.now();
    const lastWrite = this.heartbeatWrites.get(runId) || 0;
    if (now - lastWrite < 2000) {
      return;
    }
    this.heartbeatWrites.set(runId, now);
    this.updateRun(runId, { lastHeartbeat: nowIso() });
  }

  handleBackendEvent(runId, event) {
    this.emit("backend-event", { runId, event });
    const name = event && event.name ? String(event.name) : "";

    if (name === "phase_started") {
      const phase = event.phase;
      if (phase) {
        this.updateRun(runId, {
          phases: updatePhase(this.getRun(runId)?.phases, phase, "running")
        });
      }
    }

    if (name === "extraction_complete") {
      this.updateRun(runId, {
        phases: updatePhase(this.getRun(runId)?.phases, "extraction", "done")
      });
    }

    if (name === "analysis_complete" || name === "gap_analysis_complete") {
      this.updateRun(runId, {
        phases: updatePhase(this.getRun(runId)?.phases, "analysis", "done")
      });
    }

    if (name === "revision_complete" || name === "revision_outputs_ready") {
      const withRevision = updatePhase(this.getRun(runId)?.phases, "revision", "done");
      const withRoadmap = updatePhase(withRevision, "roadmap", "running");
      this.updateRun(runId, {
        phases: withRoadmap
      });
    }

    if (name === "roadmap_ready") {
      this.updateRun(runId, {
        phases: updatePhase(this.getRun(runId)?.phases, "roadmap", "done")
      });
    }

    if (name === "run_dir_created" && event.run_dir) {
      this.updateRun(runId, {
        runDir: event.run_dir,
        outputDir: event.output_dir || this.getRun(runId)?.outputDir || ""
      });
    }

    this.updateRun(runId, { lastHeartbeat: nowIso() });
  }

  startArtifactPolling(runId) {
    if (this.artifactIntervals.has(runId)) {
      return;
    }
    const interval = setInterval(() => {
      void this.refreshArtifacts(runId);
    }, 8000);
    this.artifactIntervals.set(runId, interval);
  }

  stopArtifactPolling(runId) {
    const interval = this.artifactIntervals.get(runId);
    if (interval) {
      clearInterval(interval);
      this.artifactIntervals.delete(runId);
    }
  }

  async refreshArtifacts(runId) {
    const run = this.getRun(runId);
    if (!run || !run.runDir) {
      return null;
    }

    const artifacts = await this.scanArtifacts(run.runDir);
    const nextHash = fingerprintArtifacts(artifacts);
    const currentHash = fingerprintArtifacts(run.artifacts || []);

    if (nextHash === currentHash && run.artifactsUpdatedAt) {
      return run;
    }

    const artifactTotalBytes = artifacts.reduce(
      (total, item) => total + (item.size || 0),
      0
    );
    const updated = await this.updateRun(runId, {
      artifacts,
      artifactsUpdatedAt: nowIso(),
      artifactsCount: artifacts.length,
      artifactTotalBytes
    });
    if (updated) {
      this.emit("run-event", { type: "run-artifacts", runId, artifacts });
    }

    return updated;
  }

  async scanArtifacts(runDir) {
    try {
      const entries = await fs.promises.readdir(runDir, { withFileTypes: true });
      const results = [];
      for (const entry of entries) {
        if (!entry.isFile()) {
          continue;
        }
        const filePath = path.join(runDir, entry.name);
        const stat = await fs.promises.stat(filePath);
        results.push({
          name: entry.name,
          path: filePath,
          size: stat.size,
          mtimeMs: stat.mtimeMs
        });
      }
      results.sort((a, b) => a.name.localeCompare(b.name));
      return results;
    } catch (error) {
      return [];
    }
  }

  async stopRun(runId, force = false) {
    const run = this.getRun(runId);
    if (!run) {
      return { ok: false, error: "Run not found." };
    }

    const handle = this.active.get(runId);
    if (!handle || !handle.process) {
      const updated = await this.updateRun(runId, {
        status: inferRunOutcome(run.status, run.exitCode, run.signal, run.stopRequestedAt),
        finishedAt: run.finishedAt || nowIso()
      });
      return { ok: true, run: updated };
    }

    await this.updateRun(runId, {
      status: force ? "force-stopping" : "stopping",
      stopRequestedAt: nowIso()
    });

    const pid = handle.process.pid;
    this.emit("run-log", {
      runId,
      entry: {
        time: new Date().toISOString(),
        level: force ? "WARNING" : "INFO",
        logger: "app",
        message: force
          ? `Force stopping backend (pid ${pid})`
          : `Stopping backend (pid ${pid})`,
        source: "app"
      }
    });

    this.killProcessTree(pid, force);

    if (!force) {
      handle.stopTimer = setTimeout(() => {
        const activeHandle = this.active.get(runId);
        if (activeHandle && activeHandle.process) {
          this.killProcessTree(activeHandle.process.pid, true);
        }
      }, 4000);
    }

    return { ok: true };
  }

  async refreshRun(runId) {
    const run = this.getRun(runId);
    if (!run) {
      return null;
    }

    await this.refreshArtifacts(runId);
    const summary = await this.readRunJson(runId, "summary.json");
    if (summary) {
      await this.updateRun(runId, { summary });
    }
    const latest = this.getRun(runId);
    const shouldHydrate =
      latest &&
      (latest.runType === "demo" || !ACTIVE_STATUSES.has(latest.status) || !latest.metadataUpdatedAt);
    if (shouldHydrate) {
      await this.hydrateRunMetadata(runId, summary || null);
    }
    return this.getRun(runId);
  }

  async hydrateRunMetadata(runId, summaryOverride) {
    const run = this.getRun(runId);
    if (!run) {
      return null;
    }

    if (!run.runDir || !fs.existsSync(run.runDir)) {
      return this.updateRun(runId, {
        runDirExists: false,
        missingArtifacts: ["run_dir"],
        metadataUpdatedAt: nowIso()
      });
    }

    const missingArtifacts = REQUIRED_RUN_FILES.filter((name) =>
      !fs.existsSync(path.join(run.runDir, name))
    );

    const [sections, masterList, assessments, summary] = await Promise.all([
      this.readRunJson(runId, "sections_output.json"),
      this.readRunJson(runId, "master_list.json"),
      this.readRunJson(runId, "assessments.json"),
      summaryOverride || this.readRunJson(runId, "summary.json")
    ]);

    const assessmentCounts = summarizeAssessments(assessments);
    const reportCount = summary && summary.reports
      ? Object.keys(summary.reports).length
      : null;
    const artifacts = Array.isArray(run.artifacts) ? run.artifacts : [];
    const artifactTotalBytes = artifacts.reduce((total, item) => total + (item.size || 0), 0);

    return this.updateRun(runId, {
      runDirExists: true,
      missingArtifacts,
      reportCount: Number.isFinite(reportCount) ? reportCount : null,
      sectionCount: Array.isArray(sections) ? sections.length : null,
      masterListCount: Array.isArray(masterList) ? masterList.length : null,
      assessmentCount: assessmentCounts.total,
      gapCount: assessmentCounts.notAddressed,
      partialCount: assessmentCounts.partiallyAddressed,
      addressedCount: assessmentCounts.addressed,
      outOfScopeCount: assessmentCounts.outOfScope,
      artifactsCount: artifacts.length,
      artifactTotalBytes,
      hasRevision: fs.existsSync(path.join(run.runDir, "revision_report.md")),
      hasRevisedPolicy: fs.existsSync(path.join(run.runDir, "revised_policy.md")),
      hasRoadmap: fs.existsSync(path.join(run.runDir, "improvement_roadmap.md")),
      executionMode: run.executionMode || computeExecutionMode(run),
      durationMs: run.durationMs || computeDurationMs(run.startedAt, run.finishedAt),
      metadataUpdatedAt: nowIso()
    });
  }

  async readRunJson(runId, fileName) {
    if (!ALLOWED_RUN_FILES.has(fileName)) {
      return null;
    }
    const run = this.getRun(runId);
    if (!run || !run.runDir) {
      return null;
    }
    const filePath = path.join(run.runDir, fileName);
    try {
      const stat = await fs.promises.stat(filePath);
      if (stat.size > RUN_FILE_LIMITS.json) {
        return null;
      }
      const raw = await fs.promises.readFile(filePath, "utf-8");
      return JSON.parse(raw);
    } catch (error) {
      return null;
    }
  }

  async readRunText(runId, fileName, maxBytes) {
    if (!ALLOWED_RUN_FILES.has(fileName)) {
      return null;
    }
    const run = this.getRun(runId);
    if (!run || !run.runDir) {
      return null;
    }
    const filePath = path.join(run.runDir, fileName);
    try {
      const stat = await fs.promises.stat(filePath);
      const limit = maxBytes || RUN_FILE_LIMITS.text;
      if (stat.size > limit) {
        const handle = await fs.promises.open(filePath, "r");
        try {
          const start = Math.max(0, stat.size - limit);
          const length = stat.size - start;
          const buffer = Buffer.alloc(length);
          await handle.read(buffer, 0, length, start);
          return buffer.toString("utf-8");
        } finally {
          await handle.close();
        }
      }
      return await fs.promises.readFile(filePath, "utf-8");
    } catch (error) {
      return null;
    }
  }

  async clearRunLog(runId) {
    const run = this.getRun(runId);
    if (!run || !run.runDir) {
      return { ok: false, error: "Run not found." };
    }
    if (ACTIVE_STATUSES.has(run.status)) {
      return { ok: false, error: "Stop the run before clearing logs." };
    }
    const logPath = path.join(run.runDir, "run.log");
    try {
      await fs.promises.writeFile(logPath, "", "utf-8");
      return { ok: true };
    } catch (error) {
      return { ok: false, error: "Failed to clear run log." };
    }
  }

  async scanRuns(baseDir) {
    if (!baseDir) {
      return [];
    }

    let targetDir = baseDir;
    if (!path.isAbsolute(baseDir)) {
      targetDir = path.resolve(this.baseCwd, baseDir);
    }

    let entries = [];
    try {
      entries = await fs.promises.readdir(targetDir, { withFileTypes: true });
    } catch (error) {
      return [];
    }

    const results = [];
    for (const entry of entries) {
      if (!entry.isDirectory()) {
        continue;
      }
      const runDir = path.join(targetDir, entry.name);
      const summaryPath = path.join(runDir, "summary.json");
      if (!fs.existsSync(summaryPath)) {
        continue;
      }
      const runId = entry.name;
      const existing = this.getRun(runId);
      const existingByDir = this.store.listRuns().find((run) => run.runDir === runDir);
      if (existing || existingByDir) {
        results.push(existing || existingByDir);
        continue;
      }
      const newRun = await this.store.upsertRun({
        id: runId,
        status: "completed",
        runType: "real",
        runName: "",
        createdAt: nowIso(),
        updatedAt: nowIso(),
        runDir,
        outputDir: targetDir,
        phases: clonePhases(DEFAULT_PHASES)
      });
      this.emit("run-event", { type: "run-created", run: newRun });
      await this.refreshRun(runId);
      results.push(newRun);
    }

    return results;
  }

  async ensureDemoRun(demoRunDir) {
    if (!demoRunDir || !fs.existsSync(demoRunDir)) {
      return null;
    }

    const summary = await readJsonFile(path.join(demoRunDir, "summary.json"));
    const sections = await readJsonFile(path.join(demoRunDir, "sections_output.json"));
    const policyName = Array.isArray(sections) && sections[0]?.title
      ? sections[0].title
      : "Demo policy";
    const createdAt = summary && summary.timestamp ? summary.timestamp : nowIso();
    const existing = this.getRun(DEMO_RUN_ID);

    const runRecord = await this.store.upsertRun({
      id: DEMO_RUN_ID,
      status: "completed",
      runType: "demo",
      runName: existing?.runName || "Guided demo",
      pinned: existing?.pinned ?? true,
      createdAt: existing?.createdAt || createdAt,
      updatedAt: nowIso(),
      runDir: demoRunDir,
      outputDir: path.dirname(demoRunDir),
      pdfPath: "",
      provider: existing?.provider || "demo",
      model: existing?.model || "offline-sample",
      executionMode: "Demo",
      policyName,
      phases: clonePhases(DEFAULT_PHASES),
      tags: Array.isArray(existing?.tags) && existing.tags.length ? existing.tags : ["demo"],
      notes: existing?.notes || "Read-only demo run"
    });

    if (!existing) {
      this.emit("run-event", { type: "run-created", run: runRecord });
    } else {
      this.emit("run-event", { type: "run-updated", run: runRecord });
    }

    await this.refreshRun(DEMO_RUN_ID);
    return runRecord;
  }

  async removeRun(runId, options) {
    const run = this.getRun(runId);
    if (!run) {
      return { ok: false, error: "Run not found." };
    }
    if (run.id === DEMO_RUN_ID || run.runType === "demo") {
      return { ok: false, error: "Demo runs cannot be removed." };
    }
    if (ACTIVE_STATUSES.has(run.status)) {
      return { ok: false, error: "Stop the run before removing it." };
    }

    if (options && options.deleteFiles && run.runDir) {
      try {
        await fs.promises.rm(run.runDir, { recursive: true, force: true });
      } catch (error) {
        return { ok: false, error: "Failed to delete run files." };
      }
    }

    await this.store.removeRun(runId);
    this.emit("run-event", { type: "run-removed", runId });
    return { ok: true };
  }

  async recoverRuns() {
    const runs = this.store.listRuns();
    for (const run of runs) {
      if (!ACTIVE_STATUSES.has(run.status)) {
        continue;
      }
      const alive = isProcessAlive(run.pid);
      if (alive) {
        await this.updateRun(run.id, {
          status: "recovering",
          lastHeartbeat: nowIso()
        });
        this.startArtifactPolling(run.id);
      } else {
        const summaryExists = run.runDir
          ? fs.existsSync(path.join(run.runDir, "summary.json"))
          : false;
        const nextStatus = summaryExists
          ? "completed"
          : run.stopRequestedAt
          ? "cancelled"
          : "orphaned";
        await this.updateRun(run.id, {
          status: nextStatus,
          finishedAt: run.finishedAt || nowIso(),
          lastHeartbeat: nowIso()
        });
        if (run.runDir) {
          await this.refreshArtifacts(run.id);
        }
        if (summaryExists) {
          await this.refreshRun(run.id);
        }
      }
    }
  }
}

module.exports = {
  JobManager,
  DEFAULT_PHASES
};
