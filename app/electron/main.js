const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn, execFile } = require("child_process");
const { promisify } = require("util");

const { RunStore } = require("./services/run_store");
const { JobManager } = require("./services/job_manager");

const execFileAsync = promisify(execFile);

const isDev = !app.isPackaged;
const repoRoot = path.resolve(__dirname, "..", "..");
const rendererDist = path.join(__dirname, "..", "dist", "renderer");
const preloadPath = path.join(__dirname, "preload.js");

let mainWindow = null;
let jobManager = null;
let runStore = null;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: "#0b1014",
    webPreferences: {
      contextIsolation: true,
      preload: preloadPath,
      nodeIntegration: false
    }
  });

  if (isDev) {
    const devUrl = process.env.VITE_DEV_SERVER_URL || "http://localhost:5173";
    mainWindow.loadURL(devUrl);
    if (process.env.ELECTRON_DEVTOOLS === "1") {
      mainWindow.webContents.openDevTools({ mode: "detach" });
    }
  } else {
    mainWindow.loadFile(path.join(rendererDist, "index.html"));
  }
}

function configPath() {
  return path.join(app.getPath("userData"), "config.json");
}

async function readConfig() {
  try {
    const raw = await fs.promises.readFile(configPath(), "utf-8");
    return JSON.parse(raw);
  } catch (err) {
    return {};
  }
}

async function writeConfig(nextConfig) {
  const current = await readConfig();
  const merged = { ...current, ...nextConfig };
  await fs.promises.writeFile(configPath(), JSON.stringify(merged, null, 2));
  return merged;
}

function resolvePython() {
  if (process.env.GAP_HUNTER_PYTHON) {
    return process.env.GAP_HUNTER_PYTHON;
  }

  const venvRoot = path.join(repoRoot, ".venv");
  const candidates = process.platform === "win32"
    ? [path.join(venvRoot, "Scripts", "python.exe")]
    : [
        path.join(venvRoot, "bin", "python3"),
        path.join(venvRoot, "bin", "python")
      ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return process.platform === "win32" ? "python" : "python3";
}

function backendBinaryName() {
  return process.platform === "win32" ? "gap-hunter-backend.exe" : "gap-hunter-backend";
}

function resolveBackendCommand() {
  if (isDev) {
    return {
      command: resolvePython(),
      baseArgs: ["-u", path.join(repoRoot, "src", "main.py")],
      cwd: repoRoot
    };
  }

  const backendPath = path.join(process.resourcesPath, "backend", backendBinaryName());
  if (!fs.existsSync(backendPath)) {
    throw new Error(`Backend binary not found: ${backendPath}`);
  }

  if (process.platform !== "win32") {
    try {
      fs.chmodSync(backendPath, 0o755);
    } catch (err) {
      // Ignore chmod failures
    }
  }

  return {
    command: backendPath,
    baseArgs: [],
    cwd: process.resourcesPath
  };
}

function buildBackendArgs(params) {
  const args = [];

  if (params.pdfPath) {
    args.push(params.pdfPath);
  }

  if (params.model) {
    args.push("--model", params.model);
  }

  if (params.outputDir) {
    args.push("--output-dir", params.outputDir);
  }

  if (params.runDir) {
    args.push("--run-dir", params.runDir);
  }

  if (params.windowSize) {
    args.push("--window-size", String(params.windowSize));
  }

  if (params.overlap) {
    args.push("--overlap", String(params.overlap));
  }

  if (params.extractOnly) {
    args.push("--extract-only");
  }

  if (params.skipRevision) {
    args.push("--skip-revision");
  }

  if (params.skipExtraction) {
    args.push("--skip-extraction");
  }

  if (params.revisionOnly) {
    args.push("--revision-only");
  }

  if (params.ollamaUrl) {
    args.push("--ollama-url", params.ollamaUrl);
  }

  if (params.provider) {
    args.push("--llm-provider", params.provider);
  }

  if (params.ggufModelPath) {
    args.push("--gguf-model-path", params.ggufModelPath);
  }

  return args;
}

function sendToRenderer(channel, payload) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, payload);
  }
}

function killProcessTree(pid, force) {
  if (!pid) {
    return;
  }

  if (process.platform === "win32") {
    const args = ["/PID", String(pid), "/T"];
    if (force) {
      args.push("/F");
    }
    spawn("taskkill", args, { windowsHide: true });
    return;
  }

  try {
    process.kill(-pid, force ? "SIGKILL" : "SIGTERM");
    return;
  } catch (error) {
    try {
      process.kill(pid, force ? "SIGKILL" : "SIGTERM");
    } catch (innerError) {
      // Ignore if already exited.
    }
  }
}

async function getBackendStats(pid) {
  if (!pid) {
    return null;
  }

  if (process.platform === "win32") {
    try {
      const { stdout } = await execFileAsync("tasklist", [
        "/FI",
        `PID eq ${pid}`,
        "/FO",
        "CSV",
        "/NH"
      ]);
      const line = stdout.trim();
      if (!line) {
        return null;
      }
      const cleaned = line.replace(/^"|"$/g, "");
      const parts = cleaned.split("\",\"");
      const memRaw = parts[4] || "";
      const memValue = Number(memRaw.replace(/[^0-9.]/g, ""));
      const memMb = Number.isFinite(memValue) ? memValue / 1024 : null;
      return { pid, memoryMb: memMb, cpuPercent: null };
    } catch (error) {
      return null;
    }
  }

  try {
    const { stdout } = await execFileAsync("ps", ["-o", "%cpu=,rss=", "-p", String(pid)]);
    const raw = stdout.trim();
    if (!raw) {
      return null;
    }
    const parts = raw.split(/\s+/);
    const cpu = Number.parseFloat(parts[0]);
    const rssKb = Number.parseInt(parts[1], 10);
    return {
      pid,
      cpuPercent: Number.isFinite(cpu) ? cpu : null,
      memoryMb: Number.isFinite(rssKb) ? rssKb / 1024 : null
    };
  } catch (error) {
    return null;
  }
}

function filterRunUpdates(updates) {
  const safe = {};
  if (Array.isArray(updates.tags)) {
    safe.tags = updates.tags.map((tag) => String(tag).trim()).filter(Boolean);
  }
  if (typeof updates.notes === "string") {
    safe.notes = updates.notes;
  }
  if (typeof updates.policyName === "string") {
    safe.policyName = updates.policyName;
  }
  if (typeof updates.runName === "string") {
    safe.runName = updates.runName;
  }
  if (typeof updates.pinned === "boolean") {
    safe.pinned = updates.pinned;
  }
  return safe;
}

function resolveDemoRunDir() {
  const candidates = [
    path.join(repoRoot, "app", "resources", "demo-run"),
    path.join(repoRoot, "gap_analysis_reports", "20260408_030937"),
    path.join(process.resourcesPath || "", "demo-run")
  ];
  for (const candidate of candidates) {
    if (!candidate || !fs.existsSync(candidate)) {
      continue;
    }
    const summaryPath = path.join(candidate, "summary.json");
    if (fs.existsSync(summaryPath)) {
      return candidate;
    }
  }
  return null;
}

app.whenReady().then(async () => {
  createWindow();

  runStore = new RunStore(app.getPath("userData"));
  jobManager = new JobManager({
    store: runStore,
    resolveBackendCommand,
    buildBackendArgs,
    killProcessTree,
    baseCwd: isDev ? repoRoot : process.resourcesPath
  });
  await jobManager.initialize();

  const demoRunDir = resolveDemoRunDir();
  if (demoRunDir) {
    await jobManager.ensureDemoRun(demoRunDir);
  }

  jobManager.on("run-event", (event) => sendToRenderer("runs:event", event));
  jobManager.on("run-log", (payload) =>
    sendToRenderer("runs:event", { type: "run-log", ...payload })
  );
  jobManager.on("backend-event", (payload) =>
    sendToRenderer("runs:event", { type: "backend-event", ...payload })
  );

  ipcMain.handle("config:get", async () => readConfig());
  ipcMain.handle("config:set", async (_event, config) => writeConfig(config));

  ipcMain.handle("dialog:select-pdf", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"],
      filters: [{ name: "PDF", extensions: ["pdf"] }]
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return result.filePaths[0];
  });

  ipcMain.handle("dialog:select-directory", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openDirectory", "createDirectory"]
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return result.filePaths[0];
  });

  ipcMain.handle("shell:open-path", async (_event, targetPath) => {
    if (!targetPath) {
      return;
    }
    await shell.openPath(targetPath);
  });

  ipcMain.handle("runs:snapshot", async () => jobManager.getSnapshot());

  ipcMain.handle("runs:start", async (_event, params) => {
    const policyName = params && params.pdfPath ? path.basename(params.pdfPath) : "";
    return jobManager.startRun(params, { policyName });
  });

  ipcMain.handle("runs:stop", async (_event, payload) => {
    const runId = payload && payload.runId ? payload.runId : jobManager.getSnapshot().selectedRunId;
    if (!runId) {
      return { ok: false, error: "No run selected." };
    }
    return jobManager.stopRun(runId, payload && payload.force);
  });

  ipcMain.handle("runs:select", async (_event, runId) => {
    await jobManager.selectRun(runId);
    return jobManager.getSnapshot();
  });

  ipcMain.handle("runs:update", async (_event, payload) => {
    if (!payload || !payload.runId) {
      return null;
    }
    const safeUpdates = filterRunUpdates(payload.updates || {});
    return jobManager.updateRun(payload.runId, safeUpdates);
  });

  ipcMain.handle("runs:remove", async (_event, payload) => {
    if (!payload || !payload.runId) {
      return { ok: false, error: "Run id is required." };
    }
    return jobManager.removeRun(payload.runId, {
      deleteFiles: Boolean(payload.deleteFiles)
    });
  });

  ipcMain.handle("runs:refresh", async (_event, runId) => jobManager.refreshRun(runId));
  ipcMain.handle("runs:scan", async (_event, baseDir) => jobManager.scanRuns(baseDir));

  ipcMain.handle("runs:read-json", async (_event, payload) => {
    if (!payload || !payload.runId || !payload.fileName) {
      return null;
    }
    return jobManager.readRunJson(payload.runId, payload.fileName);
  });

  ipcMain.handle("runs:read-text", async (_event, payload) => {
    if (!payload || !payload.runId || !payload.fileName) {
      return null;
    }
    return jobManager.readRunText(payload.runId, payload.fileName, payload.maxBytes);
  });

  ipcMain.handle("runs:clear-log", async (_event, runId) => {
    if (!runId) {
      return { ok: false, error: "Run id is required." };
    }
    return jobManager.clearRunLog(runId);
  });

  ipcMain.handle("app:info", async () => {
    return {
      appVersion: app.getVersion(),
      electron: process.versions.electron,
      chrome: process.versions.chrome,
      node: process.versions.node,
      platform: process.platform,
      arch: process.arch
    };
  });

  ipcMain.handle("process:stats", async (_event, runId) => {
    const targetRun = runId ? jobManager.getRun(runId) : jobManager.getActiveRun();
    const appMemory = process.memoryUsage();
    const backendStats = targetRun?.pid ? await getBackendStats(targetRun.pid) : null;
    return {
      timestamp: new Date().toISOString(),
      app: {
        rssMb: appMemory.rss / 1024 / 1024,
        heapUsedMb: appMemory.heapUsed / 1024 / 1024,
        heapTotalMb: appMemory.heapTotal / 1024 / 1024
      },
      backend: backendStats
    };
  });

  ipcMain.handle("ollama:test", async (_event, url) => {
    if (!url) {
      return { ok: false, error: "Missing Ollama URL" };
    }

    const normalized = url.replace(/\/+$/, "");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    const start = Date.now();

    try {
      const response = await fetch(`${normalized}/api/tags`, {
        signal: controller.signal
      });
      clearTimeout(timeout);

      const durationMs = Date.now() - start;

      if (!response.ok) {
        return {
          ok: false,
          status: response.status,
          error: "Request failed",
          durationMs
        };
      }

      const data = await response.json();
      const models = Array.isArray(data.models) ? data.models.map((m) => m.name) : [];
      return { ok: true, status: response.status, models, durationMs };
    } catch (error) {
      clearTimeout(timeout);
      return { ok: false, error: error.message || "Connection failed", durationMs: Date.now() - start };
    }
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("before-quit", (event) => {
  if (isQuitting) {
    return;
  }
  const activeRun = jobManager ? jobManager.getActiveRun() : null;
  if (activeRun && activeRun.id) {
    event.preventDefault();
    isQuitting = true;
    void jobManager.stopRun(activeRun.id, false);
    setTimeout(() => {
      void jobManager.stopRun(activeRun.id, true);
      if (runStore) {
        void runStore.markShutdown();
      }
      app.quit();
    }, 5000);
    return;
  }

  if (runStore) {
    void runStore.markShutdown();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
