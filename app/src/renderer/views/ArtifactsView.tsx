import React from "react";
import type { ExitEvent } from "../types";
import type { Artifact } from "../types/ui";
import { formatBytes } from "../utils/analysis";

type SummaryCounts = { functions: number; reports: number };

type ArtifactsViewProps = {
  artifacts: Artifact[];
  summaryCounts: SummaryCounts;
  exitInfo: ExitEvent | null;
  logsCount: number;
  runDir: string;
  onRefreshArtifacts: () => void;
  onRefreshSummary: () => void;
  onOpenRunDir: () => void;
};

export default function ArtifactsView({
  artifacts,
  summaryCounts,
  exitInfo,
  logsCount,
  runDir,
  onRefreshArtifacts,
  onRefreshSummary,
  onOpenRunDir
}: ArtifactsViewProps) {
  return (
    <div className="grid">
      <section className="card span-8">
        <div className="card-header">
          <div>
            <h2>Artifacts</h2>
            <span className="subtle">Run outputs and files</span>
          </div>
          <div className="inline-actions">
            <button className="ghost" onClick={onRefreshArtifacts}>
              Refresh
            </button>
            <button className="ghost" onClick={onOpenRunDir}>
              Open folder
            </button>
          </div>
        </div>
        <div className="artifact-list">
          {artifacts.length === 0 ? (
            <div className="empty">No artifacts yet.</div>
          ) : (
            artifacts.map((artifact) => (
              <div key={artifact.path} className="artifact">
                <div>
                  <strong>{artifact.name}</strong>
                  <span>{formatBytes(artifact.size)}</span>
                </div>
                <button className="ghost" onClick={() => window.api.openPath(artifact.path)}>
                  Open
                </button>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="card span-4">
        <div className="card-header">
          <div>
            <h2>Run insights</h2>
            <span className="subtle">Summary stats</span>
          </div>
          <button className="ghost" onClick={onRefreshSummary}>
            Refresh summary
          </button>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>Functions</span>
            <strong>{summaryCounts.functions}</strong>
          </div>
          <div className="stat">
            <span>Reports</span>
            <strong>{summaryCounts.reports}</strong>
          </div>
          <div className="stat">
            <span>Exit</span>
            <strong>{exitInfo?.code ?? "-"}</strong>
          </div>
          <div className="stat">
            <span>Log entries</span>
            <strong>{logsCount}</strong>
          </div>
        </div>
        <div className="note">Run directory: {runDir || "-"}</div>
      </section>
    </div>
  );
}
