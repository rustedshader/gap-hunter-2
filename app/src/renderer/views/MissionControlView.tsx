import React, { useMemo } from "react";
import type { BackendEvent, LogEntry, ProcessStats } from "../types";
import type {
  Artifact,
  Phase,
  RevisionReport,
  StatusCounts
} from "../types/ui";
import { NIST_FUNCTIONS } from "../constants";
import { formatBytes, truncate } from "../utils/analysis";

type MissionControlViewProps = {
  runStateLabel: string;
  runOutcomeLabel: string;
  runOutcomeTone: "idle" | "live" | "warning" | "error";
  progressPct: number;
  phases: Phase[];
  policyFileName: string;
  runDir: string;
  provider: string;
  model: string;
  summaryCounts: { functions: number; reports: number };
  sectionsCount: number;
  masterListCount: number;
  assessmentsCount: number;
  coverageCounts: StatusCounts;
  matrixSummary: Record<string, StatusCounts>;
  revisionReport: RevisionReport | null;
  roadmapCounts: { tiers: number; items: number; missing: number };
  artifactsPreview: Artifact[];
  recentLogs: LogEntry[];
  events: BackendEvent[];
  processStats: ProcessStats | null;
  onOpenRunDir: () => void;
  onViewArtifacts: () => void;
  onViewLogs: () => void;
};

const EMPTY_STATUS: StatusCounts = {
  total: 0,
  addressed: 0,
  partiallyAddressed: 0,
  notAddressed: 0,
  outOfScope: 0
};

export default function MissionControlView({
  runStateLabel,
  runOutcomeLabel,
  runOutcomeTone,
  progressPct,
  phases,
  policyFileName,
  runDir,
  provider,
  model,
  summaryCounts,
  sectionsCount,
  masterListCount,
  assessmentsCount,
  coverageCounts,
  matrixSummary,
  revisionReport,
  roadmapCounts,
  artifactsPreview,
  recentLogs,
  events,
  processStats,
  onOpenRunDir,
  onViewArtifacts,
  onViewLogs
}: MissionControlViewProps) {
  const progressValue = Math.min(Math.max(progressPct, 0), 100);
  const coverageTotal = coverageCounts.total || 0;
  const coveragePercent = coverageTotal
    ? Math.round((coverageCounts.addressed / coverageTotal) * 100)
    : 0;

  const coverageGradient = useMemo(() => {
    const safeTotal = coverageTotal || 1;
    const addressedPct = Math.round((coverageCounts.addressed / safeTotal) * 100);
    const partialPct = Math.round(
      (coverageCounts.partiallyAddressed / safeTotal) * 100
    );
    const gapPct = Math.round((coverageCounts.notAddressed / safeTotal) * 100);
    const outPct = Math.max(0, 100 - addressedPct - partialPct - gapPct);
    const stop1 = addressedPct;
    const stop2 = addressedPct + partialPct;
    const stop3 = addressedPct + partialPct + gapPct;
    return `conic-gradient(var(--accent-2) 0 ${stop1}%, var(--warning) ${stop1}% ${stop2}%, var(--danger) ${stop2}% ${stop3}%, rgba(159, 176, 189, 0.4) ${stop3}% ${stop3 + outPct}%)`;
  }, [coverageCounts, coverageTotal]);

  const functionRows = useMemo(() => {
    return NIST_FUNCTIONS.map((name) => {
      const summary = matrixSummary[name] || EMPTY_STATUS;
      const total = summary.total || 1;
      const addressedPct = Math.round((summary.addressed / total) * 100);
      const partialPct = Math.round((summary.partiallyAddressed / total) * 100);
      const gapPct = Math.round((summary.notAddressed / total) * 100);
      const remaining = Math.max(0, 100 - addressedPct - partialPct - gapPct);
      const stop1 = addressedPct;
      const stop2 = addressedPct + partialPct;
      const stop3 = addressedPct + partialPct + gapPct;
      const meterStyle = {
        background: `linear-gradient(90deg, var(--accent-2) 0 ${stop1}%, var(--warning) ${stop1}% ${stop2}%, var(--danger) ${stop2}% ${stop3}%, rgba(159, 176, 189, 0.35) ${stop3}% ${stop3 + remaining}%)`
      };
      return { name, summary, meterStyle };
    });
  }, [matrixSummary]);

  const tickerItems = useMemo(() => {
    if (events.length === 0) {
      return [{ label: "Awaiting pipeline events", time: "" }];
    }
    const base = events.slice(-6).map((event) => ({
      label: event.name,
      time: event.timestamp || ""
    }));
    return [...base, ...base];
  }, [events]);

  const recentLogRows = recentLogs.slice(-4);

  return (
    <div className="grid mission-grid">
      <section className="card span-12 mission-hero">
        <div className="mission-hero-main">
          <div className="mission-hero-text">
            <div className="mission-kicker">Mission Control</div>
            <h2>Gap analysis pipeline, live</h2>
            <p className="mission-lead">
              From Phase 1 extraction through roadmap delivery, every signal in one screen.
            </p>
            <div className="mission-status-row">
              <div className={`status-pill ${runOutcomeTone}`}>
                <span className="status-dot" />
                <span>{runOutcomeLabel}</span>
              </div>
              <div className="mission-chip">Run state: {runStateLabel}</div>
              <div className="mission-chip">Provider: {provider}</div>
              <div className="mission-chip">Model: {model}</div>
            </div>
            <div className="mission-actions">
              <button className="ghost" onClick={onOpenRunDir} disabled={!runDir}>
                Open run folder
              </button>
              <button className="ghost" onClick={onViewLogs}>
                View logs
              </button>
              <button className="ghost" onClick={onViewArtifacts}>
                View artifacts
              </button>
            </div>
          </div>
          <div className="mission-hero-pipeline">
            <div className="mission-hero-progress">
              <div className="mission-hero-progress-header">
                <span className="meta-label">Pipeline progress</span>
                <strong>{progressValue}% complete</strong>
              </div>
              <div className="mission-hero-progress-line">
                <div
                  className={`mission-hero-progress-fill ${runOutcomeTone}`}
                  style={{ width: `${progressValue}%` }}
                />
              </div>
              <div className="mission-hero-stops">
                {phases.map((phase, index) => (
                  <div key={phase.id} className={`mission-hero-stop ${phase.status}`}>
                    <span className="stop-dot" />
                    <div>
                      <strong>{phase.label}</strong>
                      <span className="stop-meta">Phase {index + 1} - {phase.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="mission-hero-metrics">
              <div>
                <span className="meta-label">Policy</span>
                <strong title={policyFileName}>
                  {policyFileName ? truncate(policyFileName, 32) : "-"}
                </strong>
              </div>
              <div>
                <span className="meta-label">Run directory</span>
                <strong title={runDir}>{runDir ? truncate(runDir, 40) : "-"}</strong>
              </div>
              <div>
                <span className="meta-label">Sections</span>
                <strong>{sectionsCount}</strong>
              </div>
              <div>
                <span className="meta-label">Assessments</span>
                <strong>{assessmentsCount}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="card span-12 mission-coverage">
        <div className="card-header">
          <div>
            <h2>Coverage core</h2>
            <span className="subtle">NIST alignment signal</span>
          </div>
        </div>
        <div className="coverage-layout">
          <div className="coverage-ring" style={{ background: coverageGradient }}>
            <div className="coverage-core">
              <strong>{coveragePercent}%</strong>
              <span>Addressed</span>
            </div>
          </div>
          <div className="coverage-details">
            <div className="coverage-legend">
              <div className="legend-item">
                <span className="legend-dot success" />
                <span>Addressed</span>
                <strong>{coverageCounts.addressed}</strong>
              </div>
              <div className="legend-item">
                <span className="legend-dot warning" />
                <span>Partial</span>
                <strong>{coverageCounts.partiallyAddressed}</strong>
              </div>
              <div className="legend-item">
                <span className="legend-dot danger" />
                <span>Gaps</span>
                <strong>{coverageCounts.notAddressed}</strong>
              </div>
              <div className="legend-item">
                <span className="legend-dot muted" />
                <span>Out of scope</span>
                <strong>{coverageCounts.outOfScope}</strong>
              </div>
            </div>
            <div className="function-rows">
              {functionRows.map((row) => (
                <div key={row.name} className="function-row">
                  <div>
                    <strong>{row.name}</strong>
                    <span className="meta-label">{row.summary.total} subcats</span>
                  </div>
                  <div className="function-meter" style={row.meterStyle} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="card span-4 mission-stat">
        <div className="card-header">
          <div>
            <h2>Policy map</h2>
            <span className="subtle">Document coverage</span>
          </div>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>Sections</span>
            <strong>{sectionsCount}</strong>
          </div>
          <div className="stat">
            <span>Master list</span>
            <strong>{masterListCount}</strong>
          </div>
          <div className="stat">
            <span>Functions</span>
            <strong>{summaryCounts.functions}</strong>
          </div>
          <div className="stat">
            <span>Reports</span>
            <strong>{summaryCounts.reports}</strong>
          </div>
        </div>
        <div className="note">Signals from the latest parsed policy run.</div>
      </section>

      <section className="card span-4 mission-stat">
        <div className="card-header">
          <div>
            <h2>Revision delta</h2>
            <span className="subtle">Policy edits</span>
          </div>
        </div>
        {revisionReport ? (
          <div className="stat-grid compact">
            <div className="stat">
              <span>Gaps closed</span>
              <strong>{revisionReport.totalGaps}</strong>
            </div>
            <div className="stat">
              <span>Modified</span>
              <strong>{revisionReport.modifiedSections}</strong>
            </div>
            <div className="stat">
              <span>New sections</span>
              <strong>{revisionReport.newSections}</strong>
            </div>
            <div className="stat">
              <span>Changes</span>
              <strong>{revisionReport.changes.length}</strong>
            </div>
          </div>
        ) : (
          <div className="empty">No revision report yet.</div>
        )}
        <div className="note">Generated via policy revision phase.</div>
      </section>

      <section className="card span-4 mission-stat">
        <div className="card-header">
          <div>
            <h2>Roadmap pulse</h2>
            <span className="subtle">Execution planning</span>
          </div>
        </div>
        <div className="stat-grid compact">
          <div className="stat">
            <span>Tiers</span>
            <strong>{roadmapCounts.tiers}</strong>
          </div>
          <div className="stat">
            <span>Initiatives</span>
            <strong>{roadmapCounts.items}</strong>
          </div>
          <div className="stat">
            <span>Missing docs</span>
            <strong>{roadmapCounts.missing}</strong>
          </div>
          <div className="stat">
            <span>Run dir</span>
            <strong title={runDir}>{runDir ? truncate(runDir, 40) : "-"}</strong>
          </div>
        </div>
        <div className="note">Actionable priorities and doc gaps.</div>
      </section>

      <section className="card span-7 mission-artifacts">
        <div className="card-header">
          <div>
            <h2>Artifacts dock</h2>
            <span className="subtle">Latest outputs</span>
          </div>
          <button className="ghost" onClick={onViewArtifacts}>
            View artifacts
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

      <section className="card span-5 mission-telemetry">
        <div className="card-header">
          <div>
            <h2>Telemetry</h2>
            <span className="subtle">Events and system pulse</span>
          </div>
          <button className="ghost" onClick={onViewLogs}>
            View logs
          </button>
        </div>
        <div className="telemetry-metrics">
          <div className="telemetry-chip">
            <span>App RSS</span>
            <strong>
              {processStats?.app?.rssMb ? `${processStats.app.rssMb.toFixed(1)} MB` : "-"}
            </strong>
          </div>
          <div className="telemetry-chip">
            <span>Heap used</span>
            <strong>
              {processStats?.app?.heapUsedMb
                ? `${processStats.app.heapUsedMb.toFixed(1)} MB`
                : "-"}
            </strong>
          </div>
          <div className="telemetry-chip">
            <span>Backend CPU</span>
            <strong>
              {processStats?.backend?.cpuPercent != null
                ? `${processStats.backend.cpuPercent.toFixed(1)}%`
                : "-"}
            </strong>
          </div>
          <div className="telemetry-chip">
            <span>Backend RAM</span>
            <strong>
              {processStats?.backend?.memoryMb != null
                ? `${processStats.backend.memoryMb.toFixed(1)} MB`
                : "-"}
            </strong>
          </div>
        </div>
        <div className={`mission-ticker ${events.length === 0 ? "idle" : ""}`}>
          <div className="mission-ticker-track">
            {tickerItems.map((item, index) => (
              <div key={`${item.label}-${index}`} className="mission-ticker-item">
                <strong>{item.label}</strong>
                <span>{item.time}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mission-log-list">
          {recentLogRows.length === 0 ? (
            <div className="empty">No log activity yet.</div>
          ) : (
            recentLogRows.map((entry, index) => (
              <div key={`${entry.time}-${index}`} className={`mission-log ${entry.level.toLowerCase()}`}>
                <span className="mission-log-time">{entry.time}</span>
                <span className="mission-log-message">
                  <strong>{entry.logger}</strong> {truncate(entry.message, 90)}
                </span>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
