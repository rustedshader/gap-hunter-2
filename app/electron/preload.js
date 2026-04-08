const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  loadConfig: () => ipcRenderer.invoke("config:get"),
  saveConfig: (config) => ipcRenderer.invoke("config:set", config),
  selectPdf: () => ipcRenderer.invoke("dialog:select-pdf"),
  selectDirectory: () => ipcRenderer.invoke("dialog:select-directory"),
  startRun: (params) => ipcRenderer.invoke("runs:start", params),
  stopRun: (payload) => ipcRenderer.invoke("runs:stop", payload),
  getRunsSnapshot: () => ipcRenderer.invoke("runs:snapshot"),
  selectRun: (runId) => ipcRenderer.invoke("runs:select", runId),
  updateRun: (runId, updates) => ipcRenderer.invoke("runs:update", { runId, updates }),
  refreshRun: (runId) => ipcRenderer.invoke("runs:refresh", runId),
  scanRuns: (baseDir) => ipcRenderer.invoke("runs:scan", baseDir),
  removeRun: (runId, options) => ipcRenderer.invoke("runs:remove", { runId, ...options }),
  readRunJson: (runId, fileName) =>
    ipcRenderer.invoke("runs:read-json", { runId, fileName }),
  readRunText: (runId, fileName, maxBytes) =>
    ipcRenderer.invoke("runs:read-text", { runId, fileName, maxBytes }),
  clearRunLog: (runId) => ipcRenderer.invoke("runs:clear-log", runId),
  getAppInfo: () => ipcRenderer.invoke("app:info"),
  getProcessStats: (runId) => ipcRenderer.invoke("process:stats", runId),
  openPath: (targetPath) => ipcRenderer.invoke("shell:open-path", targetPath),
  testOllama: (url) => ipcRenderer.invoke("ollama:test", url),
  onRunEvent: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on("runs:event", listener);
    return () => ipcRenderer.removeListener("runs:event", listener);
  }
});
