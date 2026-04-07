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
  openPath: (targetPath) => ipcRenderer.invoke("shell:open-path", targetPath),
  testOllama: (url) => ipcRenderer.invoke("ollama:test", url),
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
