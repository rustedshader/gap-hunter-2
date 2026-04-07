const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");

const isDev = !app.isPackaged;
const repoRoot = path.resolve(__dirname, "..", "..");
const rendererDist = path.join(__dirname, "..", "dist", "renderer");
const preloadPath = path.join(__dirname, "preload.js");

let mainWindow = null;
let backendProcess = null;
let stdoutBuffer = "";
let stderrBuffer = "";

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

function sendToRenderer(channel, payload) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, payload);
  }
}

function handleStreamData(data, source) {
  const text = data.toString();
  if (source === "stdout") {
    stdoutBuffer += text;
    const lines = stdoutBuffer.split(/\r?\n/);
    stdoutBuffer = lines.pop() || "";
    lines.filter(Boolean).forEach((line) => {
      sendToRenderer("backend:log", parseLogLine(line, "stdout"));
    });
    return;
  }

  stderrBuffer += text;
  const lines = stderrBuffer.split(/\r?\n/);
  stderrBuffer = lines.pop() || "";
  lines.filter(Boolean).forEach((line) => {
    sendToRenderer("backend:log", parseLogLine(line, "stderr"));
  });
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

app.whenReady().then(() => {
  createWindow();

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

  ipcMain.handle("backend:start", async (_event, params) => {
    if (backendProcess) {
      return { ok: false, error: "A run is already in progress." };
    }

    try {
      const { command, baseArgs, cwd } = resolveBackendCommand();
      const args = [...baseArgs, ...buildBackendArgs(params)];

      sendToRenderer("backend:log", {
        time: new Date().toISOString(),
        level: "INFO",
        logger: "app",
        message: `Launching backend: ${[command, ...args].join(" ")}`,
        source: "app"
      });

      backendProcess = spawn(command, args, {
        cwd,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: "1",
          PYTHONUTF8: "1"
        },
        detached: process.platform !== "win32"
      });

      stdoutBuffer = "";
      stderrBuffer = "";

      backendProcess.stdout.on("data", (data) => handleStreamData(data, "stdout"));
      backendProcess.stderr.on("data", (data) => handleStreamData(data, "stderr"));

      backendProcess.on("exit", (code, signal) => {
        sendToRenderer("backend:exit", { code, signal });
        sendToRenderer("backend:status", { state: "stopped" });
        backendProcess = null;
      });

      backendProcess.on("error", (error) => {
        sendToRenderer("backend:log", {
          time: new Date().toISOString(),
          level: "ERROR",
          logger: "backend",
          message: error.message,
          source: "stderr"
        });
        sendToRenderer("backend:exit", { code: 1, signal: "error" });
        sendToRenderer("backend:status", { state: "error" });
        backendProcess = null;
      });

      sendToRenderer("backend:status", { state: "running", pid: backendProcess.pid });
      return { ok: true };
    } catch (error) {
      return { ok: false, error: error.message || "Failed to start backend" };
    }
  });

  ipcMain.handle("backend:stop", async (_event, options) => {
    if (!backendProcess) {
      return { ok: true };
    }

    const force = Boolean(options && options.force);
    const pid = backendProcess.pid;

    sendToRenderer("backend:log", {
      time: new Date().toISOString(),
      level: force ? "WARNING" : "INFO",
      logger: "app",
      message: force
        ? `Force stopping backend (pid ${pid})`
        : `Stopping backend (pid ${pid})`,
      source: "app"
    });

    killProcessTree(pid, force);

    if (!force) {
      setTimeout(() => {
        if (backendProcess) {
          killProcessTree(pid, true);
        }
      }, 4000);
    }

    return { ok: true };
  });

  ipcMain.handle("backend:list-artifacts", async (_event, runDir) => {
    if (!runDir) {
      return [];
    }

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
          size: stat.size
        });
      }

      results.sort((a, b) => a.name.localeCompare(b.name));
      return results;
    } catch (error) {
      return [];
    }
  });

  ipcMain.handle("backend:read-summary", async (_event, runDir) => {
    if (!runDir) {
      return null;
    }

    const summaryPath = path.join(runDir, "summary.json");
    try {
      const raw = await fs.promises.readFile(summaryPath, "utf-8");
      return JSON.parse(raw);
    } catch (error) {
      return null;
    }
  });

  ipcMain.handle("ollama:test", async (_event, url) => {
    if (!url) {
      return { ok: false, error: "Missing Ollama URL" };
    }

    const normalized = url.replace(/\/+$/, "");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);

    try {
      const response = await fetch(`${normalized}/api/tags`, {
        signal: controller.signal
      });
      clearTimeout(timeout);

      if (!response.ok) {
        return { ok: false, status: response.status, error: "Request failed" };
      }

      const data = await response.json();
      const models = Array.isArray(data.models) ? data.models.map((m) => m.name) : [];
      return { ok: true, status: response.status, models };
    } catch (error) {
      clearTimeout(timeout);
      return { ok: false, error: error.message || "Connection failed" };
    }
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
