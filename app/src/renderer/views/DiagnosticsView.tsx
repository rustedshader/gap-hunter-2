import React from "react";
import type { AppInfo, ProcessStats } from "../types";

type DiagnosticsViewProps = {
  appInfo: AppInfo | null;
  processStats: ProcessStats | null;
  runDir: string;
  debugLog: string;
  onLoadDebugLog: () => void;
  runDataState: {
    state: string;
    updatedAt?: string;
    runId?: string | null;
    error?: string;
  };
  artifactState: {
    state: string;
    updatedAt?: string;
    runId?: string | null;
    error?: string;
  };
  runStatus: string | null;
  lastHeartbeat: string | null;
};

export default function DiagnosticsView({
  appInfo,
  processStats,
  runDir,
  debugLog,
  onLoadDebugLog,
  runDataState,
  artifactState,
  runStatus,
  lastHeartbeat
}: DiagnosticsViewProps) {
  return (
    <div className="grid">
      <section className="card span-6">
        <div className="card-header">
          <div>
            <h2>Environment snapshot</h2>
            <span className="subtle">System and runtime info</span>
          </div>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>App</span>
            <strong>{appInfo?.appVersion || "-"}</strong>
          </div>
          <div className="stat">
            <span>Electron</span>
            <strong>{appInfo?.electron || "-"}</strong>
          </div>
          <div className="stat">
            <span>Node</span>
            <strong>{appInfo?.node || "-"}</strong>
          </div>
          <div className="stat">
            <span>Platform</span>
            <strong>{appInfo?.platform || "-"}</strong>
          </div>
        </div>
        <div className="note">Active run: {runDir || "-"}</div>
      </section>

      <section className="card span-6">
        <div className="card-header">
          <div>
            <h2>Resource monitor</h2>
            <span className="subtle">App and backend usage</span>
          </div>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>App RSS</span>
            <strong>
              {processStats?.app?.rssMb
                ? `${processStats.app.rssMb.toFixed(1)} MB`
                : "-"}
            </strong>
          </div>
          <div className="stat">
            <span>Heap used</span>
            <strong>
              {processStats?.app?.heapUsedMb
                ? `${processStats.app.heapUsedMb.toFixed(1)} MB`
                : "-"}
            </strong>
          </div>
          <div className="stat">
            <span>Backend CPU</span>
            <strong>
              {processStats?.backend?.cpuPercent != null
                ? `${processStats.backend.cpuPercent.toFixed(1)}%`
                : "-"}
            </strong>
          </div>
          <div className="stat">
            <span>Backend memory</span>
            <strong>
              {processStats?.backend?.memoryMb != null
                ? `${processStats.backend.memoryMb.toFixed(1)} MB`
                : "-"}
            </strong>
          </div>
        </div>
        <div className="note">Last updated: {processStats?.timestamp || "-"}</div>
      </section>

      <section className="card span-6">
        <div className="card-header">
          <div>
            <h2>Run integrity</h2>
            <span className="subtle">State and freshness signals</span>
          </div>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>Status</span>
            <strong>{runStatus || "-"}</strong>
          </div>
          <div className="stat">
            <span>Heartbeat</span>
            <strong>{lastHeartbeat || "-"}</strong>
          </div>
          <div className="stat">
            <span>Run data</span>
            <strong>{runDataState.state}</strong>
          </div>
          <div className="stat">
            <span>Artifacts</span>
            <strong>{artifactState.state}</strong>
          </div>
        </div>
        <div className="note">
          Data refreshed: {runDataState.updatedAt || "-"}
        </div>
        <div className="note">
          Artifacts refreshed: {artifactState.updatedAt || "-"}
        </div>
        {runDataState.error && <div className="note">Run data error: {runDataState.error}</div>}
      </section>

      <section className="card span-12">
        <div className="card-header">
          <div>
            <h2>Debug log</h2>
            <span className="subtle">Backend debug trace</span>
          </div>
          <button className="ghost" onClick={onLoadDebugLog}>
            Load debug log
          </button>
        </div>
        <div className="policy-panel">
          <pre>{debugLog || "No debug log loaded."}</pre>
        </div>
      </section>
    </div>
  );
}
