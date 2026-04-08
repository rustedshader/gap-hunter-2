import React from "react";
import type { StatusEvent } from "../types";
import type { AppConfig } from "../types/ui";

type SettingsViewProps = {
  config: AppConfig;
  ollamaStatus: "unknown" | "ok" | "error";
  ollamaModels: string[];
  ollamaLatency: number | null;
  statusEvent: StatusEvent | null;
  logsCount: number;
  onUpdateConfig: (key: keyof AppConfig, value: AppConfig[keyof AppConfig]) => void;
  onTestOllama: () => void;
};

export default function SettingsView({
  config,
  ollamaStatus,
  ollamaModels,
  ollamaLatency,
  statusEvent,
  logsCount,
  onUpdateConfig,
  onTestOllama
}: SettingsViewProps) {
  const isOllama = config.provider === "ollama";
  const hasOllamaModels = ollamaModels.length > 0;
  const showOllamaSelect = isOllama && hasOllamaModels;
  const modelValue = showOllamaSelect && !ollamaModels.includes(config.model)
    ? ""
    : config.model;
  const showModelMismatch = showOllamaSelect && config.model && !ollamaModels.includes(config.model);

  return (
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
            onClick={() => onUpdateConfig("provider", "ollama")}
          >
            Ollama
          </button>
          <button
            className={config.provider === "llamacpp" ? "pill-btn active" : "pill-btn"}
            onClick={() => onUpdateConfig("provider", "llamacpp")}
          >
            Local GGUF
          </button>
        </div>

        <div className="field-group">
          <label>Model name</label>
          {showOllamaSelect ? (
            <>
              <select
                value={modelValue}
                onChange={(event) => onUpdateConfig("model", event.target.value)}
              >
                <option value="" disabled>
                  Select a model
                </option>
                {ollamaModels.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
              {showModelMismatch && (
                <p className="hint">Current model not found in Ollama. Pick from the list.</p>
              )}
            </>
          ) : (
            <input
              type="text"
              value={config.model}
              onChange={(event) => onUpdateConfig("model", event.target.value)}
              placeholder={isOllama ? "Run Test to fetch models" : ""}
            />
          )}
        </div>

        {isOllama ? (
          <>
            <div className="field-group">
              <label>Ollama URL</label>
              <div className="field-row">
                <input
                  type="text"
                  value={config.ollamaUrl}
                  onChange={(event) => onUpdateConfig("ollamaUrl", event.target.value)}
                />
                <button className="ghost" onClick={onTestOllama}>
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
              onChange={(event) => onUpdateConfig("ggufModelPath", event.target.value)}
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
            onChange={(event) => onUpdateConfig("logRetention", Number(event.target.value))}
          />
        </div>

        <label className="toggle">
          <input
            type="checkbox"
            checked={config.autoRefresh}
            onChange={(event) => onUpdateConfig("autoRefresh", event.target.checked)}
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
            <strong>{logsCount}</strong>
          </div>
          <div className="stat">
            <span>Latency</span>
            <strong>{ollamaLatency ? `${ollamaLatency} ms` : "-"}</strong>
          </div>
        </div>
      </section>
    </div>
  );
}
