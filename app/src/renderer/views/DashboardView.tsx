import React from "react";
import type { ExitEvent, LogEntry, StatusEvent } from "../types";
import type { AppConfig, Artifact, Phase } from "../types/ui";
import { formatBytes } from "../utils/analysis";

type SummaryCounts = { functions: number; reports: number };

type DashboardViewProps = {
  runStateLabel: string;
  statusEvent: StatusEvent | null;
  exitInfo: ExitEvent | null;
  progressPct: number;
  phases: Phase[];
  config: AppConfig;
  summaryCounts: SummaryCounts;
  artifacts: Artifact[];
  artifactsPreview: Artifact[];
  logs: LogEntry[];
  recentLogs: LogEntry[];
  ollamaStatus: "unknown" | "ok" | "error";
  ollamaLatency: number | null;
  ollamaModels: string[];
  onOpenRunDir: () => void;
  onViewRun: () => void;
  onViewArtifacts: () => void;
  onRefreshArtifacts: () => void;
  onViewLogs: () => void;
  onTestOllama: () => void;
};

export default function DashboardView({
  runStateLabel,
  statusEvent,
  exitInfo,
  progressPct,
  phases,
  config,
  summaryCounts,
  artifacts,
  artifactsPreview,
  logs,
  recentLogs,
  ollamaStatus,
  ollamaLatency,
  ollamaModels,
  onOpenRunDir,
  onViewRun,
  onViewArtifacts,
  onRefreshArtifacts,
  onViewLogs,
  onTestOllama
}: DashboardViewProps) {
  return (
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
          <button className="ghost" onClick={onOpenRunDir}>
            Open run folder
          </button>
          <button className="ghost" onClick={onViewRun}>
            Edit run
          </button>
        </div>
        <div className="note">Run directory: {config.runDir || "-"}</div>
      </section>

      <section className="card span-6">
        <div className="card-header">
          <div>
            <h2>LLM health</h2>
            <span className="subtle">Provider readiness</span>
          </div>
          {config.provider === "ollama" && (
            <button className="ghost" onClick={onTestOllama}>
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
            <strong>{config.provider === "ollama" ? ollamaStatus : "local"}</strong>
          </div>
          <div className="stat">
            <span>Latency</span>
            <strong>{ollamaLatency ? `${ollamaLatency} ms` : "-"}</strong>
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
        <button className="ghost" onClick={onViewArtifacts}>
          View artifacts
        </button>
      </section>

      <section className="card span-4">
        <div className="card-header">
          <div>
            <h2>Artifacts preview</h2>
            <span className="subtle">Recent outputs</span>
          </div>
          <button className="ghost" onClick={onRefreshArtifacts}>
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
                <button className="ghost" onClick={() => window.api.openPath(artifact.path)}>
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
          <button className="ghost" onClick={onViewLogs}>
            View logs
          </button>
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
  );
}
