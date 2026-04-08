const fs = require("fs");
const path = require("path");

const STORE_VERSION = 2;

function nowIso() {
  return new Date().toISOString();
}

async function safeReadJson(filePath) {
  try {
    const raw = await fs.promises.readFile(filePath, "utf-8");
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
}

async function atomicWriteJson(filePath, payload) {
  const dir = path.dirname(filePath);
  await fs.promises.mkdir(dir, { recursive: true });
  const tempPath = path.join(
    dir,
    `.${path.basename(filePath)}.${process.pid}.${Date.now()}.${Math.random()
      .toString(16)
      .slice(2)}.tmp`
  );
  const data = JSON.stringify(payload, null, 2);

  await fs.promises.writeFile(tempPath, data, "utf-8");
  try {
    await fs.promises.rename(tempPath, filePath);
  } catch (error) {
    if (error && (error.code === "EEXIST" || error.code === "EPERM")) {
      try {
        await fs.promises.unlink(filePath);
      } catch (innerError) {
        // Ignore unlink failures.
      }
      await fs.promises.rename(tempPath, filePath);
      return;
    }
    throw error;
  }
}

function normalizeStatus(status) {
  if (!status) {
    return "unknown";
  }
  const value = status.toLowerCase();
  if (value.includes("success") || value.includes("complete")) {
    return "completed";
  }
  if (value.includes("fail") || value.includes("error")) {
    return "failed";
  }
  if (value.includes("cancel")) {
    return "cancelled";
  }
  if (value.includes("running")) {
    return "running";
  }
  return status;
}

function normalizeRunRecord(run) {
  if (!run || !run.id) {
    return null;
  }

  return {
    id: String(run.id),
    status: run.status || "unknown",
    runType: run.runType || "real",
    runName: run.runName || "",
    pinned: Boolean(run.pinned),
    createdAt: run.createdAt || nowIso(),
    updatedAt: run.updatedAt || run.createdAt || nowIso(),
    startedAt: run.startedAt || null,
    finishedAt: run.finishedAt || null,
    stopRequestedAt: run.stopRequestedAt || null,
    durationMs: Number.isFinite(run.durationMs) ? run.durationMs : null,
    runDir: run.runDir || "",
    outputDir: run.outputDir || "",
    pdfPath: run.pdfPath || "",
    provider: run.provider || "",
    model: run.model || "",
    ggufModelPath: run.ggufModelPath || "",
    ollamaUrl: run.ollamaUrl || "",
    windowSize: Number.isFinite(run.windowSize) ? run.windowSize : null,
    overlap: Number.isFinite(run.overlap) ? run.overlap : null,
    extractOnly: Boolean(run.extractOnly),
    skipRevision: Boolean(run.skipRevision),
    skipExtraction: Boolean(run.skipExtraction),
    revisionOnly: Boolean(run.revisionOnly),
    executionMode: run.executionMode || "",
    pid: Number.isFinite(run.pid) ? run.pid : null,
    exitCode: run.exitCode ?? null,
    signal: run.signal ?? null,
    error: run.error || null,
    phases: Array.isArray(run.phases) ? run.phases : null,
    progress: run.progress ?? null,
    lastHeartbeat: run.lastHeartbeat || null,
    artifacts: Array.isArray(run.artifacts) ? run.artifacts : [],
    artifactsUpdatedAt: run.artifactsUpdatedAt || null,
    summary: run.summary || null,
    reportCount: Number.isFinite(run.reportCount) ? run.reportCount : null,
    sectionCount: Number.isFinite(run.sectionCount) ? run.sectionCount : null,
    masterListCount: Number.isFinite(run.masterListCount) ? run.masterListCount : null,
    assessmentCount: Number.isFinite(run.assessmentCount) ? run.assessmentCount : null,
    gapCount: Number.isFinite(run.gapCount) ? run.gapCount : null,
    partialCount: Number.isFinite(run.partialCount) ? run.partialCount : null,
    addressedCount: Number.isFinite(run.addressedCount) ? run.addressedCount : null,
    outOfScopeCount: Number.isFinite(run.outOfScopeCount) ? run.outOfScopeCount : null,
    artifactsCount: Number.isFinite(run.artifactsCount) ? run.artifactsCount : null,
    artifactTotalBytes: Number.isFinite(run.artifactTotalBytes)
      ? run.artifactTotalBytes
      : null,
    runDirExists: typeof run.runDirExists === "boolean" ? run.runDirExists : null,
    missingArtifacts: Array.isArray(run.missingArtifacts) ? run.missingArtifacts : [],
    hasRevision: Boolean(run.hasRevision),
    hasRevisedPolicy: Boolean(run.hasRevisedPolicy),
    hasRoadmap: Boolean(run.hasRoadmap),
    metadataUpdatedAt: run.metadataUpdatedAt || null,
    tags: Array.isArray(run.tags) ? run.tags : [],
    notes: run.notes || "",
    policyName: run.policyName || "",
    command: run.command || "",
    args: Array.isArray(run.args) ? run.args : [],
    cwd: run.cwd || "",
    version: Number.isFinite(run.version) ? run.version : 0
  };
}

function historyEntryToRun(entry) {
  if (!entry || !entry.runDir) {
    return null;
  }
  const runId = entry.id || path.basename(entry.runDir);
  return normalizeRunRecord({
    id: runId,
    runDir: entry.runDir,
    createdAt: entry.createdAt || nowIso(),
    updatedAt: entry.createdAt || nowIso(),
    status: normalizeStatus(entry.status),
    runType: "real",
    policyName: entry.policyName || "",
    model: entry.model || "",
    provider: entry.provider || "",
    tags: entry.tags || [],
    notes: entry.notes || ""
  });
}

class RunStore {
  constructor(baseDir) {
    this.baseDir = baseDir;
    this.storePath = path.join(baseDir, "runs.json");
    this.historyPath = path.join(baseDir, "run_history.json");
    this.state = {
      version: STORE_VERSION,
      updatedAt: nowIso(),
      runs: [],
      selectedRunId: null,
      lastShutdownAt: null
    };
  }

  async load() {
    const existing = await safeReadJson(this.storePath);
    if (existing && Array.isArray(existing.runs)) {
      this.state = {
        version: existing.version || STORE_VERSION,
        updatedAt: existing.updatedAt || nowIso(),
        runs: existing.runs.map(normalizeRunRecord).filter(Boolean),
        selectedRunId: existing.selectedRunId || null,
        lastShutdownAt: existing.lastShutdownAt || null
      };
      return this.state;
    }

    const history = await safeReadJson(this.historyPath);
    const entries = Array.isArray(history)
      ? history
      : history && Array.isArray(history.entries)
      ? history.entries
      : [];
    const runs = entries.map(historyEntryToRun).filter(Boolean);
    this.state = {
      version: STORE_VERSION,
      updatedAt: nowIso(),
      runs,
      selectedRunId: null,
      lastShutdownAt: null
    };

    if (runs.length > 0) {
      await this.save();
    }

    return this.state;
  }

  async save() {
    this.state.updatedAt = nowIso();
    await atomicWriteJson(this.storePath, this.state);
    return this.state;
  }

  listRuns() {
    return [...this.state.runs].sort((a, b) =>
      (b.updatedAt || b.createdAt || "").localeCompare(a.updatedAt || a.createdAt || "")
    );
  }

  getRun(runId) {
    return this.state.runs.find((run) => run.id === runId) || null;
  }

  async upsertRun(run) {
    const normalized = normalizeRunRecord(run);
    if (!normalized) {
      return null;
    }

    const index = this.state.runs.findIndex((item) => item.id === normalized.id);
    if (index >= 0) {
      this.state.runs[index] = { ...this.state.runs[index], ...normalized };
    } else {
      this.state.runs.unshift(normalized);
    }

    await this.save();
    return normalized;
  }

  async updateRun(runId, patch) {
    const run = this.getRun(runId);
    if (!run) {
      return null;
    }

    const updated = normalizeRunRecord({
      ...run,
      ...patch,
      id: runId,
      updatedAt: nowIso(),
      version: (run.version || 0) + 1
    });

    const index = this.state.runs.findIndex((item) => item.id === runId);
    if (index >= 0) {
      this.state.runs[index] = updated;
    }

    await this.save();
    return updated;
  }

  async removeRun(runId) {
    this.state.runs = this.state.runs.filter((run) => run.id !== runId);
    if (this.state.selectedRunId === runId) {
      this.state.selectedRunId = null;
    }
    await this.save();
  }

  async setSelectedRunId(runId) {
    this.state.selectedRunId = runId || null;
    await this.save();
  }

  async markShutdown() {
    this.state.lastShutdownAt = nowIso();
    await this.save();
  }
}

module.exports = {
  RunStore,
  STORE_VERSION
};
