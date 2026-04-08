const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  loadConfig: () => ipcRenderer.invoke("config:get"),
  saveConfig: (config) => ipcRenderer.invoke("config:set", config),
  selectPdf: () => ipcRenderer.invoke("dialog:select-pdf"),
  selectDirectory: () => ipcRenderer.invoke("dialog:select-directory"),
  startRun: (params) => ipcRenderer.invoke("backend:start", params),
  stopRun: (options) => ipcRenderer.invoke("backend:stop", options),
  listArtifacts: (runDir) => ipcRenderer.invoke("backend:list-artifacts", runDir),
  readSummary: (runDir) => ipcRenderer.invoke("backend:read-summary", runDir),
  readJson: (filePath) => ipcRenderer.invoke("backend:read-json", filePath),
  readText: (filePath, maxBytes) => ipcRenderer.invoke("backend:read-text", filePath, maxBytes),
  historyList: () => ipcRenderer.invoke("history:list"),
  historyAdd: (entry) => ipcRenderer.invoke("history:add", entry),
  historyUpdate: (entry) => ipcRenderer.invoke("history:update", entry),
  historyRemove: (runDir) => ipcRenderer.invoke("history:remove", runDir),
  historyScan: (baseDir) => ipcRenderer.invoke("history:scan", baseDir),
  getAppInfo: () => ipcRenderer.invoke("app:info"),
  getProcessStats: () => ipcRenderer.invoke("process:stats"),
  openPath: (targetPath) => ipcRenderer.invoke("shell:open-path", targetPath),
  testOllama: (url) => ipcRenderer.invoke("ollama:test", url),
  onEvent: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on("backend:event", listener);
    return () => ipcRenderer.removeListener("backend:event", listener);
  },
  onLog: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on("backend:log", listener);
    return () => ipcRenderer.removeListener("backend:log", listener);
  },
  onStatus: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on("backend:status", listener);
    return () => ipcRenderer.removeListener("backend:status", listener);
  },
  onExit: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on("backend:exit", listener);
    return () => ipcRenderer.removeListener("backend:exit", listener);
  }
});
